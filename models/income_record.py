# encoding=utf-8

"""
    @author: anzz
    @date: 2019/5/29
"""

from datetime import datetime

from models import db


class IncomeRecord(db.Model):
    __tablename__ = 'pool_bhd_income_record'
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
    # 矿机名
    capacity = db.Column(db.DECIMAL(32, 16))

    # 是否已经计算收益
    is_add_asset = db.Column(db.SmallInteger)

    create_time = db.Column(db.TIMESTAMP(), default=datetime.now)
    update_time = db.Column(db.TIMESTAMP(), default=datetime.now)

    def __setattr__(self, key, value):
        super(IncomeRecord, self).__setattr__(key, value)
        if key != "update_time":
            self.update_time = datetime.now()

    def to_dict(self):
        income_record_dict = {
            "account_key": self.account_key,
            "amount": self.amount,
            "actual_amount": self.actual_amount,
            "height": self.height,
            "mortgage_rate": self.mortgage_rate,
            "create_time": self.create_time,
            "is_add_asset": self.is_add_asset,
            "capacity": self.capacity,
        }
        return income_record_dict
