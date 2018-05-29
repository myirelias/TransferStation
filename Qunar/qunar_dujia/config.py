'''配置文件'''
HOST = '192.168.2.98'

# 起始url
START_URL = 'https://dujia.qunar.com/p/around'
ARROUND_API = 'https://dujia.qunar.com/golfz/routeList'
ARROUND_DETAIL_API = 'https://{}/user/detail/getDetail.json'
SCENIC_API = 'https://{}/user/detail/getTrffcHtlInfo.json'
COMMENTS_API = 'https://{}/user/comment/product/queryComments.json'

# 头信息
HEADERS = {
    'Host': 'dujia.qunar.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:52.0) Gecko/20100101 Firefox/52.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Proxy-Switch-Ip': 'yes'
}

HEADERS_DETAIL = {
    'Host': 'zjsd1.package.qunar.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:52.0) Gecko/20100101 Firefox/52.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Proxy-Switch-Ip': 'yes'
}
HEADERS_COMMENTS = {


}


# 请求参数

PARAMS_ARROUND = {
    'tf': 'dj_aroundnav'
}
# xpath
XPATH_CITY_A = ".//*[@class='tab_select']/descendant::a"
XPATH_CITY_NAME = ".//text()"
XPATH_CITY_URL = './/@href'
XPATH_LI = ".//*[@class='listbox']/descendant::li"
XPATH_DIV = ".//*[@class='listbox']/descendant::a[@class='titlink' and @data-beacon='around_poi']/parent::div/parent::div"
XPATH_SURROUND_NAME = ".//*[@class='cn_tit']/text()"
XPATH_SURROUND_TYPE = ".//a[@class='distance']/text()"
XPATH_SURROUND_URL = ".//a[@class='titlink']/@href"
XPATH_NEXTPAGE = ".//*[@class='b_paging']/a/text()"
XPATH_TID = ".//*[@class='cal-table']//*[@data-date='2018-05-30']/@data-tid"
XPATH_SURROUND_DETAIL = {
    "标题": "string(.//*[@class='summary']/h1)",
    "起步价格": "string(.//*[@class='summary']//*[@class='number'])",
    "产品编号": ".//*[text()='产品编号']/following-sibling::span[1]/text()",
    "行程套餐": "string(.//*[@class='basic-info'])",
    "行程包含": ".//*[@id='ss-costIncludeDesc']//*[@class='common-list word']/descendant::text()",
    "行程不含": ".//*[@id='ss-costExcludeDesc']//*[@class='common-list word']/descendant::text()",
    "线路特色": ".//*[@id='ss-line-feature']//*[contains(@class,'common-list')]/descendant::text()",
    "其他信息": ".//*[@id='ss-other']//*[contains(@class,'common-list')]/descendant::text()",
    "重要提示": ".//*[@id='ss-attention']//*[contains(@class,'common-list')]/descendant::text()",
    "退款说明": ".//*[@id='ss-refund']//*[contains(@class,'common-list')]/descendant::text()",
    "友情提示": ".//*[@id='ss-tip']//*[contains(@class,'common-list')]/descendant::text()",
    "商家资质-供应商": "string(.//*[text()='供应商']/following-sibling::em)",
    "商家资质-联系电话": "string(.//*[text()='联系电话']/following-sibling::em)",
    "商家资质-服务时间": "string(.//*[text()='服务时间']/following-sibling::em)",
    "商家资质-法定代表人": "string(.//*[text()='法定代表人']/following-sibling::em)",
    "商家资质-许可证编号": "string(.//*[text()='许可证编号']/following-sibling::em)",
    "商家资质-经营范围": "string(.//*[text()='经营范围 ']/following-sibling::em)"
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
FILE_SURROUND_LIST = 'file_surround_list.txt'
FILE_SURROUND_INFO = 'file_surround_info.txt'
FILE_SURROUND_COMMENTS = 'file_surround_comments.txt'
FILE_COMMENTS_CHECK = 'file_comments_check.txt'