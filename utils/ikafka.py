# encoding=utf-8

"""
    @author: anzz
    @date: 2019/5/16
"""
import json
import threading

from kafka import KafkaConsumer
from kafka import KafkaProducer
from kafka.errors import KafkaError, KafkaTimeoutError

from logs import job_maker_logger
from conf import KAFKA_HOST, GBT_TOPIC_BHD, JOB_TOPIC_BHD, \
    LATEST_BLOCK_MININGINFO


class KafkaClient(object):
    def __init__(self, host=KAFKA_HOST):
        self.host = host
        self.lock = threading.Lock()

    def __get__(self, instance, owner):
        if hasattr(self, "client"):
            return self.client
        self.lock.acquire()
        try:
            if not hasattr(self, "client"):
                self.client = KafkaProducer(bootstrap_servers=self.host)
        except Exception as e:
            job_maker_logger.error("kafka producer get wrong :%s" % e)
        finally:
            self.lock.release()
        return self.client


class MyKafkaProducer(object):
    client = KafkaClient()

    def __init__(self, topic):
        self.topic = topic

    def send_json_or_dict(self, params, topic=None):
        print("kafka product", params)
        if not topic:
            topic = self.topic
        try:
            if isinstance(params, dict):
                params = json.dumps(params)
            self.client.send(topic, params.encode('utf-8'))
            self.client.flush()
        except KafkaTimeoutError and KafkaError as e:
            job_maker_logger.warning("kafka send time out :%s" % e)
        except Exception as e:
            job_maker_logger.warning("kafka send error :%s" % e)
        job_maker_logger.info("kafka send %s: %s" % (topic, params))


consumer = KafkaConsumer(GBT_TOPIC_BHD, LATEST_BLOCK_MININGINFO, bootstrap_servers=KAFKA_HOST)

job_producer = MyKafkaProducer(JOB_TOPIC_BHD)


if __name__ == '__main__':
    test_topic = MyKafkaProducer('test_topic')
    test_topic.send_json_or_dict("test_msg")
