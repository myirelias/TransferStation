# !/usr/bin/env python
# coding=UTF-8

import os

try:
    from pymongo import MongoClient
except:
    import pymongo
import pickle
import pika


class Pipe(object):
    """
    功能类，主要负责对数据的输出与输入，尽量不在该类的方法中进行逻辑运算
    function _makedir: 创建DATA文件夹，用于存储数据
    function pipe_save_txt/pipe_read_txt: 与txt文件进行输入/输出操作
    function pipe_save_db/pipe_raad_db: 与mongodb数据库之间进行输入/输出操作
    function pipe_dump_pickle/pipe_load_pickle: 数据的持久化操作
    function pipe_push_rabbitmqa: 向rabbitmq中推送数据
    function pipe_pullmore_rabbitmq/pipe_pullone_rabbitmq:从rabbitmq中取出消息
    """

    def __init__(self):
        self.files = os.path.join(os.path.abspath('DATA'), '%s')
        self._makedir()
        self.client = MongoClient(host='192.168.2.75', port=27017, connect=False)

    @staticmethod
    def _makedir():  # 当前脚本所在位置若没有DATA文件夹则创建，脚本获取到的数据默认放在该文件夹里
        if not os.path.exists('DATA'):
            os.makedirs('DATA')

    def pipe_save_txt(self, data, filename, savetype='w'):
        """
        储存数据到txt文本,data格式必须为list或str
        :param data: 存储内容
        :param filename: 存储文件名
        :param savetype: 存储类型，默认为 w 重写
        :return: data类型错误返回fail
        """

        with open(self.files % filename, savetype, encoding='UTF-8') as f:
            if isinstance(data, list):
                for eachdata in data:
                    f.write(eachdata + '\n')
            elif isinstance(data, str):
                f.write(data + '\n')
            else:
                return 'fail'

    def pipe_read_txt(self, filename, readtype='r'):
        """
        读取txt中的内容并返回
        :param filename: 读取文件名
        :param readtype: 读取方式，默认为 r
        :return: 文件内容的生成器
        """

        return (eachdata for eachdata in open(self.files % filename, readtype, encoding='UTF-8'))

    def pipe_save_db(self, data, dbname, colname):
        """
        存储内容到mongodb
        :param data: 存储内容，必须为dict或dict组成的list
        :param dbname: 数据库名称
        :param colname: 集合名
        :return: 存储失败则返回 fail
        """

        db = self.client[dbname]
        col = db[colname]
        if isinstance(data, list):
            col.insert_many(data)
        elif isinstance(data, dict):
            col.insert(data)
        else:
            return 'save fail: data must be list or dict'

        return 'save succeed'

    def pipe_read_db(self, dbname, colname):
        """
        读取mongodb中的数据
        :param dbname: 数据库名称
        :param colname: 集合名称
        :return: mongodb的游标，可遍历
        """
        db = self.client[dbname]
        col = db[colname]
        res = col.find({}, {'_id': 0}, no_cursor_timeout=True)  # 默认返回该集合所有数据，并且游标cursor设置不超时

        return res

    def pipe_load_pickle(self, filename):
        """
        从指定文件中加载已持久化的内容到内存中
        :param filename: 指定文件名称
        :return: 文件中持久化的内容
        """
        with open(self.files % filename, 'rb') as f:
            data = pickle.load(f)

        return data

    def pipe_dump_pickle(self, savedata, filename):
        """
        将内存中的数据持久化到指定文件中
        :param savedata: 需要持久化的内容
        :param filename: 指定文件名称
        :return:
        """
        with open(self.files % filename, 'wb') as f:
            pickle.dump(savedata, f)

    @staticmethod
    def pipe_push_rabbitmq(data, **kw):
        """
        将消息任务发布到rabbitmq中去
        配置参数：
            user:账号 psw：密码 host:ip地址 port:端口号 vhost:虚拟环境
            qname:队列名称 durable：消息队列是否持久化
        :param data: 需要发布的消息任务，目前要求传入list类型的消息任务列表
        :param kw: 配置参数
        :return:
        """
        if not isinstance(data, list):
            print('data must be list')
            return

        # 账号密码
        cre = pika.PlainCredentials(kw.get('user', 'bana'), kw.get('psw', 'root'))
        # 创建rabbitmq连接
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=kw.get('host', '192.168.2.75'),
            port=kw.get('port', 5672),
            virtual_host=kw.get('vhost', '/'),
            credentials=cre
        ))
        # 创建消息通道
        channel = connection.channel()
        # 声明消息队列
        queue = channel.queue_declare(
            queue=kw.get('qname', 'default'),
            durable=kw.get('durable', True)
        )
        for each in data:
            # 发布消息
            channel.basic_publish(
                exchange='',
                routing_key=kw.get('qname', ''),
                body=each,
                properties=pika.BasicProperties(
                    delivery_mode=2  # 消息持久化
                )
            )
        # 关闭连接
        connection.close()

    def pipe_pullmore_rabbitmq(self, **kw):
        """
        从消息队列获取内容
        配置参数：
            user:账号 psw：密码 host:ip地址 port:端口号 vhost:虚拟环境
            qname:队列名称 durable：消息队列是否持久化
        :param kw: 配置参数
        :return: 消息队列里面的内容
        """
        # 登录信息
        cre = pika.PlainCredentials(kw.get('user', 'bana'), kw.get('psw', 'root'))
        # 创建rabbitmq连接
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=kw.get('host', '192.168.2.75'),
            port=kw.get('port', 5672),
            virtual_host=kw.get('vhost', '/'),
            credentials=cre
        ))
        # 建立channel消息通道
        channel = connection.channel()
        # 声明消息队列
        channel.queue_declare(
            queue=kw.get('qname', 'default'),
            durable=kw.get('durable', True)
        )
        # 设置分配模式：同一时间只取一个任务
        channel.basic_qos(prefetch_count=1)
        # 使用callback函数接受信息
        channel.basic_consume(
            self._pipe_rabbimq_callback,
            queue=kw.get('qname', 'default')
        )
        # 开始接受任务
        channel.start_consuming()

    @staticmethod
    def _pipe_rabbimq_callback(ch, method, properties, body):
        """
        rabbitmq回调函数
        :param ch:
        :param method:
        :param properties:
        :param body:
        :return:
        """
        print('取值%s' % body)
        # ack响应
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def pipe_pullone_rabbitmq(self, **kw):
        """
        从消息队列获取内容--返回一条数据
        配置参数：
            user:账号 psw：密码 host:ip地址 port:端口号 vhost:虚拟环境
            qname:队列名称 durable：消息队列是否持久化
        :param kw: 配置参数
        :return: 消息队列里面的内容
        """
        # 登录信息
        cre = pika.PlainCredentials(kw.get('user', 'bana'), kw.get('psw', 'root'))
        # 创建rabbitmq连接
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=kw.get('host', '192.168.2.75'),
            port=kw.get('port', 5672),
            virtual_host=kw.get('vhost', '/'),
            credentials=cre
        ))
        # 建立channel消息通道
        channel = connection.channel()
        # 声明消息队列
        channel.queue_declare(
            queue=kw.get('qname', 'default'),
            durable=kw.get('durable', True)
        )
        # 从队列中取出一个任务
        method, headers, body = channel.basic_get(
            queue=kw.get('qname', 'default')
        )
        if method.NAME == 'Basic.GetEmpty':
            connection.close()
            return None
        else:
            channel.basic_ack(delivery_tag=method.delivery_tag)
            connection.close()
            return body

