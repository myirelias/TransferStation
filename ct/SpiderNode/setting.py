HEADERS = {
    'Host': 'www.cctv.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:52.0) Gecko/20100101 Firefox/52.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate',
    'Cookie': '_CCTV_CURRENT_CITY=101270101; vjuids=-48e1cc2c7.161083c8add.0.a135dbb1a5e55; vjlast='
              '1516261641.1516261641.30; cuid=92a0a648-8136-2fce-dec5-2aaedf64cf00--1516261641039',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0',
    'Proxy-Switch-Ip': 'yes'
}

XPATHLIST = [
    {
        "title": ".//*[@class='cnt_bd']/h1/text()",
        "info": "string( .//*/span[@class='info'])",
        "content": ".//*[@class='cnt_bd']/p/text()"
    },
    {
        "title": ".//*[@class='cnt_nav']/h3/text()",
        "info": ".//*[text()='来源：']/parent::p/descendant::text()",
        "content": ".//*[text()='视频简介：']/parent::p/descendant::text()"

    },
    {
        "title": ".//*[@class='bd']/h1/text()",
        "info": ".//*[@class='date_left_yswp']/text()",
        "content": ".//*[@id='page_body']//*[@class='bd']/p/descendant::text()"
    },
    {
        "title": ".//*[@class='main']/h1/text()",
        "info": ".//*[@class='main']/h4/text()",
        "content": ".//*[@id='page_body']//*[@class='main']/p/text()"
    }

]