# encoding=utf-8

"""
    @author: anzz
    @date: 2019/5/29
"""
from time import time

from flask import g
from flask_restful import Resource, reqparse
from sqlalchemy import func

from models import db
from conf import *
from logs import api_logger
from models.income_record import IncomeRecord
from models.transfer_info import AssetTransfer
from models.user_asset import UserAsset
from resources.auth_decorator import login_required
from utils.redis_ins import redis_capacity
from utils.response import make_resp


class UserAssetApi(Resource):
    decorators = [login_required]

    def get(self):
        """
        用户资产信息获取
        :return:
        """
        account_key = g.account_key
        parse = reqparse.RequestParser()
        parse.add_argument('coin_name', type=str, required=True)
        args = parse.parse_args()
        coin_name = args.get('coin_name')

        user_asset = UserAsset.query.filter_by(account_key=account_key,
                                               coin_name=coin_name).first()
        if not user_asset:
            return make_resp(404, False)
        context = user_asset.to_dict()
        if coin_name == USDT_NAME:
            return make_resp(200, True, **context)
        keys = "miner:main:%s:*" % account_key
        miner_machines = redis_capacity.keys(keys)

        context.update({
            "earning_rate": 0,
            "theory_pledge": 0,
            "pledge_rate": 0,
            "total_income": 0,
        })
        if not miner_machines:
            return make_resp(200, True, **context)
        total_capacity = 0
        for machine in miner_machines:
            capacity_ts = redis_capacity.get(machine)
            capacity, ts = capacity_ts.split(":")
            period_validity = time() - int(ts[:-3])
            if period_validity < 7200:
                total_capacity += int(capacity)

        theory_pledge = total_capacity/1024*3

        pledge_rate = user_asset.pledge_asset/theory_pledge

        earning_rate = NOT_MORTGAGE_YIELD_RATE
        if pledge_rate > 1:
            earning_rate = MORTGAGE_YIELD_RATE

        total_income = IncomeRecord.query.with_entities(
            func.sum(IncomeRecord.amount)).filter_by(
            account_key=account_key).first()
        if not total_income:
            total_income = [0]

        calculate_data = {
            "earning_rate": earning_rate,
            "theory_pledge": theory_pledge,
            "pledge_rate": pledge_rate,
            "total_income": total_income[0],
        }

        context.update(calculate_data)

        return make_resp(200, True, **context)

    def put(self):
        """
        用户资产划转,从抵押到余额划转,余额到抵押
        :return:
        """
        parse = reqparse.RequestParser()
        parse.add_argument('amount', type=str, required=True)
        parse.add_argument('direction', type=bool, required=False, default=True,
                           help="True:抵押到余额，False:余额到抵押")
        args = parse.parse_args()
        amount = Decimal(args.get('amount'))
        direction = args.get('direction')
        account_key = g.account_key
        api_logger.info("asset transfer, amount:%s, user:%s, direction:%s"
                        % (amount, account_key, direction))
        try:
            user_asset = UserAsset.query.filter_by(
                account_key=account_key, coin_name=BHD_COIN_NAME
            ).with_for_update(read=True).first()
            if direction and user_asset.pledge_asset < amount:
                api_logger.error(
                    "asset transfer, user:%s, pledge_asset:%s, amount:%s"
                    % (account_key, user_asset.pledge_asset, amount))
                return make_resp(400, False, message="pledge_asset not enough")
            if not direction and user_asset.available_asset < amount:
                api_logger.error(
                    "asset transfer, user:%s, available_asset:%s, amount:%s"
                    % (account_key, user_asset.available_asset, amount))
                return make_resp(400, False, message="available not enough")
            if not direction:
                amount = -amount
            user_asset.pledge_asset -= amount
            user_asset.available_asset += amount
            asset_transfer = AssetTransfer(account_key, abs(amount), direction)
            db.session.add(asset_transfer)
            db.session.commit()
        except Exception as e:
            api_logger.error("asset transfer, error %s" % str(e))
            db.session.rollback()
            return make_resp(500, False, message="transfer failed")
        api_logger.info("asset transfer succeed, amount:%s, user:%s, direction:%s"
                        % (amount, account_key, direction))
        return make_resp(200, True)



