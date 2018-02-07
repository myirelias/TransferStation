# !/usr/bin/env python
# coding=UTF-8

import time
from hashlib import md5
import pickle
from tourism_administration_crawl import Crawl
from tourism_administration_spider import Spider
from tourism_administration_pipe import Pipe
import tourism_administration_setting as setting
from tools import SomeTools


class Engine(object):
    def __init__(self):
        self.crawl = Crawl()
        self.spider = Spider()
        self.pipe = Pipe()
        self.tools = SomeTools()
        self.urls = []
        self.current_news = []
        try:
            self.old_news = self._engine_load_pickle(setting.FILE_OLD_NEWS)
        except:
            self.old_news = set([])

    def _engine_get_allurls(self):
        start_url = 'http://www.cnta.gov.cn/xxfb/'
        content_door = self.crawl.crawl_get_content(start_url, headers=setting.HEADERS)
        res_door = self.spider.spider_content_data(content=content_door, xpather=setting.XPATHER_START_HREF)

        for eachdoor in res_door:
            # 时政新闻和每日更新版块分别单独抓取
            if eachdoor in ['./szxw/', './mrgx/']:
                continue
            url_door = 'http://www.cnta.gov.cn/xxfb'
            url_start = url_door + eachdoor.replace('.', '')
            count_page = 0
            while True:
                # 初始页url构建不同
                if count_page == 0:
                    url_page = url_start + 'index.shtml'
                else:
                    url_page = url_start + 'index_%s.shtml' % count_page
                content_page = self.crawl.crawl_get_content(url_page, headers=setting.HEADERS,
                                                            proxies=self.tools.tool_use_proxy())
                res_urls = self.spider.spider_content_data(content=content_page, xpather=setting.XPATHER_EACH_URLS)
                for each_url in res_urls:
                    # 构建详情url
                    url_detail = url_start + each_url[2:]
                    self.urls.append(url_detail)

                if not res_urls:
                    break
                if self.old_news and count_page >= 10:
                    print('这不是第一次抓取，只抓10页面', count_page)
                    break
                # time.sleep(2)
                count_page += 1

    def _engine_get_szxw(self):
        """
        获取时政新闻版块数据，并增量更新
        :return:
        """
        start_url_szxw = 'http://www.gov.cn/pushinfo/v150203/pushinfo.js'
        content_szxw = self.crawl.crawl_get_content(start_url_szxw, proxies=self.tools.tool_use_proxy(),
                                                    headers=setting.HEADERS)
        urls_szxw = self.spider.spider_content_data(content=content_szxw, xpather=setting.XPATHER_SZ_URLS)
        for eachurl in urls_szxw:
            self.urls.append(eachurl)

    def _engine_get_daily(self):
        """
        每日更新版块数据urls
        :return:
        """
        start_url_daily = 'http://www.cnta.gov.cn/xxfb/mrgx/'
        content_daily = self.crawl.crawl_get_content(start_url_daily, proxies=self.tools.tool_use_proxy(),
                                                     headers=setting.HEADERS)
        urls_daily = self.spider.spider_content_data(content=content_daily, xpather=setting.XPATHER_EACH_URLS)
        for eachurl in urls_daily:
            self.urls.append('http://www.cnta.gov.cn/xxfb' + eachurl[2:])

    def _engine_get_detail(self):
        """
        抓取详细数据
        :return:
        """
        new_urls = self._engine_new_news()
        print('新增新闻数量为 %s' % len(new_urls))
        while new_urls:
            url_news = new_urls.pop()
            content_detail = self.crawl.crawl_get_content(url_news, proxies=self.tools.tool_use_proxy(),
                                                          headers=setting.HEADERS)

            for each_xpather in setting.XPATHER_DETAIL:
                res_detail = self.spider.spider_content_data(content=content_detail, xpather=each_xpather)
                if res_detail.get('title'):
                    break
            res_detail['url'] = url_news
            # 部署到服务器不能使用mongo
            # self.pipe.pipe_save_db(res_detail, 'db_tourism', 'col_news')

            # 存储数据
            if res_detail.get('title', ''):
                save_data = '%(title)s\u0001%(publish_date)s\u0001%(source)s\u0001%(position)s\u0001' \
                            '%(content)s\u0001%(img)s\u0001%(editor)s\u0001%(url)s' % res_detail
                self.pipe.pipe_save_txt(save_data, setting.FILE_NEWS_HISTORY, savetype='a')
                self.current_news.append(save_data)
            time.sleep(2)

    def _engine_new_news(self):
        """
        新增新闻url
        :return:
        """
        new_news_urls = []
        for each_url in self.urls:
            url_md5 = self._engine_mk_md5(each_url)
            if url_md5 not in self.old_news:
                new_news_urls.append(each_url)
                self.old_news.add(url_md5)

        return set(new_news_urls)

    @staticmethod
    def _engine_mk_md5(data):
        """
        md5加密处理
        :param data: 需要加密的内容
        :return:
        """
        m = md5()
        m.update(data.encode('UTF-8'))
        return m.hexdigest()

    @staticmethod
    def _engine_load_pickle(filename):
        """
        将持久化内容加载到内容中
        :param filename: 文件名称
        :return:
        """
        with open(filename, 'rb') as f:
            data = pickle.load(f)

        return data

    @staticmethod
    def _engine_dump_pickle(filename, data):
        """
        将内存中的数据持久化操作并写入到文件中
        :param filename: 文件名称
        :param data: 需要持久化的数据
        :return:
        """
        with open(filename, 'wb') as f:
            pickle.dump(data, f)

    def excute(self):
        self._engine_get_allurls()
        self._engine_get_szxw()
        self._engine_get_daily()
        self._engine_get_detail()
        if self.current_news:
            self.pipe.pipe_save_txt(self.current_news, setting.FILE_CURRENT_NEWS, savetype='w')
        self._engine_dump_pickle(setting.FILE_OLD_NEWS, self.old_news)


if __name__ == '__main__':
    while True:
        start = time.time()
        proc = Engine()
        proc.excute()
        end = time.time()
        print('[%.1f s] script finish ' % (end - start))
        time.sleep(60 * 60)  # 每小时抓取一次
