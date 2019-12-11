# encoding=utf-8

"""
    @author: lyz
    @date: 2019/6/20
"""
from decimal import Decimal

from flask import g
from flask_restful import Resource, reqparse

from logs import api_logger
from models import db
from models.user_asset import UserAsset
from resources.auth_decorator import login_required
from utils.response import make_resp


class SiteTransfer(Resource):
    decorators = [login_required]

    def put(self):
        """
        站内用户资产划转
        :return:
        """

        parse = reqparse.RequestParser()
        parse.add_argument('coin_name', type=str, required=True, trim=True)
        parse.add_argument('amount', type=str, required=True)
        parse.add_argument('to_account', type=str, required=True, trim=True)
        args = parse.parse_args()
        coin_name = args.get('coin_name')
        account_key = g.account_key
        amount = Decimal(str(args.get('amount')))
        to_account = args.get('to_account')

        api_logger.info(
            "transfer api, to:%s, amount:%s, account_key:%s, coin_name:%s"
            % (to_account, amount, account_key, coin_name))

        try:
            user_asset_sender = UserAsset.query.filter_by(
                account_key=account_key, coin_name=coin_name).with_for_update(
                read=True).first()
            user_asset_receiver = UserAsset.query.filter_by(
                account_key=to_account, coin_name=coin_name).with_for_update(
                read=True).first()
            if not user_asset_sender or not user_asset_receiver:
                api_logger.error("withdrawal,user not found %s" % account_key)
                return make_resp(404, False, message="用户资产错误")

            if user_asset_sender.available_asset < amount or user_asset_sender.total_asset < amount:
                return make_resp(400, False, message="余额不足")

            user_asset_sender.available_asset -= amount
            user_asset_sender.total_asset -= amount
            user_asset_receiver.available += amount
            user_asset_receiver.total_asset += amount

            db.session.commit()
        except Exception as e:
            api_logger.error("transfer, error %s" % str(e))
            db.session.rollback()
            return make_resp(500, False, message="提现申请提交失败")

        api_logger.info("transfer api, succeed")
        return make_resp(200, True)
