"""
启动任务
"""

from ControlNode.control_manager import ControlManager
from SpiderNode.spider_schedule import SpiderSchedule
from multiprocessing import Process
import config as setting


if __name__ == '__main__':

    manager = ControlManager()
    # 创建3个进程，分别进行任务发布，结果处理以及数据存储
    proc_task = Process(target=manager.manager_publish_task, args=(setting.START_URL,))  # 此处填写启动url
    proc_result = Process(target=manager.manager_deal_result)
    proc_data = Process(target=manager.manager_save_data)
    proc_task.start()
    proc_result.start()
    proc_data.start()
    spider = SpiderSchedule()
    proc_static = Process(target=spider.schedule_static_spider)
    proc_unstatic = Process(target=spider.schedule_unstatic_spider)
    proc_unstatic.start()
    proc_static.start()