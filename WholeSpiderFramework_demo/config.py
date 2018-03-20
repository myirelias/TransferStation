# 名称
TASK_NAME = 'guangming'

# 起始URL
START_URL = 'http://www.gmw.cn/'

# 控制域，必须为list格式
DOMAIN = ['gmw']

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
FN_OLD_URLS = 'old_urls.txt'

# 正则匹配规则
REGEX_URL = r'/\d{4}-\d{2}/\d{2}/\w+_\d+.htm'

# rabbitmq host
HOST = '192.168.2.107'

# 爬虫个数
SPIDERS = 4

# 需要过滤的url后缀
URL_END = ['.mp3']