# !/usr/bin/env python
# coding=utf-8
'''百度地图数据抓取'''

from crawl import Crawl
from analysis import Analysis
from pipeline import Pipeline
import config as setting
import json
import time
from copy import deepcopy
import re


class Engine:
    def __init__(self):
        self.crawl = Crawl()
        self.pipe = Pipeline()
        self.analysis = Analysis()

    def _engine_search_by_city(self):
        """指定城市检索关键字数据"""
        type_name = self.pipe.pipe_txt_load(filename=setting.FILE_TYPE_NAME)
        city_id = self.pipe.pipe_txt_load(filename=setting.FILE_CITY_ID)
        for each_type in type_name:
            query = each_type.strip()
            current_params = deepcopy(setting.PARAMS)
            current_params['query'] = query  # 检索内容
            current_params['ak'] = setting.KEY
            filename = 'baidu_{}.txt'.format(query)
            for each_city in city_id:
                current_params['page_num'] = 0
                citycode = each_city.strip().split('\u0001')[1]
                current_params['region'] = citycode  # citycode,检索行政区域
                while True:
                    time.sleep(0.2)
                    # 每种类型
                    current_params['page_num'] += 1
                    content = self.crawl.crawl_by_get(setting.SEARCH_API, params=current_params, retry=2, timeout=20)
                    try:
                        content_dict = json.loads(content)
                    except:
                        continue
                    results = content_dict.get('results', [])
                    if not results:
                        break
                    for each in results:
                        """
                        字段说明：
                        uid: 唯一表示, name: 名称, address: 地址, province: 所在省, city: 所在城市, area: 所在区域, 
                        street_id: 街道id, location: 地图坐标
                        tag: 标签类型, type: 类型, detail_url: 详情url,
                        """
                        # 存储数据
                        # uid, name, address, province, city, area, street_id, location
                        # (detail_info) tag, type, detail_url,
                        lat = each.get('location', {}).get('lat', 0)
                        lng = each.get('location', {}).get('lng', 0)
                        save_dict = {'uid': each.get('uid', ''), 'name': each.get('name', ''),
                                     'address': each.get('address', ''), 'province': each.get('province', ''),
                                     'city': each.get('city', ''), 'area': each.get('area', ''),
                                     'street_id': each.get('street_id', ''), 'location': '{},{}'.format(lat, lng),
                                     'tag': each.get('detail_info', {}).get('tag', ''),
                                     'type': each.get('detail_info', {}).get('type', ''),
                                     'detail_url': each.get('detail_info', {}).get('detail_url', '')}
                        save_info = '{0[uid]}\u0001{0[name]}\u0001{0[address]}\u0001' \
                                    '{0[province]}\u0001{0[city]}\u0001{0[area]}\u0001' \
                                    '{0[street_id]}\u0001{0[location]}\u0001' \
                                    '{0[tag]}\u0001' \
                                    '{0[type]}\u0001{0[detail_url]}'.format(save_dict)
                        self.pipe.pipe_txt_save(save_info, filename=filename, savetype='a')

    def _engine_search_by_location(self):
        """
        指定坐标点检索关键字数据
        所有坐标数据来自 _engine_search_by_city 模块根据城市检索关键字的数据
        此模块开发原因是百度返回数据量只有400，想通过坐标获取更多数据
        :return:
        """
        type_name = self.pipe.pipe_txt_load(filename=setting.FILE_TYPE_NAME)
        city_name = list(map(lambda x: x.strip().split('\u0001')[1],
                             self.pipe.pipe_txt_load(filename=setting.FILE_CITY_ID)))
        location_list = self._engine_all_location()
        if not location_list:
            print('当前没有坐标数据，请检查')
            return
        for each_type in type_name:
            query = each_type.strip()
            current_params = deepcopy(setting.PARAMS)
            current_params['query'] = query  # 检索内容
            current_params['ak'] = setting.KEY
            filename = 'baidu_location_{}.txt'.format(query)
            for each_location in location_list:
                current_params['page_num'] = 0
                current_params['location'] = each_location  # 检索坐标
                while True:
                    time.sleep(0.2)
                    # 每种类型
                    current_params['page_num'] += 1
                    content = self.crawl.crawl_by_get(setting.SEARCH_API, params=current_params, retry=2, timeout=20)
                    try:
                        content_dict = json.loads(content)
                    except:
                        continue
                    results = content_dict.get('results', [])
                    if not results:
                        break
                    for each in results:
                        """
                        字段说明：
                        uid: 唯一表示, name: 名称, address: 地址, province: 所在省, city: 所在城市, area: 所在区域, 
                        street_id: 街道id, location: 地图坐标
                        tag: 标签类型, type: 类型, detail_url: 详情url,
                        """
                        # 存储数据
                        # uid, name, address, province, city, area, street_id, location
                        # (detail_info) tag, type, detail_url,
                        area = each.get('area', '')
                        if area not in city_name:  # 根绝坐标点抓取数据可能会超出目前限制的大成都范围，所以限制个区域吧
                            continue
                        lat = each.get('location', {}).get('lat', 0)
                        lng = each.get('location', {}).get('lng', 0)
                        save_dict = {'uid': each.get('uid', ''), 'name': each.get('name', ''),
                                     'address': each.get('address', ''), 'province': each.get('province', ''),
                                     'city': each.get('city', ''), 'area': area,
                                     'street_id': each.get('street_id', ''), 'location': '{},{}'.format(lat, lng),
                                     'tag': each.get('detail_info', {}).get('tag', ''),
                                     'type': each.get('detail_info', {}).get('type', ''),
                                     'detail_url': each.get('detail_info', {}).get('detail_url', '')}
                        save_info = '{0[uid]}\u0001{0[name]}\u0001{0[address]}\u0001' \
                                    '{0[province]}\u0001{0[city]}\u0001{0[area]}\u0001' \
                                    '{0[street_id]}\u0001{0[location]}\u0001' \
                                    '{0[tag]}\u0001' \
                                    '{0[type]}\u0001{0[detail_url]}'.format(save_dict)
                        self.pipe.pipe_txt_save(save_info, filename=filename, savetype='a')

    def _engine_all_location(self):
        """
        获取所有坐标点
        :return:
        """
        type_list = self.pipe.pipe_txt_load(filename=setting.FILE_TYPE_NAME)
        all_location = []
        for each_type in type_list:
            filename = 'baidu_{}.txt'.format(each_type.strip())
            area_list = self.pipe.pipe_txt_load(filename=filename)
            if not area_list:
                continue
            all_location.extend(list(map(lambda x: x.strip().split('\u0001')[7], area_list)))
        return all_location

    @staticmethod
    def _engine_use_proxy():
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

    def run_engine(self):
        self._engine_search_by_city()
        self._engine_search_by_location()


if __name__ == '__main__':
    start = time.time()
    proc = Engine()
    proc.run_engine()
    end = time.time()
    print('执行完毕，耗时 {:.2f} s'.format(end - start))
