# encoding=utf-8

"""
    @author: anzz
    @date: 2019/5/29
"""
import time
from datetime import datetime

from flask import g
from flask_restful import Resource, reqparse
from sqlalchemy import and_, func

from conf import *
from logs import api_logger
from models import db
from models.activity_reward import ActivityReward
from models.income_record import IncomeRecord, IncomeEcologyRecord
from models.pool_address import PoolAddress
from models.bhd_burst import BurstBlock, EcolBurstBlock
from models.deposit_transaction import DepositTranscation
from models.dl_fraction import DeadlineFraction, DeadlineFractionEcology
from models.transfer_info import AssetTransfer
from models.user_asset import UserAsset
from models.withdrawal_transactions import WithdrawalTransaction
from resources.auth_decorator import login_required
from rpc import get_rpc
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
        parse.add_argument('coin_name', type=str, required=True, trim=True)
        args = parse.parse_args()
        account_key = g.account_key
        coin_name = args.get('coin_name').lower()

        api_logger.info("generate address, account_key:%s, coin_name:%s"
                        % (account_key, coin_name))

        # 检查是否已有地址
        bhd_address = PoolAddress.query.filter_by(account_key=account_key,
                                                 coin_name=coin_name).first()

        if bhd_address:
            return make_resp(**bhd_address.to_dict())

        # 从节点获取地址
        client = get_rpc(coin_name)
        try:
            address, priv_key = client.generate_address(g.user.id)

            # 插入数据库
            bhd_address = PoolAddress(account_key, address, priv_key, coin_name)
            db.session.add(bhd_address)
            db.session.commit()

            api_logger.info("wallet address api, insert into wallet_address %s"
                            % bhd_address.to_dict())
        except Exception as e:
            db.session.rollback()
            api_logger.error("generate address %s " % e)
            return make_resp(400, False, message="生成地址失败")
        return make_resp(**bhd_address.to_dict())

    def post(self):
        """
        转账
        :return:
        """
        parse = reqparse.RequestParser()
        parse.add_argument('coin_name', type=str, required=True, trim=True)
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
                account_key=account_key, coin_name=coin_name).with_for_update(read=True).first()
            if not user_asset:
                api_logger.error("withdrawal,user not found %s" % account_key)
                return make_resp(404, False, message="用户资产错误")

            key = "withdrawal:seccode:%s" % account_key
            seccode_cache = redis_auth.get(key)
            if seccode != seccode_cache:
                api_logger.error("withdrawal, seccode error")
                return make_resp(400, False, message="验证码错误")
            redis_auth.delete(key)
            api_logger.error(
                "withdrawal, user:%s, available_asset:%s, amount:%s"
                % (account_key, user_asset.available_asset, amount))
            if user_asset.available_asset < amount or user_asset.total_asset < amount:
                return make_resp(400, False, message="可用余额不足")

            client = get_rpc(coin_name)
            if not client.check_address(to_address):
                return make_resp(400, False, message="地址错误")
            if user_asset.get_available_margin_amount() < amount:
                return make_resp(400, False, message="可提现金额不足")
            user_asset.available_asset -= amount
            user_asset.frozen_asset += amount

            withdrawal_transaction = WithdrawalTransaction(account_key,
                                                           amount,
                                                           to_address,
                                                           coin_name=coin_name)
            db.session.add(withdrawal_transaction)
            db.session.commit()
        except Exception as e:
            api_logger.error("withdrawal, error %s" % str(e))
            db.session.rollback()
            return make_resp(500, False, message="提现申请提交失败")

        api_logger.info("Withdrawal api, insert into withdrawal_transaction %s"
                        % withdrawal_transaction.to_dict())

        return make_resp(200, True)

    def put(self):
        """
        撤销转账
        :return:
        """
        parse = reqparse.RequestParser()
        parse.add_argument('id', type=int, required=True)
        args = parse.parse_args()
        account_key = g.account_key
        id = args.get('id')
        coin_name = BHD_COIN_NAME

        withdrawal = WithdrawalTransaction.query.filter_by(
            id=id, account_key=account_key).first()
        if not withdrawal:
            api_logger.warning("account_key:%s, apply revocation:%s" % withdrawal.to_dict())
            return make_resp(406, False, message="撤销订单不存在")
        if withdrawal.status != WITHDRAWAL_APPLY:
            api_logger.warning(
                "account_key:%s, apply revocation:%s" % withdrawal.to_dict())
            return make_resp(400, False, message="订单状态不可撤销")
        try:
            user_asset = UserAsset.query.filter_by(
                account_key=account_key, coin_name=coin_name).with_for_update(read=True).first()

            user_asset.frozen_asset -= withdrawal.amount
            user_asset.available_asset += withdrawal.amount
            withdrawal.status = WITHDRAWAL_UNDO
            db.session.commit()
            api_logger.info("account_key:%s, revoke:%s " % (account_key, id))
            return make_resp(200)
        except Exception as e:
            api_logger.error("account_key:%s, 撤销转账失败:%s " % (account_key, e))
            withdrawal.status = WITHDRAWAL_FAILED
            db.session.rollback()
            return make_resp(400, False, message="撤销订单失败")


class UserAssetTransferInfoAPI(Resource):
    decorators = [login_required]

    transaction_types = {
        "deposit": DepositTranscation,
        "withdrawal": WithdrawalTransaction,
        "transfer": AssetTransfer,
        "block_earnings": IncomeRecord,
        "ecol_block_earnings": IncomeEcologyRecord,
        "dl_fraction": DeadlineFraction,
        "ecol_dl_fraction": DeadlineFractionEcology,
        "blocks": BurstBlock,
        "ecol_blocks": EcolBurstBlock,
        "day_earnings": IncomeRecord,
        "ecol_day_earnings": IncomeEcologyRecord,
        "activity_income": ActivityReward,
    }

    def get(self, transaction_type):
        if transaction_type not in transaction_type:
            return make_resp(404, message="查询列表内容不存在")
        account_key = g.account_key
        model = self.transaction_types.get(transaction_type)
        parse = reqparse.RequestParser()
        now = int(time.time())
        ten_days = now - 864000
        parse.add_argument('limit', type=int, required=False, default=10)
        parse.add_argument('offset', type=int, required=False, default=0)
        parse.add_argument('from', type=int, required=False, default=ten_days)
        parse.add_argument('end', type=int, required=False, default=now)
        parse.add_argument('coin_name', type=str, required=False)
        parse.add_argument('status', type=int, required=False)
        args = parse.parse_args()
        limit = args.get('limit')
        offset = args.get('offset')
        from_ts = args.get('from')
        end_ts = args.get('end')
        coin_name = args.get('coin_name')
        status = args.get('status')
        from_dt = datetime.fromtimestamp(from_ts)
        end_dt = datetime.fromtimestamp(end_ts)
        kwargs = {"account_key": account_key}

        if coin_name:
            kwargs['coin_name'] = coin_name
        if status:
            kwargs['status'] = status
        if "block_earnings" in transaction_type or "day_earnings" in transaction_type:
            # 只展示用户挖矿收益
            kwargs['type'] = IncomeTypeMining
        if "day_earnings" in transaction_type:
            infos = model.query.filter_by(
                **kwargs
            ).with_entities(
                func.sum(model.amount), func.max(model.create_time), func.avg(model.capacity),
            ).filter(
                and_(model.create_time > from_dt,
                     model.create_time < end_dt)
            ).order_by(
                model.create_time.desc()
            ).group_by(
                func.to_days(model.create_time)
            ).limit(limit).offset(offset).all()

            total_records = model.query.filter_by(
                **kwargs
            ).group_by(
                func.to_days(model.create_time)
            ).count()
            records = []
            for amount, create_time, capacity in infos:
                records.append({
                    "amount": amount,
                    "create_time": create_time,
                    "capacity": capacity,
                })
        else:
            infos = model.query.filter_by(
                **kwargs
            ).filter(
                and_(model.create_time > from_dt,
                     model.create_time < end_dt)
            ).order_by(
                model.create_time.desc()
            ).limit(limit).offset(offset).all()

            total_records = model.query.filter_by(
                **kwargs
            ).count()

            records = [info.to_dict() for info in infos]
        return make_resp(records=records, total_records=total_records)
