# coding=UTF-8

import os
from pymongo import MongoClient


class DataManager(object):

    def __init__(self):
        self._mkdatadir()

    @staticmethod
    def _mkdatadir():
        """创建DATA文件夹存放数据"""
        if not os.path.exists('DATA'):
            os.makedirs('DATA')

        return

    def data_save(self, data, dbname, colname):
        """
        存储数据到mongodb
        :param data: 需要储存的内容
        :param dbname: 数据库名称
        :param colname: 集合名称
        :return:
        """
        try:
            client = MongoClient('localhost', 27017)
            db = client[dbname]
            col = db[colname]
            if data:
                col.insert(data)
        except Exception as e:
            print('[error] %s' % e)
            return

    def date_read(self, dbname, colname):
        """
        从mongodb中读取数据
        :param dbname: 数据库名称
        :param colname: 集合名称
        :return: 结果数据的cursor游标
        """
        try:
            client = MongoClient('localhost', 27017)
            db = client[dbname]
            col = db[colname]
            cur = col.find({}, {'_id': 0}, no_cursor_timeout=True)
            return cur
        except Exception as e:
            print('[error] %s' % e)

        return