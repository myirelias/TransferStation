# 起始URL
START_URL = 'http://www.gmw.cn/'

# 请求头
HEADERS = {
    'Host': 'www.gmw.cn',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:52.0) Gecko/20100101 Firefox/52.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0',
}

# xpath规则
XPATHER_HREF = ".//*/@href"
XPATHER_NEWS_LIST = [
    {
        "title": ".//*[@id='articleTitle']/text()",
        "publish_time": ".//*[@id='pubTime']/text()",
        "source": "substring-after(.//*[@id='source'],'来源：')",
        "content": ".//*[@id='contentMain']/descendant::text()",
        "editor": ".//*[@id='contentLiability']/text()",
    },
]

# 文件位置
FN_OLD_URLS = 'fn_old_urls.txt'