# coding=utf-8
import pika
import config as setting

queue_list = ['task', 'result', 'continue', 'data']
task_name = ['cac_gov', 'cankaoxiaoxi', 'cctv', 'ce_cn', 'china_net', 'cri_net', 'guangming', 'lwdf', 'youth',
             'china_radio']


def pruge_queue():
    cre = pika.PlainCredentials('bana', 'root')
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=setting.HOST,
        port=5672,
        virtual_host='/',
        credentials=cre
    ))
    channel = connection.channel()
    for eachtask in task_name:
        for eachqueue in queue_list:
            res = channel.queue_purge(
                queue='{}_{}'.format(eachtask, eachqueue)
            )
            print(res.method)


def pruge_one_queue(qname):
    cre = pika.PlainCredentials('bana', 'root')
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=setting.HOST,
        port=5672,
        virtual_host='/',
        credentials=cre
    ))
    channel = connection.channel()
    res = channel.queue_purge(
        queue=qname
    )
    print(res.method)


def delete_queue():
    cre = pika.PlainCredentials('bana', 'root')
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=setting.HOST,
        port=5672,
        virtual_host='/',
        credentials=cre
    ))
    channel = connection.channel()
    for eachtask in task_name:
        for eachqueue in queue_list:
            res = channel.queue_delete(
                queue='{}_{}'.format(eachtask, eachqueue)
            )
            print(res.method)

if __name__ == '__main__':
    pruge_one_queue('china_net_task')
