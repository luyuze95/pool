# encoding=utf-8

"""
    @author: anzz
    @date: 2019/8/4
"""

from functools import wraps

from utils.redis_ins import redis_lock


def distributed_lock(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        res = redis_lock.setnx(func_name, 1)
        if res is False:
            return
        try:
            redis_lock.expire(func_name, 360)
            return func(*args, **kwargs)
        finally:
            redis_lock.delete(func_name)
    return wrapper


@distributed_lock
def test():
    return 1


if __name__ == '__main__':
    test()
