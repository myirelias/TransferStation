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

    def _engine_tactic_link(self):
        """
        获取每个城市中所有的攻略的链接
        :return:
        """
        city_list = self.pipe.pipe_txt_load(filename=setting.FILE_CITY_LIST)
        tactic_check = self.pipe.pipe_pickle_load(filename=setting.FILE_TACTIC_CHECK)
        if not tactic_check:
            tactic_check = set([])
        for each_city in city_list:
            """
            http://travel.qunar.com/travelbook/list/22-城市拼音-城市id/
            hot(hot为热门游记，elite为精华游记，start为行程计划)_ctime(ctime为按最新发表排序，heat为热度排序)/页码.htm 
            """
            try:
                url = each_city.strip().split('\u0001')[1]
                name = each_city.strip().split('\u0001')[0]
                pattern = re.compile(r'p-cs(\d+)-(\w+)')
                city_pname = re.search(pattern, url).group(2)
                city_id = re.search(pattern, url).group(1)
                # 拼接攻略所在url(1.城市拼音名称:city_pname, 2.城市id:city_id, 3.分类)
                tactic_type = ['hot', 'elite', 'start']  # 攻略分类，目前脚本先抓取hot类
                tactic_url = setting.TACTIC_URL.format(city_pname, city_id, tactic_type[0])
                current_page = 0
                maxpage = 200  # 默认最大页数
                while True:
                    save_list = []
                    current_page += 1
                    content = self.crawl.crawl_by_get(tactic_url + '{}.htm'.format(current_page),
                                                      headers=setting.HEADERS, retry=2, timeout=15,
                                                      proxies=self._engine_use_proxy())
                    if not content:
                        break
                    # 获取总页数
                    if current_page == 1:
                        # 找到最大页数,使用map函数
                        pagecount = map(lambda x: int(x) if x != '下一页>' else -1,
                                        self.analysis.analysis_by_xpath(content, xpahter=setting.XPATH_NEXTPAGE))
                        try:
                            maxpage = max(pagecount)
                        except:
                            break
                    tactic_ids = self.analysis.analysis_by_xpath(content, xpahter=setting.XPATH_ID)
                    for each_id in tactic_ids:
                        each_url = 'http://travel.qunar.com/youji/{}'.format(each_id)
                        save_info = '{}\u0001{}\u0001{}\u0001{}\u0001{}'.format(name, city_pname, city_id, each_id,
                                                                                each_url)
                        if each_id not in tactic_check:
                            save_list.append(save_info)
                            tactic_check.add(each_id)
                    if save_list:
                        self.pipe.pipe_txt_save(save_list, filename=setting.FILE_TACTIC_LIST, savetype='a')
                    if current_page >= maxpage:
                        break
                    time.sleep(0.2)
            except:
                continue

    def _engine_tactic_info(self):
        """
        获取所有攻略详细数据
        :return:
        """
        tactic_list = self.pipe.pipe_txt_load(filename=setting.FILE_TACTIC_LIST)
        for each_tactic in tactic_list:
            try:
                # 攻略数据
                tactic_info = each_tactic.strip().split('\u0001')
                city_name = tactic_info[0]
                city_pname = tactic_info[1]
                city_id = tactic_info[2]
                tactic_id = tactic_info[3]
                tactic_url = tactic_info[4]
                # 获取娱乐场所详细信息
                content = self.crawl.crawl_by_get(tactic_url, headers=setting.HEADERS, proxies=self._engine_use_proxy(),
                                                  retry=3, timeout=15)
                detail = self.analysis.analysis_by_xpath(content, xpahter=setting.XPATH_TACTIC_DETAIL)
                detail['city_name'] = city_name
                detail['city_pname'] = city_pname
                detail['city_id'] = city_id
                detail['tactic_id'] = tactic_id
                detail['tactic_url'] = tactic_url
                detail['get_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                # 存储数据
                # 字段顺序
                # city_name, city_pname, city_id,
                # tactic_id,title,author,
                # create_date,start_date,days,
                # avgs_price,person,play_type,
                # content,get_time, tactic_url
                save_data = '{0[city_name]}\u0001{0[city_pname]}\u0001{0[city_id]}\u0001' \
                            '{0[tactic_id]}\u0001{0[title]}\u0001{0[author]}\u0001' \
                            '{0[create_date]}\u0001{0[start_date]}\u0001{0[days]}\u0001' \
                            '{0[avgs_price]}\u0001{0[person]}\u0001{0[play_type]}\u0001' \
                            '{0[content]}\u0001{0[get_time]}\u0001{0[tactic_url]}\u0001'.format(detail)
                self.pipe.pipe_txt_save(save_data, filename=setting.FILE_TACTIC_INFO, savetype='a')
                # self.pipe.pipe_mongo_save(detail, dbname='db_qunaer', colname='col_shop_info')
                time.sleep(0.1)
            except Exception as e:
                print('crawl error', e)
                continue

    def _engine_tactic_comments(self):
        """
        获取所有攻略评论数据
        :return:
        """
        tactic_list = self.pipe.pipe_txt_load(filename=setting.FILE_TACTIC_LIST)
        # 每个店铺最新评论时间表

        for each_tactic in tactic_list:
            try:
                # 店铺数据
                each_info = each_tactic.strip().split('\u0001')
                city_name = each_info[0]
                city_pname = each_info[1]
                city_id = each_info[2]
                tactic_id = each_info[3]
                tactic_url = each_info[4]
                setting.HEADERS_COMMENTS['Referer'] = tactic_url
                params = {
                    'bookId': tactic_id,  # 攻略id
                    'csrfToken': 'o7mGNaK63wbEaYFJTnDue14WX7sPlyXB',  # 暂时固定token
                    'page': 0,  # 页码
                    'pageSize': 30,  # 每页数量
                }
                while True:
                    params['page'] += 1
                    content = self.crawl.crawl_by_get(setting.COMMENTS_API, headers=setting.HEADERS_COMMENTS,
                                                      proxies=self._engine_use_proxy(),
                                                      params=params, retry=2, timeout=15)
                    try:
                        content_dict = json.loads(content)
                    except:
                        break
                    if not content_dict.get('data', {}).get('html'):
                        break
                    content_comments = content_dict.get('data', {}).get('html')
                    # 第一遍抓取要确定评论页数
                    elements_com = self.analysis.analysis_by_xpath(content_comments, xpahter=setting.XPATH_COMMENTS_LI)
                    if not elements_com:
                        break
                    for each_element in elements_com:
                        ask_content = self.analysis.analysis_by_xpath(each_element,
                                                                      xpahter=setting.XPATH_COMMENTS_ASK_CONTENT)
                        answer_content = self.analysis.analysis_by_xpath(each_element,
                                                                         xpahter=setting.XPATH_COMMENTS_ANSWER_CONTENT)
                        ask_date = self.analysis.analysis_by_xpath(each_element,
                                                                   xpahter=setting.XPATH_COMMENTS_ASK_DATE)
                        answer_date = self.analysis.analysis_by_xpath(each_element,
                                                                      xpahter=setting.XPATH_COMMENTS_ANSWER_DATE)

                        commetents_info = {
                            'city_name': city_name,
                            'city_id': city_id,
                            'tactic_id': tactic_id,
                            'ask_content': ask_content,
                            'answer_content': answer_content,
                            'ask_date': ask_date,
                            'answer_date': answer_date,
                            'get_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'tactic_url': tactic_url
                        }
                        for eachkey in commetents_info.keys():

                            if isinstance(commetents_info[eachkey], str):
                                commetents_info[eachkey] = commetents_info[eachkey]\
                                    .replace('\n', '').replace('\r', '').replace('\xa0', '')
                            elif isinstance(commetents_info[eachkey], list):
                                commetents_info[eachkey] = ''.join(commetents_info[eachkey])\
                                    .replace('\n', '').replace('\r', '')
                            # 存储数据
                            # 字段顺序
                            # city_name, city_id, tactic_id,
                            # ask_content, answer_content, ask_date,
                            # answer_date, get_time, tactic_url,
                        save_data = '{0[city_name]}\u0001{0[city_id]}\u0001{0[tactic_id]}\u0001' \
                                    '{0[ask_content]}\u0001{0[answer_content]}\u0001{0[ask_date]}\u0001' \
                                    '{0[answer_date]}\u0001{0[get_time]}\u0001' \
                                    '{0[tactic_url]}\u0001'.format(commetents_info)
                        self.pipe.pipe_txt_save(save_data, filename=setting.FILE_TACTIC_COMMENTS, savetype='a')
                        # self.pipe.pipe_mongo_save(commetents_info, dbname='db_qunaer', colname='col_shopping_comments')
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
        # 本版块循环策略为循环抓取攻略，然后评论每次抓取一次攻略列表之后，抓取一遍所有攻略所有评论，并入存入新的文本
        self._engine_tactic_link()
        self._engine_tactic_info()
        self._engine_tactic_comments()


if __name__ == '__main__':
    start = time.time()
    proc = Engine()
    proc.start_engine()
    end = time.time()
    print('执行完毕，耗时 {:.2f} s'.format(end - start))
