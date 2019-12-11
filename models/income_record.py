# encoding=utf-8

"""
    @author: lyz
    @date: 2019/5/29
"""

from datetime import datetime

from models import db
from models.base import BaseModel


class IncomeMixin(BaseModel):
    __abstract__ = True
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    # 用户id
    account_key = db.Column(db.String(36))
    # 区块收益bhd数量
    amount = db.Column(db.DECIMAL(32, 16))
    # 实际获取数量
    actual_amount = db.Column(db.DECIMAL(32, 16))
    # 挖出区块高度
    height = db.Column(db.INTEGER)

    # 矿工抵押率
    mortgage_rate = db.Column(db.DECIMAL(32, 16))
    # 类型
    type = db.Column(db.INTEGER)
    # 容量
    capacity = db.Column(db.DECIMAL(32, 16))

    # 是否已经计算收益
    is_add_asset = db.Column(db.SmallInteger)

    create_time = db.Column(db.TIMESTAMP(), default=datetime.now)
    update_time = db.Column(db.TIMESTAMP(), default=datetime.now)

    def __init__(self, account_key, amount, income_type, is_add_asset=0, capacity=0):
        self.account_key = account_key
        self.amount = amount
        self.actual_amount = amount
        self.mortgage_rate = 1
        self.type = income_type
        self.is_add_asset = is_add_asset
        self.capacity = capacity

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        if key != "update_time":
            self.update_time = datetime.now()

    def to_dict(self):
        income_record_dict = {
            "account_key": self.account_key,
            "amount": self.amount,
            "actual_amount": self.actual_amount,
            "height": self.height,
            "mortgage_rate": self.mortgage_rate,
            "create_time": str(self.create_time),
            "is_add_asset": self.is_add_asset,
            "capacity": self.capacity,
            "type": self.type,
        }
        return income_record_dict


class IncomeRecord(IncomeMixin, db.Model):
    __tablename__ = 'pool_bhd_income_record'


class IncomeEcologyRecord(IncomeMixin, db.Model):
    __tablename__ = 'pool_bhd_ecology_income_record'


class NBIncomeRecord(IncomeMixin, db.Model):
    __tablename__ = 'pool_newbi_income_record'


class LHDIncomeRecord(IncomeMixin, db.Model):
    __tablename__ = 'pool_lhd_income_record'


class DISKIncomeRecord(IncomeMixin, db.Model):
    __tablename__ = 'pool_disk_income_record'


class HDDIncomeRecord(IncomeMixin, db.Model):
    __tablename__ = 'pool_hdd_income_record'
