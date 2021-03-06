# encoding=utf-8

"""
    @author: lyz
    @date: 2019/5/29
"""
from conf import *
from rpc.bhd_rpc import bhd_client
from rpc.lhd_rpc import lhd_client
from rpc.nb_rpc import nb_client
from rpc.usdt_rpc import usdt_client
from rpc.disk_rpc import disk_client
from rpc.hdd_rpc import hdd_client


def get_rpc(coin_name):
    client = None
    if coin_name not in (BHD_COIN_NAME, USDT_NAME, NEWBI_NAME, LHD_NAME, DISK_NAME, HDD_NAME):
        raise Exception("币种不存在")
    if coin_name == BHD_COIN_NAME:
        client = bhd_client
    if coin_name == USDT_NAME:
        client = usdt_client
    if coin_name == NEWBI_NAME:
        client = nb_client
    if coin_name == LHD_NAME:
        client = lhd_client
    if coin_name == DISK_NAME:
        client = disk_client
    if coin_name == HDD_NAME:
        client = hdd_client
    return client
