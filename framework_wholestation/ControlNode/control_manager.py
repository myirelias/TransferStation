# !/usr/bin/env python
# coding=utf-8

import config as setting
from ControlNode.control_task import ControlTask
from ControlNode.control_data import ControlData
import pika
import time
from multiprocessing import Process
import json
import datetime


class ControlManager(object):
    """
    控制管理器，负责调度任务管理器和数据管理器
    """

    def __init__(self, **kw):
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
        print('controlmanager init finsh')

    # 使用多进程之后操作消息通道报错，添加该方法，每次连接进行该操作
    @staticmethod
    def _manager_connect_rabbitmq(**kw):
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
        return channel

    def manager_publish_task(self, start_url):
        """
        任务发布
        :param start_url: 起始url
        :return:
        """
        task_manager = ControlTask()
        # 启动时候提供起始url：start_url
        task_manager.task_check(start_url, domin=setting.DOMAIN)
        # 启动后一直循环执行
        while True:
            # 每个小时存储一次已抓取数据 或者每天23点存一次
            if datetime.datetime.now().strftime('%M') == '00' or datetime.datetime.now().strftime('%H') == '23':
                task_manager.task_save(task_manager.old_urls, '../DATA/old_urls.txt')
            # 每天零点检查抓取是否完成，如果完成则发布起始url循环抓取，此处跟据实际需求调整
            elif int(datetime.datetime.now().strftime('%H')) == 0:
                self._manager_check_none()
            while task_manager.task_has_new():  # 只要存在新增任务则会往对应队列里面推送
                static_task, unstatic_task = task_manager.task_static_unstatic(setting.REGEX_URL)
                self._manager_push_msg(static_task, qname=setting.TASK_NAME + '_task_static')
                self._manager_push_msg(unstatic_task, qname=setting.TASK_NAME + '_task_unstatic')
            try:
                url = self._manager_getone_msg(qname=setting.TASK_NAME + '_continue')
                if url:
                    task_manager.task_check(url.decode('utf-8'), domin=setting.DOMAIN)
                else:
                    time.sleep(2)
            except Exception as e:
                print(e)

    def manager_deal_result(self, **kw):
        """
        处理结果队列
        :return:
        """
        while True:
            # 取出结果队列中的数据，此处结果队列应返回dict类型的结果
            result = self._manager_getone_msg(qname='%s_%s' % (setting.TASK_NAME, 'result'))
            if result:
                try:
                    result_dict = json.loads(result)
                except Exception as e:
                    print(e)
                    continue
                content = result_dict.get('content')
                urls = result_dict.get('urls')
                if content:
                    pushdata = json.dumps(content)
                    self._manager_push_msg(pushdata, qname='%s_%s' % (setting.TASK_NAME, 'data'))
                if urls:
                    # 此处对url进行处理 针对不同网站处理不同 后期需要单独封装这块
                    # -----------BEGIN--------------单独封装--------------BEGIN--------------
                    current_url = result_dict.get('url')
                    current_urllist = []
                    for eachurl in urls:
                        # 此处过滤
                        if 'http' not in eachurl:
                            newurl = '/'.join(current_url.split('/')[0:3]) + '/' + eachurl
                            current_urllist.append(newurl)
                        else:
                            current_urllist.append(eachurl)
                    # -----------END----------------单独封装--------------END----------------
                    self._manager_push_msg(current_urllist, qname='%s_%s' % (setting.TASK_NAME, 'continue'))
            else:
                time.sleep(2)

    def manager_save_data(self, **kw):
        """
        存储数据
        配置参数：
        dbname: 数据库名称 colname:集合名称
        :return:
        """
        data_manager = ControlData()
        while True:
            # 从数据队列中取之并进行存储
            data = self._manager_getone_msg(qname='%s_%s' % (setting.TASK_NAME, 'data'))
            if data:
                save_data = json.loads(data)
                data_manager.data_save_db(data=save_data, dbname=kw.get('dbname', 'db_' + setting.TASK_NAME),
                                          colname=kw.get('colname', 'col_' + setting.TASK_NAME))
            else:
                time.sleep(10)

    def _manager_push_msg(self, data, **kw):
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
        channel = self._manager_connect_rabbitmq()

        for eachdata in pushdata:
            channel.basic_publish(
                exchange=kw.get('exchange', ''),
                routing_key=kw.get('qname', 'default'),
                body=eachdata,
                properties=pika.BasicProperties(
                    delivery_mode=2  # 消息持久化
                )
            )

    def _manager_getone_msg(self, **kw):
        """
        获取消息队列中的信息
        :param kw:
        :return:
        """
        # 创建一个消息通道
        channel = self._manager_connect_rabbitmq()
        method, header, body = channel.basic_get(
            queue=kw.get('qname', 'default')
        )
        if not method:
            return
        else:
            channel.basic_ack(delivery_tag=method.delivery_tag)
            return body

    def _manager_check_none(self):
        """
        校验如果非静态队列如果没有url则发布起始url进行循环抓取
        :return:
        """
        have_task = self._manager_getone_msg(qname='%s_%s' % (setting.TASK_NAME, 'unstatic'))
        if not have_task:
            self._manager_push_msg(setting.START_URL, qname='%s_%s' % (setting.TASK_NAME, 'unstatic'))


if __name__ == '__main__':

    manager = ControlManager()
    # 创建3个进程，分别进行任务发布，结果处理以及数据存储
    proc_task = Process(target=manager.manager_publish_task, args=(setting.START_URL,))  # 此处填写启动url
    proc_result = Process(target=manager.manager_deal_result)
    proc_data = Process(target=manager.manager_save_data)
    proc_task.start()
    proc_result.start()
    proc_data.start()