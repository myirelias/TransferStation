# coding=utf-8

from selenium import webdriver
import time
from crawl import Crawl
from analysis import Analysis
from pipeline import Pipeline
import config as setting
import re
import datetime
import os
from functools import reduce


class EngineSelenium:
    def __init__(self, name):
        self.crawl = Crawl()
        self.analysis = Analysis()
        self.pipe = Pipeline()
        self.options = webdriver.ChromeOptions()
        # 指定下载位置
        prefs = {'profile.default_content_settings.popups': 0, 'download.default_directory': os.path.abspath('DATA')}
        self.options.add_experimental_option('prefs', prefs)
        self.driver = webdriver.Chrome(chrome_options=self.options)
        self.name = str(name.encode('gbk'))[2:-1].replace('\\x', '%').upper()

    def _engine_get_trend(self):
        """
        趋势研究板块数据
        :return:
        """
        # 获取数据对应的标题
        url = 'http://index.baidu.com/?tpl=trend&word={}'.format(self.name)
        self.driver.get(url)
        time.sleep(5)
        # 整体趋势数据
        content_page = self.driver.page_source
        # 获取res 和 res2
        pattern_res = re.compile(r'res=(.*?)&', re.S)
        pattern_res2 = re.compile(r'res2=(.*?)&', re.S)
        res = re.search(pattern_res, content_page).group(1)
        res2 = re.search(pattern_res2, content_page).group(1)
        startdate = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y-%m-%d'),
        enddate = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d'),
        # 构造url用于获取res3参数（res3参数需要去请求才能得到）
        url_res3 = 'http://index.baidu.com/Interface/Search/getAllIndex' \
                   '/?res={}&res2={}&startdate={}&enddate={}'.format(res, res2, startdate, enddate)
        self.driver.get(url_res3)
        time.sleep(2)
        content_res3 = self.driver.page_source
        pattern_res3 = re.compile(r'"userIndexes_enc":"(.*?)",', re.S)
        res3 = re.search(pattern_res3, content_res3).group(1)
        res3_list = res3.split(',')
        timenow = int(time.time() * 1000)
        n = 0
        result = []
        for each_res3 in res3_list:
            trend_pic = {}
            current_date = (datetime.datetime.now() - datetime.timedelta(days=30 - n)).strftime('%Y-%m-%d')
            url_trend_pic = 'http://index.baidu.com/Interface/IndexShow/show/?res={}&res2={}&classType=1&' \
                            'res3[]={}&className=view-value&{}'.format(res, res2, each_res3, timenow)
            self.driver.get(url_trend_pic)
            # 切换到图片所在页面并等待一下
            time.sleep(2)
            content_each_pic = self.driver.page_source
            # 获取对应图片展示的html
            code = re.search(re.compile(r'"code":\[(.*?)\]', re.S), content_each_pic).group(1)
            deal_code = code.replace('\\', '').replace('&quot;', '').replace('&lt;', '<').replace('&gt;', '>')[1:-1]
            # 获取对应图片的下载链接
            url_current_pic = 'http://index.baidu.com' + re.search(re.compile(r'url\("(.*?)"\)', re.S),
                                                                   deal_code).group(1)
            # 访问以下url将会下载图片
            url_img = url_current_pic.replace('amp;', '')
            # 下载图片
            self.driver.get(url_img)
            # 读取下载的图片并用java那边提供的接口识别内容
            pic_code = self.pipe.pipe_pic_rename(filename='下载', newname=current_date)
            # 删除该图片
            # self.pipe.pipe_pic_del(filename='下载')
            # ==============等待处理这张图片
            element_span = self.analysis.analysis_by_xpath(deal_code, xpahter=".//*/span")
            res_pic = []
            for each in element_span:
                pic_info = self.analysis.analysis_by_xpath(each, xpahter=".//@style")

                pic_px = '{},{}'.format(self._engine_tool_regex(pic_info[0]).replace('px', ''),
                                        self._engine_tool_regex(pic_info[1]).replace('px', '').replace('-', ''))
                res_pic.append(pic_px)
                # 给出对应的日期？还有给出url
            trend_pic['px'] = ';'.join(res_pic)
            trend_pic['date'] = current_date
            result.append(trend_pic)
            n += 1
        print(result)

    def _engine_get_demand(self):
        """
        需求图谱板块
        :return:
        """
        url = 'http://index.baidu.com/?tpl=demand&word={}'.format(self.name)
        self.driver.get(url)
        time.sleep(6)
        content_page = self.driver.page_source
        # 需求图谱数据
        element_demand = self.analysis.analysis_by_xpath(content_page,
                                                         xpahter=".//*[@id='demand']//*[contains(@style,"
                                                                 "'text-anchor: middle')and not(contains(@fill,"
                                                                 "'#9a9a9a'))]")
        for each_demand in element_demand:
            text = self.analysis.analysis_by_xpath(each_demand, xpahter='.//descendant::text()')
            value_x = self.analysis.analysis_by_xpath(each_demand, xpahter='.//@x')
            value_y = self.analysis.analysis_by_xpath(each_demand, xpahter='.//@y')
            value_dy = self.analysis.analysis_by_xpath(each_demand, xpahter='.//tspan/@dy')
            if text:
                print('{}_{}_{}_{}'.format(''.join(text), ''.join(value_x), ''.join(value_y), ''.join(value_dy)))

        # 相关词分类数据
        element_tab = self.analysis.analysis_by_xpath(content_page, xpahter=".//*[@id='tablelist']//*[@class='listN1']")
        # 左边框内容(来源相关词)
        for i in range(0, 2):
            th = self.analysis.analysis_by_xpath(element_tab[i], xpahter=".//descendant::th/text()")
            print(''.join(th))
            trs = self.analysis.analysis_by_xpath(element_tab[i], xpahter=".//*[@class='rank']/parent::tr")
            for each_tr in trs:
                rank = self.analysis.analysis_by_xpath(each_tr, xpahter=".//*[@class='rank']/text()")
                words = self.analysis.analysis_by_xpath(each_tr, xpahter=".//*[@class='hotWord']/text()")
                style = self.analysis.analysis_by_xpath(each_tr, xpahter=".//*[@class='psBar']/@style")
                width = re.search(re.compile(r'width:(.*?);', re.S), ''.join(style)).group(1)
                print('{}{}{}'.format(''.join(rank), ''.join(words), ''.join(width)))
        # 右边框内容(搜索指数,上升最快)
        for i in range(2, 4):
            th = self.analysis.analysis_by_xpath(element_tab[i], xpahter=".//descendant::th/text()")
            print(''.join(th))
            trs = self.analysis.analysis_by_xpath(element_tab[i], xpahter=".//*[@class='rank']/parent::tr")
            for each_tr in trs:
                rank = self.analysis.analysis_by_xpath(each_tr, xpahter=".//*[@class='rank']/text()")
                words = self.analysis.analysis_by_xpath(each_tr, xpahter=".//*[@class='hotWord']/text()")
                num = self.analysis.analysis_by_xpath(each_tr, xpahter="string(.//td[last()])")
                print('{}{}{}'.format(''.join(rank), ''.join(words), num.strip()))

    def _engine_get_sentiment(self):
        """
        资讯关注板块数据
        :return:
        """
        url = 'http://index.baidu.com/?tpl=trend&word={}'.format(self.name)
        self.driver.get(url)
        # 新闻资讯监测数据
        time.sleep(2)
        content_page = self.driver.page_source
        # 获取res 和 res2
        pattern_res = re.compile(r'res=(.*?)&', re.S)
        pattern_res2 = re.compile(r'res2=(.*?)&', re.S)
        res = re.search(pattern_res, content_page).group(1)
        res2 = re.search(pattern_res2, content_page).group(1)
        # 用res/res2去请求getPcFeedIndex这个接口，此处res/res2来自需求图谱板块获取的，但是不影响数据结果
        # 资讯指数接口
        api_info = 'http://index.baidu.com/Interface/search/getPcFeedIndex/?res={}&res2={}&type=feed'.format(res, res2)
        # 新闻指数接口
        api_news = 'http://index.baidu.com/Interface/search/getNews/?res={}&res2={}&type=search'.format(res, res2)
        api_dict = {
            '资讯指数': api_info,
            '新闻指数': api_news
        }
        for api_name, api_url in api_dict.items():
            self.driver.get(api_url)
            content_data = self.driver.page_source
            # 请求对应解密码锁需要的唯一id，并且必须在一定时间内(目测在10-20s左右)要完成请求，不然请求回来的解密码就失效了
            uniqid = re.search(re.compile(r'"uniqid":"(.*?)"', re.S), content_data).group(1)
            # 所有的数据在这，为页面上选择全部数据时候的内容，后期可根据需要，选择数量，此数据需要截取
            userindexs = re.search(re.compile(r'"userIndexes":"(.*?)"', re.S), content_data).group(1)
            # 当前数据时间段
            data_date = re.search(re.compile(r'"period":"\d+\|(\d+)"', re.S), content_data).group(1)
            # 当前搜索内容
            name = re.search(re.compile(r'"key":"(.*?)",', re.S), content_data).group(1)
            # 需要拿到uniqid去请求对应解密码，以下是接口
            url_ptbk = 'http://index.baidu.com/Interface/api/ptbk?res={}&res2={}&uniqid={}'.format(res, res2, uniqid)
            self.driver.get(url_ptbk)
            content_pasw = self.driver.page_source
            # 获取返回的解密码
            pasw = re.search(re.compile(r'"data":"(.*?)"', re.S), content_pasw).group(1)
            # 将解密码组合成字典，其中，值为,的key则为本次数据中的隔断
            pasw_key = pasw[0:int(len(pasw) / 2)]
            pasw_value = pasw[int(len(pasw) / 2)::]
            pasw_dict = dict(zip(pasw_key, pasw_value))
            # 数据分割
            for k, v in pasw_dict.items():
                if v == ',':
                    data_list = userindexs.split(k)
                    break
            # 处理数据
            n = 1
            print(api_name)
            for each_data in data_list:
                current_time = (datetime.datetime.strptime(data_date, '%Y%m%d') -
                                datetime.timedelta(days=len(data_list) - n)).strftime('%Y-%m-%d')
                each_value = ''
                for i in each_data:
                    each_value += pasw_dict[i]
                # current_time 为时间 each_value 为对应的搜索数量
                print('{}-{}'.format(current_time, each_value))
                n += 1
            time.sleep(2)

        # 最下面的新闻数据
        url_news = 'http://index.baidu.com/?tpl=sentiment&word={}'.format(self.name)
        self.driver.get(url_news)
        time.sleep(6)
        content_news = self.driver.page_source
        # 直接从页面上取
        element_a = self.analysis.analysis_by_xpath(content_news, xpahter=".//*[starts-with(@class,'stmNews')]"
                                                                          "//*[@class='listN1']//*[starts-with(@class,"
                                                                          "'mhref')]/a")
        # 当前页面展示的新闻链接及标题
        for each_ele in element_a:
            title = self.analysis.analysis_by_xpath(each_ele, xpahter=".//@title")
            href = self.analysis.analysis_by_xpath(each_ele, xpahter=".//@href")
            print('{}{}'.format(''.join(title), ''.join(href)))

    def _engine_get_crowd(self):
        """
        人群画像板块数据
        :return:
        """
        url = 'http://index.baidu.com/?tpl=crowd&word={}'.format(self.name)
        self.driver.get(url)
        time.sleep(6)
        # 地域分布
        for name in ['省份', '城市', '区域']:
            element = self.driver.find_element_by_xpath(".//*[text()='{}']".format(name))
            element.click()
            time.sleep(2)
            content_page = self.driver.page_source
            ele_trs = self.analysis.analysis_by_xpath(content_page,
                                                      xpahter=".//*[@class='tang-scrollpanel-content']//*[starts-with(@class,'items')]/descendant::tr")
            for each_tr in ele_trs:
                rank = self.analysis.analysis_by_xpath(each_tr, xpahter=".//*[@class='scRank']/text()")
                cityname = self.analysis.analysis_by_xpath(each_tr, xpahter=".//*[@class='scName']/text()")
                style = self.analysis.analysis_by_xpath(each_tr, xpahter=".//*[@class='zbar'][1]/@style")
                width = re.search(re.compile(r'width:(.*?);', re.S), ''.join(style)).group(1)
                print('{}{}{}'.format(''.join(rank), ''.join(cityname), ''.join(width)))
        # 人群属性
        content_page = self.driver.page_source
        # 年龄分布
        age_height = self.analysis.analysis_by_xpath(content_page, xpahter=".//*[@id='grp_social_l']//*["
                                                                           "@fill='#3ec7f5']/@height")
        # value = self.analysis.analysis_by_xpath(content_page, xpahter=".//*[@id='grp_social_l']//*[starts-with(@style,"
        #                                                             "'text-anchor: middle')]/descendant::text()")
        # 计算总数
        total = reduce(lambda x, y: float(x) + float(y), age_height)
        # 计算每一个阶段的百分比
        percent = list(map(lambda x: '{:.2f}%'.format((float(x) / total) * 100), age_height))
        # 构造对应数据，这里把每个数据key写为固定的
        age_dict = {
            '19岁及以下': percent[0],
            '20-29岁': percent[1],
            '30-39岁': percent[2],
            '40-49岁': percent[3],
            '50岁及以上': percent[4],
        }
        print(age_dict)
        # 性别分布
        sex_height = self.analysis.analysis_by_xpath(content_page, xpahter=".//*[@id='grp_social_r']//*["
                                                                           "@fill='#3ec7f5']/@height")
        # 计算总数
        total = reduce(lambda x, y: float(x) + float(y), sex_height)
        # 计算每一个阶段的百分比
        percent = list(map(lambda x: '{:.2f}%'.format((float(x) / total) * 100), sex_height))
        # 构造对应数据，这里把每个数据key写为固定的
        sex_dict = {
            '男': percent[0],
            '女': percent[1]
        }
        print(sex_dict)

    def _engine_do_login(self):
        """
        登录处理
        :return:
        """
        login_url = 'http://index.baidu.com/'
        self.driver.get(login_url)
        element = self.driver.find_element_by_xpath(".//*[text()='登录']")
        element.click()
        time.sleep(5)
        element = self.driver.find_element_by_xpath(".//*/input[@name='userName']")
        element.send_keys('daqbigdata')
        time.sleep(3)
        element = self.driver.find_element_by_xpath(".//*/input[@name='password']")
        element.send_keys('daqsoft')
        time.sleep(1)
        element = self.driver.find_element_by_xpath(".//*/input[@type='submit']")
        element.click()
        time.sleep(8)

    @staticmethod
    def _engine_tool_regex(str_data):
        """
        正则取数据
        :return:
        """
        if isinstance(str_data, list):
            deal_data = ''.join(str_data)
        else:
            deal_data = str_data

        try:
            return re.search(re.compile(r':([-]{0,1}\d+px)', re.S), deal_data).group(1)
        except:
            return

    def run_engine(self):
        # 先登录
        self._engine_do_login()
        self._engine_get_trend()
        # self._engine_get_demand()
        # self._engine_get_sentiment()
        # self._engine_get_crowd()
        # 最后关闭浏览器
        self.driver.close()


if __name__ == '__main__':
    start = time.time()
    proc = EngineSelenium(name='王者荣耀')
    proc.run_engine()
    end = time.time()
    print('执行完毕，耗时 {:.2f} s'.format(end - start))
