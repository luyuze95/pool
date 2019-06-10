# encoding=utf-8

"""
    @author: anzz
    @date: 2019/5/29
"""
from decimal import Decimal

from flask import g
from flask_restful import Resource, reqparse

from logs import api_logger
from models import db
from models.bhd_address import BhdAddress
from models.bhd_burst import BurstBlock
from models.deposit_transaction import DepositTranscation
from models.dl_fraction import DeadlineFraction
from models.transfer_info import AssetTransfer
from models.user_asset import UserAsset
from models.withdrawal_transactions import WithdrawalTransaction
from resources.auth_decorator import login_required
from rpc.bhd_rpc import bhd_client
from utils.redis_ins import redis_auth
from utils.response import make_resp


class WalletAPI(Resource):
    decorators = [login_required]

    def get(self):
        """
        生成用户钱包地址
        :return:
        """
        parse = reqparse.RequestParser()
        parse.add_argument('coin_name', type=str, required=False, trim=True,
                           default='bhd')
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
        parse.add_argument('seccode', type=str, required=True, trim=True)
        args = parse.parse_args()
        coin_name = args.get('coin_name')
        account_key = g.account_key
        amount = Decimal(str(args.get('amount')))
        to_address = args.get('to_address')
        seccode = args.get('seccode')

        api_logger.info("Withdrawal api, to:%s, amount:%s, account_key:%s"
                        % (to_address, amount, account_key))

        try:
            user_asset = UserAsset.query.filter_by(
                account_key=account_key).with_for_update(read=True).first()
            if not user_asset:
                api_logger.error("withdrawal,user not found %s" % account_key)
                return make_resp(404, False, message="用户资产错误")

            key = "withdrawal:seccode:%s" % account_key
            seccode_cache = redis_auth.get(key)
            if seccode != seccode_cache:
                api_logger.error("withdrawal, seccode error")
                return make_resp(400, False, message="验证码错误")
            redis_auth.delete(key)
            if user_asset.available_asset < amount:
                api_logger.error(
                    "withdrawal, user:%s, available_asset:%s, amount:%s"
                    % (account_key, user_asset.available_asset, amount))
                return make_resp(400, False, message="余额不足")

            user_asset.available_asset -= amount
            actual_amount = amount * Decimal('0.995')
            poundage = amount * Decimal('0.005')
            user_asset.frozen_asset += actual_amount
            withdrawal_transaction = WithdrawalTransaction(account_key,
                                                           actual_amount,
                                                           to_address, poundage)
            db.session.add(withdrawal_transaction)
            db.session.commit()
        except Exception as e:
            api_logger.error("withdrawal, error %s" % str(e))
            db.session.rollback()
            return make_resp(500, False, message="提现失败")

        api_logger.info("Withdrawal api, insert into withdrawal_transaction %s"
                        % withdrawal_transaction.to_dict())

        return make_resp(200, True)


class UserAssetTransferInfoAPI(Resource):
    decorators = [login_required]

    transaction_types = {
        "deposit": DepositTranscation,
        "withdrawal": WithdrawalTransaction,
        "blocks": BurstBlock,
        "transfer": AssetTransfer,
        "dl_fraction": DeadlineFraction,
    }

    def get(self, transaction_type):
        if transaction_type not in transaction_type:
            return make_resp(404, message="查询列表内容不存在")
        account_key = g.account_key
        model = self.transaction_types.get(transaction_type)
        parse = reqparse.RequestParser()
        parse.add_argument('limit', type=int, required=False, default=10)
        parse.add_argument('offset', type=int, required=False, default=0)
        parse.add_argument('t', type=int, required=False)
        args = parse.parse_args()
        limit = args.get('limit')
        offset = args.get('offset')
        infos = model.query.filter_by(
            account_key=account_key).order_by(
            model.create_time.desc()).limit(limit).offset(
            offset).all()
        records = [info.to_dict() for info in infos]
        return make_resp(records=records)
