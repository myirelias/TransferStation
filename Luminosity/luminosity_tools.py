# !/usr/bin/env python
# coding=utf-8

from hashlib import md5
import re


class Tools(object):
    """
    工具类，提供各种小工具
    function tools
    """
    @staticmethod
    def tool_proxies():
        """
        使用代理ip
        :return:
        """
        proxyhost = "proxy.abuyun.com"
        proxyport = "9010"
        # 代理隧道验证信息
        proxyuser = "HY3JE71Z6CDS782P"
        proxypass = "CE68530DAD880F3B"
        proxymeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {"host": proxyhost,
                                                                    "port": proxyport,
                                                                    "user": proxyuser,
                                                                    "pass": proxypass}
        proxies = {"http": proxymeta,
                   "https": proxymeta}

        return proxies

    @staticmethod
    def tool_md5(data):
        """
        对传入的数据进行md5加密处理
        :param data: 需要加密处理的内容
        :return: 32位md5加密码
        """
        m = md5()
        m.update(data.encode('UTF-8'))
        md5code = m.hexdigest()  # 32位md5码

        return md5code

    @staticmethod
    def tool_regex(data):
        """
        正则过滤url,按照静态新闻页面和非静态新闻页面划分
        :param data: 需要过滤的url
        :return: 静态 True 非静态 False
        """
        pattern = re.compile(r'/\d{4}-\d{2}/\d{2}/\w+_\d+.htm', re.S)
        res = re.search(pattern, data)
        if res:
            return True

        return False