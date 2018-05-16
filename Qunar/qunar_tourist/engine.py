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


class Engine(object):
    def __init__(self):
        self.crawl = Crawl()
        self.analysis = Analysis()
        self.pipe = Pipeline()

    def _engine_get_citylist(self):
        """
        获取城市列表，包括城市的url及城市名称
        :return:
        """
        content = self.crawl.crawl_by_get(setting.START_URL, headers=setting.HEADERS)
        res = self.analysis.analysis_by_xpath(content, xpahter=setting.XPATH_CITYLIST_A)
        saveinfo = set([])
        for each in res:
            cityname = self.analysis.analysis_by_xpath(each, xpahter=setting.XPATH_TEXT)
            cityhref = self.analysis.analysis_by_xpath(each, xpahter=setting.XPATH_HREF)
            citylink = setting.START_URL + cityhref[0][1:]
            try:
                savelist = '{}\u0001{}'.format(cityname[0], citylink)
                saveinfo.add(savelist)
            except:
                continue
        self.pipe.pipe_txt_save(saveinfo, filename=setting.FILE_CITY_LIST, savetype='w')

    def _engine_get_touristlist(self):
        """
        获取所有景区链接以及id
        :return:
        """
        # 清空文本
        self.pipe.pipe_remove_file(setting.FILE_TOURIST_LIST)
        citylist = self.pipe.pipe_txt_load(filename=setting.FILE_CITY_LIST, loadtype='r')
        for eachcity in citylist:
            try:
                saveinfo = set([])
                params = {
                    'from': 'mpshouye_hotdest_more',
                    'keyword': '柳州',
                    'page': 1
                }
                cityname = eachcity.strip().split('\u0001')[0]
                params['keyword'] = cityname
                while True:
                    content = self.crawl.crawl_by_get(setting.TOURIS_URL, params=params, headers=setting.HEADERS,
                                                      proxies=self._engine_use_proxy(), retry=3, timeout=15)
                    res_element = self.analysis.analysis_by_xpath(content, xpahter=setting.XPATH_TOURIST_A)
                    if not res_element:
                        break
                    for eachelement in res_element:
                        tourist_name = self.analysis.analysis_by_xpath(eachelement, xpahter=setting.XPATH_TEXT)
                        tourist_href = self.analysis.analysis_by_xpath(eachelement, xpahter=setting.XPATH_HREF)
                        tourist_link = setting.START_URL + tourist_href[0][1:]
                        pattern = re.compile(r'detail_(\d+)', re.S)
                        re_id = re.search(pattern, tourist_link)
                        if re_id:
                            tourist_id = re_id.group(1)
                        else:
                            tourist_id = ''
                        # 数据结构依次为 景区名字 景区id 景区链接
                        saveinfo.add('{}\u0001{}\u0001{}'.format(tourist_name[0], tourist_id, tourist_link))
                        # print(saveinfo)
                    params['page'] += 1
                self.pipe.pipe_txt_save(saveinfo, filename=setting.FILE_TOURIST_LIST, savetype='a')
            except:
                continue

    def _engine_get_touristinfo(self):
        """
        获取每个景区详细信息
        :return:
        """
        tourist_list = self.pipe.pipe_txt_load(filename=setting.FILE_TOURIST_LIST)
        for eachtourist in tourist_list:
            try:
                tourist_url = eachtourist.strip().split('\u0001')[2]
                content = self.crawl.crawl_by_get(tourist_url, headers=setting.HEADERS, proxies=self._engine_use_proxy())
                res = self.analysis.analysis_by_xpath(content, setting.XPATH_TOURIST_DETAIL)
                # 存储数据
                # 字段顺序
                # t_name, t_type, t_des, address, score, price, describe
                save_data = '{0[t_name]}\u0001{0[t_type]}\u0001{0[t_des]}\u0001' \
                            '{0[address]}\u0001{0[score]}\u0001{0[price]}\u0001' \
                            '{0[describe]}'.format(res)
                self.pipe.pipe_txt_save(save_data, filename=setting.FILE_TOURIST_INFO, savetype='a')
                time.sleep(0.1)
            except:
                continue

    def _engine_get_comments(self):
        """
        获取景区评论数据
        :return:
        """
        # 景区名称/id/链接
        tourist_list = self.pipe.pipe_txt_load(filename='file_tourist_list.txt', loadtype='r')
        for each_tourist in tourist_list:
            try:
                tourist_id = each_tourist.strip().split('\u0001')[1]
                tourist_url = each_tourist.strip().split('\u0001')[2]
                tourist_name = each_tourist.strip().split('\u0001')[0]
                # 评论翻页参数
                params_comments = {
                    'sightId': '12579',
                    'index': 0,
                    'page': 0,
                    'pageSize': '10',
                    'tagType': '0',
                }
                # 查询景区节点数据
                check_node = self.pipe.pipe_pickle_load(filename=setting.FILE_TOURIST_CHECK)
                if not check_node:
                    check_node = {}
                tourist_node = check_node.get(tourist_id, {})
                # 节点中记录的上次抓取评论数量
                node_count = tourist_node.get('comments_count', 0)
                # 节点中记录的上次抓取的最大时间节点
                node_latest = tourist_node.get('comments_latest', '0')
                savelist = []  # 有效评论(新增评论)
                latest_time = set([])  # 评论时间集合
                datanum = -1  # 评论数量
                while True:
                    params_comments['sightId'] = tourist_id
                    params_comments['index'] += 1
                    params_comments['page'] += 1
                    setting.HEADERS_COMMENTS['Referer'] = tourist_url
                    content = self.crawl.crawl_by_get(setting.COMMENTS_API, headers=setting.HEADERS_COMMENTS,
                                                      params=params_comments, proxies=self._engine_use_proxy(),
                                                      retry=2, timeout=15)
                    contnet_dict = json.loads(content)
                    # 查看当前评论数量,自在第一页的时候进行这一步检查
                    if params_comments['page'] == 1:
                        taglist = contnet_dict.get('data', {}).get('tagList', [])
                        if taglist:
                            for each in taglist:
                                if each.get('tagName') == '全部':
                                    datanum = each.get('tagNum')
                                    break
                        # 如果节点中的数据数量与当前景区实时评论数量一致，则说明没有新增评论
                        if node_count == datanum:
                            break
                    # 获取评论列表
                    datalist = contnet_dict.get('data', {}).get('commentList', [])
                    if not datalist:
                        break
                    # 直接写到mongodb中去 如果后期需要输出到txt文本，请修改此处
                    current_data = False
                    for each in datalist:
                        current_time = each.get('date')
                        each['tourist_id'] = tourist_id
                        each['tourist_name'] = tourist_name
                        each['tourist_url'] = tourist_url
                        each['get_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        if current_time > node_latest:
                            # 存储数据
                            # 字段顺序
                            # tourist_name, tourist_id, author, commentId, content, date, score, get_time,tourist_url
                            save_data = '{0[tourist_name]}\u0001{0[tourist_id]}\u0001{0[author]}\u0001' \
                                        '{0[commentId]}\u0001{0[content]}\u0001{0[date]}\u0001' \
                                        '{0[score]}\u0001{0[get_time]}\u0001{0[tourist_url]}\u0001'.format(each)
                            self.pipe.pipe_txt_save(save_data, filename=setting.FILE_TOURIST_COMMENTS, savetype='a')
                            latest_time.add(current_time)
                            current_data = True
                    # 如果当前页面没有新增数据，且页码数大于15页面，则此景区本次评论抓取结束
                    if not current_data and params_comments['page'] >= 15:
                        break
                    time.sleep(0.2)
                # 若从页面获取数据量失败，则不更新数据量这一字段
                if datanum != -1:
                    tourist_node['comments_count'] = datanum
                # 若没有新增的数据 则不更新数据时间节点这一字段
                if latest_time:
                    tourist_node['comments_latest'] = max(latest_time)
                check_node = {tourist_id: tourist_node}
                self.pipe.pipe_pickle_save(check_node, filename=setting.FILE_TOURIST_CHECK)
            except:
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

    def engine_run(self):
        self._engine_get_citylist()
        self._engine_get_touristlist()
        self._engine_get_touristinfo()
        self._engine_get_comments()


if __name__ == '__main__':
    start = time.time()
    proc = Engine()
    proc.engine_run()
    end = time.time()
    print('执行完毕，耗时{:.2f}s'.format(end - start))
