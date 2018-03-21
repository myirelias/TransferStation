# 名称
TASK_NAME = 'china_net'

# 起始URL
START_URL = 'http://www.china.com.cn/'

# 控制域
DOMAIN = 'china.com.cn'
# 请求头
HEADERS = {
    'Host': 'www.china.com.cn',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:52.0) Gecko/20100101 Firefox/52.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate',
    'Referer': 'http://www.china.com.cn/',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

# xpath规则
XPATHER_HREF = ".//*/@href"
# 字段模版
# {
#     "title": "",
#     "publish_time": "",
#     "source": "",
#     "author": "",
#     "belong": "",
#     "content": "",
#     "editor": "",
# },
XPATHER_NEWS_LIST = [
    {
        "title": ".//*[@class='articleTitle']/descendant::text()",
        "publish_time": "substring-after(.//*[@id='pubtime_baidu'],'发布时间：')",
        "source": "substring-after(.//*[@id='source_baidu'],'来源：')",
        "author": "substring-after(.//*[@id='author_baidu'],'作者：')",
        "belong": "",
        "content": ".//*[@class='articleBody']/descendant::text()",
        "editor": "substring-after(.//*[@class='articleEditor'],'编辑：')",
    },
    {
        "title": ".//*[@class='artTitle']/text()",
        "publish_time": "substring-after(.//*[@id='pubtime_baidu'],'发布时间：')",
        "source": "substring-after(.//*[@id='source_baidu'],'来源：')",
        "author": "substring-after(.//*[@id='author_baidu'],'作者：')",
        "belong": "string(.//*[@class='artLink'])",
        "content": ".//*[@class='artCon']/descendant::text()",
        "editor": "substring-after(.//*[@id='editor_baidu'],'编辑：')",
    },
    {
        "title": ".//*[@class='cTitle']/text()",
        "publish_time": "substring-before(substring-after(.//*[@class='cInfo'],'发布时间：'),'责任编辑')",
        "source": "substring-before(substring-after(.//*[@class='cInfo'],'文章来源：'),'发布时间')",
        "author": "",
        "belong": "string(.//*[@class='cNav'])",
        "content": ".//*[@class='cBody']/descendant::text()",
        "editor": "substring-after(.//*[@class='cInfo'],'编辑：')",
    },
    {
        "title": ".//*/h1/text()",
        "publish_time": "substring-before(substring-after(.//*[@class='span'],'发布时间：'),'|')",
        "source": "substring-before(substring-after(.//*[@class='span'],'来源：'),'|')",
        "author": "substring-before(substring-after(.//*[@class='span'],'作者：'),'|')",
        "belong": "string(.//*[@class='crumbs'])",
        "content": ".//*[@class='center_box']/descendant::text()",
        "editor": "substring-after(.//*[@class='span'],'编辑：')",
    },
]

# 文件位置
FN_OLD_URLS = 'fn_old_urls.txt'

# 正则匹配规则,此处为静态页面url的正则表达式，匹配以下的规则的网址将抓取其中新闻内容
REGEX_URL = r'/\d{4}-\d{2}/\d{2}/\w+_\d+.htm'

# rabbitmq host
HOST = '192.168.2.107'

# 爬虫个数
SPIDERS = 8

# 需要过滤的url后缀
URL_END = ['mp3', 'css', 'mp4']
