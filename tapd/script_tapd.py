# !/usr/bin/env python
# coding=utf8

import time
import datetime
import requests
from lxml import etree
import os
from imp import reload

try:
    from hdfs3 import HDFileSystem
except:
    pass


class TapdEngine(object):
    def __init__(self):
        self.crawl = TapdCrawl()
        self.spider = TapdSpider()
        self.pipe = TapdPipe()
        self.tools = TapdTools()
        self.today = self.tools.get_today()
        self.filename = self.tools.make_filename()
        tapdsetting = TapdSetting()
        self.setting = tapdsetting.reload_setting()

    def excute(self):
        self.all_task_link()
        self.each_task_info()
        if int(datetime.datetime.today().strftime('%H%M')) >= 2300 \
                or int(datetime.datetime.today().strftime('%H%M')) <= 800:
            self.pipe.load_in_hdfs(self.setting.FN_ALL_TASK_INFO)
        else:
            self.pipe.load_in_hdfs(self.filename)

    # 获取所有任务的link
    def all_task_link(self):
        xpater_all = ".//*[@data-editable='text']//*[@class='editable-value']/@href"
        content = self.crawl.tapdlist()
        tasklist = self.spider.cleandata(content, xpater_all)
        self.pipe.save_list_txt(tasklist, self.setting.FN_ALL_TASK_LINK)

    # 获取所有任务的详细内容
    def each_task_info(self):
        alltasklink = self.pipe.read_alltask_url(self.setting.FN_ALL_TASK_LINK)

        for eachlink in alltasklink:
            try:
                savedata = []
                content = self.crawl.get_eachtask_info(eachlink)  # 获取页面html
                # 获取页面所有需要的信息，除评论栏，返回的是一个dict
                taskdict = self.spider.cleandata_more(content, self.setting.XPATHER_DICT)
                # 获取评论栏的html结构
                dealercontentall = self.spider.cleandata(content, self.setting.XPATHER_DEALERCONTENTALL)
                # 获取评论栏所有评论
                dealercontent = self.spider.cleanstring(dealercontentall, self.setting.XPATHER_DEALERCONTENT)
                for eachdealercontent in dealercontent:
                    #  构造存储的数据
                    dealdate = eachdealercontent[2].split(' ')[0]
                    dealer = eachdealercontent[0]
                    dealer_name = self.tools.name_change(dealer)
                    # 遍历所有任务，但只存储今天的task反馈,后期可根据字典里面解析字段扩展需要的字段
                    if dealdate == self.today:
                        createdatalist = [dealdate, taskdict['tasktype'], dealer_name, taskdict['title'],
                                          taskdict['state'], eachdealercontent[2],
                                          ''.join(eachdealercontent[3:]).strip()]
                        saveinfo = '\u0001'.join(createdatalist)
                        savedata.append(saveinfo)
                if len(savedata) != 0 and int(datetime.datetime.today().strftime('%H%M')) <= 2200:
                    self.pipe.save_list_txt(savedata, self.filename, savetype='a')
                elif int(datetime.datetime.today().strftime('%H%M')) >= 2300 or int(datetime.datetime.today().strftime('%H%M')) <= 800:
                    self.pipe.save_list_txt(savedata, self.setting.FN_ALL_TASK_INFO, savetype='a')
                time.sleep(1)
            except Exception as e:
                filename_error = 'error_log.txt'
                error_info = '[%s]|[%s]  %s' % (datetime.datetime.now().strftime('%Y%m%d %H:%M:%S'),
                                                e, eachlink,)
                self.pipe.save_list_txt(error_info, filename_error, savetype='a')
                time.sleep(10)
                continue


class TapdCrawl(object):
    def __init__(self):
        self.session = requests.Session()
        newconfig = TapdSetting()
        self.setting = newconfig.reload_setting()
        self.headers = self.setting.HEADERS
        self.session.headers.update(self.setting.HEADERS)

    # 请求tapd任务列表，pagecode默认为utf-8
    def tapdlist(self, pagecode='utf-8'):
        retry = 5
        response = 'no_data'
        try:
            while retry > 0:
                res = self.session.get(self.setting.URL, params=self.setting.PARAMS,
                                       cookies=self.setting.COOKIES, timeout=30)
                if res.status_code == 200:
                    response = res.content.decode(pagecode)
                    break
                else:
                    retry -= 1
                    continue
        except Exception:
            pass

        return response

    # 请求url，获取content
    def get_eachtask_info(self, url, pagecode='utf-8'):
        retry = 5
        response = 'no_data'
        try:
            while retry > 0:
                res = self.session.get(url, cookies=self.setting.COOKIES, timeout=30)
                if res.status_code == 200:
                    response = res.content.decode(pagecode)
                    break
                else:
                    retry -= 1
                    continue
        except Exception:
            pass

        return response


class TapdSpider(object):
    def __init__(self):
        pass

    # xpath匹配，需提供html的content和一个xpath表达式
    @staticmethod
    def _spider_data(content, xpather):
        selector = etree.HTML(content)
        res = selector.xpath(xpather)

        return res

    # xpath二次匹配(主要针对评论栏里的数据)
    @staticmethod
    def _spider_string(content, xpather):
        stringlist = []
        if isinstance(content, list):
            for each in content:
                eachlist = []
                datestr = each.xpath(xpather)
                for everystr in datestr:
                    eachlist.append(everystr.strip())
                stringlist.append(eachlist)

        return stringlist

    def cleandata(self, content, xpather):

        return self._spider_data(content, xpather)

    def cleanstring(self, content, xpather):

        return self._spider_string(content, xpather)

    # task详细信息
    def cleandata_more(self, content, xpatherdict):

        if isinstance(xpatherdict, dict):
            taskdict = {}
            for eachkey in xpatherdict.keys():
                data = self._spider_data(content, xpatherdict[eachkey])
                taskdict[eachkey] = data[0] if len(data) != 0 else 'no_data'
        else:
            taskdict = 'no_data'

        return taskdict


class TapdPipe(object):
    def __init__(self):
        self._checkdir()

    @staticmethod
    def _checkdir():
        if not os.path.exists('DATA'):
            os.makedirs('DATA')

    @staticmethod
    def _save_txt(content, filename, savetype):
        if isinstance(content, list):
            with open(os.path.join(os.path.abspath('DATA'), filename), savetype, encoding='utf8') as f:
                for each in content:
                    f.write(each + '\n')
        else:
            with open(os.path.join(os.path.abspath('DATA'), filename), savetype, encoding='utf8') as f:
                for each in content:
                    f.write(each + '\n')  # 为了记录错误日志才添加的else,因为错误信息是str不是list

    # 读取txt文件
    @staticmethod
    def _read_txt(filename):
        return (each for each in open(os.path.join(os.path.abspath('DATA'), filename), 'r', encoding='utf8'))

    # 存list到txt
    def save_list_txt(self, content, filename, savetype='w'):
        self._save_txt(content, filename, savetype)

    def read_alltask_url(self, filename):
        return self._read_txt(filename)

    # 集群操作
    def load_in_hdfs(self, filename):
        hdfs = HDFileSystem(host='192.168.100.178', port=8020)
        try:
            file_path = os.path.join(os.path.abspath('DATA'), filename)
            hdfs_path = os.path.join('/user/spider/TAPD_TASK', filename)
            hdfs.put(file_path, hdfs_path)
        except Exception as e:
            print('集群挂了', e)


class TapdTools(object):
    def __init__(self):
        config = TapdSetting()
        self.setting = config.reload_setting()

    # 获取当天日期
    @staticmethod
    def get_today():
        return datetime.datetime.today().strftime('%Y-%m-%d')

    # 构造文件名字，组合今天日期
    def make_filename(self):
        today = self.get_today()
        filename = 'tapd_task_%s.txt' % today
        return filename

    # 将拼音名字转换为中文，如有新增拼音名字，直接添加到cn_name
    def name_change(self, dealername):
        names = []
        cn_name = self.setting.CN_NAME
        namellist = dealername.split(';')
        if len(namellist) == 1:
            changename = cn_name[dealername]
        elif namellist[-1] == '':
            for each in namellist[:-1]:
                newname = cn_name[each]
                names.append(newname)
            changename = ';'.join(names)
        else:
            for each in namellist:
                newname = cn_name[each]
                names.append(newname)
            changename = ';'.join(names)

        return changename


class TapdSetting(object):
    def __init__(self):
        pass

    @staticmethod
    def reload_setting():
        """重新加载配置文件，可以动态读取配置信息"""

        with open('config.ini', 'r', encoding='UTF-8') as f:  # config.ini 为可以修改的配置文件
            with open('config_tapd.py', 'w', encoding='UTF-8') as fn:  # config_tapd.py为每次脚本执行时使用的配置
                fn.write(f.read())
        import config_tapd
        reload(config_tapd)

        return config_tapd


if __name__ == '__main__':
    # print('[%s]脚本启动' % datetime.datetime.now().strftime('%Y%m%d %H:%M:%S'))
    # i = TapdEngine()
    # starttime = time.time()
    # i.excute()
    # endtime = time.time()
    # print('[%s]执行完毕' % datetime.datetime.now().strftime('%Y%m%d %H:%M:%S'))
    # print('耗时 %.1f' % (endtime - starttime))
    while True:
        nowtime = datetime.datetime.today().strftime('%H%M')
        if nowtime == '1820':
            print('[%s]working...' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            i = TapdEngine()
            starttime = time.time()
            i.excute()
            del i
            endtime = time.time()
            time.sleep(280 * 60 - int(endtime - starttime))
        elif nowtime == '2300':
            print('[%s]working...' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            i = TapdEngine()
            starttime = time.time()
            i.excute()
            del i
            endtime = time.time()
            time.sleep(1160 * 60 - int(endtime - starttime))
        else:
            time.sleep(10)
