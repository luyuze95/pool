# encoding=utf-8

"""
    @author: anzz
    @date: 2019/5/29
"""
import os
import sys

from flask import Flask
from flask_sqlalchemy import get_debug_queries

from models import db

sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir))

import conf
from schedule.celery_ins import make_celery

app = Flask(__name__)
app.config.from_object(conf)
db.init_app(app)
celery = make_celery(app)

from utils.handler_exception import APIHandleError

api = APIHandleError(app)
from resources.user_asset_res import UserAssetApi
from resources.wallet_res import WalletAPI, UserAssetTransferInfoAPI
from resources.earnings_res import BlockEarningsApi, DayEarningsApi
from resources.verification_res import VerifyApi

api.add_resource(WalletAPI, '/v1/wallet/', '/v1/wallet', endpoint="wallet")
api.add_resource(UserAssetApi, '/v1/asset/', '/v1/asset', endpoint="asset")
api.add_resource(BlockEarningsApi, '/v1/earnings/blocks/', '/v1/earnings/blocks', endpoint="block_earnings")
api.add_resource(DayEarningsApi, '/v1/earnings/days/', '/v1/earnings/days', endpoint="day_earnings")
api.add_resource(VerifyApi, '/v1/seccode/', '/v1/seccode', endpoint="seccode")
api.add_resource(UserAssetTransferInfoAPI, '/v1/transactions/<string:transaction_type>/', '/v1/transactions/<string:transaction_type>', endpoint="transactions")


if conf.DEBUG:
    #@app.after_request
    def after_request_func(response):
        for query in get_debug_queries():
            if query.duration >= app.config['FLASKY_DB_QUERY_TIMEOUT']:
                print('Slow query:%s ,Parameters:%s, Duration:%fs, Context:%s\n' %
                      (query.statement, query.parameters, query.duration,
                       query.context))  # 打印超时sql执行信息
        return response


if __name__ == '__main__':
    app.run(host='0.0.0.0')
