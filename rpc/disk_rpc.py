# encoding=utf-8

"""
    @author: lyz
    @date: 2019/9/16
"""
from _decimal import ROUND_DOWN

from rpc.authproxy import AuthServiceProxy
from conf import *


class DiskRpcClient(object):
    def __init__(self, url, password=None):
        self.url = url
        self.client = AuthServiceProxy(service_url=self.url, timeout=30)
        self.password = password

    def block_info(self, block_number=None):
        return self.client.getblockchaininfo()

    def get_balance(self, address=None,):
        if address is not None:
            return self.client.getbalance(address)
        return self.client.getbalance()

    def generate_address(self, username):
        # self.unlock_account()
        address = self.client.getnewaddress(str(username))
        priv_key = self.client.dumpprivkey(address)
        self.client.importprivkey(priv_key)
        return address, priv_key

    def get_transactions(self, count=10, skip=0):
        return self.client.listtransactions('*', count, skip)

    def withdrawal(self, to_address, amount, from_account=None):
        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))
        amount = amount.quantize(Decimal("0.00000000"), rounding=ROUND_DOWN)
        self.unlock_account()
        if not self.check_address(to_address):
            raise Exception("disk withdraw exception, invalid address %s"
                            % to_address)

        if self.get_balance(from_account) < amount:
            raise Exception("disk withdraw exception, money not enough, "
                            "to:%s, amount:%s"
                            % (to_address, amount))
        if from_account is None:
            tx_id = self.client.sendtoaddress(to_address, amount)
        else:
            tx_id = self.client.sendfrom(from_account, to_address, amount)
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

    def list_received_by_address(self):
        data = self.client.listreceivedbyaddress()
        return data

    def list_unspent(self, minconf=1, maxconf=999999, addresses=[]):
        unspents = self.client.listunspent(minconf, maxconf, addresses)
        return unspents


disk_client = DiskRpcClient(DISK_NODE_URL, DISK_WALLET_PASSWORD)
if __name__ == '__main__':
    from pprint import pprint
    # print(disk_client.get_transaction_hashs(174096))
    last_block_num = disk_client.get_latest_block_number()
    print(last_block_num)
    # block_hashs = disk_client.get_transaction_hashs(last_block_num)
    # print(block_hashs)
    # pprint(disk_client.get_transaction_detail("f79d6c69d96375961d91600415d4947df7773feaaf247218582d55966799b551")['vout'][1][''])
    # print(disk_client.unlock_account())
    # print(disk_client.generate_address(1))
    # print(disk_client.get_balance())
    # print(disk_client.get_transactions())
    # pprint(disk_client.list_unspent())
    # pprint(disk_client.list_pledges())
    # print(disk_client.generate_address(31412))
