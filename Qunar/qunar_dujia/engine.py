# !/usr/bin/env python
# coding=utf-8
'''引擎模块'''

from crawl import Crawl
from analysis import Analysis
from pipeline import Pipeline
import config as setting
import time
import re
import json
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
        content = self.crawl.crawl_by_get(setting.START_URL, headers=setting.HEADERS, proxies=self._engine_use_proxy(),
                                          params=setting.PARAMS_ARROUND)
        element_city = self.analysis.analysis_by_xpath(content, setting.XPATH_CITY_A)
        city_list = []
        for each_element in element_city:
            city_name = self.analysis.analysis_by_xpath(each_element, setting.XPATH_CITY_NAME)
            city_url = self.analysis.analysis_by_xpath(each_element, setting.XPATH_CITY_URL)
            city_list.append('{}\u0001{}'.format(''.join(city_name), ''.join(city_url)))
        self.pipe.pipe_txt_save(city_list, filename=setting.FILE_CITY_LIST)

    def _engine_surround_link(self):
        """
        获取每个城市中所有的周边游玩地点的链接
        :return:
        """
        city_list = self.pipe.pipe_txt_load(filename=setting.FILE_CITY_LIST)
        for each_city in city_list:
            params = {
                'd': '重庆',
                'displayStatus': 'pc',
                'fl': 'url,price,totalPrice,taocanPrice,originalPrice,type,multi_price,local,extensionImg,sales,details,tripTimeTitle,allDate,summary,dep,title,sights,arrive,ttsRouteType,citys,virtual,virtual_num,hotel_title,subtitle,id,encodeId',
                'height': '201',
                'i': '1, 2, 3, 4, 5',
                'isTouch': '0',
                'linesType': '周边游, 本地游',
                'lm': '0, 30',  # 起始索引，每页数量
                'm': 'l,lm',
                'o': 'pop-desc',
                'q': '重庆',  # 城市名称
                'qs_ts': '1527059073761',  # 时间戳
                'qssrc': '',
                'random': '',
                'sourcepage': 'around',
                't': 'all',
                'tf': 'dj_aroundnav_origin',
                'ti': '4',
                'tm': 'nzb01',  # 不知道
                'width': '304',
            }

            url = each_city.strip().split('\u0001')[1]
            name = each_city.strip().split('\u0001')[0]
            page = 0
            params['d'] = name
            params['q'] = name
            params['qs_ts'] = '{:.0f}'.format(time.time() * 1000)
            while True:
                params['lm'] = '{},30'.format(page * 30)
                try:
                    content = self.crawl.crawl_by_get(setting.ARROUND_API, params=params, headers=setting.HEADERS,
                                                      proxies=self._engine_use_proxy(), retry=3, timeout=15)
                    content_dict = json.loads(content)
                    data_list = content_dict.get('data', {}).get('list', {}).get('results', [])
                    if not data_list:
                        break
                    # id, citys, arrive, allDate, detail.triptime, price, totalPrice, sights, ttsRouteType
                    # type, url
                    save_list = []
                    for each_data in data_list:
                        arround_id = each_data.get('id', '')
                        citys = each_data.get('citys', '')
                        arrive = each_data.get('arrive', '')
                        allDate = each_data.get('allDate', '')
                        triptime = each_data.get('detail', {}).get('triptime', '')
                        price = each_data.get('price', '')
                        totalPrice = each_data.get('totalPrice', '')
                        sights = each_data.get('sights', '')
                        ttsRouteType = each_data.get('ttsRouteType', '')
                        arround_type = each_data.get('type', '')
                        url = each_data.get('url', '')
                        save_url = 'http:' + url
                        save_list.append('{}\u0001{}\u0001{}\u0001{}\u0001{}\u0001{}\u0001{}\u0001{}\u0001'
                                         '{}\u0001{}\u0001{}'.format(arround_id, ''.join(citys), ''.join(arrive),
                                                                     ''.join(allDate), triptime, price, totalPrice,
                                                                     ''.join(sights), ttsRouteType,
                                                                     arround_type, save_url))
                    self.pipe.pipe_txt_save(save_list, filename=setting.FILE_SURROUND_LIST, savetype='a')
                    page += 1
                    time.sleep(10)
                except Exception as e:
                    print(e)
                    break

    def _engine_surround_info(self):
        """
        获取所有周边游场所详细数据
        :return:
        """
        surround_list = self.pipe.pipe_txt_load(filename=setting.FILE_SURROUND_LIST)
        for each_surround in surround_list:
            try:
                surround = each_surround.strip().split('\u0001')
                url = surround[-1]
                city_id = surround[0]
                city_name = surround[1]
                content = self.crawl.crawl_by_get(url, headers=setting.HEADERS, proxies=self._engine_use_proxy(),
                                                  retry=3, timeout=15)
                try:
                    href = re.search(re.compile(r"href = \'(.*?)'", re.S), content).group(1)
                    pid = re.search(re.compile(r"pid=(.*?)&", re.S), href).group(1)
                    host = re.search(re.compile(r"//(.*?)/", re.S), href).group(1)
                except:
                    continue
                if href:
                    current_headers = setting.HEADERS_DETAIL
                    current_headers['Host'] = host
                    tomorrow = (datetime.datetime.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
                    current_url = 'http:' + re.sub(re.compile(r'\d{4}-\d{2}-\d{2}', re.S), tomorrow, href)
                    content_detail = self.crawl.crawl_by_get(current_url, headers=current_headers,
                                                             proxies=self._engine_use_proxy(), retry=3, timeout=15)
                    res_detail = self.analysis.analysis_by_xpath(content_detail, xpahter=setting.XPATH_SURROUND_DETAIL)
                    if not res_detail:
                        continue
                    params = {
                        'isVer': 'false',
                        'oid': '',
                        'pId': pid,
                        'tId': '',
                        'takeoffDate': tomorrow,
                        'tuId': ''
                    }
                    params_scenic = {
                        'isVer': ' false',
                        'oid': '',
                        'pId': pid,
                        'tId': '',
                    }
                    # 部分信息在另外的请求里面
                    res_json = self.crawl.crawl_by_get(setting.ARROUND_DETAIL_API.format(host), params=params,
                                                       headers=current_headers,
                                                       proxies=self._engine_use_proxy(), retry=3, timeout=15)
                    try:
                        res_dict = json.loads(res_json)
                        feeinfo = res_dict.get('data', {}).get('feeInfo', {})
                        feature = res_dict.get('data', {}).get('feature', {})
                        costIncludeDesc = feeinfo.get('costIncludeDesc', '')  # 行程包含
                        costExcludeDesc = feeinfo.get('costExcludeDesc', '')  # 行程不含
                        refundDesc = feeinfo.get('refundDesc', '')  # 退款说明
                        attention = feeinfo.get('attention', '')  # 重要提示
                        tip = feeinfo.get('tip', '')  # 友情提示
                        standardContent = feature.get('standardContent', [])
                        if standardContent:
                            tese = standardContent[0].get('content', '')  # 线路特色
                            res_detail['线路特色'] = tese
                        res_detail['行程包含'] = self.analysis.analysis_by_xpath(costIncludeDesc,
                                                                             xpahter={'行程包含': './/text()'})['行程包含']
                        res_detail['行程不含'] = self.analysis.analysis_by_xpath(costExcludeDesc,
                                                                             xpahter={'行程不含': './/text()'})['行程不含']
                        res_detail['退款说明'] = refundDesc
                        res_detail['重要提示'] = self.analysis.analysis_by_xpath(attention,
                                                                             xpahter={'重要提示': './/text()'})['重要提示']
                        res_detail['友情提示'] = self.analysis.analysis_by_xpath(tip,
                                                                             xpahter={'友情提示': './/text()'})['友情提示']
                    except:
                        pass
                    # 景区信息在下面的请求中
                    scenic_json = self.crawl.crawl_by_get(setting.SCENIC_API.format(host), params=params_scenic,
                                                          headers=current_headers,
                                                          proxies=self._engine_use_proxy(), retry=3, timeout=15)
                    try:
                        scenic_dict = json.loads(scenic_json)

                        other = scenic_dict.get('data', {}).get('OTHER', {})
                        sight = scenic_dict.get('data', {}).get('SIGHT', {})
                        other_info = other.get('desc', '')  # 其他信息
                        res_detail['其他信息'] = other_info
                        sightInfos = sight.get('sightInfos', [])
                        if sightInfos:
                            name = sightInfos[0].get('name', '')  # 票名
                            sight_name = sightInfos[0].get('sight', '')  # 景点名称
                            star = sightInfos[0].get('star', '')  # 星级
                            address = sightInfos[0].get('address', '')  # 地址
                            openTime = sightInfos[0].get('openTime', '')  # 开放时间啊
                            ticketTypeName = sightInfos[0].get('ticketTypeName', '')  # 票类型
                            desc = sightInfos[0].get('desc', '')  # 景点简介
                            # descStandard = sightInfos[0].get('descStandard', [])
                            # if descStandard:
                            #     intro = descStandard[0].get('content', '')  # 景点介绍
                            #     res_detail['景点介绍'] = intro
                            res_detail['门票名称'] = name
                            res_detail['景点名称'] = sight_name
                            res_detail['景点级别'] = star
                            res_detail['景点地址'] = address
                            res_detail['开放时间'] = openTime
                            res_detail['门票类型'] = ticketTypeName
                            res_detail['景点简介'] = self.analysis.analysis_by_xpath(desc,
                                                                                 xpahter={'景点简介': './/text()'})['景点简介']
                    except:
                        pass
                    res_detail['城市名称'] = city_name
                    res_detail['城市id'] = city_id
                    res_detail['出发日期'] = tomorrow
                    for eachkey in res_detail.keys():
                        res_detail[eachkey] = res_detail[eachkey].replace('\n', '').replace('\r', '')
                    save_info = json.dumps(res_detail)
                    self.pipe.pipe_txt_save(save_info, filename=setting.FILE_SURROUND_INFO, savetype='a')
                    time.sleep(10)
            except Exception as e:
                print('获取info出错{}'.format(e))
                continue

    def _engine_surround_comments(self):
        """
        获取所有景区评论数据
        :return:
        """
        surround_list = self.pipe.pipe_txt_load(filename=setting.FILE_SURROUND_LIST)
        for each_surround in surround_list:
            try:
                surround = each_surround.strip().split('\u0001')
                url = surround[-1]
                city_id = surround[0]
                city_name = surround[1]
                content = self.crawl.crawl_by_get(url, headers=setting.HEADERS, proxies=self._engine_use_proxy(),
                                                  retry=3, timeout=15)
                try:
                    href = re.search(re.compile(r"href = \'(.*?)'", re.S), content).group(1)
                    pid = re.search(re.compile(r"pid=(.*?)&", re.S), href).group(1)
                    host = re.search(re.compile(r"//(.*?)/", re.S), href).group(1)
                except:
                    continue
                if pid and host:
                    data = {
                        'pageNo': 0,
                        'pageSize': '10',
                        'productIds': '2594358790',
                        'rateStatus': 'ALL',
                        'type': 'all'
                    }
                    current_headers = setting.HEADERS_DETAIL
                    current_headers['Host'] = host
                    data['productIds'] = pid
                    current_url = setting.COMMENTS_API.format(host)
                    while True:
                        data['pageNo'] += 1
                        content = self.crawl.crawl_by_post(current_url, headers=current_headers,
                                                           proxies=self._engine_use_proxy(),
                                                           data=data, retry=3, timeout=15)
                        try:
                            res_dict = json.loads(content)
                        except:
                            break
                        comments_list = res_dict.get('data', {}).get('mainCommentList')
                        if not comments_list:
                            break
                        for each_comments in comments_list:
                            id = each_comments.get('id', '')  # 评论id
                            commterId = each_comments.get('commterId')  # 用户名
                            commt_content = each_comments.get('content')  # 评论内容
                            createdtime = each_comments.get('createdTime')  # 创建时间
                            rating_hotel = each_comments.get('rating', {}).get('HOTEL')  # 酒店评分
                            rating_overview = each_comments.get('rating', {}).get('OVERVIEW')  # 概述评分
                            rating_reservation = each_comments.get('rating', {}).get('RESERVATION')  # 预订评分
                            rating_schedule = each_comments.get('rating', {}).get('SCHEDULE')  # 时刻评分
                            rating_travel = each_comments.get('rating', {}).get('TRAVEL')  # 旅游评分
                            trip_start_date = each_comments.get('tripStartDate')  # 行程开始时间
                            # 存储字段
                            #  id, commterId, commt_content, createdtime, rating_hotel, rating_overview,
                            # rating_reservation, rating_schedule, rating_travel, trip_start_date,
                            save_info = '{}\u0001{}\u0001{}\u0001{}\u0001' \
                                        '{}\u0001{}\u0001{}\u0001{}\u0001' \
                                        '{}\u0001{}'.format(id, commterId, commt_content, createdtime, rating_hotel,
                                                            rating_overview, rating_reservation, rating_schedule,
                                                            rating_travel, trip_start_date, )
                            self.pipe.pipe_txt_save(save_info, filename=setting.FILE_SURROUND_COMMENTS, savetype='a')
                        time.sleep(5)
            except Exception as e:
                print('获取comments出错{}'.format(e))
                continue

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
        self._engine_surround_link()
        self._engine_surround_info()
        self._engine_surround_comments()


if __name__ == '__main__':
    start = time.time()
    proc = Engine()
    proc.start_engine()
    end = time.time()
    print('执行完毕，耗时 {:.2f} s'.format(end - start))
