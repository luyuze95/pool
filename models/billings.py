# encoding=utf-8

"""
    @author: anzz
    @date: 2019/6/10
"""

from datetime import datetime
from models import db


class Billings(db.Model):
    """
    平台账单，记录所有资产转移记录。
    目前包括type：
        充提
            1、充值，
            2、提现，
        划转
            3、余额->抵押
            4、抵押->余额
        挖矿收益
            5、合作
            6、非合作
        7、活动奖励
        8、汇聚
    """
    __tablename__ = 'pool_billings'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    account_key = db.Column(db.String(64), index=True)
    to_address = db.Column(db.String(128), default='')
    from_address = db.Column(db.String(128), default='')
    amount = db.Column(db.DECIMAL(32, 16))
    txid = db.Column(db.String(256), default='')
    tag = db.Column(db.String(256), default='')
    type = db.Column(db.SmallInteger)
    create_time = db.Column(db.TIMESTAMP(), default=datetime.now)

    def __init__(self, account_key, amount, from_address, to_address, type, txid='', tag=''):
        self.account_key = account_key
        self.amount = amount
        self.from_address = from_address
        self.to_address = to_address
        self.type = type
        self.txid = txid
        self.tag = tag

    def to_dict(self):
        billing_dict = {
            "account_key": self.account_key,
            "from_address": self.from_address,
            "to_address": self.to_address,
            "amount": self.amount,
            "txid": self.txid,
            "create_time": str(self.create_time),
            "type": self.type,
        }

        return billing_dict
