# !/usr/bin/env python
# coding=UTF-8

import time
from luminosity_crawl import Crawl
from luminosity_spider import Spider
from luminosity_pipe import Pipe
from luminosity_tools import Tools
import luminosity_setting as setting
import threading


class Engine(object):
    """
    逻辑处理类，负责调用所有功能类并进行一定的逻辑运算
    """
    def __init__(self):
        self.crawl = Crawl()
        self.spider = Spider()
        self.pipe = Pipe()
        self.tools = Tools()
        self.urls = set([])
        # 加载已抓取过的链接记录文本
        try:
            self.old_urls = self.pipe.pipe_load_pickle(setting.FN_OLD_URLS)
        except:
            self.old_urls = set([])
        self.new_urls = set([])

    def engine_get_urls(self, url=setting.START_URL):
        """
        从指定网址获取页面所有url
        :param url:
        :return: urls列表
        """
        content_start = self.crawl.crawl_get_content(url, headers=setting.HEADERS)
        res_start = self.spider.spider_content_data(content=content_start, xpather=setting.XPATHER_HREF)

        return res_start

    def engine_check_urls(self, urls):
        """
        url校验，新增入新增队列，已抓取则丢弃
        :return:
        """
        current_urls = set([])  # 当前新增的所有url
        for each in urls:
            if 'http' not in each and each:
                current_urls.add(setting.START_URL + each)
            elif 'gmw' in each:
                current_urls.add(each)
        # url校验 没有抓取的为new 已抓取的为old
        while current_urls:
            url_current = current_urls.pop()
            md5code = self.tools.tool_md5(url_current)
            if md5code not in self.old_urls:
                self.new_urls.add(url_current)
                self.old_urls.add(md5code)

    def engine_publish_task(self):
        """
        分发url到rabbitmq消息队列中
        :return:
        """
        static_url_list = []
        unstatic_url_list = []
        while self.new_urls:
            current_url = self.new_urls.pop()
            static_url = self.tools.tool_regex(current_url)
            if static_url:
                # 推送到静态消息队列
                static_url_list.append(current_url)
            else:
                # 推送至列表消息队列继续抓取
                unstatic_url_list.append(current_url)
        # 推送至静态消息队列
        if static_url_list:
            self.pipe.pipe_push_rabbitmq(static_url_list, qname='test_static_urls')
        # 推送至非静态消息队列
        if unstatic_url_list:
            self.pipe.pipe_push_rabbitmq(unstatic_url_list, qname='test_unstatic_urls')
        self.pipe.pipe_dump_pickle(self.old_urls, setting.FN_OLD_URLS)

    def engine_get_unstatic(self):
        """
        获取非静态任务，循环执行
        :return:
        """
        while True:
            unstatic_url = self.pipe.pipe_pullone_rabbitmq(qname='test_unstatic_urls')  # 取出一条非静态url进行抓取
            # 非静态url抓取
            if unstatic_url:
                urls_list = self.engine_get_urls(unstatic_url)
                self.engine_check_urls(urls_list)
                self.engine_publish_task()
            else:
                self.new_urls.add(setting.START_URL)
                self.engine_publish_task()

    def engine_get_static(self):
        """
        获取静态任务，循环执行
        :return:
        """
        while True:
            static_url = self.pipe.pipe_pullone_rabbitmq(qname='test_static_urls')
            # 静态url抓取
            if static_url:
                current_headers = setting.HEADERS
                current_headers['Switch-Proxy-Ip'] = 'yes'
                content_news = self.crawl.crawl_get_content(static_url, headers=current_headers,
                                                            proxies=self.tools.tool_proxies())
                for eachxpath in setting.XPATHER_NEWS_LIST:
                    res_news = self.spider.spider_content_data(content=content_news, xpather=eachxpath)
                    if res_news.get('title'):
                        break
                res_news['url'] = static_url.decode('gbk')
                self.pipe.pipe_save_db(res_news, dbname='db_guangmingnet', colname='test_news')
            else:
                time.sleep(2)

    def excute(self):
        urls = self.engine_get_urls()
        self.engine_check_urls(urls)
        self.engine_publish_task()
        proc_unstatic = threading.Thread(target=self.engine_get_unstatic)
        proc_static = threading.Thread(target=self.engine_get_static)
        # self.engine_get_unstatic()
        # self.engine_get_static()
        proc_static.start()
        proc_unstatic.start()
        proc_static.join()
        proc_unstatic.join()


if __name__ == '__main__':
    start = time.time()
    proc = Engine()
    proc.excute()
    end = time.time()
    print('[%.1f s] script finish ' % (end - start))
