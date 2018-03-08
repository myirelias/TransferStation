# !/usr/bin/env python
# coding=utf-8

from SpiderNode.spider_crawl import SpiderCrawl
from SpiderNode.spider_resolve import SpiderResolve
import config as setting
import pika
import time
import json
from multiprocessing import Process


class SpiderSchedule(object):
    """
    爬虫调度节点
    """

    def __init__(self, **kw):
        self.crawl = SpiderCrawl()
        self.resolve = SpiderResolve()
        # 创建rabbitmq消息队列，队列命名通过配置文件中TASK_NAME来确定
        # 参数设置：user: 用户名 psw: 密码 host: 主机ip port: 端口号 vhost: 虚拟主机
        # 消息队列：
        # task_unstatic: 任务队列，控制节点用于发布需要抓取的非静态(非新闻，如列表页面)任务
        # task_static: 任务队列，控制节点用于发布需要抓取的静态(新闻内容页面)任务
        # result: 结果队列，主要用于爬虫节点反馈爬取结果的队列
        # continue:新增队列，用于数据处理器获取其中反馈的新任务交给任务管理器
        # data: 数据存储队列，用于数据处理器获取其中需要存储的数据进行储存
        self.queue_name = ['task_unstatic', 'task_static', 'result', 'continue', 'data']
        # 创建登录验证信息
        admin = pika.PlainCredentials(kw.get('user', 'bana'), kw.get('psw', 'root'))
        # 创建rabbitmq链接
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=kw.get('host', '192.168.2.75'),
            port=kw.get('port', 5672),
            virtual_host=kw.get('vhost', '/'),
            credentials=admin
        ))
        # 创建消息通道
        channel = connection.channel()
        # 声明消息队列
        for each in self.queue_name:
            qname = '%s_%s' % (setting.TASK_NAME, each)
            channel.queue_declare(
                queue=qname,
                durable=True
            )
        print('spiderschedule init finsh')

    @staticmethod
    def _schedule_connect_rabbitmq(**kw):
        """
        创建rabbitmq服务，打开消息通道
        :param kw: 参数配置
        :return: 消息通道
        """
        admin = pika.PlainCredentials(kw.get('user', 'bana'), kw.get('psw', 'root'))
        connect = pika.BlockingConnection(pika.ConnectionParameters(
            host=kw.get('host', '192.168.2.75'),
            port=kw.get('port', 5672),
            virtual_host=kw.get('vhost', '/'),
            credentials=admin
        ))
        channel = connect.channel()

        return channel

    def schedule_static_spider(self):
        """
        启动静态新闻爬虫
        :return:
        """
        while True:
            try:
                url = self._schedule_pullone_msg(qname='%s_%s' % (setting.TASK_NAME, 'task_static'))
                if url:
                    print('recive task %s' % url.decode('utf-8'))
                    current_headers = setting.HEADERS
                    current_headers['Proxy-Switch-Ip'] = 'yes'
                    content = self.crawl.crawl_get_content(url, headers=current_headers,
                                                           proxies=self._schedule_use_proxy())
                    res_dict = {}
                    for eachxpath in setting.XPATHER_NEWS_LIST:
                        res_dict = self.resolve.spider_content_data(content=content, xpather=eachxpath)
                        if res_dict.get('title'):
                            break
                    res_dict['url'] = url.decode('utf-8')
                    res = {'url': url.decode('utf-8'), 'content': res_dict}
                    savedata = json.dumps(res)  # 存储到rabbitmq之前需要将dict转为字符串
                    self._schedule_push_msg(savedata, qname='%s_%s' % (setting.TASK_NAME, 'result'))
                    time.sleep(1)
                else:
                    print('[static]no task')
                    time.sleep(2)
            except Exception as e:
                print('get static url error %s' % e)
                time.sleep(10)

    def schedule_unstatic_spider(self):
        """
        启动非静态新闻爬虫
        :return:
        """

        while True:
            try:
                url = self._schedule_pullone_msg(qname='%s_%s' % (setting.TASK_NAME, 'task_unstatic'))
                if url:
                    print('recive task %s' % url.decode('utf-8'))
                    current_headers = setting.HEADERS
                    current_headers['Proxy-Switch-Ip'] = 'yes'
                    content = self.crawl.crawl_get_content(url, headers=current_headers,
                                                           proxies=self._schedule_use_proxy())
                    res_list = self.resolve.spider_content_data(content=content, xpather=setting.XPATHER_HREF)
                    res = {'url': url.decode('utf-8'), 'urls': res_list}
                    savedata = json.dumps(res)  # 存储到rabbitmq之前需要将dict转为字符串
                    self._schedule_push_msg(savedata, qname='%s_%s' % (setting.TASK_NAME, 'result'))
                    time.sleep(1)
                else:
                    print('[unstatic]no task')
                    time.sleep(2)
            except Exception as e:
                print('get unstatic url error %s' % e)
                time.sleep(10)

    def _schedule_pullone_msg(self, **kw):
        """
        获取消息队列中的信息
        :param kw:
        :return:
        """
        # 创建一个消息通道
        channel = self._schedule_connect_rabbitmq()
        method, header, body = channel.basic_get(
            queue=kw.get('qname', 'default')
        )
        if not method:
            return
        else:
            channel.basic_ack(delivery_tag=method.delivery_tag)
            return body

    def _schedule_push_msg(self, data, **kw):
        """
        推送消息到消息队列
        配置参数：
        exchange:交换机 qname:消息队列名称
        :param data: 待推送的内容
        :param kw: 配置参数
        :return:
        """
        if isinstance(data, str):
            pushdata = [data]
        elif isinstance(data, list):
            pushdata = data
        else:
            print('data must be list or str')
            return
        channel = self._schedule_connect_rabbitmq()
        for eachdata in pushdata:
            channel.basic_publish(
                exchange=kw.get('exchange', ''),
                routing_key=kw.get('qname', 'default'),
                body=eachdata,
                properties=pika.BasicProperties(
                    delivery_mode=2  # 消息持久化
                )
            )

    @staticmethod
    def _schedule_use_proxy():
        """
        使用代理ip
        :return: 代理ip
        """
        proxy_host = "proxy.abuyun.com"
        proxy_port = "9010"
        proxy_user = "HY3JE71Z6CDS782P"
        proxy_pass = "CE68530DAD880F3B"
        proxy_meta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {"host": proxy_host,
                                                                     "port": proxy_port,
                                                                     "user": proxy_user,
                                                                     "pass": proxy_pass}
        proxies = {"http": proxy_meta,
                   "https": proxy_meta}

        return proxies


if __name__ == '__main__':
    spider = SpiderSchedule()
    proc_static = Process(target=spider.schedule_static_spider)
    proc_unstatic = Process(target=spider.schedule_unstatic_spider)
    # spider.schedule_static_spider()
    # spider.schedule_unstatic_spider()
    proc_unstatic.start()
    proc_static.start()