# encoding=utf-8

"""
    @author: anzz
    @date: 2019/5/29
"""
from decimal import Decimal

from flask import g
from flask_restful import Resource, reqparse

from models import db
from logs import api_logger
from models.bhd_address import BhdAddress
from models.user_asset import UserAsset
from models.withdrawal_transactions import WithdrawalTransaction
from resources.auth_decorator import login_required
from rpc.bhd_rpc import bhd_client
from utils.response import make_resp


class WalletAPI(Resource):
    decorators = [login_required]

    def get(self):
        """
        生成用户钱包地址
        :return:
        """
        parse = reqparse.RequestParser()
        parse.add_argument('coin_name', type=str, required=False, trim=True, default='bhd')
        args = parse.parse_args()
        account_key = g.account_key
        coin_name = args.get('coin_name').lower()

        api_logger.info("generate address, account_key:%s, coin_name:%s"
                        % (account_key, coin_name))

        # 检查是否已有地址
        bhd_address = BhdAddress.query.filter_by(account_key=account_key,
                                                 coin_name=coin_name).first()

        if bhd_address:
            return make_resp(**bhd_address.to_dict())

        # 从节点获取地址
        address, priv_key = bhd_client.generate_address(g.user.id)

        # 插入数据库
        bhd_address = BhdAddress(account_key, address, priv_key)
        db.session.add(bhd_address)
        db.session.commit()

        api_logger.info("wallet address api, insert into wallet_address %s"
                        % bhd_address.to_dict())

        return make_resp(**bhd_address.to_dict())

    def post(self):
        """
        转账
        :return:
        """
        parse = reqparse.RequestParser()
        parse.add_argument('coin_name', type=str, required=False, trim=True)
        parse.add_argument('amount', type=str, required=True)
        parse.add_argument('to_address', type=str, required=True, trim=True)
        args = parse.parse_args()
        coin_name = args.get('coin_name')
        account_key = g.account_key
        amount = Decimal(str(args.get('amount')))
        to_address = args.get('to_address')

        api_logger.info("Withdrawal api, to:%s, amount:%s, account_key:%s"
                        % (to_address, amount, account_key))

        try:
            user_asset = UserAsset.query.filter_by(
                account_key=account_key).with_for_update(read=True).first()
            if not user_asset:
                api_logger.error("withdrawal,user not found %s" % account_key)
                return make_resp(404, False, message="user asset not found")
            if user_asset.available_asset < amount:
                api_logger.error(
                    "withdrawal, user:%s, available_asset:%s, amount:%s"
                    % (account_key, user_asset.available_asset, amount))
                return make_resp(400, False, message="balance not enough")
            user_asset.pledge_asset -= amount
            user_asset.total_asset -= amount
            db.session.commit()
        except Exception as e:
            api_logger.error("withdrawal, error %s" % str(e))
            db.session.rollback()
            return make_resp(500, False, message="withdrawal failed")

        txid = bhd_client.withdrawal(to_address, amount)
        withdrawal_transaction = WithdrawalTransaction(account_key, amount,
                                                       txid,
                                                       to_address)
        db.session.add(withdrawal_transaction)
        db.session.commit()

        api_logger.info("Withdrawal api, insert into withdrawal_transaction %s"
                        % withdrawal_transaction.to_dict())

        return make_resp(txid=withdrawal_transaction.txid)
