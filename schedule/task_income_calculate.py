# encoding=utf-8

"""
    @author: anzz
    @date: 2019/5/29
"""
from sqlalchemy import and_

from app import celery
from models import db
from logs import celery_logger
from models.income_record import IncomeRecord
from models.user_asset import UserAsset
from rpc.bhd_rpc import bhd_client


@celery.task
def calculate_income():
    # 查询未统计收益
    latest_height = bhd_client.get_latest_block_number()
    mature_height = latest_height - 100
    not_add_incomes = IncomeRecord.query.filter(and_(IncomeRecord.is_add_asset==0,
                                                     IncomeRecord.height>mature_height))
    for income in not_add_incomes:
        try:
            user_asset = UserAsset.query.filter_by(
                account_key=income.account_key).with_for_update(
                read=True).first()
            db.session.begin_nested()
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
