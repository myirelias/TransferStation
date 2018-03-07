# !/usr/bin/env python
# coding=utf-8

import os
import pickle
from hashlib import md5
import re


class ControlTask(object):
    """
    任务管理器，负责任务相关操作，如校验是否新增，读取已抓取任务文本
    """
    def __init__(self):
        self._mkdata()
        self.old_urls = self._task_read('../DATA/old_urls.txt')
        self.new_urls = set()

    @staticmethod
    def _task_read(path):
        """
        任务加载方法
        :param path: 存储位置
        :return: 加载内容
        """
        try:
            with open(path, 'rb') as f:
                data = pickle.load(f)
                return data
        except Exception as e:
            print(e)
            print('[error] %s not exists, create it now' % path)
            open(path, 'w')

        return set()

    @staticmethod
    def task_save(data, path):
        """
        存储数据
        :param data: 存储内容
        :param path: 存储位置
        :return:
        """
        with open(path, 'wb') as f:
            pickle.dump(data, f)

    @staticmethod
    def _mkdata():
        """
        创建data文件夹，用于存放数据
        :return:
        """
        if not os.path.exists('../DATA'):
            os.makedirs('../DATA')

    def task_check(self, task):
        """
        任务检验，是否为新增任务
        :param task: task内容，此处为url
        :return:
        """
        if isinstance(task, str):
            task_list = [task]
        elif isinstance(task, list):
            task_list = task
        else:
            print('task must be list or str, not %s' % type(task))
            return

        # 这里页面匹配规则可能因网站需要修改
        # 此处应该单独封装起来
        for eachtask in task_list:
            # 控制抓取的域
            if 'gmw' not in eachtask:
                continue
            m = md5()
            m.update(eachtask.encode('utf-8'))
            current_md5 = m.hexdigest()
            if current_md5 not in self.old_urls:
                self.new_urls.add(eachtask)

    def task_get_new(self):
        """
        获取新增任务
        :return:
        """
        if self.new_urls:
            url = self.new_urls.pop()
            m = md5()
            m.update(url.encode('utf-8'))
            self.old_urls.add(m.hexdigest())
            return url

        return 'no_data'

    def task_has_new(self):
        """
        是否有新增任务
        :return: 如果有新增任务，则返回具体任务数量，否则返回false
        """
        if self.new_urls:
            return len(self.new_urls)
        else:
            return False

    def task_static_unstatic(self, regexer):
        """
        区分新增静态任务和非静态任务
        :return:依次返回静态任务和非静态任务
        """
        static_task = []
        unstatic_task = []
        while self.new_urls:
            url = self.task_get_new()
            if self.task_regex(url, regexer):
                static_task.append(url)
            else:
                unstatic_task.append(url)

        return static_task, unstatic_task

    @staticmethod
    def task_regex(data, regexer):
        """
        正则过滤url,按照静态新闻页面和非静态新闻页面划分
        :param data: 需要过滤的url
        :return: 静态 True 非静态 False
        """
        pattern = re.compile(regexer, re.S)
        res = re.search(pattern, data)
        if res:
            return True

        return False

