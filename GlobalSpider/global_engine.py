# !/usr/bin/env python
# coding=UTF-8

import time
from global_crawl import Crawl
from global_spider import Spider
from global_pipe import Pipe
import global_setting as setting
import pickle
from tools import SomeTools


class Engine(object):

    def __init__(self):
        self.crawl = Crawl()
        self.spider = Spider()
        self.pipe = Pipe()
        try:
            self.old_news_max_datetime = self._engine_pickle_load()
        except:
            self.old_news_max_datetime = {}
        self.current_news = []
        self.tools = SomeTools()
        self.current_detail = []

    def _engine_current_news(self):
        """
        获取新增的新闻
        :return:
        """
        for eachkey in setting.URL_DICT.keys():
            next_flag = True
            current_url = setting.URL_DICT[eachkey]
            max_datetime = set([])
            already_page = []
            while True:
                time.sleep(1)
                print('当前链接%s' % current_url)
                content_eachpage = self.crawl.crawl_get_content(current_url, headers=setting.HEADERS,
                                                                proxies=self.tools.tool_use_proxy())
                already_page.append(current_url)
                # 找到每页所有的新闻块
                elements = self.spider.spider_content_data(content=content_eachpage, xpather=setting.XPATHER_ELEMENT)
                # 每个新闻块单独解析
                for each_element in elements:
                    res = self.spider.spider_content_data(content=each_element, xpather=setting.XPATHER_EACH_NEWS)
                    # 校验是否为新增
                    if res.get('publish_date'):
                        current_datetime = float(self._engine_mk_datetime(res['publish_date']))
                        if current_datetime > float(self.old_news_max_datetime.get(eachkey, 0.0)):
                            self.current_news.append(res)
                            max_datetime.add(current_datetime)
                        else:
                            next_flag = False
                            break

                # 是否翻页,如果当前页面所有内容都为新增，则会继续翻页，否则翻页表示next_flag将为false，则不继续翻页
                if next_flag:
                    res = self.spider.spider_content_data(content=content_eachpage, xpather=".//*[text()='下一页']/@href")
                    try:
                        next_url = res[0]
                    except Exception as e:
                        print('翻页出错' % e)

                    if res and next_url not in already_page:
                        current_url = next_url
                        continue
                    else:
                        break

                else:
                    break

            if max_datetime:
                self.old_news_max_datetime[eachkey] = max(max_datetime)

    def _engine_news_detail(self, news_dict):
        """
        获取每条新闻的详细内容
        :param news_dict: 新闻字典
        :return:
        """
        url = news_dict.get('link')
        if url:
            content_detail = self.crawl.crawl_get_content(url, headers=setting.HEADERS,
                                                          proxies=self.tools.tool_use_proxy())
            for each_xpather in setting.XPATHER_DETAIL:
                news_detail = self.spider.spider_content_data(content=content_detail, xpather=each_xpather)
                news_detail['url'] = url
                if news_detail.get('title'):
                    break

            save_data = '%(title)s\u0001%(publish_date)s\u0001%(source)s\u0001%(position)s\u0001%(content)s\u0001' \
                        '%(img)s\u0001%(author)s\u0001%(url)s' % news_detail
            self.pipe.pipe_save_txt(save_data, setting.FILE_HISTORY, savetype='a')
            self.current_detail.append(save_data)

    @staticmethod
    def _engine_mk_datetime(data):
        """
        将字符串日期转换为时间戳
        :param data: 时间格式字符串 ==> %Y-%m-%d %H:%M:%S
        :return:
        """
        return time.mktime(time.strptime(data, '%Y-%m-%d%H:%M'))

    @staticmethod
    def _engine_pickle_load():
        """持久化文件加载到内存"""
        with open(setting.FILE_OLD_NEWS, 'rb') as f:
            return pickle.load(f)

    @staticmethod
    def _engine_pickle_dump(data):
        """内存上的数据持久化存储到文本中"""
        with open(setting.FILE_OLD_NEWS, 'wb') as f:
            pickle.dump(data, f)

    def excute(self):
        self._engine_current_news()
        # print(self.old_news_max_datetime)
        print('新增新闻 %s' % len(self.current_news))
        while self.current_news:
            each_news = self.current_news.pop()
            self._engine_news_detail(each_news)
        self.pipe.pipe_save_txt(self.current_detail, setting.FILE_CURRENT, savetype='w')
        self._engine_pickle_dump(self.old_news_max_datetime)


if __name__ == '__main__':
    start = time.time()
    proc = Engine()
    proc.excute()
    end = time.time()
    print('[%.1f s] script finish ' % (end - start))
