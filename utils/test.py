# encoding=utf-8

"""
    @author: anzz
    @date: 2019/5/18
"""
import time
from concurrent.futures.thread import ThreadPoolExecutor


pool = ThreadPoolExecutor(max_workers=10)


def test(nu):
    print(nu)
    return nu


def execute_pool():
    for i in range(10):
        future = pool.submit(test, i)
        while 1:
            if future.done():
                print(future.result())
                return future.result()
            time.sleep(0.5)


if __name__ == '__main__':
    execute_pool()
