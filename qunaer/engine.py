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

    def _engine_restaurant_link(self):
        """
        获取每个城市中所有的美食店铺的链接
        :return:
        """
        city_list = self.pipe.pipe_txt_load(filename=setting.FILE_CITY_LIST)
        for each_city in city_list:
            url = each_city.strip().split('\u0001')[1] + '-meishi'
            name = each_city.strip().split('\u0001')[0]
            params_city = {'page': 0}
            maxpage = 200  # 默认最大页数
            while True:
                save_list = []
                params_city['page'] += 1
                content = self.crawl.crawl_by_get(url, headers=setting.HEADERS, params=params_city,
                                                  proxies=self._engine_use_proxy(), retry=5)
                # 获取总页数
                if params_city['page'] == 1:
                    # 找到最大页数,使用map函数
                    pagecount = map(lambda x: int(x) if x != '下一页' else -1,
                                    self.analysis.analysis_by_xpath(content, xpahter=setting.XPATH_NEXTPAGE))
                    maxpage = max(pagecount)
                element_li = self.analysis.analysis_by_xpath(content, xpahter=setting.XPATH_LI)
                if element_li:
                    for each_ele in element_li:
                        restaurant_name = self.analysis.analysis_by_xpath(each_ele, xpahter=setting.XPATH_RES_NAME)
                        restaurant_type = self.analysis.analysis_by_xpath(each_ele, xpahter=setting.XPATH_RES_TYPE)
                        restaurant_url = self.analysis.analysis_by_xpath(each_ele, xpahter=setting.XPATH_RES_URL)
                        try:
                            save_info = '{}\u0001{}\u0001{}\u0001{}'.format(name, ''.join(restaurant_name),
                                                                            ''.join(restaurant_type),
                                                                            ''.join(restaurant_url))
                        except:
                            continue
                        save_list.append(save_info)
                else:
                    continue
                self.pipe.pipe_txt_save(save_list, filename=setting.FILE_RESTAURANT_LIST, savetype='a')
                if params_city['page'] >= maxpage:
                    break
                time.sleep(0.2)

    def _engine_restaurant_info(self):
        """
        获取所有餐厅详细数据
        :return:
        """
        res_list = self.pipe.pipe_txt_load(filename=setting.FILE_RESTAURANT_LIST)
        for each_res in res_list:
            # 店铺数据
            res_info = each_res.strip().split('\u0001')
            city_name = res_info[0]
            res_name = res_info[1]
            res_type = res_info[2]
            res_url = res_info[3]
            find_id = re.search(re.compile(r'p-oi(\d+)-'), res_url)
            if find_id:
                res_id = find_id.group(1)
            else:
                res_id = 0
            # 获取店铺详细信息
            content = self.crawl.crawl_by_get(res_url, headers=setting.HEADERS, proxies=self._engine_use_proxy(),
                                              retry=5)
            detail = self.analysis.analysis_by_xpath(content, xpahter=setting.XPATH_RES_DETAIL)
            detail['city_name'] = city_name
            detail['restaurant_name'] = res_name
            detail['restaurant_type'] = res_type
            detail['restaurant_url'] = res_url
            detail['restaurant_id'] = res_id
            self.pipe.pipe_mongo_save(detail, dbname='db_qunaer', colname='col_food_info')
            time.sleep(0.2)

    def _engine_restaurant_comments(self):
        """
        获取所有餐厅评论数据
        :return:
        """
        res_list = self.pipe.pipe_txt_load(filename=setting.FILE_RESTAURANT_LIST)
        # 每个店铺最新评论时间表
        check_dict = self.pipe.pipe_pickle_load(filename=setting.FILE_COMMENTS_CHECK)
        if not check_dict:
            check_dict = {}
        for each_res in res_list:
            # 店铺数据
            city = each_res.strip().split('\u0001')[0]
            food = each_res.strip().split('\u0001')[1]
            type = each_res.strip().split('\u0001')[2]
            res_url = each_res.strip().split('\u0001')[3]
            find_id = re.search(re.compile(r'p-oi(\d+)-'), res_url)
            if find_id:

                res_id = find_id.group(1)
            else:
                continue
            api = setting.COMMENTS_API.format(res_id)
            setting.HEADERS_COMMENTS['Referer'] = res_url
            params = {
                'page': 0,
                'pageSize': '10',
                'poiList': 'true',
                'rank': 0,  # 全部评论
                'sortField': 0  # 按照时间排序
            }
            comments_time = set([])
            current_time = check_dict.get(res_id, '0')
            max_page = 1
            save_list = []
            while True:
                params['page'] += 1
                content = self.crawl.crawl_by_get(api, headers=setting.HEADERS_COMMENTS,
                                                  proxies=self._engine_use_proxy(),
                                                  params=params, retry=3, timeout=20)
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
                if elements_com:
                    for each_element in elements_com:
                        title = self.analysis.analysis_by_xpath(each_element, xpahter=setting.XPATH_COMMENTS_TITLE)
                        start = self.analysis.analysis_by_xpath(each_element, xpahter=setting.XPATH_COMMENTS_START)
                        nick = self.analysis.analysis_by_xpath(each_element, xpahter=setting.XPATH_COMMENTS_NICK)
                        more = self.analysis.analysis_by_xpath(each_element, xpahter=setting.XPATH_COMMENTS_MORE)
                        if more:
                            content_more = self.crawl.crawl_by_get(more[0], headers=setting.HEADERS,
                                                                   proxies=self._engine_use_proxy())
                            content = self.analysis.analysis_by_xpath(content_more, xpahter=setting.XPATH_COMMENTS_DETAIL)
                        else:
                            content = self.analysis.analysis_by_xpath(each_element, xpahter=setting.XPATH_COMMENTS_CONTENT)
                        date = self.analysis.analysis_by_xpath(each_element, xpahter=setting.XPATH_COMMENTS_DATE)
                        deal_content = ''.join(list(map(lambda x: x.replace('\n', '').replace('\r', '').replace('\t', '').
                                                        replace(' ', ''), content)))
                        if ''.join(date) > current_time:
                            commetents_info = {
                                'city': city,
                                'food': food,
                                'food_id': res_id,
                                'type': type,
                                'title': ''.join(title),
                                'nick': ''.join(nick),
                                'start': ''.join(start),
                                'content': deal_content,
                                'date': ''.join(date),
                                'get_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                'url': res_url
                            }
                            save_list.append(commetents_info)
                            comments_time.add(''.join(date))
                else:
                    continue
                # 超过评论最大页数则切换
                if params['page'] >= max_page:
                    break
                # 当前页面没有新增评论也切换至下一店铺
                if not len(comments_time):
                    break
            # 每个店铺最新的评论时间
            if comments_time:
                check_dict[res_id] = max(comments_time)
            # 抓取到的评论数据
            if save_list:
                self.pipe.pipe_mongo_save(save_list, dbname='db_qunaer', colname='col_food_comments')
        self.pipe.pipe_pickle_save(check_dict, filename=setting.FILE_COMMENTS_CHECK)

    @staticmethod
    def _engine_use_proxy():
        """
        使用代理ip
        :return: 代理ip
        """
        proxy_host = "proxy.abuyun.com"
        proxy_port = "****"
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
        self._engine_restaurant_link()
        # 店铺信息和店铺评论可以同时抓取的，用多进程实现，后期可根据需求添加该功能，目前未开发循环抓取功能
        self._engine_restaurant_info()
        self._engine_restaurant_comments()


if __name__ == '__main__':
    start = time.time()
    proc = Engine()
    proc.start_engine()
    end = time.time()
    print('执行完毕，耗时 {:.2f} s'.format(end - start))
