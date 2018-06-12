'''配置文件'''
HOST = '192.168.2.54'

# key
KEY = '****'


# 检索关键字及tag标签
QUERY_DICT = {
    '住宅': {'query': ['住宅', '小区'], 'tag': ['房地产']},
    '学校': {'query': ['幼儿园', '小学', '中学', '初中', '高中', '大学', '学院'], 'tag': ['教育培训']},
    '工厂': {'query': ['工业厂房', '工厂', '厂房', '厂区'], 'tag': ['公司企业']},
    '道路': {'query': ['道路'], 'tag': ['道路', '出入口']},
    '公园': {'query': ['公园'], 'tag': ['旅游景点']}
}

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
FILE_HISTORY_ID = 'bmap_history_id.txt'
FILE_LOG_INFO = 'log.txt'
