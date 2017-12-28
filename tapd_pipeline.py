# !/usr/bin/env python
# coding=utf-8

import os
# from hdfs3 import HDFileSystem


class TapdPipe(object):

    def __init__(self):
        pass

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

    # # 集群操作
    # def load_in_hdfs(self, filename):
    #     hdfs = HDFileSystem(host='192.168.100.178', port=8020)
    #     try:
    #         file_path = os.path.join(os.path.abspath('DATA'), filename)
    #         hdfs_path = os.path.join('/user/spider/TAPD_TASK', filename)
    #         hdfs.put(file_path, hdfs_path)
    #     except Exception as e:
    #         print('集群挂了', e)
