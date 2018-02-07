# coding=UTF-8

"""工具模块"""


class SomeTools(object):

    @staticmethod
    def tool_use_proxy():
        """代理"""
        # 要访问的目标页面
        # targetUrl = "http://test.abuyun.com/proxy.php"
        # 代理服务器
        proxyhost = "proxy.abuyun.com"
        # proxyPort = "9020"
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