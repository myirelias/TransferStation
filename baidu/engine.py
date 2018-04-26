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
    """
    引擎模块
    """

    def __init__(self):
        self.crawl = Crawl()
        self.analysis = Analysis()
        self.pipe = Pipeline()

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
        self.pipe.pipe_txt_save(city_list, filename=setting.FILE_CITY_LIST)

    def _engine_tourist_list(self):
        """
        获取所有景区数据
        :return:
        """
        city_list = self.pipe.pipe_txt_load(filename=setting.FILE_CITY_LIST)
        params = {
            'format': 'ajax',
            'cid': '0',  # 景点类型id,0为全部
            'playid': '0',  # 游玩时间id,0为全部
            'seasonid': '5',  # 适宜季节id(春1夏2秋3冬4四季皆宜0全部5)
            'surl': 'chengdu',  # 初步调研为城市拼音名
            'pn': 0,  # 当前页码
            'rn': '18'  # 当页展示数量
        }
        for eachcity in tqdm(city_list):
            try:
                surl = eachcity.strip().split('\u0001')[1]
            except:
                continue
            params['surl'] = surl
            while True:
                params['pn'] += 1
                content = self.crawl.crawl_by_get(setting.TOURIS_API, headers=setting.HEADERS, params=params,
                                                  proxies=self._engine_use_proxy(), retry=5, timeout=30)
                try:
                    data_dict = json.loads(content)
                except:
                    break
                data_info = data_dict.get('data', {})
                scene_list = data_info.get('scene_list', [])
                if not scene_list:
                    break
                request_id = data_info.get('request_id')
                save_data = []
                for each_scene in scene_list:
                    # 各个字段说明
                    """
                    sid: 景区id, sname:景区名称, surl:景区拼音名称, cid:景区类型id, star:景区级别, remark_count:评论数量,
                    current_idx:景区当前所在页面序号
                    """
                    # 景区信息字段
                    scene_info = {'sid': each_scene.get('sid', ''), 'sname': each_scene.get('sname', ''),
                                  'surl': each_scene.get('surl', ''), 'cid': each_scene.get('cid', ''),
                                  'star': each_scene.get('star', ''),
                                  'remark_count': each_scene.get('remark_count', ''),
                                  'current_idx': str(scene_list.index(each_scene)), 'map_info': '',
                                  'address': '', 'phone': '', 'level': '', 'website': '', 'sketch_desc': '',
                                  'more_desc': '', 'impression': '', 'besttime': '', 'recommend_visit_time': '',
                                  'traffic': '', 'ticket': '', 'open_time': ''}
                    # 此处为在列表时候能获取到的景区相关，只取了部分出来
                    ext = each_scene.get('ext', [])
                    if ext:
                        scene_info['map_info'] = ext.get('map_info', '')  # 地图信息
                        scene_info['address'] = ext.get('address', '')  # 地址
                        scene_info['phone'] = ext.get('phone', '')  # 联系电话
                        scene_info['level'] = ext.get('level', '')  # 景区等级
                        scene_info['website'] = ext.get('website', '')  # 官网
                        scene_info['sketch_desc'] = ext.get('sketch_desc', '')  # 简介描述，使用详细描述可替代
                        scene_info['more_desc'] = ext.get('more_desc', '')  # 详细描述
                        scene_info['impression'] = ext.get('impression', '')  # 印象
                    # 构造请求参数，前往每个景区页面，获取所有数据
                    params_each_tourist = {'accur_thirdpar': 'destination', 'idx': scene_list.index(each_scene),
                                           'innerfr_pg': 'sceneListPg', 'lowflow': '1', 'request_id': request_id}
                    each_tourist_url = each_scene.get('surl')
                    content_page = self.crawl.crawl_by_get(setting.EACH_TOURIST_API.format(each_tourist_url),
                                                           headers=setting.HEADERS, retry=5, timeout=30,
                                                           params=params_each_tourist, proxies=self._engine_use_proxy())
                    # 页面中包含的数据正则取出来
                    pattern = re.compile(r'sceneArr.push\(({.*?})\)', re.S)
                    try:
                        page_info = re.search(pattern, content_page)
                    except:
                        page_info = None  # 请求不到景区详情页面则不提供详情页面字段，只存储列表页面中获取的字段
                    if page_info:
                        page_dict = json.loads(page_info.group(1))
                        # print(page_dict.get('content'))
                        p_dict = page_dict.get('content', {})
                        if p_dict:
                            scene_info['besttime'] = p_dict.get('besttime', {}).get('more_desc', '')  # 最佳旅游季节
                            # 建议游玩时长
                            scene_info['recommend_visit_time'] = p_dict.get('besttime', {}).get('recommend_visit_time',
                                                                                                '')
                            # 交通方式
                            try:
                                scene_info['traffic'] = p_dict.get('traffic', {}).get('desc')[0].get('content', '')
                            except:
                                pass
                            # 门票
                            scene_info['ticket'] = p_dict.get('ticket_info', {}).get('price_desc', '')
                            # 开放时间
                            scene_info['open_time'] = p_dict.get('ticket_info', {}).get('open_time_desc', '')
                    # 构造需要存储的函数
                    save_info = '\u0001'.join(
                        list(map(lambda x: x.replace('\r', '').replace('\n', ''), list(scene_info.values()))))
                    save_data.append(save_info)
                    time.sleep(0.5)
                self.pipe.pipe_txt_save(save_data, filename=setting.FILE_TOURIST_LIST, savetype='a')

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
        tourist_list = self.pipe.pipe_txt_load(filename=setting.FILE_TOURIST_LIST)
        # 景区信息数据，包含景区上次抓取最新评论时间(pub_time)，景区评论总数(count)，景区id(sid)，景区name(sname)
        tourist_info = self.pipe.pipe_pickle_load(filename=setting.FILE_COMMENTS_INFO)
        # 防止首次抓取没有该文件
        if not tourist_info:
            tourist_info = {}
        print(tourist_info)
        for each_tourist in tourist_list:
            tourist = each_tourist.strip().split('\u0001')
            xid = tourist[0]  # 景区的id
            sname = tourist[1]
            surl = tourist[2]
            n = 0
            # tourist_info赋值

            # 在景区信息数据中根据sid(xid)找到景区数据
            control_dict = tourist_info.get(xid, {})
            control_dict['sid'] = xid
            control_dict['sname'] = sname
            current_time = control_dict.get('time', -1)
            current_count = control_dict.get('count', -1)
            parmas_comments['xid'] = xid
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
                        save_info = '\u0001'.join(list(map(lambda x: str(x).replace('\n', '').replace('\r', ''), list(comments_dict.values()))))
                        save_list.append(save_info)
                        save_dict.append(comments_dict)  # 测试用，正式删除
                n += 1
                # 新增数量//15 + 1则表示新增内容所在的页数，当超过此页数后则切换下一个景区进行抓取
                if n > (int(comments_count) - int(current_count)) // 15 + 1:
                    break
                # break
            if time_list:
                control_dict['time'] = max(time_list)
            control_dict['count'] = comments_count
            tourist_info[xid] = control_dict
            self.pipe.pipe_txt_save(save_list, filename=setting.FILE_COMMENTS_LIST, savetype='a')
            self.pipe.pipe_mongo_save(save_dict, dbname='db_baidu', colname='col_tourist_comments')
            self.pipe.pipe_pickle_save(tourist_info, filename=setting.FILE_COMMENTS_INFO)
            # break

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
        """
        启动模块
        :return:
        """
        # self._engine_city_list()
        # self._engine_tourist_list()
        self._engine_comments_list()


if __name__ == '__main__':
    start = time.time()
    proc = Engine()
    proc.run_engine()
    end = time.time()
    print('执行完毕，耗时 {:.1f} s'.format(end - start))
