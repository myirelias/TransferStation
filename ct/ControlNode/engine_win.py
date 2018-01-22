# coding=UTF-8

from multiprocessing.managers import BaseManager
from multiprocessing import Queue
from multiprocessing import Process
from ControlNode.manager_url import UrlManager
from ControlNode.manager_data import DataManager
import time, datetime


class Engine(object):

    def __init__(self):
        self.dater = DataManager()

    @staticmethod
    def create_manager(url_q, result_q):
        """
        创建一个manager并将队列暴露在网络上
        :param url_q: 控制节点负责分发url到url_q,爬虫节点负责从url_q获取url来进行爬取
        :param result_q: 爬虫节点将爬去结果放到result_q中，控制节点从result_q中获取结果，交给本地队列，进行数据处理
        :return:
        """
        def _get_url():
            return url_q

        def _get_result():
            return result_q

        # 将两个网络队列暴露在网上
        BaseManager.register('get_url_q', callable=_get_url)
        BaseManager.register('get_result_q', callable=_get_result)
        # 创建一个manager实例，绑定ip/port以及密匙
        manager = BaseManager(address=('127.0.0.1', 8898), authkey='ajiao'.encode('UTF-8'))

        return manager

    @staticmethod
    def proc_publish_url(url_q, con_q, urls):
        """
        url管理：发布url到网络队列，供爬虫节点抓取
        :param url_q: 负责发布url的网络队列
        :param con_q: 负责将爬取结果中的url交给控制节点，由控制节点发布给爬虫节点
        :param urls: 待抓取url
        :return:
        """
        url_manager = UrlManager()
        url_manager.url_check(urls)
        while True:
            while url_manager.has_new_url():
                url = url_manager.get_new_url()
                url_q.put(url)

            try:
                if not con_q.empty():
                    newurl = con_q.get()
                    url_manager.url_check(newurl)
            except Exception as e:
                print(e)
                time.sleep(0.5)

    @staticmethod
    def proc_deal_result(result_q, con_q, store_q):
        """
        数据处理：处理爬虫节点返回的结果队列
        :param result_q: 盘虫节点返回的结果队列
        :param con_q: 需要继续爬取的新url队列
        :param store_q: 需要进行数据存储的数据队列
        :return:
        """
        while True:
            if not result_q.empty():
                content = result_q.get(True)
                if isinstance(content, dict):
                    if content.get('content', ''):
                        print(content)
                    con_q.put(content.get('url', ''))
                    store_q.put(content.get('content', ''))
            else:
                time.sleep(0.5)

    @staticmethod
    def proc_store_data(store_q, dbname, colname):
        """
        数据存储
        :param store_q: 本地数据队列，由数据处理进程负责从中提取数据并存储
        :param colname: 集合名称
        :param dbname: 数据库名称
        :return:
        """
        data_manager = DataManager()
        while True:
            if not store_q.empty():
                now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                data = store_q.get(True)
                if data:
                    data['time'] = now
                data_manager.data_save(data, dbname, colname)
            else:
                time.sleep(0.5)


if __name__ == '__main__':
    # 创建4个队列，其中con_q、store_q为本地实体队列，
    print('===控制节点启动===')
    url_q = Queue()
    result_q = Queue()
    con_q = Queue()
    store_q = Queue()
    # 实例化控制节点
    engine_node = Engine()
    manager = engine_node.create_manager(url_q, result_q)
    # 创建3个进程，分别是url管理进程、数据处理进程和数据存储进程
    proc_url = Process(target=engine_node.proc_publish_url, args=(url_q, con_q, 'http://www.cctv.com/'))
    proc_datadeal = Process(target=engine_node.proc_deal_result, args=(result_q, con_q, store_q))
    proc_datasave = Process(target=engine_node.proc_store_data, args=(store_q, 'db_cctv', 'col_cctv_info'))
    proc_url.start()
    proc_datadeal.start()
    proc_datasave.start()
    manager.get_server().serve_forever()