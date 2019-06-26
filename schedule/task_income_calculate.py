# encoding=utf-8

"""
    @author: anzz
    @date: 2019/5/29
"""
from sqlalchemy import and_

from app import celery
from models import db
from logs import celery_logger
from models.activity_reward import ActivityReward
from models.income_record import IncomeRecord, IncomeEcologyRecord
from models.user_asset import UserAsset
from rpc.bhd_rpc import bhd_client
from conf import *


@celery.task
def calculate_income():
    # 查询未统计收益
    latest_height = bhd_client.get_latest_block_number()
    mature_height = latest_height - 100
    not_add_incomes = IncomeRecord.query.filter(and_(IncomeRecord.is_add_asset==0,
                                                     IncomeRecord.height<mature_height))
    for income in not_add_incomes:
        try:
            user_asset = UserAsset.query.filter_by(
                account_key=income.account_key,
                coin_name=BHD_COIN_NAME).with_for_update(
                read=True).first()
            # 添加用户资产
            user_asset.available_asset += income.amount
            user_asset.total_asset += income.amount
            income.is_add_asset = 1
            celery_logger.info("user:%s, income %s " % (
                user_asset.to_dict(), income.to_dict()))
            db.session.commit()
        except Exception as e:
            celery_logger.error("calculate_income error:%s" % str(e))
            db.session.rollback()


@celery.task
def calculate_income_ecol():
    # 查询未统计收益
    latest_height = bhd_client.get_latest_block_number()
    mature_height = latest_height - 100
    not_add_incomes = IncomeEcologyRecord.query.filter(and_(IncomeEcologyRecord.is_add_asset==0,
                                                            IncomeEcologyRecord.height>mature_height))
    for income in not_add_incomes:
        try:
            user_asset = UserAsset.query.filter_by(
                account_key=income.account_key,
                coin_name=BHD_COIN_NAME).with_for_update(
                read=True).first()
            # 添加用户资产
            user_asset.available_asset += income.amount
            user_asset.total_asset += income.amount
            income.is_add_asset = 1
            celery_logger.info("user:%s, income %s " % (
                user_asset.to_dict(), income.to_dict()))
            db.session.commit()
        except Exception as e:
            celery_logger.error("calculate_income error:%s" % str(e))
            db.session.rollback()


@celery.task
def calculate_activity_reward():
    rewards = ActivityReward.query.filter_by(is_add_asset=0).all()
    if not rewards:
        return
    for reward in rewards:
        try:
            user_asset = UserAsset.query.filter_by(
                account_key=reward.account_key).with_for_update(
                read=True).first()
            # 添加用户资产
            if reward.amount > 0:
                user_asset.available_asset += reward.amount
                user_asset.total_asset += reward.amount
            reward.is_add_asset = 1
            celery_logger.info("user:%s, income %s " % (
                user_asset.to_dict(), reward.to_dict()))
            db.session.commit()
        except Exception as e:
            celery_logger.error("calculate_activity_reward error:%s" % str(e))
            db.session.rollback()