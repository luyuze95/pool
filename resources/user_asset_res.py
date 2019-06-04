# encoding=utf-8

"""
    @author: anzz
    @date: 2019/5/29
"""

from flask import g
from flask_restful import Resource, reqparse
from sqlalchemy import func

from models import db
from conf import *
from logs import api_logger
from models.income_record import IncomeRecord
from models.miner_plotter import MinerPlotter
from models.user_asset import UserAsset
from resources.auth_decorator import login_required
from utils.response import make_resp


class UserAssetApi(Resource):
    decorators = [login_required]

    def get(self):
        """
        用户资产信息获取
        :return:
        """
        account_key = g.account_key

        user_asset = UserAsset.query.filter_by(account_key=account_key).first()
        if not user_asset:
            return make_resp(404, False)
        income = IncomeRecord.query.filter_by(account_key=account_key).order_by(IncomeRecord.height.desc()).limit(1).first()
        if not income:
            return make_resp(404, False)
        user_capacity = income.capacity
        if not user_capacity:
            return make_resp(401, False, message="user capacity not found")
        theory_pledge = user_capacity[0]*3

        pledge_rate = user_asset.pledge_asset/theory_pledge

        earning_rate = NOT_MORTGAGE_YIELD_RATE
        if pledge_rate > 1:
            earning_rate = MORTGAGE_YIELD_RATE

        context = {
            "total_asset": user_asset.total_asset,
            "pledge_asset": user_asset.pledge_asset,
            "available_asset": user_asset.available_asset,
            "earning_rate": earning_rate,
            "theory_pledge": theory_pledge,
            "pledge_rate": pledge_rate,
        }

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
        print(direction)
        account_key = g.account_key
        api_logger.info("asset transfer, amount:%s, user:%s, direction:%s"
                        % (amount, account_key, direction))
        try:
            user_asset = UserAsset.query.filter_by(
                account_key=account_key).with_for_update(read=True).first()
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
            print(amount)
            user_asset.pledge_asset -= amount
            user_asset.available_asset += amount
            db.session.commit()
        except Exception as e:
            api_logger.error("asset transfer, error %s" % str(e))
            db.session.rollback()
            return make_resp(500, False, message="transfer failed")
        api_logger.info("asset transfer succeed, amount:%s, user:%s, direction:%s"
                        % (amount, account_key, direction))
        return make_resp(200, True)



