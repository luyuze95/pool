# encoding=utf-8

"""
    @author: anzz
    @date: 2019/5/14
"""
from decimal import Decimal

DEBUG = False

''' email config'''
MAIL_APP_ID = '13140'
MAIL_APP_KEY = '6761599fc5e24ab82e2646069d517b87'

DOMAIN = 'www.bpool.io'

USERNAME = 'noreply@noreply.exnow.com'
PASSWORD = 'ExnowBimao12345678'


''' secret'''
JWT_SECRET = 'dpool9787506377294'

''' redis config'''
REDIS_PASSWORD = '5ZHx3IYixd'
REDIS_HOST = 'pool.redis.server'
REDIS_PORT = 6379
# miner capacity
CAPACITY_DB = 9
AUTH_DB = 0


''' mysql config'''
MYSQL_USER = 'root'
MYSQL_PASSWORD = '5ZHx3IYixd'
MYSQL_HOST = 'pool.mysql.server'
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
FLASKY_DB_QUERY_TIMEOUT = 0.001
SQLALCHEMY_COMMIT_ON_TEARDOWN = True
SQLALCHEMY_RECORD_QUERIES = True


""" kafka config"""
KAFKA_HOST = ["pool.kafka.server:9092"]
GBT_TOPIC_BHD = "BitcoinHDRaw"
JOB_TOPIC_BHD = "JobMakerMsgBhd"
LATEST_BLOCK_MININGINFO = "latestBlockMiniInfo"


#################### wallet settings #########################
''' bhd node config'''
BHD_NODE_URL = "http://hemon:16761123@pool.bhd.server:8888/"
ADDRESS_LEAST_REMAINING_COUNT = 10
BHD_COIN_NAME = "bhd"
BHD_WALLET_PASSWORD = "7ujMko0admin"
BHD_MINER_ADDRESS = "3PURWR7vxZRiK8afgLB1Brx9Y9cBEan7gL"

# 全抵押和非全抵押收益
MORTGAGE_YIELD_RATE = Decimal('1')
NOT_MORTGAGE_YIELD_RATE = Decimal('0.3')

MIN_DEPOSIT_AMOUNT = {
    BHD_COIN_NAME: Decimal("0.0001")
}

MIN_CONFIRMED = {
    BHD_COIN_NAME: 3
}

# 最小汇聚余额
MIN_CONVERGE_AMOUNT = Decimal('0.1')
# 手续费保留金
POUNDAGE_BAlANCE = Decimal('0.00006')