# !/usr/bin/env python
# coding=UTF-8

import time
from hashlib import md5
import pickle
import json
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
            self.maxtime = self._engine_load_cpickle()
        except:
            self.maxtime = {}

    def _engine_allnews(self):
        """
        获取所有新闻链接
        :return: 返回新闻信息字典
        """
        url = 'http://qc.wa.news.cn/nodeart/list'
        allnews_list = []
        for each in setting.NID:
            for k, v in each.items():
                position = k
                nid = v

            params = setting.PARAMS_NEWS
            params['nid'] = nid
            pagenum = 0
            noinfonum = 0
            while True:
                # 当当前日期不大于已抓取最大日期，且连续翻页10页时，则认定为无新增新闻，则break
                if noinfonum == 10:
                    break
                pagenum += 1
                params['pgnum'] = str(pagenum)
                content = self.crawl.crawl_get_content(url, params=params, headers=setting.HEADERS,
                                                       proxies=self._engine_use_proxy())
                try:
                    res = json.loads(content[1:-1])
                except Exception as e:
                    res = {}
                    print(e)
                if res.get('data'):
                    reslist = res.get('data', {}).get('list', [])
                    for each in reslist:
                        savedict = {}
                        publish = each.get('PubTime', '')
                        if self._engine_mk_timestamp(publish) > float(self.maxtime[position]):
                            # DocID = each.get('DocID', '')
                            # NodeId = each.get('NodeId', '')
                            # intro = each.get('Abstract', '')
                            # keyword = each.get('keyword', '')
                            # editor = each.get('Editor', '')
                            # author = each.get('Author', '')
                            # source = each.get('SourceName', '')
                            # pics = each.get('allPics', '')
                            savedict['title'] = each.get('Title', '')
                            savedict['position'] = position
                            savedict['link'] = each.get('LinkUrl', '')
                            allnews_list.append(savedict)
                            self.maxtime[position] = str(self._engine_mk_timestamp(publish))
                        else:
                            print('无新增新闻')
                            noinfonum += 1
                            break
                else:
                    break
                time.sleep(0.5)

        return allnews_list

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
        # if news_info.get('title'):
        self.pipe.pipe_save_db(news_info, dbname='db_xinhua_news', colname='col_sz_df_fz')
        time.sleep(0.5)

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
        with open('DATA/' + setting.FILE_MAXTIME, 'wb') as f:
            pickle.dump(data, f)

    @staticmethod
    def _engine_load_cpickle():
        """
        读取文本中的数据并放到内容中
        """
        with open('DATA/' + setting.FILE_MAXTIME, 'rb') as f:
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

    @staticmethod
    def _engine_mk_timestamp(timestr):
        """
        将时间格式字符串转换为时间戳
        :param timestr: 时间格式的字符串
        :return:
        """
        try:
            timemodel = time.strptime(timestr, '%Y-%m-%d %H:%M:%S')
            timestamp = time.mktime(timemodel)
        except:
            return

        return timestamp

    def excute(self):
        newslist = self._engine_allnews()
        print('新增新闻数量 %s' % len(newslist))
        for eachnews in newslist:
            self._engine_update_news(eachnews)
        print('目前最大时间 %s' % self.maxtime)
        self._engine_cpickle_data(self.maxtime)


if __name__ == '__main__':
    start = time.time()
    proc = Engine()
    proc.excute()
    end = time.time()
    print('[%.1f s] script finish ' % (end - start))
