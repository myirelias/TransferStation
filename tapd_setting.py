# 入口地址
URL = 'https://www.tapd.cn/20175631/prong/stories/stories_list'

# 请求参数
PARAMS = {'conf_id': '1120175631001000270',
          'perpage': '1000',
          'category_id': '0',
          'page': 1}

HEADERS = {'Host': 'www.tapd.cn',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
           'Accept-Encoding': 'gzip, deflate, br',
           'Referer': 'https://www.tapd.cn/20175631/prong/stories/stories_list',
           'Connection': 'keep-alive',
           'Upgrade-Insecure-Requests': '1'}

COOKIES = {'cookie': 'worktable_index_order1000000000000000082sort=%7B%22wangjiawei_70_'
                     '20175631%22%3A%22created%7EDESC%7E20171009%22%7D;'
                     ' worktable_index_order1000000000000000081sort=%7B%2'
                     '2wangjiawei_59_20175631%22%3A%22created%7EDESC%7E20171009%22%7D;'
                     ' selected_workspace_tab70=20175631;'
                     ' worktable_last_visit=story;'
                     ' selected_workspace_tab59=20175631;'
                     ' selected_workspace_tabexpiration_date=20175631; pgv_pvi=5316867072;'
                     ' 2001883701_left_tree_status=open;'
                     ' CAKEPHP=7f5b4be15e8c219072655c971e640c45b5436fb988e7c8124f139fa2d4f4f34a;'
                     ' locale=zh_cn;'
                     ' t_cloud_login=18200120030;'
                     ' t_u=b88645efac96c12e0d0816b7a4f7e2f09103120cd31d3e47a1a6d2a8c030'
                     '4534f8bb37de1996e86e27a9b60d3ba8473f725d42c45208ac592452f7283b7aa5c178754f04fe8ae321%7C1;'
                     ' new_worktable=todo%7C%7C67%7Cexpiration_date'}

# 所有任务链接文件地址
FN_ALL_TASK_LINK = 'all_task_link.txt'

# 所有每天的任务的地址
FN_ALL_TASK_INFO = 'task_cmt2.txt'

XPATHER_DICT = {"title": ".//*[@class='subject_title']//*[@class='editable-value']/text()",
                "title_id": ".//*[@class='title-id']/text()",
                "state": ".//*[@class='c-red2']/text()",
                "taskcontent": ".//*[@class='description_div editor-content']/text()",
                "father": ".//*[@id='ContentParent']//*[@class='editable-value']/text()",  # 父需求
                "priority": ".//*[@id='ContentPriority']//*[@class='editable-value']/text()",  # 优先级
                "taskdealer": ".//*[@id='ContentStatusOwner']//*[@class='editable-value']/text()",  # 处理人
                "start_time": ".//*[@id='ContentEst.Start']//*[@class='editable-value']/text()",
                "end_time": ".//*[@id='ContentEst.End']//*[@class='editable-value']/text()",
                "tasktype": ".//*[@id='ContentCategory']//*[@class='editable-value']/text()", # 需求分类
                "taskowner": ".//*[@id='ContentCreatedBy']//*[@class='editable-value']/text()",
                "createtime": ".//*[@id='ContentCreationTime']//*[@class='editable-value']/text()",
                "finshtime": ".//*[@id='ContentCompletionTime']//*[@class='editable-value']/text()"}

XPATHER_DEALERCONTENTALL = ".//*[@id='comment_area']//*[@class='comment_content']"
XPATHER_DEALERCONTENT = ".//*[@class='rich-comment']//*[@class='field-author']/text()|" \
                ".//*[@class='rich-comment']//*[@class='field-active']/text()|" \
                ".//*[@class='rich-comment']//*[@class='field-time']/text()|" \
                ".//*[@class='rich-comment']//*[@class='editor-content " \
                "comment_con_main comment_type_text']/descendant::text()"