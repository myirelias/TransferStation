# !/usr/bin/env python
# coding=utf-8
'''引擎模块'''

import os
os.chdir(os.path.split(os.path.realpath(__file__))[0])
import time
import re
import json
import datetime
import shutil
import logging
import sys
from crawl import Crawl
from analysis import Analysis
from pipeline import Pipeline
from configbag import config as setting
try:
    from hdfs3 import HDFileSystem
except:
    pass
from dolog import AliyunLog
import queue

endpoint = 'cn-shenzhen.log.aliyuncs.com'  # 日志服务的http地址，必选参数
accessKeyId = 'F8TzTgiG8arBQSsb'  # 用户身份标识，必选参数
accessKey = 'pPNGvSuULYJChpvlfdwOWOhTFX4xSN'
project = 'daqsoft-test'  # 日志服务的项目名，必选参数
logstore = 'team_test'  # 日志服务的日志库名，必选参数


class Engine:

    def __init__(self):
        self.crawl = Crawl()
        self.analysis = Analysis()
        self.pipe = Pipeline()
        self._use_log()
        try:
            self.args_dict = eval(sys.argv[1:])
            if not isinstance(self.args_dict, dict):
                raise ValueError('args must be like key-value ')
        except Exception as e:
            self.args_dict = {}
            logging.warning('get args failed:{}'.format(e))
        self.proxies = self.args_dict.get('proxies')  # 代理配置
        self.hdfs = self.args_dict.get('hdfs', {})  # hdfs配置
        # 如果没有这两个参数 直接报异常 不执行
        if not self.hdfs or not self.proxies:
            raise ValueError('args not have hdfs or proxies')
        self.sleep_time = self.args_dict.get('sleep_time', 0.2)  # 休眠时间
        self.service_args = self.args_dict.get('service_args', {})  # PhantomJS代理配置
        self.aliyun_log = self.args_dict.get('aliyun_log', {})
        self.alilog = AliyunLog('{}_{}'.format(setting.OTA_NAME, setting.CATEGORY_NAME),
                                endp=self.aliyun_log.get('endpoint', endpoint),
                                accid=self.aliyun_log.get('accessKeyId', accessKeyId),
                                acckey=self.aliyun_log.get('accessKey', accessKey),
                                proj=self.aliyun_log.get('project', project),
                                logst=self.aliyun_log.get('logstore', logstore))  # 阿里云log配置文件,需要校验如果没有该参数会不会报错
        try:
            self.HDFS = HDFileSystem(host=self.hdfs.get('ip', '192.168.100.178'), port=self.hdfs.get('port', 8020))
        except:
            pass

    def _engine_city_link(self):
        """
        获取所有城市的名称和url链接，结果输出到file_city_list.txt文本中
        :return:
        """
        content = self.crawl.crawl_by_get(setting.START_URL, headers=setting.HEADERS, proxies=self.proxies)
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
        抓取之前获取当前已抓取的美食店铺id，当前抓取的id或进行校验是否为新增
        新增数据则存入到对应的TEMP文件中，最后本次循化完毕后，统一推送新增数据到HDFS
        本次循化所有模块执行完毕后，新增数据要追加入历史数据中，追加成功后修改新增数据文件名称，以便后面的新增文件不与前一次数据冲突
        修改新政文件名称时候使用完成抓取当日的日期作为文件名称前缀
        :return:
        """
        city_list = self.pipe.pipe_txt_load(filename=setting.FILE_CITY_LIST)
        # 获取已经抓取店铺id，便于识别新增数据
        history_restautrant = self.pipe.pipe_txt_load(filename=setting.FILE_RESTAURANT_LIST)
        history_id = set(map(lambda x: x.strip().split('\u0001')[2], [each for each in history_restautrant]))
        for each_city in set(city_list):
            # try:
            url = each_city.strip().split('\u0001')[1] + '-meishi'
            name = each_city.strip().split('\u0001')[0]
            params_city = {'page': 0}
            maxpage = 200  # 默认最大页数
            while True:
                save_list = []
                params_city['page'] += 1
                content = self.crawl.crawl_by_get(url, headers=setting.HEADERS, params=params_city,
                                                  proxies=self.proxies, retry=5)
                if not content:
                    break
                element_li = self.analysis.analysis_by_xpath(content, xpahter=setting.XPATH_LI)
                if not element_li:
                    break
                for each_ele in element_li:
                    restaurant_name = self.analysis.analysis_by_xpath(each_ele, xpahter=setting.XPATH_RES_NAME)
                    restaurant_type = self.analysis.analysis_by_xpath(each_ele, xpahter=setting.XPATH_RES_TYPE)
                    restaurant_url = self.analysis.analysis_by_xpath(each_ele, xpahter=setting.XPATH_RES_URL)
                    current_id = re.search(re.compile(r'p-oi(\d+)-'), ''.join(restaurant_url)).group(1)
                    if current_id in history_id:
                        continue
                    else:
                        history_id.add(current_id)
                    try:
                        # 存储字段
                        # name, restaurant_name, current_id, restaurant_type，, restaurant_url
                        save_info = '{}\u0001{}\u0001{}\u0001{}\u0001{}'.format(name, ''.join(restaurant_name),
                                                                                current_id,
                                                                                ''.join(restaurant_type),
                                                                                ''.join(restaurant_url))
                    except Exception as e:
                        self.alilog.warning('[list] {}'.format(e))
                        continue
                    save_list.append(save_info)
                if save_list:
                    self.pipe.pipe_txt_save(save_list, filename=setting.TEMP_RESTAURANT_LIST, savetype='a')
                if params_city['page'] >= maxpage:
                    break
                time.sleep(self.sleep_time)
                # except:
                #     continue

    def _engine_restaurant_info(self):
        """
        获取所有餐厅详细数据
        :return:
        """
        res_list = self.pipe.pipe_txt_load(filename=setting.FILE_RESTAURANT_LIST)
        temp_list = self.pipe.pipe_txt_load(filename=setting.TEMP_RESTAURANT_LIST)
        res_list.extend(temp_list)
        history_restautrant = self.pipe.pipe_txt_load(filename=setting.FILE_RESTAURANT_INFO)
        history_id = set(map(lambda x: x.strip().split('\u0001')[2], [each for each in history_restautrant]))
        for each_res in set(res_list):
            try:
                # 店铺数据
                res_info = each_res.strip().split('\u0001')
                city_name = res_info[0]
                res_name = res_info[1]
                res_id = res_info[2]
                if res_id in history_id:
                    continue
                else:
                    history_id.add(res_id)
                res_type = res_info[3]
                res_url = res_info[4]
                # 获取店铺详细信息
                content = self.crawl.crawl_by_get(res_url, headers=setting.HEADERS, proxies=self.proxies,
                                                  retry=5, timeout=10)
                detail = self.analysis.analysis_by_xpath(content, xpahter=setting.XPATH_RES_DETAIL)
                detail['city_name'] = city_name
                detail['restaurant_name'] = res_name
                detail['restaurant_type'] = res_type
                detail['restaurant_url'] = res_url
                detail['restaurant_id'] = res_id
                detail['get_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                # 构建存储的数据
                # 字段：
                # city_name, restaurant_name, restaurant_id, restaurant_type,
                # score, ranking, price, describe, address, tel, open_time, dish, arrive, intro, restaurant_url,
                # get_time datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                savedata = '{0[city_name]}\u0001{0[restaurant_name]}\u0001{0[restaurant_id]}\u0001' \
                           '{0[restaurant_type]}\u0001{0[score]}\u0001{0[ranking]}\u0001{0[price]}\u0001' \
                           '{0[describe]}\u0001{0[address]}\u0001{0[tel]}\u0001{0[open_time]}\u0001' \
                           '{0[dish]}\u0001{0[arrive]}\u0001{0[intro]}\u0001{0[restaurant_url]}\u0001' \
                           '{0[get_time]}'.format(detail)
                self.pipe.pipe_txt_save(savedata, filename=setting.TEMP_RESTAURANT_INFO, savetype='a')
                time.sleep(self.sleep_time)
            except Exception as e:
                self.alilog.warning('[detail] {}'.format(e))
                continue

    def _engine_restaurant_comments(self):

        """
        获取所有餐厅评论数据
        :return:
        """
        res_list = self.pipe.pipe_txt_load(filename=setting.FILE_RESTAURANT_LIST)
        temp_list = self.pipe.pipe_txt_load(filename=setting.TEMP_RESTAURANT_LIST)
        res_list.extend(temp_list)
        # 每个店铺最新评论时间表
        check_dict = self.pipe.pipe_pickle_load(filename=setting.FILE_COMMENTS_CHECK)
        if not check_dict:
            check_dict = {}
        for each_res in res_list:
            try:
                # 店铺数据
                city = each_res.strip().split('\u0001')[0]
                food = each_res.strip().split('\u0001')[1]
                res_id = each_res.strip().split('\u0001')[2]
                type = each_res.strip().split('\u0001')[3]
                res_url = each_res.strip().split('\u0001')[4]
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
                while True:
                    time.sleep(self.sleep_time)
                    try:
                        params['page'] += 1
                        content = self.crawl.crawl_by_get(api, headers=setting.HEADERS_COMMENTS,
                                                          proxies=self.proxies,
                                                          params=params, retry=3, timeout=20)
                        content_dict = json.loads(content)
                        if not content_dict.get('data'):
                            break
                        content_comments = content_dict.get('data')
                        elements_com = self.analysis.analysis_by_xpath(content_comments,
                                                                       xpahter=setting.XPATH_COMMENTS_LI)
                        if not elements_com:
                            break
                        for each_element in elements_com:
                            title = self.analysis.analysis_by_xpath(each_element, xpahter=setting.XPATH_COMMENTS_TITLE)
                            start = self.analysis.analysis_by_xpath(each_element, xpahter=setting.XPATH_COMMENTS_START)
                            nick = self.analysis.analysis_by_xpath(each_element, xpahter=setting.XPATH_COMMENTS_NICK)
                            more = self.analysis.analysis_by_xpath(each_element, xpahter=setting.XPATH_COMMENTS_MORE)
                            if more:
                                content_more = self.crawl.crawl_by_get(more[0], headers=setting.HEADERS,
                                                                       proxies=self.proxies)
                                content = self.analysis.analysis_by_xpath(content_more,
                                                                          xpahter=setting.XPATH_COMMENTS_DETAIL)
                            else:
                                content = self.analysis.analysis_by_xpath(each_element,
                                                                          xpahter=setting.XPATH_COMMENTS_CONTENT)
                            date = self.analysis.analysis_by_xpath(each_element, xpahter=setting.XPATH_COMMENTS_DATE)
                            try:
                                deal_content = ''.join(
                                    list(map(lambda x: x.replace('\n', '').replace('\r', '').replace('\t', '').
                                             replace(' ', ''), content)))
                            except:
                                self.alilog.info('[review] have no deal_content')
                                deal_content = ''
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
                                for eachkey in commetents_info.keys():
                                    commetents_info[eachkey] = commetents_info[eachkey].replace('\n', '').replace('\r',
                                                                                                                  '')
                                # 存储数据
                                # 字段顺序：city, food, food_id, type, title, nick, start, content, date, get_time, url
                                save_info = '{0[city]}\u0001{0[food]}\u0001{0[food_id]}\u0001' \
                                            '{0[type]}\u0001{0[title]}\u0001{0[nick]}\u0001' \
                                            '{0[start]}\u0001{0[content]}\u0001{0[date]}\u0001' \
                                            '{0[get_time]}\u0001{0[url]}'.format(commetents_info)

                                self.pipe.pipe_txt_save(save_info, filename=setting.TEMP_RESTAURANT_COMMENTS,
                                                        savetype='a')
                                comments_time.add(''.join(date))
                        # 当前页面没有新增评论也切换至下一店铺
                        if not len(comments_time):
                            break
                    except Exception as e:
                        self.alilog.warning('[review] {}'.format(e))
                        break
                # 每个店铺最新的评论时间
                if comments_time:
                    check_dict[res_id] = max(comments_time)
                    # 抓取到的评论数据
                self.pipe.pipe_pickle_save(check_dict, filename=setting.FILE_COMMENTS_CHECK)
            except Exception as e:
                self.alilog.warning('[review] {}'.format(e))
                continue

    def _engine_restaurant_link_by_args(self):
        """
        根据配置参数来进行抓取，从该模块提供参数的接口
        :return:
        """
        # 传入的参数中是否有dist参数,此处暂时默认arg_dist为一个字符串参数，实际是一个列表
        arg_dist = self.args_dict.get('dist', [])
        # 如果没该参数，则全部抓取所有城市数据
        if not arg_dist:
            self._engine_restaurant_link()
        else:
            try:
                city_dict = eval(self.pipe.pipe_txt_load(filename='./DATA/file_city_dict.txt'))
            except Exception as e:
                logging.warning('get city dict error: {}'.format(e))
            # 假设此处获取到了待抓取的url
            prov = arg_dist[0]  # 省
            city = arg_dist[1]  # 市
            area = arg_dist[2]  # 县

            city_dict = {'四川省':
                {
                    '成都市': {'': 'http1'},
                    '德阳市': {'': 'http2'},
                    '眉山市': {'': 'http3'},
                    '人寿市': {'': 'http4'},
                }
            }
            if prov and city and area:
                current_list = city_dict.get(prov, {}).get(city, {}).get(area, '')
                city_list = [current_list]
            elif prov and city and not area:
                current_list = city_dict.get(prov, {}).get(city, {})
                city_list = set([])
                for name, url in current_list.items():
                    city_list.add(url)
            elif prov and not city and not area:
                current_list = city_dict.get(prov, {})
                city_list = set([])
                for eachkey in current_list.keys():
                    for url in current_list[eachkey].values():
                        city_list.add(url)
            else:
                raise ValueError('args_dist error')

            # 获取已经抓取店铺id，便于识别新增数据
            history_restautrant = self.pipe.pipe_txt_load(filename=setting.FILE_RESTAURANT_LIST)
            history_id = set(map(lambda x: x.strip().split('\u0001')[2], [each for each in history_restautrant]))
            for each_city in set(city_list):
                # try:
                url = each_city.strip().split('\u0001')[1] + '-meishi'
                name = each_city.strip().split('\u0001')[0]
                params_city = {'page': 0}
                maxpage = 200  # 默认最大页数
                while True:
                    save_list = []
                    params_city['page'] += 1
                    content = self.crawl.crawl_by_get(url, headers=setting.HEADERS, params=params_city,
                                                      proxies=self.proxies, retry=5)
                    if not content:
                        break
                    element_li = self.analysis.analysis_by_xpath(content, xpahter=setting.XPATH_LI)
                    if not element_li:
                        break
                    for each_ele in element_li:
                        restaurant_name = self.analysis.analysis_by_xpath(each_ele, xpahter=setting.XPATH_RES_NAME)
                        restaurant_type = self.analysis.analysis_by_xpath(each_ele, xpahter=setting.XPATH_RES_TYPE)
                        restaurant_url = self.analysis.analysis_by_xpath(each_ele, xpahter=setting.XPATH_RES_URL)
                        current_id = re.search(re.compile(r'p-oi(\d+)-'), ''.join(restaurant_url)).group(1)
                        if current_id in history_id:
                            continue
                        else:
                            history_id.add(current_id)
                        try:
                            # 存储字段
                            # name, restaurant_name, current_id, restaurant_type，, restaurant_url
                            save_info = '{}\u0001{}\u0001{}\u0001{}\u0001{}'.format(name, ''.join(restaurant_name),
                                                                                    current_id,
                                                                                    ''.join(restaurant_type),
                                                                                    ''.join(restaurant_url))
                        except Exception as e:
                            self.alilog.warning('[list] {}'.format(e))
                            continue
                        save_list.append(save_info)
                    if save_list:
                        self.pipe.pipe_txt_save(save_list, filename=setting.TEMP_RESTAURANT_LIST, savetype='a')
                    if params_city['page'] >= maxpage:
                        break
                    time.sleep(self.sleep_time)
                    # except:
                    #     continue



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
        proxy_host = "****"
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

    # 集群操作
    def _engine_push_hdfs(self, filename):
        try:
            if os.path.exists('DATA/' + filename):
                # HDFS.put(当前文件，目标文件)
                self.HDFS.put('DATA/' + filename,
                         '/user/spider/everyday/{}'.format(filename))
            # 推送备份数据
            for eachfile in [setting.FILE_RESTAURANT_LIST, setting.FILE_RESTAURANT_INFO,
                             setting.FILE_RESTAURANT_COMMENTS]:
                if os.path.exists('DATA/' + eachfile):
                    # HDFS.put(当前文件，目标文件)
                    self.HDFS.put('DATA/' + eachfile,
                             '/user/spider/xieyangjie/Qunar/{}'.format(eachfile))
        except Exception as e:
            print('集群挂了', e)

    @staticmethod
    def _use_log(LOGFMT=None, DATEFMT=None):
        """
        本地日志记录
        该模块用于配置日志记录格式以及存储位置等
        :return:
        """
        LOGFMT = "%(asctime)s - %(levelname)s - %(message)s"
        DATEFMT = "%Y/%m/%d %H:%M:%S"
        logging.basicConfig(filename='./logbag/{}_{}_{}.log'.format(setting.OTA_NAME, setting.CATEGORY_NAME,
                                                                    datetime.datetime.today().strftime('%Y%m%d')),
                            format=LOGFMT, datefmt=DATEFMT, level=logging.INFO)

    def start_engine(self):
        self.alilog.debug('script {}_{} running'.format(setting.OTA_NAME, setting.CATEGORY_NAME))
        self._engine_restaurant_link_by_args()
        return
        self._engine_restaurant_link_by_args()
        self._engine_restaurant_info()
        self._engine_restaurant_comments()
        logging.info('{}_{} spider running'.format(setting.OTA_NAME, setting.CATEGORY_NAME))
        try:
            self._engine_city_link()
            self.alilog.debug('script {}_{} running'.format(setting.OTA_NAME, setting.CATEGORY_NAME))
            while True:
                self._engine_restaurant_link()
                self._engine_restaurant_info()
                self._engine_restaurant_comments()
                current_time = datetime.datetime.now().strftime('%Y-%m-%d')
                file_dict = {
                    setting.FILE_RESTAURANT_LIST: setting.TEMP_RESTAURANT_LIST,
                    setting.FILE_RESTAURANT_INFO: setting.TEMP_RESTAURANT_INFO,
                    setting.FILE_RESTAURANT_COMMENTS: setting.TEMP_RESTAURANT_COMMENTS
                }
                for f, t in file_dict.items():
                    newname = 'qunar{}({}).txt'.format(t[4:-4], current_time)
                    if os.path.exists('DATA/{}'.format(f)):
                        temp = self.pipe.pipe_txt_load(filename=t)
                        if temp:
                            self.pipe.pipe_txt_save(list(map(lambda x: x.strip(), temp)), filename=f, savetype='a')
                            os.rename('DATA/{}'.format(t), 'DATA/{}'.format(newname))
                        else:
                            self.pipe.pipe_txt_save('', filename=newname)
                    else:
                        os.rename('DATA/{}'.format(t), 'DATA/{}'.format(f))
                        shutil.copy('DATA/{}'.format(f), 'DATA/{}'.format(newname))
                    self._engine_push_hdfs(newname)
                self.alilog.debug('script {}_{} finish'.format(setting.OTA_NAME, setting.CATEGORY_NAME))
        except Exception as e:
            self.alilog.error('script {}_{} error {}'.format(setting.OTA_NAME, setting.CATEGORY_NAME, e))


if __name__ == '__main__':
    start = time.time()
    proc = Engine()
    proc.start_engine()
    end = time.time()
    print('执行完毕，耗时 {:.2f} s'.format(end - start))
