'''配置文件'''
HOST = '192.168.2.98'

# 起始url
START_URL = 'http://travel.qunar.com/place/'
TACTIC_URL = 'http://travel.qunar.com/travelbook/list/22-{}-{}/{}_ctime/'
COMMENTS_API = 'http://travel.qunar.com/travelbook/comments'

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
    'Proxy-Switch-Ip': 'yes'
}

HEADERS_COMMENTS = {
    'Host': 'travel.qunar.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:52.0) Gecko/20100101 Firefox/52.0',
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'http://travel.qunar.com/youji/6341579',
    'Connection': 'keep-alive',
    'Proxy-Switch-Ip': 'yes'
}


# 请求参数

PARAMS_COMMENTS = {

}
# xpath
XPATH_CITY_A = ".//*/div[starts-with(@class,'list')][1]/div[starts-with(@class,'contbox')]/descendant::a"
XPATH_CITY_NAME = ".//text()"
XPATH_CITY_URL = './/@href'
XPATH_ID = ".//*[contains(@class,'b_strategy_list')]//*[@class='tit']/@data-bookid"
XPATH_NEXTPAGE = ".//*[@class='b_paging']/a/text()"
XPATH_TACTIC_DETAIL = {
    "title": ".//*[@id='booktitle' and @class='title']/text()",
    "author": ".//*[@class='e_line2']//*[@class='head']/descendant::text()",
    "create_date": ".//*[@class='e_line2']//*[@class='head']/descendant::text()",
    "start_date": "substring-after(.//*[contains(text(),'出发日期')],'/')",
    "days": "substring-after(.//*[contains(text(),'天数')],'/')",
    "avgs_price": "substring-after(.//*[contains(text(),'人均费用')],'/')",
    "person": "substring-after(.//*[contains(text(),'人物')],'/')",
    "play_type": "substring-after(.//*[contains(text(),'玩法')],'/')",
    "content": ".//*[@class='e_main']/descendant::text()"

}
XPATH_COMMENTS_PAGE = ".//*[@class='b_paging']/a[last()-1]/text()"
XPATH_COMMENTS_LI = ".//*[starts-with(@id,'commentlst_bottom')]"

XPATH_COMMENTS_ASK_CONTENT = "string(.//*[@class='bodystr'])"
XPATH_COMMENTS_ANSWER_CONTENT = "string(.//*[@class='q_box_r_author'])"
XPATH_COMMENTS_ASK_DATE = ".//*[starts-with(@class,'opts_l')]//*[@class='c_time']/text()"
XPATH_COMMENTS_ANSWER_DATE = ".//*[starts-with(@class,'q_box_r_attribute')]//*[@class='c_time']/text()"
# file
FILE_CITY_LIST = 'file_city_list.txt'
FILE_TACTIC_LIST = 'file_tactic_list.txt'
FILE_TACTIC_INFO = 'file_tactic_info.txt'
FILE_TACTIC_COMMENTS = 'file_tactic_comments.txt'
FILE_TACTIC_CHECK = 'file_tactic_check.txt'