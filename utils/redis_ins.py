# encoding=utf-8

"""
    @author: anzz
    @date: 2019/5/30
"""
import redis
from conf import *

pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=CAPACITY_DB,
                            decode_responses=True,
                            password=REDIS_PASSWORD)

redis_capacity = redis.Redis(connection_pool=pool)
