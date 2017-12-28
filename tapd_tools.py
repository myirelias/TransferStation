# !/usr/bin/env python
# coding=utf8

import datetime


class TapdTools(object):

    def __init__(self):
        pass

    # 获取当天日期
    @staticmethod
    def get_today():
        return datetime.datetime.today().strftime('%Y-%m-%d')

    # 构造文件名字，组合今天日期
    def make_filename(self):
        today = self.get_today()
        filename = 'tapd_task_%s.txt' % today
        return filename

    # 将拼音名字转换为中文，如有新增拼音名字，直接添加到cn_name
    @staticmethod
    def name_change(dealername):
        names = []
        cn_name = {'gaopeng': '高鹏',
                   'xieh': '谢浩',
                   'xieyangjie': '谢洋杰',
                   'wangjiawei': '王家葳',
                   'huangzj': '黄志江',
                   'wangxy': '王学艳',
                   'zhangl': '张力',
                   'humw': '胡明伟',
                   '龙超国': '龙超国',
                   '黄欣凯': '黄欣凯',
                   '古鹏飞': '古鹏飞',
                   '郑小乐': '郑小乐'}
        namellist = dealername.split(';')
        if len(namellist) == 1:
            changename = cn_name[dealername]
        elif namellist[-1] == '':
            for each in namellist[:-1]:
                newname = cn_name[each]
                names.append(newname)
            changename = ';'.join(names)
        else:
            for each in namellist:
                newname = cn_name[each]
                names.append(newname)
            changename = ';'.join(names)

        return changename

