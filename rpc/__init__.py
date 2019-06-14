# encoding=utf-8

"""
    @author: anzz
    @date: 2019/5/29
"""
from conf import *
from rpc.bhd_rpc import bhd_client
from rpc.usdt_rpc import usdt_client


def get_rpc(coin_name):
    client = None
    if coin_name not in (BHD_COIN_NAME, USDT_NAME):
        raise Exception("币种不存在")
    if coin_name == BHD_COIN_NAME:
        client = bhd_client
    if coin_name == USDT_NAME:
        client = usdt_client
    return client
