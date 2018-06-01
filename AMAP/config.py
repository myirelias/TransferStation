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
# city=510104&citylimit=true&extensions=all&key=19bb8490a86b16e901a701178d6ed6aa&keywords=&offset=25&page=1&types=120300
PARAMS = {
    'keywords': '',  # 查询关键字
    'types': '120302',  # 查询POI类型
    'city': '',  # 查询城市
    'citylimit': 'true',  # 仅返回指定城市数据
    'offset': 25,  # 每页记录数据
    'page': 1,  # 当前页数
    'extensions': 'all',  # 返回结果控制
    'output': 'xml'  # 千万不能用json，数据是乱的，名称地址无法一一对应，坑
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
FILE_CITY_ID = 'amap_city_id.txt'
FILE_TYPE_ID = 'amap_type_id.txt'
