# !/usr/bin/env python
# coding=utf8

import requests
from tapd_setting import HEADERS, COOKIES, PARAMS, URL


class TapdCrawl(object):

    def __init__(self):
        self.session = requests.Session()
        self.headers = HEADERS
        self.session.headers.update(HEADERS)

    # 请求tapd任务列表，pagecode默认为utf-8
    def tapdlist(self, pagecode='utf-8'):
        retry = 5
        response = 'no_data'
        try:
            while retry > 0:
                res = self.session.get(URL, params=PARAMS, cookies=COOKIES, timeout=30)
                if res.status_code == 200:
                    response = res.content.decode(pagecode)
                    break
                else:
                    retry -= 1
                    continue
        except Exception:
            pass

        return response

    # 请求url，获取content
    def get_eachtask_info(self, url, pagecode='utf-8'):
        retry = 5
        response = 'no_data'
        try:
            while retry > 0:
                res = self.session.get(url, cookies=COOKIES, timeout=30)
                if res.status_code == 200:
                    response = res.content.decode(pagecode)
                    break
                else:
                    retry -= 1
                    continue
        except Exception:
            pass

        return response


