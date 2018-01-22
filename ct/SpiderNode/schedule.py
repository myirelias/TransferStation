# !/usr/bin/env python
# coding=UTF-8

from multiprocessing.managers import BaseManager
from SpiderNode.spider_crawl import SpiderCrawl
from SpiderNode.spider_xpath import SpiderXpather
import SpiderNode.setting as setting
import time
import re


class Schedule(object):

    def __init__(self):
        self.crawl = SpiderCrawl()
        self.xpather = SpiderXpather()
        # 注册网络队列
        BaseManager.register('get_url_q')
        BaseManager.register('get_result_q')
        manager = BaseManager(address=('127.0.0.1', 8898), authkey='ajiao'.encode('UTF-8'))
        manager.connect()
        self.url_q = manager.get_url_q()
        self.result_q = manager.get_result_q()
        print('init finish')

    def start_spider(self):
        print('爬虫节点启动')
        while True:
            try:
                if not self.url_q.empty():
                    url = self.url_q.get(True)
                    print('获取到任务 %s' % url)
                    realurl = self._schedule_re(url)
                    if realurl:
                        content = self.crawl.crawl_get_content(url, pagecode='UTF-8', proxies=self._schedule_proxies(),
                                                               headers=setting.HEADERS)
                        for eachxpath in setting.XPATHLIST:
                            res = self.xpather.xpath_content_data(content=content, xpather=eachxpath)
                            if res.get('title', '') == '':
                                continue
                            else:
                                break
                        res['url'] = url
                        resdict = {'url': url, 'content': res}
                    else:
                        content = self.crawl.crawl_get_content(url, pagecode='UTF-8', proxies=self._schedule_proxies(),
                                                               headers=setting.HEADERS)
                        resdict = self._schedule_xpath(content)
                    if isinstance(resdict, list):
                        for each in resdict:
                            self.result_q.put(each)
                    else:
                        self.result_q.put(resdict)
                    time.sleep(2)
            except Exception as e:
                print('[error] %s ' % e)
                continue

    def _schedule_xpath(self, content):
        """
        页面数据处理
        :param content:
        :return:
        """
        xpther_url = ".//@href"
        res = self.xpather.xpath_content_data(content=content, xpather=xpther_url)
        reslist = []
        for eachurl in res:
            if 'cctv.com' in eachurl or 'cctv.cn' in eachurl or 'cntv.cn' in eachurl:
                resdict = {'url': eachurl, 'content': ''}
                reslist.append(resdict)
        return reslist

    @staticmethod
    def _schedule_re(urlstr):
        """
        正则过滤url
        :param urlstr: 需要过滤的url
        :return:
        """
        pattern = re.compile(r'/\d{4}/\d{2}/\d{2}/.*?\.shtml')
        res = re.search(pattern, urlstr)
        if res:
            return str(res.group())
        return

    @staticmethod
    def _schedule_proxies():
        """
        使用代理ip
        :return: 代理ip
        """
        pass


if __name__ == '__main__':
    sche = Schedule()
    sche.start_spider()
