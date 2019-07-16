# encoding=utf-8

"""
    @author: anzz
    @date: 2019/5/16
"""
import base64
import json
from concurrent.futures.thread import ThreadPoolExecutor
from time import time, sleep
from queue import Queue

from conf import GBT_TOPIC_BHD, LATEST_BLOCK_MININGINFO, JOB_TOPIC_BHD
from logs import job_maker_logger
from utils.ikafka import consumer, job_producer
from collections import OrderedDict


gbt_msg_queue = OrderedDict()
gbt_height_msgs = {}
thread_pool = ThreadPoolExecutor(max_workers=10)
msg_queue = Queue(maxsize=20)


def main():
    for msg in consumer:
        future = None
        if msg.topic == GBT_TOPIC_BHD:
            future = thread_pool.submit(handler_gbt_msg, msg.value)
        if msg.topic == LATEST_BLOCK_MININGINFO:
            future = thread_pool.submit(send_latest_msg)


def handler_gbt_msg(gbt_msg_str):
    gbt_msg = json.loads(gbt_msg_str)

    created_at_ts = gbt_msg['created_at_ts']
    block_template_base64 = gbt_msg['block_template_base64']

    block_template_str = base64.decodebytes(block_template_base64.encode())

    block_template = json.loads(block_template_str)

    gbt_result = block_template['result']

    baseTarget = gbt_result['baseTarget']
    generationSignature = gbt_result['generationSignature']
    targetDeadline = gbt_result['targetDeadline']
    height = gbt_result['height']

    if height in gbt_height_msgs.keys() and targetDeadline == gbt_height_msgs[height]['targetDeadline']:
        return gbt_height_msgs.get(height)

    if gbt_height_msgs:
        already_latest_height = max(gbt_height_msgs.keys())
    else:
        already_latest_height = height

    if already_latest_height > height:
        return gbt_height_msgs[already_latest_height]

    if len(gbt_height_msgs.keys()) > 20:
        outdated_height = min(gbt_height_msgs.keys())
        del gbt_height_msgs[outdated_height]

    """
        height, version, coinbasevalue, previousblockhash
    """
    stratum_msg = {
        "baseTarget": baseTarget,
        "generationSignature": generationSignature,
        "height": height,
        "job_id": str(time()) + str(height),
        "current_time": time(),
        "targetDeadline": targetDeadline
    }

    job_maker_logger.info("send handle msg ", stratum_msg)
    gbt_height_msgs[height] = stratum_msg
    job_producer.send_json_or_dict(stratum_msg, topic=JOB_TOPIC_BHD)


def send_latest_msg():
    try_num = 0
    while 1:
        if try_num > 30:
            return
        if not gbt_height_msgs:
            sleep(1)
            try_num += 1
            continue
        latest_height = max(gbt_height_msgs.keys())
        stratum_msg = gbt_height_msgs[latest_height]
        job_maker_logger.info("send latest msg ", stratum_msg)
        job_producer.send_json_or_dict(stratum_msg, topic=JOB_TOPIC_BHD)
        break


def run_always():
    while 1:
        try:
            main()
        except Exception:
            run_always()
            import time
            time.sleep(1)
            print("restarting" + "*"*99)


if __name__ == '__main__':
    run_always()
