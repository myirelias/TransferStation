#!/usr/bin/python
# coding=utf-8
'''
Created on 2018年9月3日

@author: humingwei
'''
import time
from aliyun.log import LogClient
from aliyun.log.putlogsrequest import PutLogsRequest
from aliyun.log.logitem import LogItem

# 账号等配置信息
# endpoint = 'cn-shenzhen.log.aliyuncs.com' # 日志服务的http地址，必选参数
# accessKeyId = 'LTAINzhqTlomTNJA' #用户身份标识，必选参数
# accessKey = '5pUScRlSstFDlXahZUAdTR4zZ30Xq4'
#
# project = 'daqsoft' # 日志服务的项目名，必选参数
# logstore = 'task_scheduling' # 日志服务的日志库名，必选参数

endpoint = 'cn-shenzhen.log.aliyuncs.com'  # 日志服务的http地址，必选参数
accessKeyId = 'F8TzTgiG8arBQSsb'  # 用户身份标识，必选参数
accessKey = 'pPNGvSuULYJChpvlfdwOWOhTFX4xSN'

project = 'daqsoft-test'  # 日志服务的项目名，必选参数
logstore = 'team_test'  # 日志服务的日志库名，必选参数

# 日志等级
CRITICAL = 'critical'
ERROR = 'error',
WARNING = 'warning'
INFO = 'info'
DEBUG = 'debug'

# 日志必要字段
LEVEL = 'level'
PROJECT = 'project'
CLASS = 'class'
DATE = 'date'
MESSAGE = 'message'


class AliyunLog(object):
    ''''''
    client = LogClient(endpoint, accessKeyId, accessKey)
    request_set_data = PutLogsRequest(project, logstore)
    default_time_format = '%Y-%m-%d %H:%M:%S'

    def __init__(self, ota_category):
        self.category = ota_category.split('_')[1]
        self.project = ota_category

    def debug(self, message, class_=''):
        '''调试'''
        self.put_data(DEBUG, message, class_)

    def info(self, message, class_=''):
        '''提示信息'''
        self.put_data(INFO, message, class_)

    def warning(self, message, class_=''):
        '''警告'''
        self.put_data(WARNING, message, class_)

    def error(self, message, class_=''):
        '''错误'''
        self.put_data(ERROR, message, class_)

    def critical(self, message, class_=''):
        '''致命错误'''
        self.put_data(CRITICAL, message, class_)

    def put_data(self, level, message, class_):
        '''写日志'''
        client = self.client
        request = self.request_set_data
        contents = [
            (LEVEL, level),
            (PROJECT, self.project),
            (CLASS, class_),
            (DATE, time.strftime(self.default_time_format, time.localtime())),
            (MESSAGE, str(message))
        ]
        logItem = LogItem(int(time.time()), contents)
        request.set_log_items([logItem])
        try:
            client.put_logs(request)
        # res2 = client.put_logs(request)
        #             res2.log_print()
        except Exception as e:
            print(e)

    def test_get_data(self):
        client = self.client
        listShardRes = client.list_shards(project, logstore)
        for shard in listShardRes.get_shards_info():
            shard_id = shard["shardID"]
            # get_cursor 获取特定时间的游标 - 可以特定日志库分区的特定接受时间最接近的一个游标.
            res = client.get_begin_cursor(project, logstore,
                                          shard_id)  # get_cursor(project, logstore, shard["shardID"], 'begin')
            start_cursor = res.get_cursor()
            res = client.get_end_cursor(project, logstore,
                                        shard_id)  # get_cursor(project, logstore, shard["shardID"], 'end')
            end_cursor = res.get_cursor()
            loggroup_count = 10  # 每次读取10个包
            while True:
                res = client.pull_logs(project, logstore, shard_id, start_cursor, loggroup_count, end_cursor)
                res.log_print()
                next_cursor = res.get_next_cursor()
                if next_cursor == end_cursor:
                    break
                start_cursor = next_cursor


# if __name__ == '__main__':
#     log = AliyunLog('test')
#     log.debug('测试aliyun_log')
#     # log.test_get_data()
#
#     print('__end__')
