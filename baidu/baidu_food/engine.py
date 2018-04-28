# !/usr/bin/env python
# coding=utf-8
'''引擎模块'''

from crawl import Crawl
from analysis import Analysis
from pipeline import Pipeline
import config as setting
import time

try:
    from tqdm import tqdm
except:
    pass
import re
import json


class Engine:
    def __init__(self):
        self.crawl = Crawl()
        self.pipe = Pipeline()
        self.analysis = Analysis()

    def _engine_city_list(self):
        """
        获取城市列表
        :return:
        """
        content = self.crawl.crawl_by_get(setting.START_URL, headers=setting.HEADERS)
        elements = self.analysis.analysis_by_xpath(content, xpahter=setting.XPATH_CITYLIST_A)
        city_list = []
        for each_ele in elements:
            city_url = self.analysis.analysis_by_xpath(each_ele, xpahter=setting.XPATH_HREF)
            city_name = self.analysis.analysis_by_xpath(each_ele, xpahter=setting.XPATH_TEXT)
            cityinfo = '{}\u0001{}'.format(''.join(city_name), ''.join(city_url).replace('/', ''))
            city_list.append(cityinfo)
        self.pipe.pipe_txt_save(city_list, filename=setting.FILE_CITY_LIST, savetype='w')

    def _engine_cityid_list(self):
        """
        获取所有城市的sid
        :return:
        """
        city_list = self.pipe.pipe_txt_load(filename=setting.FILE_CITY_LIST)
        save_data = []
        for eachcity in tqdm(city_list):
            params = {
                'format': 'ajax',
                'cid': '0',  # 景点类型id,0为全部
                'playid': '0',  # 游玩时间id,0为全部
                'seasonid': '5',  # 适宜季节id(春1夏2秋3冬4四季皆宜0全部5)
                'surl': 'chengdu',  # 初步调研为城市拼音名
                'pn': 0,  # 当前页码
                'rn': '18'  # 当页展示数量
            }
            try:
                surl = eachcity.strip().split('\u0001')[1]
            except:
                continue
            params['surl'] = surl
            content = self.crawl.crawl_by_get(setting.TOURIS_API, headers=setting.HEADERS, params=params,
                                              proxies=self._engine_use_proxy(), retry=5, timeout=30)
            try:
                data_dict = json.loads(content)
            except:
                continue
            data = data_dict.get('data', {})
            sid = data.get('sid', {})
            current_surl = data.get('surl', {})
            sname = data.get('sname', {})
            save_data.append('{}\u0001{}\u0001{}'.format(sname, current_surl, sid))
        self.pipe.pipe_txt_save(save_data, filename=setting.FILE_CITYID_LIST, savetype='a')

    def _engine_comments_list(self):
        """
        获取所有景区评论数据
        :return:
        """
        parmas_comments = {
            'flag': '1',
            'format': 'ajax',
            'pn': '15',  # 当前页第一条评论序号(每页15条，pn从0开始，均为15的倍数)
            'rn': '15',  # 每页展示数量,默认
            'score': '0',  # 评分，0为全部,默认
            'style': 'recent',  # 评论排序方式 热门hot 最新recent,默认
            't': '{:.0f}'.format(time.time() * 1000),  # 时间戳
            'xid': '0e2b4b57f9374db66f54e1fa'  # 为前面请求景点数据时候，其中的sid
        }
        city_list = self.pipe.pipe_txt_load(filename=setting.FILE_CITYID_LIST)
        # 景区信息数据，包含景区上次抓取最新评论时间(pub_time)，景区评论总数(count)，景区id(sid)，景区name(sname)
        tourist_info = self.pipe.pipe_pickle_load(filename=setting.FILE_COMMENTS_INFO)
        # 防止首次抓取没有该文件
        if not tourist_info:
            tourist_info = {}
        for each_tourist in tqdm(city_list):
            city = each_tourist.strip().split('\u0001')
            sname = city[0]  # 景区的id
            surl = city[1]
            sid = city[2]
            n = 0
            # 在景区信息数据中根据sid(xid)找到景区数据
            control_dict = tourist_info.get(sid, {})
            control_dict['sid'] = sid
            control_dict['sname'] = sname
            current_time = control_dict.get('time', -1)
            current_count = control_dict.get('count', -1)
            parmas_comments['xid'] = sid
            time_list = set([])
            save_list = []
            save_dict = []  # 测试用，正式删除
            while True:
                parmas_comments['pn'] = n * 15
                # 请求评论时使用referer字段
                setting.HEADERS_COMMENTS['Referer'] = setting.REFER_URL.format(surl, parmas_comments['pn'])
                content = self.crawl.crawl_by_get(setting.COMMENTS_API, headers=setting.HEADERS_COMMENTS,
                                                  params=parmas_comments,
                                                  proxies=self._engine_use_proxy(), retry=3, timeout=20)
                try:
                    data_dict = json.loads(content)
                except:
                    continue
                # 获取评论最大数量
                comments_count = data_dict.get('data', {}).get('total', -1)
                comments_list = data_dict.get('data', {}).get('list', [])
                # 如果没有新增数据则不抓取,只在第一遍抓取时候执行此操作
                if n == 0 and int(comments_count) <= int(current_count):
                    break
                # 页面没有数据则切换
                if not comments_list:
                    break
                for each_comments in comments_list:
                    """
                    uid:用户id nickname:用户昵称 score(user中):用户旅历值 wealth:用户财富值 level:用户等级
                    remark_id:评论id score:评分 content:评论内容 create_time:评论创建时间 update_time:评论更新时间
                    pics:用户评论照片,暂时不拿
                    """
                    # 用户基本信息
                    user_info = each_comments.get('user', {})
                    # 时间
                    comments_time = each_comments.get('create_time', '')
                    update_time = each_comments.get('update_time', '')
                    save_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(comments_time)))
                    save_update_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(update_time)))
                    # 对比确认是否需要入库
                    if comments_time > current_time:
                        # 评论信息
                        comments_dict = {
                            'sid': sid,
                            'sname': sname,
                            'uid': user_info.get('uid', ''),
                            'nickname': user_info.get('nickname', ''),
                            'userscore': user_info.get('score', ''),
                            'wealth': user_info.get('wealth', ''),
                            'level': user_info.get('level', ''),
                            'remark_id': each_comments.get('remark_id', ''),
                            'score': each_comments.get('score', ''),
                            'content': each_comments.get('content', ''),
                            'create_time': save_time,
                            'update_time': save_update_time,
                            'pics': each_comments.get('pics', []),
                        }
                        time_list.add(comments_time)
                        # 此处评论详情存txt文本，改造下数据
                        # start----写到txt文本中的操作-----start
                        # save_info = '\u0001'.join(list(map(lambda x: str(x).replace('\n', '').replace('\r', ''), list(comments_dict.values()))))
                        # save_list.append(save_info)
                        # end----写到txt文本中的操作-----end
                        save_dict.append(comments_dict)  # 测试用，正式删除
                n += 1
                # 新增数量//15 + 1则表示新增内容所在的页数，当超过此页数后则切换下一个景区进行抓取
                if n > (int(comments_count) - int(current_count)) // 15 + 1:
                    break
                # break
                print('{} : 当前第 {} 页, 已获取 {} 条评论'.format(sname, n, len(save_dict)))
                # time.sleep(0.5)
            if time_list:
                control_dict['time'] = max(time_list)
                control_dict['count'] = comments_count
            tourist_info[sid] = control_dict
            # # start----写到txt文本中的操作-----start
            # self.pipe.pipe_txt_save(save_list, filename=setting.FILE_COMMENTS_LIST, savetype='a')
            # end----写到txt文本中的操作-----end
            if save_dict:
                self.pipe.pipe_mongo_save(save_dict, dbname='db_baidu', colname='col_city_comments')
            self.pipe.pipe_pickle_save(tourist_info, filename=setting.FILE_COMMENTS_INFO)
            # break

    def _engine_food_list(self):
        """
        获取城市美食数据
        :return:
        """
        city_list = self.pipe.pipe_txt_load(filename=setting.FILE_CITYID_LIST)
        for each_city in city_list:
            save_list = []
            surl = each_city.strip().split('\u0001')[1]
            sid = each_city.strip().split('\u0001')[2]
            sname = each_city.strip().split('\u0001')[0]
            request_url = setting.FOOD_URL.format(surl)
            content = self.crawl.crawl_by_get(request_url, headers=setting.HEADERS, proxies=self._engine_use_proxy())
            food_list = self.analysis.analysis_by_xpath(content, setting.XPATH_FOOD_LIST)
            for each_food in food_list:
                food_name = self.analysis.analysis_by_xpath(each_food, setting.XPATH_FOOD_NAME)
                food_des = self.analysis.analysis_by_xpath(each_food, setting.XPATH_FOOD_DESCRIB)
                shop_list = self.analysis.analysis_by_xpath(each_food, setting.XPATH_SHOP_LIST)
                shop_info = []
                for each_shop in shop_list:
                    shop_name = self.analysis.analysis_by_xpath(each_shop, setting.XPATH_SHOP_NAME)
                    shop_url = self.analysis.analysis_by_xpath(each_shop, setting.XPATH_SHOP_URL)
                    shop = {''.join(shop_name).replace('\n', ''): 'https://lvyou.baidu.com' + ''.join(shop_url)}
                    shop_info.append(shop)
                save_food_name = ''.join(food_name).replace('\n', '').replace('\r', '')
                save_food_des = ''.join(food_des).replace('\n', '').replace('\r', '')
                """
                sname: 城市名称 surl: 城市拼音名 sid: 城市id
                save_food_name: 美食名称 save_food_des: 美食描述
                shop_info: 店铺信息(列表，每个元素为{店铺名称: 店铺url})
                """
                current_food = '{}\u0001{}\u0001{}\u0001{}\u0001{}\u0001{}\u0001'.format(sname, surl, sid,
                                                                                         save_food_name, save_food_des,
                                                                                         shop_info)
                save_list.append(current_food)
            self.pipe.pipe_txt_save(save_list, filename=setting.FILE_FOOD_INFO)

    def start_engine(self):
        self._engine_city_list()
        self._engine_food_list()
        self._engine_cityid_list()
        self._engine_comments_list()

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


if __name__ == '__main__':
    start = time.time()
    proc = Engine()
    proc.start_engine()
    end = time.time()
    print('执行完毕，耗时 {:.2f} s'.format(end - start))
