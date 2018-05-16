# !/usr/bin/env python
# coding=utf-8
'''引擎模块'''

from crawl import Crawl
from analysis import Analysis
from pipeline import Pipeline
import config as setting
import time
import json


class Engine:
    def __init__(self):
        self.crawl = Crawl()
        self.pipe = Pipeline()
        self.analysis = Analysis()

    def _engine_city_list(self):
        """
        获取城市列表
        :return:
        """
        content = self.crawl.crawl_by_get(setting.START_URL, headers=setting.HEADERS)
        elements = self.analysis.analysis_by_xpath(content, xpahter=setting.XPATH_CITYLIST_A)
        city_list = []
        for each_ele in elements:
            city_url = self.analysis.analysis_by_xpath(each_ele, xpahter=setting.XPATH_HREF)
            city_name = self.analysis.analysis_by_xpath(each_ele, xpahter=setting.XPATH_TEXT)
            cityinfo = '{}\u0001{}'.format(''.join(city_name), ''.join(city_url).replace('/', ''))
            city_list.append(cityinfo)
        self.pipe.pipe_txt_save(city_list, filename=setting.FILE_CITY_LIST, savetype='w')

    def _engine_cityid_list(self):
        """
        获取所有城市的sid
        :return:
        """
        city_list = self.pipe.pipe_txt_load(filename=setting.FILE_CITY_LIST)
        save_data = []
        for eachcity in city_list:
            try:
                params = {
                    'format': 'ajax',
                    'cid': '0',  # 景点类型id,0为全部
                    'playid': '0',  # 游玩时间id,0为全部
                    'seasonid': '5',  # 适宜季节id(春1夏2秋3冬4四季皆宜0全部5)
                    'surl': 'chengdu',  # 初步调研为城市拼音名
                    'pn': 0,  # 当前页码
                    'rn': '18'  # 当页展示数量
                }
                try:
                    surl = eachcity.strip().split('\u0001')[1]
                except:
                    continue
                params['surl'] = surl
                content = self.crawl.crawl_by_get(setting.TOURIS_API, headers=setting.HEADERS, params=params,
                                                  proxies=self._engine_use_proxy(), retry=3, timeout=15)
                try:
                    data_dict = json.loads(content)
                except:
                    continue
                data = data_dict.get('data', {})
                sid = data.get('sid', {})
                current_surl = data.get('surl', {})
                sname = data.get('sname', {})
                save_data.append('{}\u0001{}\u0001{}'.format(sname, current_surl, sid))
            except:
                continue
        self.pipe.pipe_txt_save(save_data, filename=setting.FILE_CITYID_LIST, savetype='a')

    def _engine_food_list(self):
        """
        获取城市美食数据
        :return:
        """
        city_list = self.pipe.pipe_txt_load(filename=setting.FILE_CITYID_LIST)
        for each_city in city_list:
            try:
                save_list = []
                surl = each_city.strip().split('\u0001')[1]
                sid = each_city.strip().split('\u0001')[2]
                sname = each_city.strip().split('\u0001')[0]
                request_url = setting.FOOD_URL.format(surl)
                content = self.crawl.crawl_by_get(request_url, headers=setting.HEADERS, proxies=self._engine_use_proxy())
                food_list = self.analysis.analysis_by_xpath(content, setting.XPATH_FOOD_LIST)
                for each_food in food_list:
                    food_name = self.analysis.analysis_by_xpath(each_food, setting.XPATH_FOOD_NAME)
                    food_des = self.analysis.analysis_by_xpath(each_food, setting.XPATH_FOOD_DESCRIB)
                    shop_list = self.analysis.analysis_by_xpath(each_food, setting.XPATH_SHOP_LIST)
                    shop_info = []
                    for each_shop in shop_list:
                        shop_name = self.analysis.analysis_by_xpath(each_shop, setting.XPATH_SHOP_NAME)
                        shop_url = self.analysis.analysis_by_xpath(each_shop, setting.XPATH_SHOP_URL)
                        shop = {''.join(shop_name).replace('\n', ''): 'https://lvyou.baidu.com' + ''.join(shop_url)}
                        shop_info.append(shop)
                    save_food_name = ''.join(food_name).replace('\n', '').replace('\r', '')
                    save_food_des = ''.join(food_des).replace('\n', '').replace('\r', '')
                    """
                    sname: 城市名称 surl: 城市拼音名 sid: 城市id
                    save_food_name: 美食名称 save_food_des: 美食描述
                    shop_info: 店铺信息(列表，每个元素为{店铺名称: 店铺url})
                    """
                    current_food = '{}\u0001{}\u0001{}\u0001{}\u0001{}\u0001{}\u0001'.format(sname, surl, sid,
                                                                                             save_food_name, save_food_des,
                                                                                             shop_info)
                    save_list.append(current_food)
                self.pipe.pipe_txt_save(save_list, filename=setting.FILE_FOOD_INFO)
            except:
                continue

    def start_engine(self):
        self._engine_city_list()
        self._engine_cityid_list()
        self._engine_food_list()

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


if __name__ == '__main__':
    start = time.time()
    proc = Engine()
    proc.start_engine()
    end = time.time()
    print('执行完毕，耗时 {:.2f} s'.format(end - start))
