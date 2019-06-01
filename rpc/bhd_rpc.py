# encoding=utf-8

"""
    @author: anzz
    @date: 2019/5/29
"""
import time
from threading import Thread

from rpc.authproxy import AuthServiceProxy
from conf import *


class BhdRpcClient(object):
    def __init__(self, url, password=None):
        self.url = url
        self.client = AuthServiceProxy(service_url=self.url, timeout=30)
        self.password = password
        heat = Thread(target=self.heartbeat)
        heat.setDaemon(True)
        heat.start()

    def heartbeat(self):
        while 1:
            self.block_info()
            time.sleep(10)

    def block_info(self, block_number=None):
        return self.client.getblockchaininfo()

    def get_balance(self, address=None,):
        if address:
            return self.client.getbalance(address)
        return self.client.getbalance()

    def generate_address(self, username):
        self.unlock_account()
        resp = self.client.dumpprivkeys(username, username + 1)
        address = resp['keys'][0]['address']
        priv_key = resp['keys'][0]['privkey']
        return address, priv_key

    def get_transactions(self, count=5, skip=0):
        return self.client.listtransactions('*', count, skip)[::-1]

    def withdrawal(self, to_address, amount, from_address=None):
        self.unlock_account()
        if not self.check_address(to_address):
            raise Exception("bhd withdraw exception, invalid address %s"
                            % to_address)

        if self.get_balance() < amount:
            raise Exception("bhd withdraw exception, money not enough, "
                            "to:%s, amount:%s"
                            % (to_address, amount))
        tx_id = self.client.sendtoaddress(to_address, amount)
        return tx_id

    def check_address(self, address):
        data = self.client.validateaddress(address)
        return True if data['isvalid'] else False

    def unlock_account(self, timeout=5):
        return self.client.walletpassphrase(self.password, timeout)

    def list_accounts(self):
        return self.client.listaccounts()

    def get_transaction_detail(self, tx_hash):
        return self.client.getrawtransaction(tx_hash, 1)

    def get_latest_block_number(self):
        return int(self.client.getblockcount())

    def get_transaction_hashs(self, blocknumber=None):
        block_hash = self.client.getblockhash(blocknumber)
        block_info = self.client.getblock(block_hash)
        return block_info.get('tx')


bhd_client = BhdRpcClient(BHD_NODE_URL, BHD_WALLET_PASSWORD)
if __name__ == '__main__':
    # print(bhd_client.get_latest_block_number())
    # print(bhd_client.get_transaction_hashs(86346))
    from pprint import pprint
    # pprint(bhd_client.get_transaction_detail("34f4127fb39d2ce22f4601cdbc4d9a4fddfe159115e44b1cd6075f017024c8ec"))
    # print(bhd_client.unlock_account())
    # print(bhd_client.generate_address(1))
    print(bhd_client.get_balance())
