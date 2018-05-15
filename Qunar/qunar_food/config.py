'''配置文件'''
HOST = '192.168.2.54'

# 起始url
START_URL = 'http://travel.qunar.com/place/'
COMMENTS_API = 'http://travel.qunar.com/place/api/html/comments/poi/{}'

# 头信息
HEADERS = {
    'Host': 'travel.qunar.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:52.0) Gecko/20100101 Firefox/52.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate',
    'Referer': 'http://travel.qunar.com/place/?from=header',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Proxy-Switch_Ip': 'yes'
}

HEADERS_COMMENTS = {
    'Host': 'travel.qunar.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:52.0) Gecko/20100101 Firefox/52.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'http://travel.qunar.com/p-oi3213042-quanjudekaoyadian',
    'Connection': 'keep-alive',
    'Proxy-Switch_Ip': 'yes'
}


# 请求参数

PARAMS_COMMENTS = {

}
# xpath
XPATH_CITY_A = ".//*/div[starts-with(@class,'list')][1]/div[starts-with(@class,'contbox')]/descendant::a"
XPATH_CITY_NAME = ".//text()"
XPATH_CITY_URL = './/@href'
XPATH_LI = ".//*[@class='listbox']/descendant::li"
XPATH_RES_NAME = ".//*[@class='cn_tit']/text()"
XPATH_RES_TYPE = ".//*[text()='类　型']/following-sibling::dd/text()"
XPATH_RES_URL = ".//a[@class='titlink']/@href"
XPATH_NEXTPAGE = ".//*[@class='b_paging']/a/text()"
XPATH_RES_DETAIL = {
    "score": ".//*[@class='scorebox clrfix']//*[@class='cur_score']/text()",
    "ranking": "string(.//*[@class='ranking'])",
    "price": "substring-after(.//*[contains(text(),'人均')],'人均：')",
    "describe": ".//*[@class='e_db_content_box']/descendant::text()",
    "address": "string(.//*[contains(text(),'地址:')]/following-sibling::dd)",
    "tel": "string(.//*[contains(text(),'电话:')]/following-sibling::dd)",
    "open_time": "string(.//*[contains(text(),'营业时间:')]/following-sibling::dd)",
    "dish": ".//*/h3[contains(text(),'推荐菜')]/parent::div/following-sibling::div/descendant::text()",
    "arrive": ".//*/h3[contains(text(),'交通指南')]/parent::div/following-sibling::div/descendant::text()",
    "intro": ".//*/h2[contains(text(),'推荐商家')]/parent::div/following-sibling::div/descendant::a[@class='titlink']/@href"
}

XPATH_COMMENTS_PAGE = ".//*[@class='b_paging']/a[last()-1]/text()"
XPATH_COMMENTS_LI = ".//*[@id='comment_box']/li"
XPATH_COMMENTS_TITLE = ".//*[@class='e_comment_title']/descendant::text()"
XPATH_COMMENTS_CONTENT = ".//*[@class='e_comment_content']/descendant::text()"
XPATH_COMMENTS_MORE = ".//*[@class='seeMore']/@href"
XPATH_COMMENTS_DATE = ".//*[@class='e_comment_add_info']/descendant::li[1]/text()"
XPATH_COMMENTS_START = ".//*[starts-with(@class,'cur_star')]/@class"
XPATH_COMMENTS_DETAIL = ".//*[@class='comment_content']/descendant::text()"
XPATH_COMMENTS_NICK = ".//*[@class='e_comment_usr_name']/descendant::text()"
# file
FILE_CITY_LIST = 'file_city_list.txt'
FILE_RESTAURANT_LIST = 'file_restaurant_list.txt'
FILE_RESTAURANT_INFO = 'file_restaurant_info.txt'
FILE_RESTAURANT_COMMENTS = 'file_restaurant_comments.txt'
FILE_COMMENTS_CHECK = 'file_comments_check.txt'