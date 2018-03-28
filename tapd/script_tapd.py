# !/usr/bin/env python
# coding=utf8
# version=1.2
"""
v 1.1
新增方法
    1. crawl_get_content:获取页面content
    2. spider_content_data:解析页面数据
    3. tool_data_format:将每天数据格式化输出
新增逻辑 抓取目录列表，以目录列表为单位抓取每个目录列表下面所有任务，并添加目录列表标签
修改config.ini： URL

v 1.2
调整抓取策略：
    1.新增每日22：00再次抓取当日任务，并进行格式化输出，推送至hdfs
    2.新增当日任务txt文本校验，若当日任务txt文本已存在，则删除该文件，以便第二次抓取
"""
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
    """
    逻辑处理类，包含所有对其他类的调用以及逻辑处理
    function excute: 启动方法，负责对各个方法进行启动，对数据结果进行推送
    function all_task_link: 获取所有需要抓取的任务，新增遍历项目目录逻辑，所有任务链接输出到all_task_link.txt文本
    function each_task_info: 获取每个任务的所有评论内容，将当日发布的内容进行提取
    """

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
        """
        启动方法
        每日抓取完成后推送到HDFS上
        :return:
        """
        if 2200 <= int(datetime.datetime.today().strftime('%H%M')) < 2300:
            self.tools.tool_check_file(self.filename)
        self.all_task_link()
        self.each_task_info()
        # if int(datetime.datetime.today().strftime('%H%M')) >= 2300 \
        #         or int(datetime.datetime.today().strftime('%H%M')) <= 800:
        #     self.pipe.load_in_hdfs(self.setting.FN_ALL_TASK_INFO)
        # else:
        #     self.pipe.load_in_hdfs(self.filename)

    # 获取所有任务的link
    def all_task_link(self):
        """
        获取所有任务的链接
        1.1版本新增多项目目录遍历，不再只有单一的'实验室事项'目录
        抓取每个项目目录中的全部任务，目的是避免漏抓以前发布的项目的迭代更新内容
        所有获取到的任务链接输出到DATA/all_task_link.txt中
        """
        xpater_project = ".//*[@class='project-list']/li/a/@href"
        content_project = self.crawl.crawl_get_contnet(self.setting.URL, headers=self.setting.HEADERS)
        res_project = self.spider.spider_content_data(content_project, xpater_project)
        xpater_all = ".//*[@data-editable='text']//*[@class='editable-value']/@href"
        all_task = []
        for eachurl in res_project:
            content = self.crawl.tapdlist(eachurl + '/prong/stories/stories_list')
            tasklist = self.spider.cleandata(content, xpater_all)
            for eachone in tasklist:
                all_task.append(eachone)
        self.pipe.save_list_txt(all_task, self.setting.FN_ALL_TASK_LINK)

    # 获取所有任务的详细内容
    def each_task_info(self):
        """
        对TAPD所有的任务进行抓取
        从DATA/all_task_link.txt中加载所有任务链接
        每个任务获取其所有评论内容并提取当日的数据
        对当日数据进行格式化处理并输出到DATA/tapd_task_xxxx-xx-xx.txt中
        当日数据追加到历史数据中DATA/task_cmt2.txt
        :return:
        """
        alltasklink = self.pipe.read_alltask_url(self.setting.FN_ALL_TASK_LINK)
        savedata = []
        for eachlink in alltasklink:
            try:
                savehistory = []
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
                        # 历史数据存储的内容
                        createdatalist = [dealdate, taskdict['tasktype'], dealer_name, taskdict['title'],
                                          taskdict['state'], eachdealercontent[2],
                                          ''.join(eachdealercontent[3:]).strip()]
                        # 当日数据存储的内容
                        createdatadict1 = [taskdict['title'],
                                           taskdict['state'], eachdealercontent[2],
                                           ''.join(eachdealercontent[3:]).strip()]
                        # 当日数据格式化
                        saveinfo = '\t'.join(createdatadict1)
                        # 历史数据格式化
                        savehis = '\u0001'.join(createdatalist)
                        # 当日数据格式化
                        createdatadict = {
                            'dealdate': dealdate,
                            'tasktype': taskdict['tasktype'],
                            'dealer_name': dealer_name,
                            'info': saveinfo
                        }
                        savehistory.append(savehis)
                        savedata.append(createdatadict)
                # 23点以后的抓取内容只存入到历史数据中
                if int(datetime.datetime.today().strftime('%H%M')) >= 2300 or int(
                        datetime.datetime.today().strftime('%H%M')) <= 800:
                    self.pipe.save_list_txt(savehistory, self.setting.FN_ALL_TASK_INFO, savetype='a')
                time.sleep(0.5)
            except Exception as e:
                filename_error = 'error_log.txt'
                error_info = '[%s]|[%s]  %s' % (datetime.datetime.now().strftime('%Y%m%d %H:%M:%S'),
                                                e, eachlink,)
                self.pipe.save_list_txt(error_info, filename_error, savetype='a')
                time.sleep(10)
                continue
        # 当日数据抓取后经过格式化处理直接写入到当天的文本中
        if len(savedata) != 0 and int(datetime.datetime.today().strftime('%H%M')) < 2300:
            self.tools.tool_data_format(savedata, self.filename)
            # self.pipe.save_list_txt(savedata, self.filename, savetype='a')


class TapdCrawl(object):
    """
    功能类，主要提供页面content的抓取
    function tapdlist: 请求TAPD项目页面content
    function get_eachtask_info: 请求每个任务的content
    function crawl_get_content: 请求指定url的页面content
    """

    def __init__(self):
        self.session = requests.Session()
        newconfig = TapdSetting()
        self.setting = newconfig.reload_setting()
        self.headers = self.setting.HEADERS
        self.session.headers.update(self.setting.HEADERS)

    # 请求tapd任务列表，pagecode默认为utf-8
    def tapdlist(self, url, pagecode='utf-8'):
        retry = 5
        response = 'no_data'
        try:
            while retry > 0:
                res = self.session.get(url, params=self.setting.PARAMS,
                                       headers=self.setting.HEADERS, cookies=self.setting.COOKIES, timeout=30)
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
                res = self.session.get(url, headers=self.setting.HEADERS, cookies=self.setting.COOKIES, timeout=30)
                if res.status_code == 200:
                    response = res.content.decode(pagecode)
                    break
                else:
                    retry -= 1
                    continue
        except Exception:
            pass

        return response

    # get请求页面content
    def crawl_get_contnet(self, url, **kw):
        retry = 5  # 重试次数
        response = 'no_data'  # 响应内容
        while retry:
            retry -= 1
            try:
                res = self.session.get(url, params=kw.get('params', ''), headers=kw.get('headers', ''),
                                       proxies=kw.get('proxies', ''), cookies=kw.get('cookies', ''), timeout=30)
                if res.status_code == 200:
                    response = res.content.decode(kw.get('pagecode', 'utf-8'))
                    break
                else:
                    continue
            except:
                continue

        return response


class TapdSpider(object):
    """
    功能类，负责对页面content进行解析
    function _spider_data: 根据提供的页面content和xpath解析规则解析其中的数据并返回
    function _spider_string: 主要是针对页面的多次解析，负责对提供的xpath解析的element对象类型进行二次解析
    function cleandata_more: 主要通过提供dict类型的xpath规则对页面进行解析
    function spider_content_data: 根据提供的页面content和xpath解析规则解析其中的数据并返回，增加了xpath类可扩展功能
    """

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

    # 解析页面内容
    @staticmethod
    def spider_content_data(content, xpather):
        """
        解析页面content，使用xpath规则
        :param content: 待解析的页面content
        :param xpather: xpath规则，目前只接受dict和str两种类型的参数
        :return: 返回解析的结果
        """
        response = 'no_data'
        try:
            selector = etree.HTML(content)
        except:
            selector = content

        if isinstance(xpather, dict):
            response = {}
            for eachkey in xpather.keys():
                try:
                    response[eachkey] = ''.join(selector.xpath(xpather[eachkey]))
                except:
                    continue
        elif isinstance(xpather, str):
            response = selector.xpath(xpather)
        else:
            print('xpather must be dict or str')

        return response


class TapdPipe(object):
    """
    功能类，主要负责数据的输出/输入操作
    function _checkdir: 创建DATA文件夹
    function _save_txt: 存储数据到指定txt文本中
    function _read_txt: 读取指定txt文本中的数据
    function load_in_hdfs: 推送数据到hdfss
    function pipe_save_txt: 新增的存储数据到txt文本
    """

    def __init__(self):
        self._checkdir()

    @staticmethod
    def _checkdir():
        """
        创建data文件夹
        :return:
        """
        if not os.path.exists('DATA'):
            os.makedirs('DATA')

    @staticmethod
    def _save_txt(content, filename, savetype):
        """
        存储数据到指定txt文本中
        :param content: 存储内容
        :param filename: 文件名
        :param savetype: 存储方式
        :return:
        """
        if isinstance(content, list):
            with open(os.path.join(os.path.abspath('DATA'), filename), savetype, encoding='utf8') as f:
                for each in content:
                    f.write(each + '\n')
        else:
            with open(os.path.join(os.path.abspath('DATA'), filename), savetype, encoding='utf8') as f:
                f.write(content + '\n')  # 为了记录错误日志才添加的else,因为错误信息是str不是list

    # 读取txt文件
    @staticmethod
    def _read_txt(filename):
        """
        读取指定txt中的数据内容
        :param filename: 文件名称
        :return: 文件中的内容
        """
        return (each for each in open(os.path.join(os.path.abspath('DATA'), filename), 'r', encoding='utf8'))

    # 存list到txt
    def save_list_txt(self, content, filename, savetype='w'):
        self._save_txt(content, filename, savetype)

    def read_alltask_url(self, filename):
        return self._read_txt(filename)

    # 集群操作
    def load_in_hdfs(self, filename):
        """
        集群操作
        :param filename: 需要推送的文件
        :return:
        """
        hdfs = HDFileSystem(host='192.168.100.178', port=8020)
        try:
            file_path = os.path.join(os.path.abspath('DATA'), filename)
            hdfs_path = os.path.join('/user/spider/TAPD_TASK', filename)
            hdfs.put(file_path, hdfs_path)
        except Exception as e:
            print('集群挂了', e)

    @staticmethod
    def pipe_save_txt(content, filename, savetype):
        if isinstance(content, list):
            with open(os.path.join(os.path.abspath('DATA'), filename), savetype, encoding='utf8') as f:
                for each in content:
                    f.write(each + '\n')
        else:
            with open(os.path.join(os.path.abspath('DATA'), filename), savetype, encoding='utf8') as f:
                f.write(content + '\n')  # 为了记录错误日志才添加的else,因为错误信息是str不是list


class TapdTools(object):
    """
    功能类，主要是一些小工具
    function get_today: 获取当天日期
    function makefile: 创建当日的文件名称
    function name_change: 将拼音名称转换为中文名称
    function tool_data_format: 对数据进行格式化处理
    """

    def __init__(self):
        config = TapdSetting()
        self.setting = config.reload_setting()
        self.pipe = TapdPipe()

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

    # 数据格式化
    def tool_data_format(self, data, filename):
        """
        对数据进行格式化，目前只接受由dict类型组成的list的数据
        :param filename: 存储位置
        :param data: 一个或多个dict组成的list
        :return: 格式化后的数据
        """
        today = datetime.datetime.now().strftime('%Y-%m-%d') + ':\n'
        self.pipe.pipe_save_txt(today, filename, savetype='a')
        all_name = set([])
        # 获取当前data中所有人员名称
        for each in data:
            all_name.add(each.get('dealer_name'))

        # 把所有任务按照每个人为单位分组
        for one in all_name:
            save_data = ''
            onelist = []
            for each in data:
                if each.get('dealer_name') == one:
                    onelist.append(each)

            typename = set([])
            # 获取每个人所有任务
            for eveyone in onelist:
                tasktype = eveyone.get('tasktype')
                typename.add(tasktype)
            save_data += one.strip() + ':' + '\n'
            # 将每个人的数据按照任务分组
            for eachtype in typename:
                typelist = []
                for eveyone in onelist:
                    if eveyone.get('tasktype') == eachtype:
                        typelist.append(eveyone.get('info'))
                save_data += eachtype.strip() + '\n'
                for each in typelist:
                    save_data += '\t\t' + each.strip() + '\n'

            self.pipe.pipe_save_txt(save_data, filename, savetype='a')

    # 文件校验
    @staticmethod
    def tool_check_file(filename):
        """
        当日任务文本校验，如果存在则删除当日任务文本，以便第二次抓取
        :param filename:当日任务文件名称
        :return:
        """
        today_task = os.path.join(os.path.abspath('DATA'), filename)
        if not os.path.exists(today_task):
            return
        os.remove(today_task)


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
    """
    循环执行
    每天18:00开始抓取，数据入当日任务txt文本中
    每天22:00第二次抓取，数据入当日任务txt文本中
    每天23:00第三次抓取，数据入历史任务txt文本中
    """
    while True:
        nowtime = datetime.datetime.today().strftime('%H%M')
        if nowtime == '1800' or nowtime == '2200':
            # print('[%s]working...' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))  # 部署时请注释该行
            i = TapdEngine()
            starttime = time.time()
            i.excute()
            del i
            endtime = time.time()
            # time.sleep(60 * 60 - int(endtime - starttime))
        elif nowtime == '2300':
            # print('[%s]working...' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))  # 部署时请注释该行
            i = TapdEngine()
            starttime = time.time()
            i.excute()
            del i
            endtime = time.time()
            time.sleep(1140 * 60 - int(endtime - starttime))
        else:
            time.sleep(10)
