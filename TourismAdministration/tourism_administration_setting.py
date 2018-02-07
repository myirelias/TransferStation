# 请求头
HEADERS = {
    'Host': 'www.cnta.gov.cn',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:52.0) Gecko/20100101 Firefox/52.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate',

    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0',
    'Switch-Proxy-Ip': 'yes'
}


# xpath规则
XPATHER_START_HREF = ".//*[@class='more']/@href"
XPATHER_NEXT = ".//*[text()='下一页']/@href"
XPATHER_EACH_URLS = ".//*[@class='lie_main_m']/descendant::a/@href"
XPATHER_SZ_URLS = ".//*/a/@href"
XPATHER_DETAIL = [
    {
        "title": ".//*[@class='tpbfmain']/h2/text()",
        "publish_date": "substring-before(.//*[@class='main_t'], '来源')",
        "source": "substring-before(substring-after(.//*[@class='main_t'], '来源：'), '[')",
        "position": "string(.//*[@class='main_local marl30'])",
        "content": ".//*[@class='TRS_Editor']/descendant::text()",
        "img": ".//*[@class='TRS_Editor']/descendant::img/@src",
        "editor": "substring-before(substring-after(.//*[contains(text(),'责任编辑')], '责任编辑：'),')')"
    },
    {
        "title": ".//*/h1/text()",
        "publish_date": "substring-before(.//*[@class='pages-date'], '来源：')",
        "source": "substring-before(substring-after(.//*[@class='pages-date'], '来源：'),'【')",
        "position": "string(.//*[@class='BreadcrumbNav'])",
        "content": ".//*[@class='pages_content']/descendant::text()",
        "img": ".//*[@class='pages_content']/descendant::img/@src",
        "editor": "substring-after(.//*[contains(text(),'责任编辑')],'责任编辑：')"
    },
    {
        "title": ".//*[contains(text(),'标　　题：')]/parent::td/following-sibling::td/text()",
        "publish_date": ".//*[contains(text(),'发布日期：')]/parent::td/following-sibling::td/text()",
        "source": ".//*[contains(text(),'发文机关：')]/parent::td/following-sibling::td[1]/text()",
        "position": "string(.//*[@class='BreadcrumbNav'])",
        "content": ".//*/td[@id='UCAP-CONTENT']/descendant::text()",
        "img": "",
        "editor": ""
    }
]
# urls
URLS = {
    '焦点新闻': 'http://www.cnta.gov.cn/xxfb/jdxwnew2/index.shtml',
    '时政新闻': 'http://www.cnta.gov.cn/xxfb/szxw/index.shtml',
    '地方新闻': 'http://www.cnta.gov.cn/xxfb/xxfb_dfxw/index.shtml',
    '每日更新': 'http://www.cnta.gov.cn/xxfb/mrgx/index.shtml',
    '聚焦港澳台': 'http://www.cnta.gov.cn/xxfb/jjgat/index.shtml',
    '新闻联播': 'http://www.cnta.gov.cn/xxfb/xwlb/index.shtml',
    '行业动态': 'http://www.cnta.gov.cn/xxfb/hydt/index.shtml',
    '文献资料': 'http://www.cnta.gov.cn/xxfb/wxzl/index.shtml',
    '教育培训': 'http://www.cnta.gov.cn/xxfb/jzpx/index.shtml'
}

# 文件名
FILE_OLD_NEWS = r'DATA/file_old_news.txt'




