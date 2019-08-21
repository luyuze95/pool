# coding: utf-8
"""
Created by chuwt on 18/3/6.
"""
# os

# third

# self
import logging
import os
from logging import DEBUG, INFO
from logging.handlers import TimedRotatingFileHandler

from conf import DEBUG as RUN_ENV

if RUN_ENV:
    level = DEBUG
else:
    level = INFO


def get_logger(name="debug", level=level):
    file_name = os.path.join(os.path.dirname(__file__), name + ".log")

    logger = logging.getLogger(name)

    logger.setLevel(level=level)

    handler = TimedRotatingFileHandler(file_name, when="MIDNIGHT", interval=1,
                                       backupCount=5, )
    formatter = logging.Formatter(
        '%(asctime)s-%(filename)s-%(levelname)s-[%(module)s.%(funcName)s.%(lineno)s]---%(message)s')
    handler.setFormatter(formatter)

    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    # 设置日志格式
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    # 将相应的handler添加在logger对象中
    logger.addHandler(ch)

    logger.addHandler(handler)

    return logger


job_maker_logger = get_logger("job_maker_log")
api_logger = get_logger("api_log")
celery_logger = get_logger("celery_log")
