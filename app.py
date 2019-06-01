# encoding=utf-8

"""
    @author: anzz
    @date: 2019/5/29
"""
import os
import sys

from flask import Flask

from models import db
from resources.earnings_res import EarningsApi

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
from resources.wallet_res import WalletAPI

api.add_resource(WalletAPI, '/v1/wallet/', '/v1/wallet', endpoint="wallet")
api.add_resource(UserAssetApi, '/v1/asset/', '/v1/asset', endpoint="asset")
api.add_resource(EarningsApi, '/v1/earnings/', '/v1/earnings', endpoint="earnings")

if __name__ == '__main__':
    app.run(host='0.0.0.0')
