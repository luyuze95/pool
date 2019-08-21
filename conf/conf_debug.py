# encoding=utf-8

"""
    @author: anzz
    @date: 2019/5/14
"""
from decimal import Decimal

DEBUG = True

''' email config'''
MAIL_APP_ID = '13140'
MAIL_APP_KEY = '6761599fc5e24ab82e2646069d517b87'

DOMAIN = 'www.f1pool.com'

USERNAME = 'noreply@mail.f1pool.com'
PASSWORD = 'ExnowBimao12345678'


''' secret'''
JWT_SECRET = 'dpool9787506377294'

''' redis config'''
REDIS_PASSWORD = 'bhdpool'
REDIS_HOST = '47.97.116.19'
REDIS_PORT = 6379
# miner capacity
CAPACITY_DB = 9
AUTH_DB = 0
LOCK_DB = 1


''' mysql config'''
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'bhdpool'
MYSQL_HOST = '47.97.116.19'
MYSQL_PORT = 3306
MYSQL_DB = 'pool'


''' celery config'''
CELERY_BROKER_DB = 2
CELERY_BACKEND_DB = 3
CELERY_MAX_CHILDREN_TASK = 10

CELERY_BROKER_URL = 'redis://:%s@%s:%s/%s' %\
                    (REDIS_PASSWORD, REDIS_HOST, REDIS_PORT, CELERY_BROKER_DB)
CELERY_BACKEND_URL = 'redis://:%s@%s:%s/%s' %\
                     (REDIS_PASSWORD, REDIS_HOST, REDIS_PORT, CELERY_BACKEND_DB)

''' sqlalchemy config'''
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' %\
                          (MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_PORT, MYSQL_DB)
SQLALCHEMY_TRACK_MODIFICATIONS = True
FLASKY_DB_QUERY_TIMEOUT = 0.001
SQLALCHEMY_COMMIT_ON_TEARDOWN = True
SQLALCHEMY_RECORD_QUERIES = True


""" kafka config"""
KAFKA_HOST = ["47.97.116.19:9092"]
GBT_TOPIC_BHD = "BitcoinHDRaw"
JOB_TOPIC_BHD = "JobMakerMsgBhd"
LATEST_BLOCK_MININGINFO = "latestBlockMiniInfo"

GBT_TOPIC_NEWBI = "NewBiRaw"
JOB_TOPIC_NEWBI = "JobMakerMsgNewbi"
NEWBI_LATEST_BLOCK_MININGINFO = "newBilatestBlockMiniInfon"

#################### wallet settings #########################
''' bhd node config'''
BHD_NODE_URL = "http://hemon:16761123@47.97.116.19:8888/"
ADDRESS_LEAST_REMAINING_COUNT = 10
BHD_COIN_NAME = "bhd"
BHD_WALLET_PASSWORD = "7ujMko0admin"
BHD_MINER_ADDRESS = "2N46yZncdY3vUnHUBUdhTJ2urFZmGozhFvw"

""" usdt node config"""
USDT_WITHDRAWAL_ADDRESS = 'n1ErRubbXNKP59gdFf4joWepskgGq7P6mN'
USDT_CONVERGE_ADDRESS = USDT_WITHDRAWAL_ADDRESS
USDT_URI = 'http://bimaousdt:lfkdsjalfdsafjkdshfakjdsffkldsjalfkj@127.0.0.1:8332'
USDT_NAME = "usdt"


""" boom node config"""
BOOM_NODE_URI = "http://192.168.10.17:9125/boom"
BOOM_ACCOUNT = "8237986060609785054"


""" newbi node config"""
NEWBI_NODE_URI = "http://47.75.133.66:8125/burst"
NEWBI_ACCOUNT = "NEWBI-TRJF-WX42-WMUP-7E7F8"
# NEWBI_ACCOUNT = "NEWBI-N8AF-3AR9-RRHT-BBBBB"
NEWBI_ACCOUNT_PASSWORD = "7ujMko0admin"
NEWBI_NAME = "newbi"

# 全抵押和非全抵押收益
MORTGAGE_YIELD_RATE = Decimal('1')
NOT_MORTGAGE_YIELD_RATE = Decimal('0.3')

MIN_DEPOSIT_AMOUNT = {
    BHD_COIN_NAME: Decimal("0.0001"),
    NEWBI_NAME: Decimal("0.0001")
}

MIN_CONFIRMED = {
    BHD_COIN_NAME: 3,
    USDT_NAME: 3,
    NEWBI_NAME: 6,
}

# 最小汇聚余额
MIN_CONVERGE_AMOUNT_BHD = Decimal('0.1')
MIN_CONVERGE_AMOUNT_USDT = Decimal('1')
# 手续费
POUNDAGE_BALANCE = Decimal('0.00006')
MIN_FEE = Decimal('0.01')


""" lhd node config"""
LHD_NAME = "lhd"
LHD_NODE_URL = "http://hemon:16761123@47.75.133.66:8888/"
LHD_WALLET_PASSWORD = "7ujMko0admin"
LHD_MINER_ADDRESS = "3Qch21MpAtkrUQjHpogDigL9LFCjxci3rP"