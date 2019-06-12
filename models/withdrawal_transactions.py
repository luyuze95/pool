# encoding=utf-8

"""
    @author: anzz
    @date: 2019/5/29
"""
from datetime import datetime
from models import db
from conf import *


class WithdrawalTransaction(db.Model):
    __tablename__ = 'pool_withdrawal_transaction'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    account_key = db.Column(db.String(64), index=True)
    to_address = db.Column(db.String(128))
    amount = db.Column(db.DECIMAL(32, 16))
    actual_amount = db.Column(db.DECIMAL(32, 16))
    coin_name = db.Column(db.String(32))
    txid = db.Column(db.String(256), default='')
    status = db.Column(db.SmallInteger, default='1')
    create_time = db.Column(db.TIMESTAMP(), default=datetime.now)

    def __init__(self, account_key, amount, to_address, status=WITHDRAWAL_APPLY, coin_name=BHD_COIN_NAME):
        self.account_key = account_key
        self.amount = amount
        self.coin_name = coin_name
        self.to_address = to_address
        self.actual_amount = amount*WITHDRAWAL_ACTUAL
        self.status = status

    def to_dict(self):
        withdrawal_transaction_dict = {
            "id": self.id,
            "account_key": self.account_key,
            "to_address": self.to_address,
            "amount": self.amount,
            "coin_name": self.coin_name,
            "txid": self.txid,
            "create_time": str(self.create_time),
            "status": self.status,
        }

        return withdrawal_transaction_dict
