# encoding=utf-8

"""
    @author: anzz
    @date: 2019/5/29
"""

from celery.schedules import crontab

from app import celery
from models import db
from conf import *
from logs import celery_logger
from models.bhd_address import BhdAddress
from rpc.bhd_rpc import bhd_client
from schedule.task_bhd_deposit import bhd_block_number_deposit_task, \
    confirm_deposit_transaction, bhd_block_scan
from schedule.task_email import email_sender_task
from schedule.task_income_calculate import calculate_income


@celery.on_after_configure.connect
def setup_period_task(sender, **kwargs):
    # sender.add_periodic_task(crontab(minute='*/3'),
    #                          add_wallet_address.s())
    sender.add_periodic_task(crontab(minute='*/1'),
                             bhd_block_scan.s())
    sender.add_periodic_task(crontab(minute='*/1'),
                             confirm_deposit_transaction.s())
    sender.add_periodic_task(crontab(hour='*/24'),
                             calculate_income.s())


@celery.task
def add_wallet_address():
    remaining_address_count = BhdAddress.query.filter_by(occupied=0).count()
    add_address_count = 0
    if remaining_address_count < ADDRESS_LEAST_REMAINING_COUNT:
        add_address_count = ADDRESS_LEAST_REMAINING_COUNT - remaining_address_count
    try:
        for _ in range(add_address_count):
            addr, pub_key, private_key = bhd_client.generate_address()
            address_orm = BhdAddress(addr.lower(), pub_key, private_key, addr, )
            db.session.add(address_orm)
            db.session.commit()
    except Exception as e:
        celery_logger.error(str(e))


