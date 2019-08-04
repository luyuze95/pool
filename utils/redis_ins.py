# encoding=utf-8

"""
    @author: anzz
    @date: 2019/5/30
"""
import redis

from conf import *

pool_capacity = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT,
                                     db=CAPACITY_DB,
                                     decode_responses=True,
                                     password=REDIS_PASSWORD)

pool_auth = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=AUTH_DB,
                                 decode_responses=True,
                                 password=REDIS_PASSWORD)

pool_lock = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=LOCK_DB,
                                 decode_responses=True,
                                 password=REDIS_PASSWORD)

redis_capacity = redis.Redis(connection_pool=pool_capacity)
redis_auth = redis.Redis(connection_pool=pool_auth)
redis_lock = redis.Redis(connection_pool=pool_lock)
