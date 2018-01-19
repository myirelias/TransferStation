# coding=UTF-8

import os
import pickle
from hashlib import md5


class UrlManager(object):

    def __init__(self):
        self.new_urls = self.url_read('DATA/new_url.txt')
        self.old_urls = self.url_read('DATA/old_url.txt')

    @staticmethod
    def url_save(path, data):
        """
        保存数据到txt文件
        """
        with open(path, 'wb') as f:
            pickle.dump(data, f)

    @staticmethod
    def url_read(path):
        """
        读取文件中的数据
        """
        try:
            with open(path, 'rb') as f:
                data = pickle.load(f)
                return data
        except Exception:
            print('[error] %s not exists,create it now' % path)
            open(path, 'w', encoding='UTF-8')

        return set()

    @staticmethod
    def data_md5(data):
        """
        对数据进行md5加密
        """
        if isinstance(data, str):
            m = md5()  # 创建一个md5对象
            m.update(data.encode('UTF-8'))  # 使用md5对象对数据进行加密
            res = m.hexdigest()  # 加密后的十六进制结果
            return res
        else:
            print('[error]data must be str')

        return

    def url_check(self, url):
        """
        校验url是否已抓取
        """
        if isinstance(url, str):
            urls = [url]
        elif isinstance(url, list):
            urls = url
        else:
            print('values must be str or list')
            return

        for each in urls:
            m = md5()
            m.update(each.encode('UTF-8'))
            new = m.hexdigest()
            if new not in self.old_urls:
                self.new_urls.add(each)
            else:
                pass

    def get_new_url(self):
        """
        获取新的url
        """
        if len(self.new_urls) != 0:
            url = self.new_urls.pop()
            m = md5()
            m.update(url.encode('UTF-8'))
            self.old_urls.add(m.hexdigest())
            return url

        return 'no_data'

    def has_new_url(self):
        """
        是否有新的url
        """
        return self.new_url_size() != 0

    def new_url_size(self):
        """
        待爬取的新url数量
        """
        return len(self.new_urls)

