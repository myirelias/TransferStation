'''配置文件'''
HOST = '192.168.2.54'

# 起始url
START_URL = 'https://lvyou.baidu.com/scene/'
TOURIS_API = 'http://lvyou.baidu.com/destination/ajax/jingdian'
EACH_TOURIST_API = 'http://lvyou.baidu.com/{}'
COMMENTS_API = 'https://lvyou.baidu.com/user/ajax/remark/getsceneremarklist'
REFER_URL = 'https://lvyou.baidu.com/{}/remark/?rn=15&pn={}&style=recent'

# 头信息
HEADERS = {
    'Host': 'lvyou.baidu.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:52.0) Gecko/20100101 Firefox/52.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Proxy-Switch-Ip': 'yes'
}

HEADERS_COMMENTS = {
    'Host': 'lvyou.baidu.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:52.0) Gecko/20100101 Firefox/52.0',
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://lvyou.baidu.com/huanglongxi/remark/?rn=15&pn=15&style=hot',
    'Connection': 'keep-alive'
}


# 请求参数
PARAMS_COMMENTS = {

}
# xpath
XPATH_CITYLIST_A = ".//*[starts-with(@class,'china-visit-list') and contains(@data-nslog, 'china-visit')]/descendant::a"
XPATH_TEXT = ".//text()"
XPATH_HREF = ".//@href"
XPATH_TOURIST_A = ""
XPATH_TOURIST_DETAIL = {
    '暂无指定字段'
}

# file
FILE_CITY_LIST = 'file_city_list.txt'  # 城市列表
FILE_TOURIST_LIST = 'file_tourist_list.txt'  # 景区列表
FILE_COMMENTS_INFO = 'file_comments_info.txt'  # 评论信息，包括最新评论时间，评论总数，景区id,景区name等
FILE_COMMENTS_LIST = 'file_comments_list.txt'  # 所有评论内容