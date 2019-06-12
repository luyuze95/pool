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
from conf import *


@celery.task
def withdrawal_coin():
    withdrawal_applys = WithdrawalTransaction.query.filter_by(status=WITHDRAWAL_PASS).all()
    for withdrawal_apply in withdrawal_applys:
        account_key = withdrawal_apply.account_key

        user_asset = UserAsset.query.filter_by(
            account_key=account_key).with_for_update(read=True).first()
        assert user_asset
        assert withdrawal_apply.amount <= user_asset.frozen_asset
        try:
            txid = bhd_client.withdrawal(withdrawal_apply.to_address,
                                         withdrawal_apply.actual_amount)
            status = WITHDRAWAL_SENDING
        except Exception as e:
            celery_logger.error("withdrawal task,withdrawal error %s" % str(e))
            txid = 0
            status = WITHDRAWAL_FAILED
        try:
            if status == WITHDRAWAL_SENDING:
                user_asset.frozen_asset -= withdrawal_applys.amount
                user_asset.total_asset -= withdrawal_applys.amount
            withdrawal_apply.txid = txid
            withdrawal_apply.status = status
            db.session.commit()
            celery_logger.info(
                "withdrawal task success, %s" % withdrawal_apply.to_dict())
        except Exception as e:
            db.session.rollback()
            celery_logger.error("withdrawal task, error %s" % str(e))
            continue


@celery.task
def withdrawal_confirm():
    withdrawal_sendings = WithdrawalTransaction.query.filter_by(
        status=WITHDRAWAL_SENDING).all()

    for withdrawal_sending in withdrawal_sendings:
        detail = bhd_client.get_transaction_detail(withdrawal_sending.txid)
        confirmed = detail.get('confirmations', 0)
        if confirmed > MIN_CONFIRMED[BHD_COIN_NAME]:
            try:
                withdrawal_sending.status = WITHDRAWAL_SENDED
                celery_logger.info("withdrawal confirmed %s " % withdrawal_sending.to_dict())
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                celery_logger.error("withdrawal confirmed, error %s" % str(e))
