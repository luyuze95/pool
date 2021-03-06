# encoding=utf-8

"""
    @author: lyz
    @date: 2019/5/29
"""
from _decimal import ROUND_DOWN
from datetime import datetime
from models import db
from conf import *
from models.base import BaseModel


class WithdrawalTransaction(BaseModel):
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
        if coin_name == DISK_NAME:
            if amount < 50:
                raise ValueError
            elif amount >= 50 and amount <= 500:
                self.actual_amount = (amount - Decimal("5")).quantize(Decimal('.00000000'), rounding=ROUND_DOWN)
            elif amount > 500:
                self.actual_amount = (amount * DISK_WITHDRAWAL_ACTUAL).quantize(Decimal('.00000000'), rounding=ROUND_DOWN)
        else:
            if amount < 100:
                self.actual_amount = (amount - Decimal("0.1")).quantize(Decimal('.00000000'), rounding=ROUND_DOWN)
            else:
                self.actual_amount = (amount * WITHDRAWAL_ACTUAL).quantize(Decimal('.00000000'), rounding=ROUND_DOWN)
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
