# !/usr/bin/env python
# coding=UTF-8

import time
from hashlib import md5
import pickle
from news_crawl import Crawl
from news_spider import Spider
from news_pipe import Pipe
import news_setting as setting


class Engine(object):

    def __init__(self):
        self.crawl = Crawl()
        self.spider = Spider()
        self.pipe = Pipe()
        try:
            self.old_news = set(self._engine_load_cpickle())
        except:
            self.old_news = set([])

    def _engine_allnews(self):
        """
        获取人事、理论、舆情版块所有新闻
        :return: 所有新闻链接
        """

        news_list = []
        for each in [setting.URL_RENSHI, setting.URL_LILUN, setting.URL_YUQING]:
            for position, eachurl in each.items():
                position = position
                eachurl = eachurl

            content = self.crawl.crawl_get_content(url=eachurl)
            XPATHER_ALLNEWS = ".//*[@class='clearfix']/h3/a"
            allnews = self.spider.spider_content_data(content=content, xpather=XPATHER_ALLNEWS)
            XPATHER_EACHNEWS = {"title": ".//text()", "link": ".//@href"}
            for eachnews in allnews:
                eachinfo = self.spider.spider_content_data(content=eachnews,
                                                           xpather=XPATHER_EACHNEWS)
                eachinfo['position'] = position
                news_list.append(eachinfo)
            time.sleep(2)

        return news_list

    def _engine_update_news(self, news_dict):
        """
        抓取新的新闻数据并入库
        :param news_dict:新闻字典，包含url和title
        :return:
        """

        if not isinstance(news_dict, dict):
            return

        url = news_dict.get('link')
        title = news_dict.get('title')

        md5_url = self._engine_get_md5(url)

        if md5_url not in self.old_news:
            print('新增新闻 %s' % title)
            content_news = self.crawl.crawl_get_content(url, proxies=self._engine_use_proxy(),
                                                        headers=setting.HEADERS)
            for eachxpather in setting.XPATHER_NEWS_INFO:
                news_info = self.spider.spider_content_data(content=content_news, xpather=eachxpather)
                if news_info.get('title'):
                    break

            news_info['url'] = url
            news_info['position'] = news_dict.get('position')
            news_info['out_title'] = title
            if news_info.get('title'):
                self.pipe.pipe_save_db(news_info, dbname='db_xinhua_news', colname='col_rs_yq_ll')
            self.old_news.add(md5_url)
            time.sleep(0.5)
        else:
            return

    @staticmethod
    def _engine_get_md5(data):
        """
        对数据进行md5加密
        """
        m = md5()
        m.update(data.encode('UTF_8'))
        md5code = m.hexdigest()

        return md5code

    @staticmethod
    def _engine_cpickle_data(data):
        """
        持久化内存中的数据并存储到文本中
        """
        with open('DATA/' + setting.FILE_OLDNEWS, 'wb') as f:
            pickle.dump(data, f)

    @staticmethod
    def _engine_load_cpickle():
        """
        读取文本中的数据并放到内容中
        """
        with open('DATA/' + setting.FILE_OLDNEWS, 'rb') as f:
            return pickle.load(f)

    @staticmethod
    def _engine_use_proxy():
        """代理"""
        # 要访问的目标页面
        # targetUrl = "http://test.abuyun.com/proxy.php"
        # 代理服务器
        proxyhost = "proxy.abuyun.com"
        # proxyPort = "9020"
        proxyport = "9010"
        # 代理隧道验证信息
        proxyuser = "HY3JE71Z6CDS782P"
        proxypass = "CE68530DAD880F3B"
        proxymeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {"host": proxyhost,
                                                                    "port": proxyport,
                                                                    "user": proxyuser,
                                                                    "pass": proxypass}
        proxies = {"http": proxymeta,
                   "https": proxymeta}

        return proxies

    def excute(self):
        news_list = self._engine_allnews()
        for eachnews in news_list:
            self._engine_update_news(eachnews)
        self._engine_cpickle_data(self.old_news)


if __name__ == '__main__':
    start = time.time()
    proc = Engine()
    proc.excute()
    end = time.time()
    print('[%.1f s] script finish ' % (end - start))