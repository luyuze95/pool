# encoding=utf-8

"""
    @author: anzz
    @date: 2019/5/29
"""
from datetime import datetime
from models import db


class AssetTransfer(db.Model):
    __tablename__ = 'pool_asset_transfer'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    account_key = db.Column(db.String(64), index=True)
    amount = db.Column(db.DECIMAL(32, 16))
    direction = db.Column(db.BOOLEAN, comment="True:抵押到余额，False:余额到抵押")
    create_time = db.Column(db.TIMESTAMP(), default=datetime.now)
    coin_name = db.Column(db.String(32), default='0')

    def __init__(self, account_key, amount, direction, coin_name):
        self.account_key = account_key
        self.amount = amount
        self.direction = direction
        self.coin_name = coin_name

    def to_dict(self):
        transfer_dict = {
            "account_key": self.account_key,
            "amount": self.amount,
            "coin_name": self.coin_name,
            "direction": self.direction,
            "create_time": str(self.create_time),
        }

        return transfer_dict
