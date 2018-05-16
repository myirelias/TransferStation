'''配置文件'''
HOST = '192.168.2.90'

# 起始url
START_URL = 'http://piao.qunar.com/'
TOURIS_URL = 'http://piao.qunar.com/ticket/list.htm'
COMMENTS_API = 'http://piao.qunar.com/ticket/detailLight/sightCommentList.json'

# 头信息
HEADERS = {
    'Host': 'piao.qunar.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:52.0) Gecko/20100101 Firefox/52.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate',
    'Referer': 'http://piao.qunar.com/index.htm?region=%E4%B8%89%E4%BA%9A&from=mpshouye_city',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Proxy-Switch-Ip': 'yes'
}

HEADERS_COMMENTS = {
    'Host': 'piao.qunar.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:52.0) Gecko/20100101 Firefox/52.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'http://piao.qunar.com/ticket/detail_2721389637.html?st=a3clM0QlRTYlODglOTAlRTklODMlQkQlMjZpZCUzRDEyNTc5JTI2dHlwZSUzRDAlMjZpZHglM0QxJTI2cXQlM0RyZWdpb24lMjZhcGslM0QyJTI2c2MlM0RXV1clMjZhYnRyYWNlJTNEYndkJTQwJUU2JTlDJUFDJUU1JTlDJUIwJTI2dXIlM0QlRTYlODglOTAlRTklODMlQkQlMjZsciUzRCVFNiU4OCU5MCVFOSU4MyVCRCUyNmZ0JTNEJTdCJTdE',
    'Connection': 'keep-alive',
    'Proxy-Switch-Ip': 'yes'
}


# 请求参数
PARAMS_COMMENTS = {
    'sightId': '12579',
    'index': '2',
    'page': '2',
    'pageSize': '10',
    'tagType': '0',
}
# xpath
XPATH_CITYLIST_A = ".//*[@class='mp-city-list']/descendant::a"
XPATH_TEXT = ".//text()"
XPATH_HREF = ".//@href"
XPATH_TOURIST_A = ".//*/a[@class='name']"
XPATH_TOURIST_DETAIL = {
    "t_name": ".//*[@ class='mp-description-name']/text()",
    "t_type": ".//*[@class='mp-description-level']/text()",
    "t_des": ".//*[@class='mp-description-onesentence']/text()",
    "address": ".//*[@class='mp-description-address']/text()",
    "score": ".//*[@id='mp-description-commentscore']/descendant::text()",
    "price": ".//*[@class='mp-description-price']/descendant::text()",
    "describe": ".//*[@class='mp-charact-desc']/descendant::text()"
}

# file
FILE_CITY_LIST = 'file_city_list.txt'
FILE_TOURIST_LIST = 'file_tourist_list.txt'
FILE_TOURIST_INFO = 'file_tourist_info.txt'
FILE_TOURIST_COMMENTS = 'file_tourist_comments.txt'
FILE_TOURIST_CHECK = 'file_tourist_check.txt'