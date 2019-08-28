# encoding=utf-8

"""
    @author: anzz
    @date: 2019/5/29
"""

from celery.schedules import crontab

from app import celery
from conf import *
from schedule.task_bhd_deposit import confirm_deposit_transaction, \
    deposit_add_asset, bhd_deposit_scan, usdt_deposit_scan, nb_deposit_scan, \
    lhd_deposit_scan
from schedule.task_converge import bhd_converge, usdt_converge, lhd_converge
from schedule.task_email import email_sender_task
from schedule.task_income_calculate import calculate_income, \
    calculate_activity_reward, nb_calculate_income, lhb_calculate_income
from schedule.task_timing_remote_pledge_lhd import lhd_check_pledges, lhd_statistic_pledges
from schedule.task_withdrawal import withdrawal_coin, withdrawal_confirm
from schedule.task_timing_remote_pledge import statistic_pledges, check_pledges


@celery.on_after_configure.connect
def setup_period_task(sender, **kwargs):
    sender.add_periodic_task(crontab(minute='*/1'),
                             confirm_deposit_transaction.s())
    sender.add_periodic_task(crontab(minute='*/1'),
                             bhd_deposit_scan.s())
    sender.add_periodic_task(crontab(minute='*/15'),
                             usdt_deposit_scan.s())
    sender.add_periodic_task(crontab(minute='*/1'),
                             deposit_add_asset.s())
    sender.add_periodic_task(crontab(minute='*/5'),
                             calculate_income.s())
    # sender.add_periodic_task(crontab(minute='*/5'),
    #                          calculate_income_ecol.s())
    sender.add_periodic_task(crontab(minute='*/5'),
                             withdrawal_coin.s())
    sender.add_periodic_task(crontab(minute='*/3'),
                             withdrawal_confirm.s())
    sender.add_periodic_task(crontab(minute='*/60'),
                             bhd_converge.s())
    # sender.add_periodic_task(crontab(minute='*/90'),
    #                          usdt_converge.s())
    sender.add_periodic_task(crontab(hour='0'),
                             calculate_activity_reward.s())
    sender.add_periodic_task(crontab(minute="*/1"),
                             statistic_pledges.s())
    sender.add_periodic_task(crontab(minute="*/1"),
                             check_pledges.s())
    sender.add_periodic_task(crontab(minute="*/1"),
                             nb_deposit_scan.s())
    sender.add_periodic_task(crontab(minute="*/1"),
                             nb_calculate_income.s())
    sender.add_periodic_task(crontab(minute="*/1"),
                             lhb_calculate_income.s())
    sender.add_periodic_task(crontab(minute="*/1"),
                             lhd_deposit_scan.s())
    sender.add_periodic_task(crontab(minute="*/1"),
                             lhd_statistic_pledges.s())
    sender.add_periodic_task(crontab(minute="*/1"),
                             lhd_check_pledges.s())
    sender.add_periodic_task(crontab(minute="*/1"),
                             lhd_converge.s())

