# encoding=utf-8

"""
    @author: anzz
    @date: 2019/6/25
"""
from time import time
import requests
from conf import *
from decimal import Decimal


class BoomRPCClient(object):

    def __init__(self, url):
        self.url = url
        self.session = self.get_session()

    def get_session(self, pool_connections=10, pool_maxsize=10, max_retries=3):
        session = requests.Session()
        # 创建一个适配器，连接池的数量pool_connections, 最大数量pool_maxsize, 失败重试的次数max_retries
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize, max_retries=max_retries)
        # 告诉requests，http协议和https协议都使用这个适配器
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def withdrawal(self, to_address, amountNQT, deadline=1440, feeNQT=735000):
        amount = Decimal(amountNQT).quantize("0.000000000") * 100000000
        params = {
            "requestType": "sendMoney"
        }
        data = {
            "recipient": to_address,
            "deadline": deadline,
            "feeNQT": feeNQT,
            "amountNQT": amount,
        }
        resp = self.session.post(self.url, params=params, data=data).json()
        return resp

    def get_account_transactions(self, account, firstIndex=0, lastIndex=99):
        params = {
            "requestType": "getAccountTransactions",
            "account": account,
            "firstIndex": firstIndex,
            "lastIndex": lastIndex,
            "_": time()*1000
        }

        resp = self.session.get(self.url, params=params).json()
        return resp


boom_client = BoomRPCClient(BOOM_NODE_URI)

if __name__ == '__main__':
    print(boom_client.get_account_transactions(BOOM_ACCOUNT))


