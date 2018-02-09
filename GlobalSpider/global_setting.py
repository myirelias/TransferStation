# 请求头
HEADERS = {
    'Host': 'opinion.huanqiu.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:52.0) Gecko/20100101 Firefox/52.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate',
    'Referer': 'http://opinion.huanqiu.com/roll_2.html',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'If-Modified-Since': 'Fri, 09 Feb 2018 01:20:00 GMT',
    'Cache-Control': 'max-age=0',
    'Switch-Proxy-Ip': 'yes'
}

# xpath规则
XPATHER_ELEMENT = ".//*[@class='listPicBox']/li[@class='item']"
XPATHER_EACH_NEWS = {
    "title": ".//h3/a/text()",
    "intro": ".//h5/descendant::text()",
    "publish_date": ".//h6/text()",
    "link": ".//*[text()='详细']/@href"
}
XPATHER_DETAIL = [
    {
        "title": ".//*[@class='conText']/h1/descendant::text()",
        "publish_date": ".//*[@class='timeSummary']/text()",
        "source": ".//*[@class='fromSummary']/descendant::text()",
        "position": "string(.//*[@class='topPath'])",
        "content": ".//*[@class='text']/descendant::p/text()",
        "img": ".//*[@class='text']/descendant::p/img/@src",
        "author": ".//*[@class='author']/descendant::text()"
    }
]

# url
URL_DICT = {
    '滚动新闻': 'http://opinion.huanqiu.com/roll.html',
    '内地新闻': 'http://china.huanqiu.com/local/',
    '社会新闻': 'http://society.huanqiu.com/socialnews/',
    '旅游黑榜': 'http://go.huanqiu.com/list/black/',
    '旅游红榜': 'http://go.huanqiu.com/list/red/',
    '旅游新闻-出游': 'http://go.huanqiu.com/news/tour/',
    '旅游新闻-酒店': 'http://go.huanqiu.com/news/hotel/',
    '旅游新闻-航空': 'http://go.huanqiu.com/news/airline/',
    '旅游新闻-业内': 'http://go.huanqiu.com/news/tourism/',
    '旅游新闻-全域旅游': 'http://go.huanqiu.com/news/qyly/',
    '旅游新闻-厕所革命 ': 'http://go.huanqiu.com/news/csgm/',
    '旅游新闻-旅游扶贫': 'http://go.huanqiu.com/news/lyfp/'
}

# file
FILE_OLD_NEWS = 'DATA/file_old_news.txt'
FILE_HISTORY = 'file_history_news.txt'
FILE_CURRENT = 'file_current_news.txt'