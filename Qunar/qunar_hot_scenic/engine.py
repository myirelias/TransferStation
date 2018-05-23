# !/usr/bin/env python
# coding=utf-8
'''引擎模块'''

from crawl import Crawl
from analysis import Analysis
from pipeline import Pipeline
import config as setting
import time
import re
import datetime


class Engine:
    def __init__(self):
        self.crawl = Crawl()
        self.analysis = Analysis()
        self.pipe = Pipeline()

    def _engine_city_link(self):
        """
        获取所有城市的名称和url链接，结果输出到file_city_list.txt文本中
        :return:
        """
        content = self.crawl.crawl_by_get(setting.START_URL, headers=setting.HEADERS, proxies=self._engine_use_proxy())
        element_city = self.analysis.analysis_by_xpath(content, setting.XPATH_CITY_A)
        city_list = []
        for each_element in element_city:
            city_name = self.analysis.analysis_by_xpath(each_element, setting.XPATH_CITY_NAME)
            city_url = self.analysis.analysis_by_xpath(each_element, setting.XPATH_CITY_URL)
            city_list.append('{}\u0001{}'.format(''.join(city_name), ''.join(city_url)))
        self.pipe.pipe_txt_save(city_list, filename=setting.FILE_CITY_LIST)

    def _engine_scenic_link(self):
        """
        获取每个城市中所有的热门景点的链接
        :return:
        """
        city_list = self.pipe.pipe_txt_load(filename=setting.FILE_CITY_LIST)
        for each_city in city_list:
            url = each_city.strip().split('\u0001')[1] + '-jingdian'
            city_name = each_city.strip().split('\u0001')[0]
            content = self.crawl.crawl_by_get(url, headers=setting.HEADERS, proxies=self._engine_use_proxy(),
                                              retry=2, timeout=15)
            element_a = self.analysis.analysis_by_xpath(content, xpahter=setting.XPATH_HOT_A)
            save_list = []
            for each_ele in element_a:
                scenic_full_name = self.analysis.analysis_by_xpath(each_ele, xpahter=setting.XPATH_HOT_NAME)
                current_url = self.analysis.analysis_by_xpath(each_ele, xpahter=setting.XPATH_HOT_HREF)
                scenic_name = ''.join(scenic_full_name).replace('旅游攻略', '')
                scenic_url = ''.join(current_url)
                scenic_id = re.search(re.compile(r'p-oi(\d+)-'), scenic_url).group(1)
                # 存储字段
                # city_name, scenic_id, scenic_name, scenic_url
                save_info = '{}\u0001{}\u0001{}\u0001{}'.format(city_name, scenic_id, scenic_name, scenic_url)
                save_list.append(save_info)
            self.pipe.pipe_txt_save(save_list, filename=setting.FILE_SCENIC_LIST, savetype='a')

    @staticmethod
    def _engine_use_proxy():
        """
        使用代理ip
        :return: 代理ip
        """
        proxy_host = "proxy.abuyun.com"
        proxy_port = "9010"
        proxy_user = "****"
        proxy_pass = "****"
        proxy_meta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {"host": proxy_host,
                                                                     "port": proxy_port,
                                                                     "user": proxy_user,
                                                                     "pass": proxy_pass}
        proxies = {"http": proxy_meta,
                   "https": proxy_meta}

        return proxies

    def start_engine(self):
        self._engine_city_link()
        self._engine_scenic_link()
        # 店铺信息和店铺评论可以同时抓取的，用多进程实现，后期可根据需求添加该功能，目前未开发循环抓取功能


if __name__ == '__main__':
    start = time.time()
    proc = Engine()
    proc.start_engine()
    end = time.time()
    print('执行完毕，耗时 {:.2f} s'.format(end - start))
