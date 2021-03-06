# encoding=utf-8

"""
    @author: lyz
    @date: 2019/9/23
"""
from sqlalchemy import and_

from app import celery
from models import db
from logs import celery_logger
from models.activity_reward import ActivityReward
from models.billings import Billings
from models.income_record import IncomeRecord, IncomeEcologyRecord, NBIncomeRecord, \
    LHDIncomeRecord, DISKIncomeRecord, HDDIncomeRecord
from models.user_asset import UserAsset
from rpc import nb_client, lhd_client
from rpc.bhd_rpc import bhd_client
from rpc.disk_rpc import disk_client
from rpc.hdd_rpc import hdd_client
from conf import *
from schedule.distributed_lock_decorator import distributed_lock


@celery.task
@distributed_lock
def calculate_income():
    # 查询未统计收益
    latest_height = bhd_client.get_latest_block_number()
    mature_height = latest_height - 6
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


@celery.task
@distributed_lock
def nb_calculate_income():
    # 查询未统计收益
    latest_height = nb_client.get_latest_block_number()
    mature_height = latest_height - 6
    not_add_incomes = NBIncomeRecord.query.filter(and_(NBIncomeRecord.is_add_asset==0,
                                                       NBIncomeRecord.height<mature_height)).all()
    for income in not_add_incomes:
        try:
            income_num = income.query.filter_by(id=income.id, is_add_asset=0).update({NBIncomeRecord.is_add_asset: 1})
            if income_num == 0:
                continue

            user_asset = UserAsset.query.filter_by(
                account_key=income.account_key,
                coin_name=NEWBI_NAME).with_for_update(
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


@celery.task
@distributed_lock
def lhb_calculate_income():
    # 查询未统计收益
    latest_height = lhd_client.get_latest_block_number()
    mature_height = latest_height - 6
    not_add_incomes = LHDIncomeRecord.query.filter(and_(LHDIncomeRecord.is_add_asset==0,
                                                        LHDIncomeRecord.height<mature_height)).all()
    for income in not_add_incomes:
        try:
            income_num = income.query.filter_by(id=income.id, is_add_asset=0).update({LHDIncomeRecord.is_add_asset: 1})
            if income_num == 0:
                continue

            user_asset = UserAsset.query.filter_by(
                account_key=income.account_key,
                coin_name=LHD_NAME).with_for_update(
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


@celery.task
@distributed_lock
def disk_calculate_income():
    # 查询未统计收益
    latest_height = disk_client.get_latest_block_number()
    mature_height = latest_height - 6
    not_add_incomes = DISKIncomeRecord.query.filter(and_(DISKIncomeRecord.is_add_asset == 0,
                                                        DISKIncomeRecord.height < mature_height)).all()
    for income in not_add_incomes:
        try:
            income_num = income.query.filter_by(id=income.id, is_add_asset=0).update({DISKIncomeRecord.is_add_asset: 1})
            if income_num == 0:
                continue

            user_asset = UserAsset.query.filter_by(
                account_key=income.account_key,
                coin_name=DISK_NAME).with_for_update(
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


@celery.task
@distributed_lock
def hdd_calculate_income():
    # 查询未统计收益
    latest_height = hdd_client.get_latest_block_number()
    mature_height = latest_height - 6
    not_add_incomes = HDDIncomeRecord.query.filter(and_(HDDIncomeRecord.is_add_asset == 0,
                                                        HDDIncomeRecord.height < mature_height)).all()
    for income in not_add_incomes:
        try:
            income_num = income.query.filter_by(id=income.id, is_add_asset=0).update({HDDIncomeRecord.is_add_asset: 1})
            if income_num == 0:
                continue

            user_asset = UserAsset.query.filter_by(
                account_key=income.account_key,
                coin_name=HDD_NAME).with_for_update(
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


@celery.task
def calculate_income_ecol():
    # 查询未统计收益
    latest_height = bhd_client.get_latest_block_number()
    mature_height = latest_height - 6
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
