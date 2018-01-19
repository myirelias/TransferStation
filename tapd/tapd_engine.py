# !/usr/bin/env python
# coding=utf8

import time
import datetime
from tapd_setting import FN_ALL_TASK_LINK, XPATHER_DICT, XPATHER_DEALERCONTENTALL, XPATHER_DEALERCONTENT, FN_ALL_TASK_INFO
from tapd_crawl import TapdCrawl
from tapd_spider import TapdSpider
from tapd_pipeline import TapdPipe
from tapd_tools import TapdTools


class TapdEngine(object):

    def __init__(self):
        self.crawl = TapdCrawl()
        self.spider = TapdSpider()
        self.pipe = TapdPipe()
        self.tools = TapdTools()
        self.today = self.tools.get_today()
        self.filename = self.tools.make_filename()

    def excute(self):
        self.all_task_link()
        self.each_task_info()
        if int(datetime.datetime.today().strftime('%H%M')) >= 2300:
            for eachname in [self.filename, FN_ALL_TASK_INFO]:
                self.pipe.load_in_hdfs(eachname)

    # 获取所有任务的link
    def all_task_link(self):
        xpater_all = ".//*[@data-editable='text']//*[@class='editable-value']/@href"
        content = self.crawl.tapdlist()
        tasklist = self.spider.cleandata(content, xpater_all)
        self.pipe.save_list_txt(tasklist, FN_ALL_TASK_LINK)

    # 获取所有任务的详细内容
    def each_task_info(self):
        alltasklink = self.pipe.read_alltask_url(FN_ALL_TASK_LINK)

        for eachlink in alltasklink:
            try:
                savedata = []
                content = self.crawl.get_eachtask_info(eachlink) # 获取页面html
                taskdict = self.spider.cleandata_more(content, XPATHER_DICT) # 获取页面所有需要的信息，除评论栏，返回的是一个dict
                dealercontentall = self.spider.cleandata(content, XPATHER_DEALERCONTENTALL) # 获取评论栏的html结构
                dealercontent = self.spider.cleanstring(dealercontentall, XPATHER_DEALERCONTENT) # 获取评论栏所有评论
                for eachdealercontent in dealercontent:
                    #  构造存储的数据
                    dealdate = eachdealercontent[2].split(' ')[0]
                    dealer = eachdealercontent[0]
                    dealer_name = self.tools.name_change(dealer)
                    if dealdate == '2017-10-30':  # 遍历所有任务，但只存储今天的task反馈,后期可根据字典里面解析字段扩展需要的字段
                        createdatalist = [dealdate, taskdict['tasktype'], dealer_name, taskdict['title'],
                                          taskdict['state'], eachdealercontent[2], ''.join(eachdealercontent[3:]).strip()]
                        saveinfo = '\u0001'.join(createdatalist)
                        savedata.append(saveinfo)
                if len(savedata) != 0 and int(datetime.datetime.today().strftime('%H%M')) <= 2200:
                    self.pipe.save_list_txt(savedata, self.filename, savetype='a')
                    self.pipe.save_list_txt(savedata, FN_ALL_TASK_INFO, savetype='a')
                else:
                    self.pipe.save_list_txt(savedata, FN_ALL_TASK_INFO, savetype='a')
                time.sleep(1)
            except Exception as e:
                filename_error = 'error_log.txt'
                error_info = '[%s]|[%s]  %s' % (datetime.datetime.now().strftime('%Y%m%d %H:%M:%S'),
                                                        e, eachlink,)
                self.pipe.save_list_txt(error_info, filename_error, savetype='a')
                time.sleep(10)
                continue


if __name__ == '__main__':
    # i = TapdEngine()
    # starttime = datetime.datetime.now()
    # i.excute()
    # endtime = datetime.datetime.now()
    # print('耗时 %s' % (endtime - starttime))
    while True:
        print('working...')
        nowtime = datetime.datetime.today().strftime('%H%M')
        if nowtime == '1820':
            i = TapdEngine()
            starttime = time.time()
            i.excute()
            del i
            endtime = time.time()
            time.sleep(280*60 - int(endtime-starttime))
        elif nowtime == '2300':
            i = TapdEngine()
            starttime = time.time()
            i.excute()
            del i
            endtime = time.time()
            time.sleep(1160*60 - int(endtime-starttime))
        else:
            time.sleep(10)


