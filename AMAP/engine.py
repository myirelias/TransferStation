# !/usr/bin/env python
# coding=utf-8
'''引擎模块'''

from crawl import Crawl
from analysis import Analysis
from pipeline import Pipeline
import config as setting
import json
import time
from copy import deepcopy

class Engine:

    def __init__(self):
        self.crawl = Crawl()
        self.pipe = Pipeline()
        self.analysis = Analysis()

    def _engine_residential_area(self):
        """获取小区数据"""
        citys = self.pipe.pipe_txt_load(filename=setting.FILE_CITY_ID)
        types = self.pipe.pipe_txt_load(filename=setting.FILE_TYPE_ID)
        current_params = deepcopy(setting.PARAMS)
        current_params['key'] = setting.KEY
        # 每种类型
        for each_type in types:
            typeinfo = each_type.strip().split('\u0001')
            type_id = typeinfo[0]  # 类型id
            type_large = typeinfo[1]  # 类型大分类
            type_middle = typeinfo[2]  # 类型中分类
            type_small = typeinfo[3]  # 类型小分类
            current_params['types'] = type_id
            save_filename = '{}_{}_{}_{}.txt'.format(type_id, type_large, type_middle, type_small)
            # 每个城市
            for each_city in citys:
                cityinfo = each_city.strip().split('\u0001')
                province = cityinfo[0]  # 省名
                city_name = cityinfo[1]  # 城市名
                city_id = cityinfo[2]  # 城市id
                current_params['city'] = city_id
                current_params['page'] = 0
                save_data = []
                while True:
                    current_params['page'] += 1
                    content_json = self.crawl.crawl_by_get(setting.SEARCH_API, params=current_params,
                                                           retry=2, timeout=30)
                    try:
                        data_json = json.loads(content_json)
                    except:
                        continue
                    pois_list = data_json.get('pois')
                    if not pois_list:
                        break
                    for each_poi in pois_list:
                        """
                        字段说明：
                        id: 唯一ID, name: 名称, pcode: poi所在省份编码,  pname: poi所在省份名称,citycode: 城市编码, 
                        cityname: 城市名,adcode: 区域编码, adname: 区域名称,address: 地址,  alias: 别名, 
                        biz_ext: 深度信息, biz_type: 行业类型, business_area: 所在商圈, discount_num: 优惠信息数目,
                        distance: 离中心点距离(此结果仅在周边搜索的时候有值), email: 该POI的电子邮箱, entr_location: 入口经纬度,
                        exit_location: 出口经纬度, gridcode: 地理格ID, groupbuy_num: 团购数据, indoor_data: 室内地图相关数据, 
                        indoor_map: 是否有室内地图标志, location: 经纬度, navi_poiid: 地图编号, photos: 照片相关信息, 
                        postcode: 邮编, tag: 该POI的特色内容, tel: 该POI的电话, type: 兴趣点类型, typecode: 兴趣点类型编码, 
                        website: 该POI的网址
                        """
                        save_dict = {}
                        save_dict['id'] = each_poi.get('id', '')  # id: 唯一ID
                        save_dict['name'] = each_poi.get('name', '')  # name: 名称
                        save_dict['pcode'] = each_poi.get('pcode', '')  # pcode: poi所在省份编码
                        save_dict['pname'] = each_poi.get('pname', '')  # pname: poi所在省份名称
                        save_dict['citycode'] = each_poi.get('citycode', '')  # citycode: 城市编码
                        save_dict['cityname'] = each_poi.get('cityname', '')  # cityname: 城市名
                        save_dict['adcode'] = each_poi.get('adcode', '')  # adcode: 区域编码
                        save_dict['adname'] = each_poi.get('adname', '')  # adname: 区域名称
                        save_dict['address'] = each_poi.get('address', '')  # address: 地址
                        save_dict['alias'] = each_poi.get('alias', '')  # alias: 别名
                        save_dict['biz_ext'] = each_poi.get('biz_ext', '')  # biz_ext: 深度信息
                        save_dict['biz_type'] = each_poi.get('biz_type', '')  # biz_type: 行业类型
                        save_dict['business_area'] = each_poi.get('business_area', '')  # business_area: 所在商圈
                        save_dict['discount_num'] = each_poi.get('discount_num', '')  # discount_num: 优惠信息数目
                        save_dict['email'] = each_poi.get('email', '')  # email: 该POI的电子邮箱
                        save_dict['entr_location'] = each_poi.get('entr_location', '')  # entr_location: 入口经纬度
                        save_dict['exit_location'] = each_poi.get('exit_location', '')  # exit_location: 出口经纬度
                        save_dict['gridcode'] = each_poi.get('gridcode', '')  # gridcode: 地理格ID
                        save_dict['groupbuy_num'] = each_poi.get('groupbuy_num', '')  # groupbuy_num: 团购数据
                        save_dict['indoor_data'] = each_poi.get('indoor_data', '')  # indoor_data: 室内地图相关数据
                        save_dict['indoor_map'] = each_poi.get('indoor_map', '')  # indoor_map: 是否有室内地图标志
                        save_dict['location'] = each_poi.get('location', '')  # location: 经纬度
                        save_dict['navi_poiid'] = each_poi.get('navi_poiid', '')  # navi_poiid: 地图编号
                        photos = each_poi.get('photos', [])  # photos: 照片相关信息
                        save_dict['photo_info'] = ''
                        for each_photo in photos:
                            if isinstance(each_photo.get('title', {}), dict):
                                each_photo['title'] = 'notitle'
                            save_dict['photo_info'] += '{0[title]}-{0[url]},'.format(each_photo)
                        save_dict['postcode'] = each_poi.get('postcode', '')  # postcode: 邮编
                        save_dict['tag'] = each_poi.get('tag', '')  # tag: 该POI的特色内容
                        save_dict['tel'] = each_poi.get('tel', '')  # tel: 该POI的电话
                        save_dict['type'] = each_poi.get('type', '')  # type: 兴趣点类型
                        save_dict['typecode'] = each_poi.get('typecode', '')  # typecode: 兴趣点类型编码
                        save_dict['website'] = each_poi.get('website', '')  # website: 该POI的网址
                        for each_key in save_dict.keys():
                            save_dict[each_key] = \
                                save_dict[each_key] if not isinstance(save_dict[each_key], dict) else ''
                        # 存储字段类型
                        # id, name, pcode, pname, citycode, cityname, adcode, adname,
                        # address, alias, biz_type, business_area, discount_num, email,
                        # entr_location, exit_location, gridcode, groupbuy_num, indoor_data,
                        # indoor_map, location, navi_poiid, photo_info, postcode, tag, tel, type, typecode, website,
                        save_info = '{0[id]}\u0001{0[name]}\u0001{0[pcode]}\u0001{0[pname]}\u0001' \
                                    '{0[citycode]}\u0001{0[cityname]}\u0001{0[adcode]}\u0001{0[adname]}\u0001' \
                                    '{0[address]}\u0001{0[alias]}\u0001{0[biz_type]}\u0001{0[business_area]}\u0001' \
                                    '{0[discount_num]}\u0001{0[email]}\u0001{0[entr_location]}\u0001' \
                                    '{0[exit_location]}\u0001' \
                                    '{0[gridcode]}\u0001{0[groupbuy_num]}\u0001{0[indoor_data]}\u0001' \
                                    '{0[indoor_map]}\u0001' \
                                    '{0[location]}\u0001{0[navi_poiid]}\u0001{0[photo_info]}\u0001{0[postcode]}\u0001' \
                                    '{0[tag]}\u0001{0[tel]}\u0001{0[type]}\u0001{0[typecode]}\u0001' \
                                    '{0[website]}'.format(save_dict)
                        save_data.append(save_info)
                        time.sleep(0.1)
                self.pipe.pipe_txt_save(save_data, filename=save_filename, savetype='a')



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
        self._engine_residential_area()


if __name__ == '__main__':
    start = time.time()
    proc = Engine()
    proc.run_engine()
    end = time.time()
    print('执行完毕，耗时 {:.2f} s'.format(end - start))
