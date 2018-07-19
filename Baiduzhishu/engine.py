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
import json
import base64


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
        self.realname = name
        self.name = str(name.encode('gbk'))[2:-1].replace('\\x', '%').upper()

    def _engine_get_trend(self):
        """
        趋势研究板块数据
        :return:
        """
        # 获取数据对应的标题
        url = 'http://index.baidu.com/?tpl=trend&word={}'.format(self.name)
        self.driver.get(url)
        # 等待页面跳转
        time.sleep(5)
        content_page = self.driver.page_source
        page_str_date = self.analysis.analysis_by_xpath(content_page,
                                                        xpahter="substring-after(.//*[text()='搜索指数概况']/parent::div//*[@class='compInfo'][2], '至')")
        end_date = page_str_date.strip()
        element_div_all = self.analysis.analysis_by_xpath(content_page, xpahter=setting.XPATH_DIV)
        element_dict = {
            "近7天": element_div_all[0:6],
            "近30天": element_div_all[6::]
        }
        for element_name, element_div in element_dict.items():
            ele_title = element_div[0:3]  # 前3个element为标题
            ele_content = element_div[3:6]  # 后3个element为图片数据
            for i in range(3):
                if i == 0:
                    value_pic = {}
                    title = self.analysis.analysis_by_xpath(ele_title[i], xpahter=setting.XPATH_TITLE)
                    element_pic = self.analysis.analysis_by_xpath(ele_content[i],
                                                                  xpahter=".//span[starts-with(@class, 'ftlwhf')]")
                    # ===========图片操作
                    pic_url = self.analysis.analysis_by_xpath(ele_content[i], xpahter=setting.XPATH_PIC)
                    if pic_url:
                        downurl = ''.join(pic_url)
                        try:
                            url = 'http://index.baidu.com' + re.search(re.compile(r'url\("(.*?)"\)', re.S),
                                                                       downurl).group(1)
                        except:
                            url = ''
                    # 去访问图片的下载链接
                    url_real = url.replace('amp;', '')
                    self.driver.get(url_real)
                    time.sleep(1)
                    # 读取下载的图片并用java那边提供的接口识别内容
                    pic_code = self.pipe.pipe_pic_load(filename='下载')
                    # 删除该图片
                    self.pipe.pipe_pic_del(filename='下载')
                    # ===========图片操作
                    n = 1
                    titles = list(map(lambda x: x.replace(' ', ''), title.split('|')))
                    for each in element_pic:
                        pic_info = self.analysis.analysis_by_xpath(each, xpahter=".//span[@class='imgval']")
                        res_pic = []
                        for each_info in pic_info:
                            imgval = self.analysis.analysis_by_xpath(each_info, xpahter="@style")
                            imgtxt = self.analysis.analysis_by_xpath(each_info, xpahter=".//*[@class='imgtxt']/@style")
                            pic_px = '{},{}'.format(self._engine_tool_regex(imgval), self._engine_tool_regex(imgtxt))
                            res_pic.append(pic_px.replace('px', '').replace('-', ''))
                        value_pic[titles[n - 1]] = ';'.join(res_pic)
                        n += 1
                    # 图片识别完输出数据,此处图片二进制文件进行base64处理
                    for pic_name, pic_px in value_pic.items():
                        data = {'data': base64.b64encode(pic_code), 'num1': pic_px, 'type': 'm'}
                        pic_value = self.crawl.crawl_by_post(url=setting.RECOGNITION_URL, data=data)
                        print(end_date, element_name, pic_name, pic_value)
                        save_data = '{}\u0001{}\u0001{}\u0001{}\u0001{}'.format(self.realname, end_date, element_name,
                                                                                pic_name, pic_value)
                        self.pipe.pipe_txt_save(save_data,
                                                filename=setting.FILE_TREND_ZSGK.format(self.realname, end_date),
                                                savetype='a')
                else:
                    title = self.analysis.analysis_by_xpath(ele_title[i], xpahter=setting.XPATH_TITLE)
                    titles = title.replace(' ', '').split('|')
                    element_pic = self.analysis.analysis_by_xpath(ele_content[i],
                                                                  xpahter=".//span[starts-with(@class, 'ftlwhf')]")
                    pics = []
                    n = 1
                    for each in element_pic:
                        syboml = self.analysis.analysis_by_xpath(each, xpahter=".//*[starts-with(@class,'rat')]/text()")
                        pic_info = list(map(self._engine_tool_regex,
                                            self.analysis.analysis_by_xpath(each, xpahter=".//*/i/@style")))
                        pic_px = list(map(lambda x: int(x.replace('-', '').replace('px', '')), pic_info))
                        pic_value = ''.join(list(map(lambda x: '{:.0f}'.format(x / 8) if x != 80 else '%', pic_px)))
                        value = ''.join(syboml) + pic_value
                        pics.append(value)
                        n += 1
                    # 可以直接输出的数据
                    current_pic = dict(zip(titles, pics))
                    for pic_name, pic_value in current_pic.items():
                        print(end_date, element_name, pic_name, pic_value)
                        save_data = '{}\u0001{}\u0001{}\u0001{}\u0001{}'.format(self.realname, end_date, element_name,
                                                                                pic_name, pic_value)
                        self.pipe.pipe_txt_save(save_data,
                                                filename=setting.FILE_TREND_ZSGK.format(self.realname, end_date),
                                                savetype='a')
        # 搜索指数趋势
        content_page = self.driver.page_source
        # 获取res 和 res2
        pattern_res = re.compile(r'res=(.*?)&', re.S)
        pattern_res2 = re.compile(r'res2=(.*?)&', re.S)
        res = re.search(pattern_res, content_page).group(1)
        res2 = re.search(pattern_res2, content_page).group(1)
        page_str_date = self.analysis.analysis_by_xpath(content_page,
                                                        xpahter="substring-after(.//*[text()='搜索指数趋势']/parent::div//*[@class='compInfo'][2], '至')")
        page_date = datetime.datetime.strptime(page_str_date.strip(), '%Y-%m-%d')
        # 此处调节日期
        startdate = (page_date - datetime.timedelta(days=29)).strftime('%Y-%m-%d')
        enddate = page_date.strftime('%Y-%m-%d')
        # 构造url用于获取res3参数（res3参数需要去请求才能得到）
        url_res3 = 'http://index.baidu.com/Interface/Search/getAllIndex' \
                   '/?res={}&res2={}&startdate={}&enddate={}'.format(res, res2, startdate, enddate)
        self.driver.get(url_res3)
        time.sleep(2)
        content_res3 = self.driver.page_source
        # 返回的数据有整体趋势 pc趋势 移动趋势
        pattern_res3 = re.compile(r'<body>(.*?)</body>', re.S)
        res3 = re.search(pattern_res3, content_res3).group(1)
        # 取3种趋势的对应参数
        res3_dict = json.loads(res3)
        res3_data = res3_dict.get('data')
        if not res3_data:
            print('未能获取搜索指数趋势res3数据')
            return
        # all 整体趋势 pc pc趋势 wise 移动趋势
        try:
            data_dict = {
                '整体趋势': res3_data.get('all')[0].get('userIndexes_enc'),
                'pc趋势': res3_data.get('pc')[0].get('userIndexes_enc'),
                '移动趋势': res3_data.get('wise')[0].get('userIndexes_enc')
            }
        except Exception as e:
            data_dict = {}
            print('获取对应res3数据出错：{}'.format(e))
        for name, current_res3 in data_dict.items():
            res3_list = current_res3.split(',')[::-1]
            timenow = int(time.time() * 1000)
            n = 0
            for each_res3 in res3_list:
                if n >= 7:
                    break
                trend_pic = {}
                # 当前日期
                current_date = (page_date - datetime.timedelta(days=n)).strftime('%Y-%m-%d')
                url_trend_pic = 'http://index.baidu.com/Interface/IndexShow/show/?res={}&res2={}&classType=1&' \
                                'res3[]={}&className=view-value&{}'.format(res, res2, each_res3, timenow)
                self.driver.get(url_trend_pic)
                # 切换到图片所在页面并等待一下
                time.sleep(1)
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
                time.sleep(0.5)
                # 读取下载的图片并用java那边提供的接口识别内容
                pic_code = self.pipe.pipe_pic_load(filename='下载')
                # 图片有可能下载失败, 后期这里可能需要调整
                if not pic_code:
                    return
                # 删除该图片
                self.pipe.pipe_pic_del(filename='下载')
                # ==============等待处理这张图片
                element_span = self.analysis.analysis_by_xpath(deal_code, xpahter=".//*/span")
                res_pic = []
                for each in element_span:
                    pic_info = self.analysis.analysis_by_xpath(each, xpahter=".//@style")
                    pic_px = '{},{}'.format(self._engine_tool_regex(pic_info[0]), self._engine_tool_regex(pic_info[1]))
                    res_pic.append(pic_px.replace('px', '').replace('-', ''))
                    # 给出对应的日期？还有给出url
                trend_pic['date'] = current_date
                trend_pic['name'] = name
                data = {'data': base64.b64encode(pic_code), 'num1': ';'.join(res_pic), 'type': 'm'}
                pic_value = self.crawl.crawl_by_post(url=setting.RECOGNITION_URL, data=data)
                # 数据输出
                print(current_date, name, pic_value)
                save_data = '{}\u0001{}\u0001{}\u0001{}'.format(self.realname, current_date, name, pic_value)
                self.pipe.pipe_txt_save(save_data, filename=setting.FILE_TREND_ZSQS.format(self.realname, enddate),
                                        savetype='a')
                n += 1

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
        page_str_date = self.analysis.analysis_by_xpath(content_page,
                                                        xpahter="substring-after(.//*[text()='需求图谱']/parent::div//*[@class='compInfo'][2], '至')")
        end_date = page_str_date.strip()
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
                save_data = '{}\u0001{}\u0001{}\u0001{}'.format(''.join(text), ''.join(value_x),
                                                                ''.join(value_y), ''.join(value_dy))
                print('{}_{}_{}_{}'.format(''.join(text), ''.join(value_x), ''.join(value_y), ''.join(value_dy)))
                self.pipe.pipe_txt_save(save_data, filename=setting.FILE_DEMAND_XQTP.format(self.realname, end_date),
                                        savetype='a')

        # 相关词分类数据
        element_tab = self.analysis.analysis_by_xpath(content_page, xpahter=".//*[@id='tablelist']//*[@class='listN1']")
        page_str_date = self.analysis.analysis_by_xpath(content_page,
                                                        xpahter="substring-after(.//*[text()='相关词分类']/parent::div//*[@class='compInfo'][2], '至')")
        enddate = page_str_date.strip()
        # 左边框内容(来源相关词)
        for i in range(0, 2):
            th = self.analysis.analysis_by_xpath(element_tab[i], xpahter=".//descendant::th/text()")
            title = ''.join(th)
            trs = self.analysis.analysis_by_xpath(element_tab[i], xpahter=".//*[@class='rank']/parent::tr")
            for each_tr in trs:
                rank = self.analysis.analysis_by_xpath(each_tr, xpahter=".//*[@class='rank']/text()")
                words = self.analysis.analysis_by_xpath(each_tr, xpahter=".//*[@class='hotWord']/text()")
                style = self.analysis.analysis_by_xpath(each_tr, xpahter=".//*[@class='psBar']/@style")
                width = re.search(re.compile(r'width:(.*?);', re.S), ''.join(style)).group(1)
                save_data = '{}\u0001{}\u0001{}\u0001{}'.format(title, ''.join(rank), ''.join(words), width.strip())
                print(save_data)
                self.pipe.pipe_txt_save(save_data, filename=setting.FILE_DEMAND_XGC.format(self.realname, enddate))
        # 右边框内容(搜索指数,上升最快)
        for i in range(2, 4):
            th = self.analysis.analysis_by_xpath(element_tab[i], xpahter=".//descendant::th/text()")
            title = ''.join(th)
            trs = self.analysis.analysis_by_xpath(element_tab[i], xpahter=".//*[@class='rank']/parent::tr")
            for each_tr in trs:
                rank = self.analysis.analysis_by_xpath(each_tr, xpahter=".//*[@class='rank']/text()")
                words = self.analysis.analysis_by_xpath(each_tr, xpahter=".//*[@class='hotWord']/text()")
                num = self.analysis.analysis_by_xpath(each_tr, xpahter="string(.//td[last()])")
                save_data = '{}\u0001{}\u0001{}\u0001{}'.format(title, ''.join(rank), ''.join(words), num.strip())
                print(save_data)
                self.pipe.pipe_txt_save(save_data, filename=setting.FILE_DEMAND_XGC.format(self.realname, enddate))

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
            '媒体指数': api_news
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
                save_data = '{}\u0001{}\u0001{}'.format(api_name, current_time, each_value)
                print(save_data)
                self.pipe.pipe_txt_save(save_data, filename=setting.FILE_SENTIMENT_XWZS.format(self.realname, data_date),
                                        savetype='a')
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
            save_data = '{}\u0001{}'.format(''.join(title), ''.join(href))
            print(save_data)
            self.pipe.pipe_txt_save(save_data, filename=setting.FILE_SENTIMENT_NEWS.format(self.realname, data_date),
                                    savetype='a')

    def _engine_get_crowd(self):
        """
        人群画像板块数据
        :return:
        """
        url = 'http://index.baidu.com/?tpl=crowd&word={}'.format(self.name)
        self.driver.get(url)
        time.sleep(6)
        content_page = self.driver.page_source
        page_str_date = self.analysis.analysis_by_xpath(content_page,
                                                        xpahter="substring-after(.//*[text()='地域分布']/parent::div//*[@class='compInfo'][2], '至')")
        end_date = page_str_date.strip()
        # 地域分布
        for name in ['省份', '城市', '区域']:
            element = self.driver.find_element_by_xpath(".//*[text()='{}']".format(name))
            element.click()
            time.sleep(2)
            content_page = self.driver.page_source
            ele_trs = self.analysis.analysis_by_xpath(content_page,
                                                      xpahter=".//*[@class='tang-scrollpanel-content']//*[starts-with(@class,'items')]/descendant::tr")
            # 区域只有7个，后面的数据为城市的
            if name == '区域':
                ele_trs = ele_trs[0:7]
            for each_tr in ele_trs:
                rank = self.analysis.analysis_by_xpath(each_tr, xpahter=".//*[@class='scRank']/text()")
                cityname = self.analysis.analysis_by_xpath(each_tr, xpahter=".//*[@class='scName']/text()")
                style = self.analysis.analysis_by_xpath(each_tr, xpahter=".//*[@class='zbar'][1]/@style")
                width = re.search(re.compile(r'width:(.*?);', re.S), ''.join(style)).group(1)
                save_data = '{}\u0001{}\u0001{}\u0001{}'.format(end_date, ''.join(rank), ''.join(cityname),
                                                                ''.join(width))
                print(save_data)
                self.pipe.pipe_txt_save(save_data, filename=setting.FILE_CROWD_DYFB.format(self.realname, end_date),
                                        savetype='a')
        # 人群属性
        content_page = self.driver.page_source
        page_str_date = self.analysis.analysis_by_xpath(content_page,
                                                        xpahter="substring-after(.//*[text()='人群属性']/parent::div//*[@class='compInfo'][2], '至')")
        enddate = page_str_date.strip()
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
        save_data = []
        for k, v in age_dict.items():
            save_info = '{}\u0001年龄分布\u0001{}\u0001{}'.format(enddate, k, v)
            save_data.append(save_info)
        for k1, v1 in sex_dict.items():
            save_info = '{}\u0001性别分布\u0001{}\u0001{}'.format(enddate, k1, v1)
            save_data.append(save_info)
        print(save_data)
        self.pipe.pipe_txt_save(save_data, filename=setting.FILE_CROWD_RQSX.format(self.realname, enddate),
                                savetype='a')

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
        self._engine_get_demand()
        self._engine_get_sentiment()
        self._engine_get_crowd()
        # 最后关闭浏览器
        self.driver.close()


if __name__ == '__main__':
    start = time.time()
    proc = EngineSelenium(name='可可托海')
    proc.run_engine()
    end = time.time()
    print('执行完毕，耗时 {:.2f} s'.format(end - start))
