'''配置文件'''
HOST = '192.168.2.54'

# key
KEY = '****'

# 起始url
SEARCH_API = 'http://restapi.amap.com/v3/place/text'
TOURIS_URL = ''
COMMENTS_API = ''

# 头信息
HEADERS = {
    'Proxy-Switch-Ip': 'yes'
}

HEADERS_COMMENTS = {

}


# 请求参数
PARAMS = {
    'keywords': '',  # 查询关键字
    'types': '120302',  # 查询POI类型
    'city': '',  # 查询城市
    'citylimit': 'true',  # 仅返回指定城市数据
    'offset': 20,  # 每页记录数据
    'page': 1,  # 当前页数
    'extensions': 'all',  # 返回结果控制
}
# xpath
XPATH_CITYLIST_A = ".//*[@class='mp-city-list']/descendant::a"
XPATH_TEXT = ".//text()"
XPATH_HREF = ".//@href"
XPATH_TOURIST_A = ".//*/a[@class='name']"
XPATH_TOURIST_DETAIL = {
    '暂无指定字段'
}

# file
FILE_CITY_ID = 'amap_city_id.txt'
FILE_TYPE_ID = 'amap_type_id.txt'
