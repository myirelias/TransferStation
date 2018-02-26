# 入口地址
URL = 'https://www.tapd.cn/company/participant_projects'

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
           'Upgrade-Insecure-Requests': '1',
          'Cookie': 'pgv_pvi=281752576; locale=zh_cn; new_worktable=todo%7C20175631%7Ctodo_all%7Cnormal_list; left_tree_status=1; 2003421881_left_tree_status=open; CAKEPHP=7d3303346f46e39b28686f3a7ce0490a8520acc23305a36065d30da46ad9df44; pgv_si=s3241845760; t_u=efddc1b7d5e578b45180957d09c8ce449103120cd31d3e4720806c5f8047b879bd838778eef9b3b915a0292779d38c6a8b419f0a38926bcb8f57eef70da40f2f7e60783763008737%7C1; t_cloud_login=xieyj%40daqsoft.com.cn'}

COOKIES = {'Cookie': 'pgv_pvi=281752576; locale=zh_cn; new_worktable=todo%7C20175631%7Ctodo_all%7Cnormal_list; left_tree_status=1; 2003421881_left_tree_status=open; CAKEPHP=7d3303346f46e39b28686f3a7ce0490a8520acc23305a36065d30da46ad9df44; pgv_si=s3241845760; t_u=efddc1b7d5e578b45180957d09c8ce449103120cd31d3e4720806c5f8047b879bd838778eef9b3b915a0292779d38c6a8b419f0a38926bcb8f57eef70da40f2f7e60783763008737%7C1; t_cloud_login=xieyj%40daqsoft.com.cn'}

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

CN_NAME = {'gaopeng': '高鹏',
                   'xieh': '谢浩',
                   'xieyangjie': '谢洋杰',
                   'wangjiawei': '王家葳',
                   'huangzj': '黄志江',
                   'wangxy': '王学艳',
                   'zhangl': '张力',
                   'humw': '胡明伟',
                   '龙超国': '龙超国',
                   '黄欣凯': '黄欣凯',
                   '古鹏飞': '古鹏飞',
                   '郑小乐': '郑小乐',
                   '杨森': '杨森',
                    '刘敏':'刘敏'}