'''配置文件'''
HOST = '192.168.2.54'

# 起始url
START_URL = ''
RECOGNITION_URL = 'http://192.168.0.51:8080/recognition'

# 头信息
HEADERS = {
    'Host': 'index.baidu.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:52.0) Gecko/20100101 Firefox/52.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate',
    'Referer': 'http://index.baidu.com/?tpl=trend&word=%E8%B6%B3%E7%90%83',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cookie': 'BAIDUID=B9FEB50754E1B11AFAF48F5FA76D79EA:FG=1; Hm_lvt_d101ea4d2a5c67dab98251f0b5de24dc=1530522434; FP_UID=96256d124334b118806edfe8e6c77911; BDUSS=lxNDJnbzdGdjlZVkcxQX5jLWlnZUJNWDBSakp2c0dURUJTQmtoUndrQjVlR0ZiQVFBQUFBJCQAAAAAAAAAAAEAAADosPnMZGFxYmlnZGF0YQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHnrOVt56zlbLU; CHKFORREG=a583f1be934da65aca2ca3f0618e1d91; bdshare_firstime=1530522459281; Hm_lpvt_d101ea4d2a5c67dab98251f0b5de24dc=1530522546'
}




# 请求参数
PARAMS = {

}
# xpath

XPATH_ = ".//*[@class='tabCont gColor1 dsn']//*[@class='lrRadius']/span"
XPATH_TR = ".//*[@class='tabCont gColor1 dsn']/descendant::tr"  # 两行图片所在的表
XPATH_DIV = ".//*[@class='lrRadius']"
XPATH_TITLE = "string(.//*[@class='lrRc'])"
XPATH_DATE = "string(.//*[contains(text(),'搜索指数概况')]/parent::div)"
XPATH_PIC = ".//span[starts-with(@class, 'ftlwhf')]//style/text()"
# .//*[@class='tabCont gColor1 dsn']/descendant::tr//*[@class='lrRadius']//span[starts-with(@class, 'ftlwhf')]//style/text()

# file
FILE_TREND_ZSGK = 'file_trend_zsgk_{}_{}.txt'  # 指数概况
FILE_TREND_ZSQS = 'file_trend_zsqs_{}_{}.txt'  # 指数趋势
FILE_DEMAND_XQTP = 'file_demand_xqtp_{}_{}.txt'  # 需求图谱
FILE_DEMAND_XGC = 'file_demand_xgc_{}_{}.txt'  # 相关词
FILE_SENTIMENT_XWZS = 'file_sentiment_xwzs_{}_{}.txt'  # 新闻资讯监测
FILE_SENTIMENT_NEWS = 'file_sentiment_news_{}_{}.txt'  # 新闻
FILE_CROWD_DYFB = 'file_crowd_dyfb_{}_{}.txt'  # 地域分布
FILE_CROWD_RQSX = 'file_crowd_rqsx_{}_{}.txt'  # 人群属性
