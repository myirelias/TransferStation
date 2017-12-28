# !/usr/bin/env python
# coding=utf-8

import os
from hdfs3 import HDFileSystem


# 集群操作
def load_in_hdfs(name):
    hdfs = HDFileSystem(host='192.168.100.178', port=8020)
    try:
        file_path = os.path.join(os.path.abspath('DATA'), name)
        hdfs_path = os.path.join('/user/spider/TAPD_TASK', name)
        hdfs.put(file_path, hdfs_path)
    except Exception as e:
        print('集群挂了', e)

FN_ALL_TASK_INFO = 'task_cmt2.txt'
filename = 'tapd_task_2017-10-30.txt'

for each in [filename, FN_ALL_TASK_INFO]:
    load_in_hdfs(each)