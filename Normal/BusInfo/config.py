'''配置文件'''
HOST = '192.168.2.54'

# 起始url
START_URL = 'http://chengdu.8684.cn/'

DOMAIN_URL = 'http://chengdu.8684.cn{}'
# 头信息
HEADERS = {
    'Host': 'chengdu.8684.cn',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:52.0) Gecko/20100101 Firefox/52.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}


# 请求参数
PARAMS_COMMENTS = {

}
# xpath
XPATH_LIST = ".//*[@class='bus_kt_r1']/a/@href"
XPATH_BUS = ".//*[@class='stie_list']/a/@href"
XPATH_DETAIL = {
    "name": ".//*[@class='bus_i_t1']/h1/text()",
    "time": "substring-after(.//*[contains(text(),'运行时间')],'运行时间：')",
    "ticket": "substring-after(.//*[contains(text(),'票价信息')],'票价信息：')",
    "company": "substring-after(.//*[contains(text(),'公交公司')],'公交公司：')",
    "update": "substring-after(.//*[contains(text(),'最后更新')],'最后更新：')",
    "station": "string(.//*[starts-with(@class,'bus_line_site')][1])"
}
# file
FILE_BUS_LIST = 'file_bus_list.txt'
FILE_BUS_DETAIL = 'file_bus_detail.txt'
