# coding=utf-8

from lxml import etree


class SpiderXpather(object):

    def __init__(self):
        pass

    @staticmethod
    def xpath_content_data(**kwargs):
        """
        页面解析，必须提供content和xpather
        :param kwargs:
        :return:
        """
        if kwargs.get('content', '') == '' or kwargs.get('xpather', '') == '':
            return 'no content or xpather'
        content = kwargs['content']
        xpather = kwargs['xpather']
        try:
            selector = etree.HTML(content)
        except:
            selector = content
        try:
            if isinstance(xpather, dict):
                resdict = {}
                for eachkey in xpather.keys():
                    reslist = selector.xpath(xpather[eachkey])
                    resdict[eachkey] = ''.join(reslist).replace('\n', '').replace('\r', '')
                res = resdict
            elif isinstance(xpather, str):
                res = selector.xpath(xpather)
            else:
                return 'xpather must be str or dict'
        except:
            return

        return res
