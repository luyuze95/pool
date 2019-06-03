# encoding=utf-8

"""
    @author: anzz
    @date: 2019/6/3
"""

from app import celery
from logs import celery_logger
from models import db
from models.user_asset import UserAsset
from models.withdrawal_transactions import WithdrawalTransaction
from rpc.bhd_rpc import bhd_client


@celery.task
def withdrawal_coin():
    withdrawal_applys = WithdrawalTransaction.query.filter_by(status=2).all()
    for withdrawal_apply in withdrawal_applys:
        account_key = withdrawal_apply.account_key
        user_asset = UserAsset.query.filter_by(
            account_key=account_key).with_for_update(read=True).first()
        assert user_asset
        assert withdrawal_apply.mount <= user_asset.frozen_asset
        try:
            user_asset.frozen_asset -= withdrawal_apply.mount
            user_asset.total_asset -= withdrawal_apply.mount
            txid = bhd_client.withdrawal(withdrawal_apply.to_address,
                                         withdrawal_apply.mount)
            withdrawal_apply.txid = txid
            withdrawal_apply.status = 3
        except Exception as e:
            celery_logger.error("withdrawal task, error %s" % str(e))
            db.session.rollback()
            continue
        celery_logger.info(
            "withdrawal task success, %s" % withdrawal_apply.to_dict())
