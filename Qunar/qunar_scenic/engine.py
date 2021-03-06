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

    def _engine_scenic_link(self):
        """
        获取每个城市中所有的景点的链接
        :return:
        """
        city_list = self.pipe.pipe_txt_load(filename=setting.FILE_CITY_LIST)
        for each_city in city_list:
            url = each_city.strip().split('\u0001')[1] + '-jingdian'
            name = each_city.strip().split('\u0001')[0]
            page = 1
            maxpage = 200  # 默认最大页数
            while True:
                try:
                    next_url = url + '-1-{}'.format(page)
                    save_list = []
                    # 获取总页数
                    if page == 1:
                        content = self.crawl.crawl_by_get(url, headers=setting.HEADERS, proxies=self._engine_use_proxy(),
                                                          retry=5)
                        # 找到最大页数,使用map函数
                        pagecount = map(lambda x: int(x) if x != '下一页' else -1,
                                        self.analysis.analysis_by_xpath(content, xpahter=setting.XPATH_NEXTPAGE))
                        if not pagecount:
                            break
                        maxpage = max(pagecount)
                    else:
                        content = self.crawl.crawl_by_get(next_url, headers=setting.HEADERS,
                                                          proxies=self._engine_use_proxy(),
                                                          retry=5)
                    element_li = self.analysis.analysis_by_xpath(content, xpahter=setting.XPATH_LI)
                    if not element_li:
                        break
                    for each_ele in element_li:
                        scenic_name = self.analysis.analysis_by_xpath(each_ele, xpahter=setting.XPATH_SCEN_NAME)
                        scenic_url = self.analysis.analysis_by_xpath(each_ele, xpahter=setting.XPATH_SCEN_URL)
                        try:
                            save_info = '{}\u0001{}\u0001{}'.format(name, ''.join(scenic_name),
                                                                    ''.join(scenic_url))
                        except:
                            continue
                        save_list.append(save_info)
                    self.pipe.pipe_txt_save(save_list, filename=setting.FILE_SCENIC_LIST, savetype='a')
                    if page >= maxpage:
                        break
                    page += 1
                    time.sleep(0.2)
                except:
                    break

    def _engine_scenic_info(self):
        """
        获取所有景点详细数据
        :return:
        """
        scen_list = self.pipe.pipe_txt_load(filename=setting.FILE_SCENIC_LIST)
        for each_res in scen_list:
            try:
                # 景区数据
                scen_info = each_res.strip().split('\u0001')
                city_name = scen_info[0]
                scen_name = scen_info[1]
                scen_url = scen_info[2]
                find_id = re.search(re.compile(r'p-oi(\d+)-'), scen_url)
                if find_id:
                    scen_id = find_id.group(1)
                else:
                    scen_id = 0
                # 获取店铺详细信息
                content = self.crawl.crawl_by_get(scen_url, headers=setting.HEADERS, proxies=self._engine_use_proxy(),
                                                  retry=5, timeout=15)
                detail = self.analysis.analysis_by_xpath(content, xpahter=setting.XPATH_SCEN_DETAIL)
                detail['city_name'] = city_name
                detail['scenic_name'] = scen_name
                detail['scenic_url'] = scen_url
                detail['scenic_id'] = scen_id
                detail['get_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                # 存储数据
                # 字段顺序：city_name, scenic_name, scenic_id
                # score, ranking, describe, address, tel, web, time, open_time, arrive,
                # ticket, travel_time, tip, scenic_url, get_time
                save_data = '{0[city_name]}\u0001{0[scenic_name]}\u0001{0[scenic_id]}\u0001' \
                            '{0[score]}\u0001{0[ranking]}\u0001{0[describe]}\u0001' \
                            '{0[address]}\u0001{0[tel]}\u0001{0[web]}\u0001' \
                            '{0[time]}\u0001{0[open_time]}\u0001{0[arrive]}\u0001' \
                            '{0[ticket]}\u0001{0[travel_time]}\u0001{0[tip]}\u0001' \
                            '{0[scenic_url]}\u0001{0[get_time]}'.format(detail)
                self.pipe.pipe_txt_save(save_data, filename=setting.FILE_SCENIC_INFO, savetype='a')
                # self.pipe.pipe_mongo_save(detail, dbname='db_qunaer', colname='col_scenic_info')
                time.sleep(0.2)
            except:
                continue

    def _engine_scenic_comments(self):
        """
        获取所有景区评论数据
        :return:
        """
        scen_list = self.pipe.pipe_txt_load(filename=setting.FILE_SCENIC_LIST)
        # 每个景区最新评论时间表
        check_dict = self.pipe.pipe_pickle_load(filename=setting.FILE_COMMENTS_CHECK)
        if not check_dict:
            check_dict = {}
        for each_res in scen_list:
            try:
                # 景区数据
                city = each_res.strip().split('\u0001')[0]
                scen = each_res.strip().split('\u0001')[1]
                scen_url = each_res.strip().split('\u0001')[2]
                find_id = re.search(re.compile(r'p-oi(\d+)-'), scen_url)
                if find_id:
                    scen_id = find_id.group(1)
                else:
                    continue
                api = setting.COMMENTS_API.format(scen_id)
                setting.HEADERS_COMMENTS['Referer'] = scen_url
                params = {
                    'page': 0,
                    'pageSize': '10',
                    'poiList': 'true',
                    'rank': 0,  # 全部评论
                    'sortField': 0  # 按照时间排序
                }
                comments_time = set([])
                current_time = check_dict.get(scen_id, '0')
                max_page = 1
                while True:
                    params['page'] += 1
                    content = self.crawl.crawl_by_get(api, headers=setting.HEADERS_COMMENTS,
                                                      proxies=self._engine_use_proxy(),
                                                      params=params, retry=3, timeout=15)
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
                                                                   proxies=self._engine_use_proxy(), retry=2, timeout=15)
                            content = self.analysis.analysis_by_xpath(content_more, xpahter=setting.XPATH_COMMENTS_DETAIL)
                        else:
                            content = self.analysis.analysis_by_xpath(each_element, xpahter=setting.XPATH_COMMENTS_CONTENT)
                        date = self.analysis.analysis_by_xpath(each_element, xpahter=setting.XPATH_COMMENTS_DATE)
                        deal_content = ''.join(list(map(lambda x: x.replace('\n', '').replace('\r', '').replace('\t', '').
                                                        replace(' ', ''), content)))
                        if ''.join(date) > current_time:
                            commetents_info = {
                                'city': city,
                                'scenic': scen,
                                'scen_id': scen_id,
                                'title': ''.join(title),
                                'nick': ''.join(nick),
                                'start': ''.join(start),
                                'content': deal_content,
                                'date': ''.join(date),
                                'get_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                'url': scen_url
                            }
                            comments_time.add(''.join(date))
                            # 存储数据
                            # 字段顺序
                            # city, scenic, scen_id, title, nick, start, content, date, get_time, url
                            save_data = '{0[city]}\u0001{0[scenic]}\u0001{0[scen_id]}\u0001' \
                                        '{0[title]}\u0001{0[nick]}\u0001{0[start]}\u0001' \
                                        '{0[content]}\u0001{0[date]}\u0001{0[get_time]}\u0001' \
                                        '{0[url]}\u0001'.format(commetents_info)
                            self.pipe.pipe_txt_save(save_data, filename=setting.FILE_SCENIC_COMMENTS,
                                                    savetype='a')
                            # self.pipe.pipe_mongo_save(save_list, dbname='db_qunaer', colname='col_scenic_comments')

                    if params['page'] >= max_page:
                        break
                    # 当前页面没有新增评论也切换至下一店铺
                    if not len(comments_time):
                        break
                if comments_time:
                    check_dict[scen_id] = max(comments_time)
                # 抓取到的评论数据
                self.pipe.pipe_pickle_save(check_dict, filename=setting.FILE_COMMENTS_CHECK)
            except:
                continue
            # 每个店铺最新的评论时间

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
        self._engine_scenic_info()
        self._engine_scenic_comments()


if __name__ == '__main__':
    start = time.time()
    proc = Engine()
    proc.start_engine()
    end = time.time()
    print('执行完毕，耗时 {:.2f} s'.format(end - start))
