# coding=utf-8
'''存储模块'''

import pickle
import os
from pymongo import MongoClient
import config as setting


class Pipeline(object):
    """
    存储模块，负责对数据进行持久化操作或读取数据操作
    pipe_mongo_save 存储数据到mongodb
    pipe_mongo_load 读取数据到mongodb
    pipe_txt_save 存储数据到txt文本
    pipe_txt_load 从txt文本加载数据
    pipe_pickle_save 将内存中的数据持久化到硬盘中
    pipe_pickle_load 将硬盘中的数据加载并置于内存
    """

    def __init__(self):
        self.conn = MongoClient(setting.HOST, 27017)
        self.path = os.path.join(os.path.abspath('DATA'), '{}')
        self._pipe_create_data()

    @staticmethod
    def _pipe_create_data():
        """
        创建DATA文件夹
        :return:
        """
        if not os.path.exists('DATA'):
            os.makedirs('DATA')

    def pipe_remove_file(self, filename):
        """
        创建DATA文件夹
        :return:
        """
        if os.path.exists(self.path.format(filename)):
            os.remove(self.path.format(filename))

    def pipe_mongo_save(self, data, **kw):
        """
        使用mongodb存储数据
        :param data:
        :param kw:
        :return:
        """
        try:
            db = self.conn[kw.get('dbname', 'default')]
            col = db[kw.get('colname', 'default')]
            col.insert(data)
        except Exception as e:
            print('[error]by save mongo', e)

    def pipe_mongo_load(self, **kw):
        """
        加载mongodb中的数据
        :param kw:
        :return:
        """
        if kw.get('value'):
            value = kw['value']
        else:
            value = {}
        try:
            db = self.conn[kw.get('dbname', 'default')]
            col = db[kw.get('colname', 'default')]
            res = col.find(value, {'_id': 0})
            return list(res)
        except Exception as e:
            print('[error]by save mongo', e)

    def pipe_mongo_update(self, data, **kw):
        """
        更新或插入数据
        :param data:
        :param kw:
        :return:
        """
        tourist_id = data['tourist_id']
        try:
            db = self.conn[kw.get('dbname', 'default')]
            col = db[kw.get('colname', 'default')]
            res = col.update({'tourist_id': tourist_id}, {'$set': data})
            # 更新数据失败，不存在该数据，则插入数据
            if not res.get('updatedExisting'):
                col.insert(data)
        except Exception as e:
            print('[error]by save mongo', e)

    def pipe_txt_save(self, data, **kw):
        """
        将数据存储到txt文本中
        :param data:
        :param kw:
        :return:
        """
        with open(self.path.format(kw.get('filename', 'default.txt')), kw.get('savetype', 'a'), encoding='utf-8') as f:
            if isinstance(data, list) or isinstance(data, set):
                for each in data:
                    f.write(each + '\n')
            elif isinstance(data, str):
                f.write(data + '\n')

    def pipe_txt_load(self, **kw):
        """
        从txt文本中加载数据
        :param kw:
        :return:
        """
        try:
            with open(self.path.format(kw.get('filename', 'default.txt')), kw.get('loadtype', 'r'), encoding='utf-8') as f:
                return f.readlines()
        except:
            return

    def pipe_pickle_save(self, data, **kw):
        """
        从内存持久化到硬盘中
        :param data:
        :param kw:
        :return:
        """
        with open(self.path.format(kw.get('filename', 'default.txt')), 'wb') as f:
            pickle.dump(data, f)

    def pipe_pickle_load(self, **kw):
        """
        将硬盘中持久化的数据加载到内存
        :return:
        """
        try:
            with open(self.path.format(kw.get('filename', 'default.txt')), 'rb') as f:
                return pickle.load(f)
        except:
            return
