

class TapdSpider(object):

    def __init__(self):
        pass

    # xpath匹配，需提供html的content和一个xpath表达式
    @staticmethod
    def _spider_data(content, xpather):
        selector = etree.HTML(content)
        res = selector.xpath(xpather)

        return res

    # xpath二次匹配(主要针对评论栏里的数据)
    @staticmethod
    def _spider_string(content, xpather):
        stringlist = []
        if isinstance(content, list):
            for each in content:
                eachlist = []
                datestr = each.xpath(xpather)
                for everystr in datestr:
                    eachlist.append(everystr.strip())
                stringlist.append(eachlist)

        return stringlist

    def cleandata(self, content, xpather):

        return self._spider_data(content, xpather)

    def cleanstring(self, content, xpather):

        return self._spider_string(content, xpather)

    # task详细信息
    def cleandata_more(self, content, xpatherdict):

        if isinstance(xpatherdict, dict):
            taskdict = {}
            for eachkey in xpatherdict.keys():
                data = self._spider_data(content, xpatherdict[eachkey])
                taskdict[eachkey] = data[0] if len(data) != 0 else 'no_data'
        else:
            taskdict = 'no_data'

        return taskdict
