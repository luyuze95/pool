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
from models.billings import Billings
from models.income_record import IncomeRecord, IncomeEcologyRecord
from models.user_asset import UserAsset
from rpc.bhd_rpc import bhd_client
from conf import *
from utils.redis_ins import redis_capacity


@celery.task
def calculate_income():
    # 查询未统计收益
    calculate_income_lock = redis_capacity.get("calculate_income_lock")
    if calculate_income_lock:
        return
    redis_capacity.set("calculate_income_lock", 1)
    latest_height = bhd_client.get_latest_block_number()
    mature_height = latest_height - 100
    not_add_incomes = IncomeRecord.query.filter(and_(IncomeRecord.is_add_asset==0,
                                                     IncomeRecord.height<mature_height)).all()
    for income in not_add_incomes:
        try:
            income_num = income.query.filter_by(id=income.id, is_add_asset=0).update({IncomeRecord.is_add_asset: 1})
            if income_num == 0:
                continue

            user_asset = UserAsset.query.filter_by(
                account_key=income.account_key,
                coin_name=BHD_COIN_NAME).with_for_update(
                read=False).first()
            # 添加用户资产
            if not user_asset:
                continue
            user_asset.available_asset += income.amount
            user_asset.total_asset += income.amount
            # income.update(is_add_asset=1).where(id=income.id, is_add_asset=0)
            celery_logger.info("user:%s, income %s " % (
                user_asset.to_dict(), income.to_dict()))
            income_type = MINING_COOPERATION
            if income.type == IncomeTYpeCoopReward:
                income_type = COOP_MINE_EARNINGS
            billing = Billings(user_asset.account_key, income.amount, '', '', income_type, create_time=income.create_time)
            db.session.add(billing)
            db.session.commit()
        except Exception as e:
            celery_logger.error("calculate_income error:%s" % str(e))
            db.session.rollback()
    redis_capacity.delete("calculate_income_lock")


@celery.task
def calculate_income_ecol():
    # 查询未统计收益
    latest_height = bhd_client.get_latest_block_number()
    mature_height = latest_height - 100
    not_add_incomes = IncomeEcologyRecord.query.filter(and_(IncomeEcologyRecord.is_add_asset==0,
                                                            IncomeEcologyRecord.height>mature_height))
    for income in not_add_incomes:
        try:
            income_num = income.query.filter_by(id=income.id, is_add_asset=0).update({IncomeRecord.is_add_asset: 1})
            if income_num == 0:
                continue
            user_asset = UserAsset.query.filter_by(
                account_key=income.account_key,
                coin_name=BHD_COIN_NAME).with_for_update(
                read=False).first()
            if not user_asset:
                continue
            # 添加用户资产
            user_asset.available_asset += income.amount
            user_asset.total_asset += income.amount
            billing = Billings(user_asset.account_key, income.amount, '', '', ECOL_MINE_EARNINGS, create_time=income.create_time)
            db.session.add(billing)
            celery_logger.info("user:%s, income %s " % (
                user_asset.to_dict(), income.to_dict()))
            db.session.commit()
        except Exception as e:
            celery_logger.error("calculate_income error:%s" % str(e))
            db.session.rollback()


@celery.task
def calculate_activity_reward():
    calculate_activity_reward_lock = redis_capacity.get("calculate_activity_reward_lock")
    if calculate_activity_reward_lock:
        return
    redis_capacity.set("calculate_activity_reward_lock", 1)
    rewards = ActivityReward.query.filter_by(is_add_asset=0).all()
    if not rewards:
        return
    for reward in rewards:
        try:
            income_num = reward.query.filter_by(id=reward.id, is_add_asset=0).update({ActivityReward.is_add_asset: 1})
            if income_num == 0:
                continue
            user_asset = UserAsset.query.filter_by(
                account_key=reward.account_key).with_for_update(
                read=True).first()
            if not user_asset:
                continue
            # 添加用户资产
            if reward.amount > 0:
                user_asset.available_asset += reward.amount
                user_asset.total_asset += reward.amount
            billing = Billings(user_asset.account_key, reward.amount, '', '', ACTIVITY_REWORD)
            db.session.add(billing)
            celery_logger.info("user:%s, income %s " % (
                user_asset.to_dict(), reward.to_dict()))
            db.session.commit()
        except Exception as e:
            celery_logger.error("calculate_activity_reward error:%s" % str(e))
            db.session.rollback()
    redis_capacity.delete("calculate_activity_reward_lock")