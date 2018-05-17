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

    def _engine_surround_link(self):
        """
        获取每个城市中所有的周边游玩地点的链接
        :return:
        """
        city_list = self.pipe.pipe_txt_load(filename=setting.FILE_CITY_LIST)
        for each_city in city_list:
            url = each_city.strip().split('\u0001')[1] + '-zhoubian'
            name = each_city.strip().split('\u0001')[0]
            page = 1
            maxpage = 200  # 默认最大页数
            while True:
                try:
                    next_url = url + '-2-1-{}'.format(page)
                    save_list = []
                    # 获取总页数

                    content = self.crawl.crawl_by_get(next_url, headers=setting.HEADERS,
                                                      proxies=self._engine_use_proxy(),
                                                      retry=3, timeout=15)
                    # 找到最大页数,使用map函数
                    if page == 1:
                        pagecount = map(lambda x: int(x) if x != '下一页' else -1,
                                        self.analysis.analysis_by_xpath(content, xpahter=setting.XPATH_NEXTPAGE))
                        if pagecount:
                            maxpage = max(pagecount)
                    element_li = self.analysis.analysis_by_xpath(content, xpahter=setting.XPATH_DIV)
                    if not element_li:
                        break
                    for each_ele in element_li:
                        surround_name = self.analysis.analysis_by_xpath(each_ele, xpahter=setting.XPATH_SURROUND_NAME)
                        surround_type = self.analysis.analysis_by_xpath(each_ele, xpahter=setting.XPATH_SURROUND_TYPE)
                        surround_url = self.analysis.analysis_by_xpath(each_ele, xpahter=setting.XPATH_SURROUND_URL)
                        try:
                            save_info = '{}\u0001{}\u0001{}\u0001{}'.format(name, ''.join(surround_name),
                                                                            '-'.join(surround_type),
                                                                            ''.join(surround_url))
                        except:
                            continue
                        save_list.append(save_info)
                    self.pipe.pipe_txt_save(save_list, filename=setting.FILE_SURROUND_LIST, savetype='a')
                    if page >= maxpage:
                        break
                    page += 1
                    time.sleep(0.2)
                except:
                    break

    def _engine_surround_info(self):
        """
        获取所有周边游场所详细数据
        :return:
        """
        surround_list = self.pipe.pipe_txt_load(filename=setting.FILE_SURROUND_LIST)
        for each_res in surround_list:
            try:
                # 景区数据
                surround_info = each_res.strip().split('\u0001')
                city_name = surround_info[0]
                surround_name = surround_info[1]
                surround_url = surround_info[3]
                surround_type = surround_info[2]
                find_id = re.search(re.compile(r'p-oi(\d+)-'), surround_url)
                if find_id:
                    surround_id = find_id.group(1)
                else:
                    surround_id = 0
                # 获取店铺详细信息
                content = self.crawl.crawl_by_get(surround_url, headers=setting.HEADERS, proxies=self._engine_use_proxy(),
                                                  retry=5, timeout=15)
                detail = self.analysis.analysis_by_xpath(content, xpahter=setting.XPATH_SURROUND_DETAIL)
                detail['city_name'] = city_name
                detail['surround_name'] = surround_name
                detail['surround_url'] = surround_url
                detail['surround_id'] = surround_id
                detail['surround_type'] = surround_type
                detail['get_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                # 字段顺序：city_name, surround_name, surround_id, surround_type
                # score, ranking, describe, address, tel, web, time, open_time, arrive,
                # ticket, travel_time, tip, surround_url, get_time
                save_data = '{0[city_name]}\u0001{0[surround_name]}\u0001{0[surround_id]}\u0001{0[surround_type]}\u0001' \
                            '{0[score]}\u0001{0[ranking]}\u0001{0[describe]}\u0001' \
                            '{0[address]}\u0001{0[tel]}\u0001{0[web]}\u0001' \
                            '{0[time]}\u0001{0[open_time]}\u0001{0[arrive]}\u0001' \
                            '{0[ticket]}\u0001{0[travel_time]}\u0001{0[tip]}\u0001' \
                            '{0[surround_url]}\u0001{0[get_time]}'.format(detail)
                self.pipe.pipe_txt_save(save_data, filename=setting.FILE_SURROUND_INFO, savetype='a')
                # self.pipe.pipe_mongo_save(detail, dbname='db_qunaer', colname='col_scenic_info')
                time.sleep(0.2)
            except:
                continue

    def _engine_surround_comments(self):
        """
        获取所有景区评论数据
        :return:
        """
        scen_list = self.pipe.pipe_txt_load(filename=setting.FILE_SURROUND_LIST)
        # 每个景区最新评论时间表
        check_dict = self.pipe.pipe_pickle_load(filename=setting.FILE_COMMENTS_CHECK)
        if not check_dict:
            check_dict = {}
        for each_res in scen_list:
            try:
                # 景区数据
                city = each_res.strip().split('\u0001')[0]
                surround = each_res.strip().split('\u0001')[1]
                surround_type = each_res.strip().split('\u0001')[2]
                surround_url = each_res.strip().split('\u0001')[3]
                find_id = re.search(re.compile(r'p-oi(\d+)-'), surround_url)
                if find_id:
                    surround_id = find_id.group(1)
                else:
                    continue
                api = setting.COMMENTS_API.format(surround_id)
                setting.HEADERS_COMMENTS['Referer'] = surround_url
                params = {
                    'page': 0,
                    'pageSize': '10',
                    'poiList': 'true',
                    'rank': 0,  # 全部评论
                    'sortField': 0  # 按照时间排序
                }
                comments_time = set([])
                current_time = check_dict.get(surround_id, '0')
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
                                                                   proxies=self._engine_use_proxy(), retry=2,
                                                                   timeout=15)
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
                                'surround': surround,
                                'surround_id': surround_id,
                                'title': ''.join(title),
                                'nick': ''.join(nick),
                                'start': ''.join(start),
                                'content': deal_content,
                                'date': ''.join(date),
                                'get_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                'url': surround_url
                            }
                            comments_time.add(''.join(date))
                            for eachkey in commetents_info.keys():
                                commetents_info[eachkey] = commetents_info[eachkey].replace('\n', '').replace('\r', '')
                            # 存储数据
                            # 字段顺序
                            # city, surround, surround_id, title, nick, start, content, date, get_time, url
                            save_data = '{0[city]}\u0001{0[surround]}\u0001{0[surround_id]}\u0001' \
                                        '{0[title]}\u0001{0[nick]}\u0001{0[start]}\u0001' \
                                        '{0[content]}\u0001{0[date]}\u0001{0[get_time]}\u0001' \
                                        '{0[url]}\u0001'.format(commetents_info)
                            self.pipe.pipe_txt_save(save_data, filename=setting.FILE_SURROUND_COMMENTS,
                                                    savetype='a')
                            # self.pipe.pipe_mongo_save(save_list, dbname='db_qunaer', colname='col_scenic_comments')

                    if params['page'] >= max_page:
                        break
                    # 当前页面没有新增评论也切换至下一店铺
                    if not len(comments_time):
                        break
                if comments_time:
                    check_dict[surround_id] = max(comments_time)
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
        self._engine_surround_link()
        self._engine_surround_info()
        self._engine_surround_comments()


if __name__ == '__main__':
    start = time.time()
    proc = Engine()
    proc.start_engine()
    end = time.time()
    print('执行完毕，耗时 {:.2f} s'.format(end - start))
