# coding=UTF-8

import requests


class SpiderCrawl(object):

    def __init__(self):
        self.session = requests.Session()

    def crawl_get_content(self, url, **kwargs):
        """
        get请求页面数据
        :param url: 请求地址
        :param kwargs: 参数字典
        :return: 页面content
        """
        retry = 5
        while retry:
            retry -= 1
            try:
                page = self.session.get(url, headers=kwargs.get('headers', ''),
                                        params=kwargs.get('params', ''), proxies=kwargs.get('proxies', ''))
                if page.status_code == 200:
                    res = page.content.decode(kwargs.get('pagecode', 'UTF-8'))
                    return res
                else:
                    continue
            except:
                continue

            return

    def crawl_post_content(self):
        pass