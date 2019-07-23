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
from resources.activity_incomes import ActivityRewards
from resources.billings_res import OthersBill
from resources.burst_block import BurstBlockApi
from resources.dl_fraction import DeadlineFractionApi
from resources.site_transfer import SiteTransfer

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
from resources.earnings_res import EarningsTotalApi, DayEarningsApi, \
    MiningIncomeApi, CoopIncomeApi
from resources.verification_res import VerifyApi

# 生成地址、转账、撤销转账
api.add_resource(WalletAPI, '/v1/wallet/', '/v1/wallet', endpoint="wallet")
# 用户资产信息、资产划转
api.add_resource(UserAssetApi, '/v1/asset/', '/v1/asset', endpoint="asset")
# 总收益
api.add_resource(EarningsTotalApi, '/v1/earnings/total/', '/v1/earnings/total', endpoint="total_earnings")
# 按天收益
api.add_resource(DayEarningsApi, '/v1/earnings/days/', '/v1/earnings/days', endpoint="day_earnings")
# 挖矿明细
api.add_resource(MiningIncomeApi, '/v1/earnings/blocks/', '/v1/earnings/blocks', endpoint="block_earnings")
# 合作收益
api.add_resource(CoopIncomeApi, '/v1/earnings/coop_incomes/', '/v1/earnings/coop_incomes', endpoint="coop_incomes")
# 爆块查询
api.add_resource(BurstBlockApi, '/v1/blocks/', '/v1/blocks', endpoint="blocks")
# 贡献点查询
api.add_resource(DeadlineFractionApi, '/v1/dl_fraction/', '/v1/dl_fraction', endpoint="dl_fraction")

api.add_resource(VerifyApi, '/v1/seccode/', '/v1/seccode', endpoint="seccode")
api.add_resource(SiteTransfer, '/v1/transfer/', '/v1/transfer', endpoint="transfer")
api.add_resource(ActivityRewards, '/v1/activity_income/', '/v1/activity_income', endpoint="activity_income")
api.add_resource(OthersBill, '/v1/other_bills/', '/v1/other_bills', endpoint="other_bills")
api.add_resource(UserAssetTransferInfoAPI, '/v1/<string:transaction_type>/', '/v1/<string:transaction_type>', endpoint="transactions")


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
