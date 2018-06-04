'''配置文件'''
HOST = '192.168.2.54'

# key
KEY = '****'

# 起始url
SEARCH_API = 'http://api.map.baidu.com/place/v2/search'
TOURIS_URL = ''
COMMENTS_API = ''

# 头信息
HEADERS = {
    'Proxy-Switch-Ip': 'yes'
}

HEADERS_COMMENTS = {

}

# 请求参数
# query=小区&tag=房地产&region=75&city_limit=true&output=json&scope=2&page_size=20&page_num=0&ak=
PARAMS = {
    'query': '小区',  # 检索关键字
    'tag': '',  # poi分类
    'region': '75',  # 检索行政区域， citycode
    'city_limit': 'true',  # 区域数据召回限制
    'output': 'json',  # 输出个事为json或xml
    'scope': '2',  # 1或空为基本信息, 2为poi详细信息
    'page_size': '20',  # 单次召回POI数量，默认为10，最大为20
    'page_num': '0',  # 分页页码， 默认为0，代表第1页，依次类推
    'ak': '',  # key
}


# xpath
XPATH_POIS = ".//*/pois[@type='list']/poi"
XPATH_DETAIL = {
    "id": ".//id/text()",
    "name": ".//name/text()",
    "pcode": ".//pcode/text()",
    "pname": ".//pname/text()",
    "citycode": ".//citycode/text()",
    "cityname": ".//cityname/text()",
    "adcode": ".//adcode/text()",
    "adname": ".//adname/text()",
    "address": ".//address/text()",
    "alias": ".//alias/text()",
    "biz_ext": ".//biz_ext/text()",
    "biz_type": ".//biz_type/text()",
    "business_area": ".//business_area/text()",
    "discount_num": ".//discount_num/text()",
    "email": ".//email/text()",
    "entr_location": ".//entr_location/text()",
    "exit_location": ".//exit_location/text()",
    "gridcode": ".//gridcode/text()",
    "groupbuy_num": ".//groupbuy_num/text()",
    "indoor_data": ".//indoor_data/text()",
    "indoor_map": ".//indoor_map/text()",
    "location": ".//location/text()",
    "navi_poiid": ".//navi_poiid/text()",
    "postcode": ".//postcode/text()",
    "tag": ".//tag/text()",
    "tel": ".//tel/text()",
    "type": ".//type/text()",
    "typecode": ".//typecode/text()",
    "website": ".//website/text()"
}
XPATH_PHOTOS = ".//photo"
XPATH_PHOTO_DETAIL = {
    "title": ".//title/text()",
    "url": ".//url/text()"
}

# file
FILE_TYPE_NAME = 'bmap_type_name.txt'
FILE_CITY_ID = 'bmap_city_id.txt'
