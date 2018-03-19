# coding=utf-8
import pika
import time


class getbody(object):

    def __init__(self):
        self.url = []

    def con_rabbitmq(self):
        cre = pika.PlainCredentials('bana', 'root')
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='localhost',
            port=5672,
            virtual_host='/',
            credentials=cre
        ))
        channel = connection.channel()
        res = channel.basic_consume(
            self.callback,
            queue='china_net_task_static'
        )

        channel.start_consuming()

    def callback(self, ch, method, properties, body):
        # ch.basic_ack(delivery_tag=method.delivery_tag)
        self.url.append(body)
        print(method)


if __name__ == '__main__':
    proc = getbody()
    proc.con_rabbitmq()