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
        content = self.crawl.crawl_by_get(setting.START_URL, headers=setting.HEADERS, proxies=self._engine_use_proxy())
        element_city = self.analysis.analysis_by_xpath(content, setting.XPATH_CITY_A)
        city_list = []
        for each_element in element_city:
            city_name = self.analysis.analysis_by_xpath(each_element, setting.XPATH_CITY_NAME)
            city_url = self.analysis.analysis_by_xpath(each_element, setting.XPATH_CITY_URL)
            city_list.append('{}\u0001{}'.format(''.join(city_name), ''.join(city_url)))
        self.pipe.pipe_txt_save(city_list, filename=setting.FILE_CITY_LIST)

    def _engine_shop_link(self):
        """
        获取每个城市中所有的购物店铺的链接
        :return:
        """
        city_list = self.pipe.pipe_txt_load(filename=setting.FILE_CITY_LIST)
        for each_city in city_list:
            try:
                url = each_city.strip().split('\u0001')[1] + '-gouwu'
                name = each_city.strip().split('\u0001')[0]
                params_city = {'page': 0}
                maxpage = 200  # 默认最大页数
                while True:
                    save_list = []
                    params_city['page'] += 1
                    content = self.crawl.crawl_by_get(url, headers=setting.HEADERS, params=params_city,
                                                      proxies=self._engine_use_proxy(), retry=2, timeout=15)
                    if not content:
                        break
                    # 获取总页数
                    if params_city['page'] == 1:
                        # 找到最大页数,使用map函数
                        pagecount = map(lambda x: int(x) if x != '下一页' else -1,
                                        self.analysis.analysis_by_xpath(content, xpahter=setting.XPATH_NEXTPAGE))
                        try:
                            maxpage = max(pagecount)
                        except:
                            break
                    element_li = self.analysis.analysis_by_xpath(content, xpahter=setting.XPATH_LI)
                    if not element_li:
                        break

                    for each_ele in element_li:
                        restaurant_name = self.analysis.analysis_by_xpath(each_ele, xpahter=setting.XPATH_SHOP_NAME)
                        restaurant_type = self.analysis.analysis_by_xpath(each_ele, xpahter=setting.XPATH_SHOP_TYPE)
                        restaurant_url = self.analysis.analysis_by_xpath(each_ele, xpahter=setting.XPATH_SHOP_URL)
                        try:
                            save_info = '{}\u0001{}\u0001{}\u0001{}'.format(name, ''.join(restaurant_name),
                                                                            ''.join(restaurant_type),
                                                                            ''.join(restaurant_url))
                        except:
                            continue
                        save_list.append(save_info)
                    self.pipe.pipe_txt_save(save_list, filename=setting.FILE_SHOP_LIST, savetype='a')
                    if params_city['page'] >= maxpage:
                        break
                    time.sleep(0.2)
            except:
                continue

    def _engine_shop_info(self):
        """
        获取所有购物地点详细数据
        :return:
        """
        shop_list = self.pipe.pipe_txt_load(filename=setting.FILE_SHOP_LIST)
        for each_shop in shop_list:
            try:
                # 店铺数据
                shop_info = each_shop.strip().split('\u0001')
                city_name = shop_info[0]
                shop_name = shop_info[1]
                shop_type = shop_info[2]
                shop_url = shop_info[3]
                find_id = re.search(re.compile(r'p-oi(\d+)-'), shop_url)
                if find_id:
                    shop_id = find_id.group(1)
                else:
                    shop_id = 0
                # 获取店铺详细信息
                content = self.crawl.crawl_by_get(shop_url, headers=setting.HEADERS, proxies=self._engine_use_proxy(),
                                                  retry=5, timeout=10)
                detail = self.analysis.analysis_by_xpath(content, xpahter=setting.XPATH_SHOP_DETAIL)
                detail['city_name'] = city_name
                detail['shop_name'] = shop_name
                detail['shop_type'] = shop_type
                detail['shop_url'] = shop_url
                detail['shop_id'] = shop_id
                detail['get_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                # 存储数据
                # 字段顺序
                # city_name, shop_name, shop_type, shop_id,
                # score, ranking, describe, address, tel, open_time, arrive, intro, web, get_time, shop_url
                save_data = '{0[city_name]}\u0001{0[shop_name]}\u0001{0[shop_type]}\u0001' \
                            '{0[shop_id]}\u0001{0[score]}\u0001{0[ranking]}\u0001' \
                            '{0[describe]}\u0001{0[address]}\u0001{0[tel]}\u0001' \
                            '{0[open_time]}\u0001{0[arrive]}\u0001{0[intro]}\u0001' \
                            '{0[web]}\u0001{0[get_time]}\u0001{0[shop_url]}\u0001'.format(detail)
                self.pipe.pipe_txt_save(save_data, filename=setting.FILE_SHOP_INFO, savetype='a')
                # self.pipe.pipe_mongo_save(detail, dbname='db_qunaer', colname='col_shop_info')
                time.sleep(0.1)
            except Exception as e:
                print('crawl error', e)
                continue

    def _engine_shop_comments(self):
        """
        获取所有购物店评论数据
        :return:
        """
        shop_list = self.pipe.pipe_txt_load(filename=setting.FILE_SHOP_LIST)
        # 每个店铺最新评论时间表
        check_dict = self.pipe.pipe_pickle_load(filename=setting.FILE_COMMENTS_CHECK)
        if not check_dict:
            check_dict = {}
        for each_shop in shop_list:
            try:
                # 店铺数据
                city = each_shop.strip().split('\u0001')[0]
                food = each_shop.strip().split('\u0001')[1]
                type = each_shop.strip().split('\u0001')[2]
                shop_url = each_shop.strip().split('\u0001')[3]
                find_id = re.search(re.compile(r'p-oi(\d+)-'), shop_url)
                if not find_id:
                    break
                shop_id = find_id.group(1)
                api = setting.COMMENTS_API.format(shop_id)
                setting.HEADERS_COMMENTS['Referer'] = shop_url
                params = {
                    'page': 0,
                    'pageSize': '10',
                    'poiList': 'true',
                    'rank': 0,  # 全部评论
                    'sortField': 0  # 按照时间排序
                }
                comments_time = set([])
                current_time = check_dict.get(shop_id, '0')
                max_page = 1
                while True:
                    params['page'] += 1
                    content = self.crawl.crawl_by_get(api, headers=setting.HEADERS_COMMENTS,
                                                      proxies=self._engine_use_proxy(),
                                                      params=params, retry=2, timeout=15)
                    try:
                        content_dict = json.loads(content)
                    except:
                        break
                    if not content_dict.get('data'):
                        break
                    content_comments = content_dict.get('data')
                    # 第一遍抓取要确定评论页数
                    if params['page'] == 1:
                        page = self.analysis.analysis_by_xpath(content_comments, xpahter=setting.XPATH_COMMENTS_PAGE)
                        if page:
                            max_page = int(''.join(page))
                    elements_com = self.analysis.analysis_by_xpath(content_comments, xpahter=setting.XPATH_COMMENTS_LI)
                    if not elements_com:
                        break
                    for each_element in elements_com:
                        title = self.analysis.analysis_by_xpath(each_element, xpahter=setting.XPATH_COMMENTS_TITLE)
                        start = self.analysis.analysis_by_xpath(each_element, xpahter=setting.XPATH_COMMENTS_START)
                        nick = self.analysis.analysis_by_xpath(each_element, xpahter=setting.XPATH_COMMENTS_NICK)
                        more = self.analysis.analysis_by_xpath(each_element, xpahter=setting.XPATH_COMMENTS_MORE)
                        if more:
                            content_more = self.crawl.crawl_by_get(more[0], headers=setting.HEADERS,
                                                                   proxies=self._engine_use_proxy())
                            content = self.analysis.analysis_by_xpath(content_more,
                                                                      xpahter=setting.XPATH_COMMENTS_DETAIL)
                        else:
                            content = self.analysis.analysis_by_xpath(each_element,
                                                                      xpahter=setting.XPATH_COMMENTS_CONTENT)
                        date = self.analysis.analysis_by_xpath(each_element, xpahter=setting.XPATH_COMMENTS_DATE)
                        deal_content = ''.join(
                            list(map(lambda x: x.replace('\n', '').replace('\r', '').replace('\t', '').
                                     replace(' ', ''), content)))
                        if ''.join(date) > current_time:
                            commetents_info = {
                                'city': city,
                                'food': food,
                                'food_id': shop_id,
                                'type': type,
                                'title': ''.join(title),
                                'nick': ''.join(nick),
                                'start': ''.join(start),
                                'content': deal_content,
                                'date': ''.join(date),
                                'get_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                'url': shop_url
                            }
                            # 存储数据
                            # 字段顺序
                            # city, food, food_id, type, title, nick, start, content, date, get_time, url
                            save_data = '{0[city]}\u0001{0[food]}\u0001{0[food_id]}\u0001' \
                                        '{0[type]}\u0001{0[title]}\u0001{0[nick]}\u0001' \
                                        '{0[start]}\u0001{0[content]}\u0001{0[date]}\u0001' \
                                        '{0[get_time]}\u0001{0[url]}'.format(commetents_info)
                            self.pipe.pipe_txt_save(save_data, filename=setting.FILE_SHOP_COMMENTS, savetype='a')
                            # self.pipe.pipe_mongo_save(commetents_info, dbname='db_qunaer', colname='col_shopping_comments')
                            comments_time.add(''.join(date))
                    # 超过评论最大页数则切换
                    if params['page'] >= max_page:
                        break
                    # 当前页面没有新增评论也切换至下一店铺
                    if not len(comments_time):
                        break
                # 每个店铺最新的评论时间
                if comments_time:
                    check_dict[shop_id] = max(comments_time)
                # 抓取到的评论数据
                self.pipe.pipe_pickle_save(check_dict, filename=setting.FILE_COMMENTS_CHECK)
            except:
                continue

    def _temp_city_info(self, cityname):
        """
        做22项数据处理时临时用
        :return:
        """
        citylist = self.pipe.pipe_txt_load(filename='city_list_total.txt')
        city_params = {'国别': '&',
                       '省自治区全称': '&',
                       '省自治区简称': '&',
                       '市州全称': '&',
                       '市州简称': '&',
                       '区县全称': '&',
                       '区县简称': '&',
                       '地区编码': '&',
                       '等级': '&'}
        spec_city = {'北京': '110000',
                     '天津': '120000',
                     '上海': '310000',
                     '重庆': '500000'}
        for each in citylist:
            cityinfo = each.split('\u0001')
            if cityname in cityinfo:
                site = cityinfo.index(cityname)
                if site == 4 or site == 5:
                    city_params['国别'] = 'CN'
                    city_params['省自治区全称'] = cityinfo[0].strip()
                    city_params['省自治区简称'] = cityinfo[1].strip()
                    city_params['市州全称'] = cityinfo[2].strip()
                    city_params['市州简称'] = cityinfo[3].strip()
                    city_params['区县全称'] = cityinfo[4].strip()
                    city_params['区县简称'] = cityinfo[5].strip()
                    city_params['地区编码'] = cityinfo[-1].strip()
                    city_params['等级'] = '区县级'
                elif site == 2 or site == 3:
                    city_params['国别'] = 'CN'
                    city_params['省自治区全称'] = cityinfo[0].strip()
                    city_params['省自治区简称'] = cityinfo[1].strip()
                    city_params['市州全称'] = cityinfo[2].strip()
                    city_params['市州简称'] = cityinfo[3].strip()
                    city_params['地区编码'] = cityinfo[-1].strip()[:-2] + '00'
                    city_params['等级'] = '地市级'
                elif cityname in ['北京', '重庆', '上海', '天津']:
                    city_params['国别'] = 'CN'
                    city_params['省自治区全称'] = cityname + '市'
                    city_params['省自治区简称'] = cityname
                    city_params['市州全称'] = cityname + '市'
                    city_params['市州简称'] = cityname
                    city_params['地区编码'] = spec_city[cityname]
                    city_params['等级'] = '直辖'
                break

        return city_params

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
        self._engine_shop_link()
        # 店铺信息和店铺评论可以同时抓取的，用多进程实现，后期可根据需求添加该功能，目前未开发循环抓取功能
        self._engine_shop_info()
        self._engine_shop_comments()


if __name__ == '__main__':
    start = time.time()
    proc = Engine()
    proc.start_engine()
    end = time.time()
    print('执行完毕，耗时 {:.2f} s'.format(end - start))
