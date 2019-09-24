# encoding=utf-8

"""
    @author: lyz
    @date: 2019/9/23
"""
from conf import *
from rpc.bhd_rpc import BhdRpcClient


class HddRpcClient(BhdRpcClient):

    def generate_address(self, username):
        self.unlock_account()
        resp = self.client.dumpprivkeys(username, username+1)
        address = resp['keys'][0]['address']
        priv_key = resp['keys'][0]['privkey']
        self.client.importprivkey(priv_key)
        return address, priv_key

    def list_pledges(self, count=1000):
        pledges = self.client.listpointto(count)
        return pledges


hdd_client = HddRpcClient(HDD_NODE_URL, HDD_WALLET_PASSWORD)


if __name__ == '__main__':
    from pprint import pprint
    # print(lhd_client.get_transaction_hashs(174096))
    last_block_num = hdd_client.get_latest_block_number()
    print(last_block_num)
    # block_hashs = lhd_client.get_transaction_hashs(last_block_num)
    # print(block_hashs)
    # pprint(lhd_client.get_transaction_detail(block_hashs[0]))
    # print(lhd_client.unlock_account())
    # print(lhd_client.generate_address(1))
    # print(lhd_client.get_balance())
    # print(lhd_client.list_received_by_address())
    # pprint(lhd_client.list_unspent())
    # pprint(lhd_client.list_pledges())
