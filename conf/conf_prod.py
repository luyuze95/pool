# encoding=utf-8

"""
    @author: anzz
    @date: 2019/5/14
"""
DEBUG = False

''' redis config'''
REDIS_PASSWORD = 'exnow2018'
REDIS_HOST = '192.168.10.144'
REDIS_PORT = 6379

''' mysql config'''
MYSQL_USER = 'root'
MYSQL_PASSWORD = '123456'
MYSQL_HOST = '192.168.10.144'
MYSQL_PORT = 3306
MYSQL_DB = 'pool'


''' celery config'''
CELERY_BROKER_DB = 0
CELERY_BACKEND_DB = 1

CELERY_BROKER_URL = 'redis://:%s@%s:%s/%s' %\
                    (REDIS_PASSWORD, REDIS_HOST, REDIS_PORT, CELERY_BROKER_DB)
CELERY_BACKEND_URL = 'redis://:%s@%s:%s/%s' %\
                     (REDIS_PASSWORD, REDIS_HOST, REDIS_PORT, CELERY_BACKEND_DB)

''' sqlalchemy config'''
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' %\
                          (MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_PORT, MYSQL_DB)

SQLALCHEMY_TRACK_MODIFICATIONS = True


""" kafka config"""
KAFKA_HOST = ["172.31.22.192:9092", "172.31.18.96:9092", "172.31.24.209:9092"]
GBT_TOPIC = "BitcoinHDRaw"
