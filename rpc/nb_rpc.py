# encoding=utf-8

"""
    @author: lyz
    @date: 2019/6/25
"""
import re
from time import time
import requests
from conf import *
from decimal import Decimal


class NBRPCClient(object):

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

    def withdrawal(self, to_address, amountNQT, secret=NEWBI_ACCOUNT_PASSWORD,
                   deadline=1440, feeNQT=735000):
        amount = Decimal(amountNQT).quantize(Decimal("0.000000000")) * 100000000
        params = {
            "requestType": "sendMoney"
        }
        data = {
            "recipient": to_address,
            "deadline": deadline,
            "feeNQT": feeNQT,
            "amountNQT": int(amount),
            "secretPhrase": secret
        }
        resp = self.session.post(self.url, params=params, data=data).json()
        tx_id = resp.get('transaction')
        if not tx_id:
            raise Exception(resp.get("errorDescription"))
        return tx_id

    def get_account_transactions(self, account, firstIndex=0, lastIndex=99):
        params = {
            "requestType": "getAccountTransactions",
            "account": account,
            "firstIndex": firstIndex,
            "lastIndex": lastIndex,
            "_": time() * 1000
        }

        resp = self.session.get(self.url, params=params).json()
        transactions = resp.get('transactions', [])
        return transactions

    def get_balance(self, account=NEWBI_ACCOUNT):

        params = {
            "requestType": "getAccount",
            "account": account,
            "_": time() * 1000,
        }
        resp = self.session.get(self.url, params=params).json()
        unit_balance = Decimal(resp.get("balanceNQT", 0))
        balance = unit_balance/Decimal("100000000")

        return balance

    def block_info(self):
        params = {
            "requestType": "getBlockchainStatus",
            "_": time() * 1000,
        }

        resp = self.session.get(self.url, params=params).json()
        return resp

    def generate_address(self, password=NEWBI_ACCOUNT_PASSWORD):
        params = {
            "requestType": "getAccountId",
            "secretPhrase": password,
            "_": time() * 1000,
        }
        resp = self.session.get(self.url, params=params).json()
        address = resp.get('account')
        accountRS = resp.get('accountRS')
        return address, accountRS

    def get_latest_block_number(self):
        params = {
            "requestType": "getBlockchainStatus",
            "_": time() * 1000,
        }
        resp = self.session.get(self.url, params=params).json()
        block_height = resp.get("numberOfBlocks")
        return block_height

    def get_transaction_detail(self, tx_id):
        params = {
            "requestType": "getTransaction",
            "transaction": tx_id,
            "_": time() * 1000,
        }
        resp = self.session.get(self.url, params=params).json()
        return resp

    @staticmethod
    def check_address(address):
        if len(address) != 26:
            return False
        if not isinstance(address, str):
            return False
        pattern = "NEWBI-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{5}"
        result = re.match(pattern, address)
        return result


nb_client = NBRPCClient(NEWBI_NODE_URI)

if __name__ == '__main__':
    from pprint import pprint

    pprint(nb_client.get_account_transactions(NEWBI_ACCOUNT))
    # pprint(nb_client.block_info())
    # pprint(nb_client.generate_address())
    # pprint(nb_client.get_balance())
    # pprint(nb_client.get_latest_block_number())
    # pprint(nb_client.withdrawal("NEWBI-ZN2F-6V46-LLYH-7WKKF", Decimal('0.01')))
    # pprint(nb_client.get_transaction_detail("2190776444372974349"))
