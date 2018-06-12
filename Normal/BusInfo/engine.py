# !/usr/bin/env python
# coding=utf-8
'''引擎模块'''

from crawl import Crawl
from analysis import Analysis
from pipeline import Pipeline
import config as setting
import time


class Engine:
    """
    成都公交线路数据抓取脚本
    """
    def __init__(self):
        self.crawl = Crawl()
        self.analysis = Analysis()
        self.pipe = Pipeline()

    def _engine_bus_info(self):
        """
        获取所有bus的urls
        :return:
        """
        content_home = self.crawl.crawl_by_get(setting.START_URL, headers=setting.HEADERS, retry=2, timeout=30)
        each_list = self.analysis.analysis_by_xpath(content_home, xpahter=setting.XPATH_LIST)
        urls = list(map(lambda x: setting.DOMAIN_URL.format(x), each_list))
        for each in urls:
            content_bus = self.crawl.crawl_by_get(each, headers=setting.HEADERS, retry=2, timeout=30)
            bus_list = self.analysis.analysis_by_xpath(content_bus, xpahter=setting.XPATH_BUS)
            bus_urls = list(map(lambda x: setting.DOMAIN_URL.format(x), bus_list))
            if bus_urls:
                self.pipe.pipe_txt_save(bus_urls, filename=setting.FILE_BUS_LIST)

    def _engine_bus_detail(self):
        """
        获取bus详细信息
        :return:
        """
        bus_urls = self.pipe.pipe_txt_load(filename=setting.FILE_BUS_LIST)
        for each_bus in bus_urls:
            content_detail = self.crawl.crawl_by_get(each_bus, headers=setting.HEADERS, retry=2, timeout=30)
            detail_info = self.analysis.analysis_by_xpath(content_detail, xpahter=setting.XPATH_DETAIL)
            # 存储字段
            # name,time,ticket,company,update,station
            """
            name:线路名称，time:收发时间,ticket:票价,
            company:所属公司,update:最后更新时间,station:途经站点,
            """
            save_info = '{0[name]}\u0001{0[time]}\u0001{0[ticket]}\u0001' \
                        '{0[company]}\u0001{0[update]}\u0001{0[station]}'.format(detail_info)
            self.pipe.pipe_txt_save(save_info, filename=setting.FILE_BUS_DETAIL)
            time.sleep(2)


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
        self._engine_bus_info()
        self._engine_bus_detail()


if __name__ == '__main__':
    start = time.time()
    pro = Engine()
    pro.run_engine()
    end = time.time()
    print('执行完毕，耗时 {:.2f} s'.format(end - start))
