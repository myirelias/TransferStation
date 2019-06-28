# coding=utf-8

"""
加入显示等待页面加载
加入选择爬取第几页的功能
入库前进行去重判断
"""

import os
os.chdir(os.path.split(os.path.realpath(__file__))[0])
from selenium import webdriver
import time
from analysis import Analysis
from pipeline import Pipeline
import config as setting
import datetime
from selenium.webdriver.support.ui import WebDriverWait as w_wait


'''进口药品'''

DBNAME='db_zself'
COLNAME='col_sfda_import_new'
CHECK_NAME = '注册证号'
API = 'http://app1.sfda.gov.cn/datasearch/face3/base.jsp?tableId=36&tableName=TABLE36&title=%BD%F8%BF%DA%D2%A9%C6%B7&bcId=124356651564146415214424405468'


class SfdaSelenium:
    def __init__(self):
        self.analysis = Analysis()
        self.pipe = Pipeline()
        self.driver = webdriver.Firefox(executable_path=r'D:\banana\Part-y\SFDA批文\sfda\geckodriver-v0.16.0-win64\geckodriver.exe')

    def _engine_req_data(self):
        """
        数据请求
        :return:
        """
        self.driver.get(API)
        time.sleep(2)
        choice_page = input('输出起始页码:')
        self.driver.find_element_by_id("goInt").clear()
        self.driver.find_element_by_id("goInt").send_keys(f"{choice_page}")
        time.sleep(1)
        self.driver.find_element_by_xpath(".//*[@src='images/dataanniu_11.gif']").click()
        time.sleep(1.5)
        # --------------不跳转页面之前必须经过以下步骤才能正确抓取
        w_wait(self.driver, 60).until(# .//*[@id='content']/div/table[2]/descendant::a[1]
            lambda x: x.find_element_by_xpath(".//*[@id='content']/table[2]/tbody/tr[1]/td/p/a"))
        self.driver.find_element_by_xpath(".//*[@id='content']/table[2]/tbody/tr[1]/td/p/a").click()
        w_wait(self.driver, 60).until(
            lambda x: x.find_element_by_xpath(".//*[@src='images/search_back.gif']"))
        time.sleep(1.5)
        self.driver.find_element_by_xpath(".//*[@src='images/search_back.gif']").click()
        # --------------不跳转页面之前必须经过以下步骤才能正确抓取（原因：第一次请求之后跟继续返回的xpath页面内容有差异）
        page = int(choice_page)
        while 1:
            per_count = list(filter(lambda x: x if x % 2 == 1 else False, [i for i in range(1, 30)]))
            print(f'[{datetime.datetime.now().strftime("%Y%m%d %H:%M:%S")}]当前页{page}')
            for n in per_count:
                # 显示等待
                w_wait(self.driver, 60).until(
                    lambda x: x.find_element_by_xpath(f".//*[@id='content']/table[2]/tbody/tr[{n}]/td/p/a"))
                self.driver.find_element_by_xpath(f".//*[@id='content']/table[2]/tbody/tr[{n}]/td/p/a").click()
                time.sleep(2)
                # 取值
                content = self.driver.page_source
                td_name = self.analysis.analysis_by_xpath(content=content, xpahter=".//*[@class='listmain']/descendant::tr//td[@width='17%']/descendant::text()")
                xpather_dict = {}
                for each_name in td_name:
                    if each_name:
                        xpather_each = f"normalize-space(.//*[@class='listmain']//*[contains(text(),'{each_name}')]/following-sibling::td)"
                        xpather_dict[each_name] = xpather_each
                res_dict = self.analysis.analysis_by_xpath(content=content, xpahter=xpather_dict)
                current_name = res_dict.get(CHECK_NAME)
                check = self.pipe.pipe_mongo_load(dbname=DBNAME, colname=COLNAME, value=f"{{'{CHECK_NAME}':'{current_name}'}}")
                if not check and res_dict.get('注册证号'):
                    self.pipe.pipe_mongo_save(res_dict, dbname=DBNAME, colname=COLNAME)
                w_wait(self.driver, 60).until(lambda x: x.find_element_by_xpath(".//*[@src='images/search_back.gif']"))
                self.driver.find_element_by_xpath(".//*[@src='images/search_back.gif']").click()
                time.sleep(2)
            try:
                w_wait(self.driver, 60).until(lambda x: x.find_element_by_xpath(".//*[@src='images/dataanniu_07.gif' and contains(@onclick,'javascript:devPage')]"))
                next_page = self.driver.find_element_by_xpath(".//*[@src='images/dataanniu_07.gif' and contains(@onclick,'javascript:devPage')]")
            except:
                next_page = None
            if next_page:
                next_page.click()
            else:
                break
            time.sleep(2)
            page += 1
        self.driver.quit()

    def run_engine(self):
        self._engine_req_data()


if __name__ == '__main__':
    start = time.time()
    proc = SfdaSelenium()
    proc.run_engine()
    del proc
    end = time.time()
    print('[{}]本轮抓取完毕，耗时 {:.2f} s'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), end - start))
