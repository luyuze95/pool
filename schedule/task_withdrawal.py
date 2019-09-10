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
from rpc import get_rpc
from conf import *
from schedule.distributed_lock_decorator import distributed_lock


@celery.task
@distributed_lock
def withdrawal_coin():
    withdrawal_applys = WithdrawalTransaction.query.filter_by(status=WITHDRAWAL_PASS).all()
    if not withdrawal_applys:
        return
    for withdrawal_apply in withdrawal_applys:
        account_key = withdrawal_apply.account_key

        try:
            user_asset = UserAsset.query.filter_by(
                account_key=account_key, coin_name=withdrawal_apply.coin_name).with_for_update(read=True).first()
            assert user_asset
            assert withdrawal_apply.amount <= user_asset.frozen_asset
            assert withdrawal_apply.amount <= user_asset.total_asset - user_asset.available_asset - user_asset.trading_asset - user_asset.pledge_asset

            client = get_rpc(withdrawal_apply.coin_name)
            txid = client.withdrawal(withdrawal_apply.to_address, withdrawal_apply.actual_amount)
            status = WITHDRAWAL_SENDING
            user_asset.frozen_asset -= withdrawal_apply.amount
            user_asset.total_asset -= withdrawal_apply.amount
        except Exception as e:
            celery_logger.error("withdrawal task,withdrawal error %s" % str(e))
            txid = 0
            status = WITHDRAWAL_FAILED
        try:
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
@distributed_lock
def withdrawal_confirm():
    withdrawal_sendings = WithdrawalTransaction.query.filter_by(
        status=WITHDRAWAL_SENDING).all()
    if not withdrawal_sendings:
        return

    for withdrawal_sending in withdrawal_sendings:
        client = get_rpc(withdrawal_sending.coin_name)
        detail = client.get_transaction_detail(withdrawal_sending.txid)
        confirmed = detail.get('confirmations', 0)
        if confirmed > MIN_CONFIRMED[withdrawal_sending.coin_name]:
            try:
                withdrawal_sending.status = WITHDRAWAL_SENDED
                celery_logger.info("withdrawal confirmed %s " % withdrawal_sending.to_dict())
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                celery_logger.error("withdrawal confirmed, error %s" % str(e))
