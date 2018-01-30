# 请求头
HEADERS = {
    'Host': 'www.xinhuanet.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:52.0) Gecko/20100101 Firefox/52.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Proxy_Switch_Ip': 'yes'
}

# url
URL_YUQING = {'舆情': 'http://www.news.cn/yuqing/index.htm'}
URL_RENSHI = {'人事': 'http://www.xinhuanet.com/politics/rs.htm'}
URL_LILUN = {'理论': 'http://www.news.cn/politics/xhll.htm'}

# xpath规则
XPATHER_HREF = ".//*/li/a/@href"
XPATHER_NEWS_INFO = [
    {
        "title": ".//*[@class='h-title']/text()",
        "publish": ".//*[@class='h-time']/text()",
        "source": "substring-after(.//*[@class='h-info'], '来源：')",
        "position": "string(.//*[@class='news-position'])",
        "content": ".//*[@id='p-detail']/descendant::text()"
    },
    {
        "title": ".//*[@id='title']/text()",
        "publish": ".//*[@class='time']/text()",
        "source": ".//*[@class='sourceText']/text()",
        "position": "string(.//*[@class='news-position'])",
        "content": ".//*[@id='article']/descendant::p/text()"
    }
]



# files
FILE_OLDNEWS = 'file_old_news.txt'