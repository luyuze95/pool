# encoding=utf-8

"""
    @author: anzz
    @date: 2019/5/14
"""
from decimal import Decimal

DEBUG = True


''' secret'''
JWT_SECRET = 'bimao'

''' redis config'''
REDIS_PASSWORD = 'bhdpool'
REDIS_HOST = '47.97.116.19'
REDIS_PORT = 6379
# miner capacity
CAPACITY_DB = 9


''' mysql config'''
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'bhdpool'
MYSQL_HOST = '47.97.116.19'
MYSQL_PORT = 3306
MYSQL_DB = 'pool'


''' celery config'''
CELERY_BROKER_DB = 0
CELERY_BACKEND_DB = 1
CELERY_MAX_CHILDREN_TASK = 10

CELERY_BROKER_URL = 'redis://:%s@%s:%s/%s' %\
                    (REDIS_PASSWORD, REDIS_HOST, REDIS_PORT, CELERY_BROKER_DB)
CELERY_BACKEND_URL = 'redis://:%s@%s:%s/%s' %\
                     (REDIS_PASSWORD, REDIS_HOST, REDIS_PORT, CELERY_BACKEND_DB)

''' sqlalchemy config'''
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' %\
                          (MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_PORT, MYSQL_DB)
SQLALCHEMY_TRACK_MODIFICATIONS = True


""" kafka config"""
KAFKA_HOST = ["192.168.10.134:9092", "192.168.10.134:9094", "192.168.10.134:9093"]
GBT_TOPIC_BHD = "BitcoinHDRaw"
JOB_TOPIC_BHD = "JobMakerMsgBhd"
LATEST_BLOCK_MININGINFO = "latestBlockMiniInfo"


#################### wallet settings #########################
''' bhd node config'''
BHD_NODE_URL = "http://hemon:16761123@47.97.116.19:8888/"
ADDRESS_LEAST_REMAINING_COUNT = 10
BHD_COIN_NAME = "bhd"
BHD_WALLET_PASSWORD = "7ujMko0admin"
# 全抵押和非全抵押收益
MORTGAGE_YIELD_RATE = Decimal('1')
NOT_MORTGAGE_YIELD_RATE = Decimal('0.3')

MIN_DEPOSIT_AMOUNT = {
    BHD_COIN_NAME: Decimal("0.0001")
}

MIN_CONFIRMED = {
    BHD_COIN_NAME: 12
}