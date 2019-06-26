# encoding=utf-8

"""
    @author: anzz
    @date: 2019/6/12
"""

from rpc.authproxy import AuthServiceProxy
from conf import *


class USDTRPCClient():
    def __init__(self, url, address, password=None):
        self.url = url
        self.client = AuthServiceProxy(service_url=self.url, timeout=20)
        self.password = password
        self.property_id = 31
        self.address = address

    def block_info(self, block_number=None):
        return self.client.getblockchaininfo()

    def get_balance(self, address=None, is_btc=False):
        if is_btc:
            return self.client.getbalance()
        address = address or self.address
        return Decimal(self.client.omni_getbalance(address, self.property_id)['balance'])

    def generate_address(self, username):
        return self.client.getnewaddress(str(username)), ''

    def get_transactions(self, count=5, skip=10):
        return self.client.omni_listtransactions('*', 10000)

    def withdrawal(self, to_address, amount, from_address=None, is_btc=False):
        from_address = from_address or self.address
        if is_btc:
            if self.get_balance(from_address, True) < amount:
                raise Exception("btc, money not enough,from:%s, to:%s, "
                                "transfer:%s, amount:%s"
                                % (self.address, to_address, is_btc, amount))
            return self.client.sendtoaddress(to_address, amount)
        if self.get_balance(from_address) < amount:
            raise Exception("usdt withdraw exception, money not enough, "
                            "from:%s, to:%s, amount:%s"
                            % (self.address, to_address, amount))
        return self.client.omni_send(from_address, to_address,
                                     self.property_id, str(amount))

    def funded_sendall(self, from_address,
                       to_address=None,
                       eco_system=1,
                       fee_address=None):
        to_address = to_address or self.address
        fee_address = fee_address or self.address
        tx_id = self.client.omni_funded_sendall(from_address, to_address,
                                                eco_system, fee_address)
        return tx_id

    def list_unspent(self, address, min_confirm=0, max_confirm=9999999,):
        return self.client.listunspent(min_confirm, max_confirm, [address])

    def get_all_addresses_balance(self):
        return self.client.omni_getwalletaddressbalances()

    def check_address(self, address):
        data = self.client.validateaddress(address)
        return True if data['isvalid'] else False

    def unlock_account(self, timeout=5):
        return self.client.walletpassphrase(self.password, timeout)

    def local_syncing(self):
        return self.block_info().get("headers")

    def get_transaction_detail(self, tx_hash):
        return self.client.getrawtransaction(tx_hash, 1)


usdt_client = USDTRPCClient(USDT_URI, USDT_WITHDRAWAL_ADDRESS)

if __name__ == '__main__':
    print(usdt_client.block_info())
    # tx_id = client.withdrawal(USDT_WITHDRAWAL_ADDRESS, 1000, None,
    #  "1Pv2wHJoqeDUwufr7NXoExiM5AtAZhiEko")
    # print(tx_id)

