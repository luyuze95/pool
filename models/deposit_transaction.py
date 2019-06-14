# encoding=utf-8

"""
    @author: anzz
    @date: 2019/5/29
"""
from datetime import datetime
from conf import DEPOSIT_CONFIRMING
from models import db


class DepositTranscation(db.Model):
    __tablename__ = 'pool_deposit_transaction'
    id = db.Column(db.Integer, primary_key=True)
    # 用户id
    account_key = db.Column(db.String(64), index=True)
    # 交易所在区块高度
    block_number = db.Column(db.Integer)
    # 确认数
    confirmed = db.Column(db.SmallInteger)
    # 需要确认数
    need_confirm_num = db.Column(db.SmallInteger)
    # 推送过的确认数
    pushed_confirm = db.Column(db.SmallInteger, server_default='0')
    # 币种名
    coin_name = db.Column(db.String(32))
    # 交易id
    tx_id = db.Column(db.String(255), index=True)
    # 充值数量
    amount = db.Column(db.DECIMAL(32, 16))

    # 交易状态，1 确认中， 2 成功, 3 失败
    status = db.Column(db.SmallInteger)
    create_time = db.Column(db.TIMESTAMP(), default=datetime.now)
    update_time = db.Column(db.TIMESTAMP(), default=datetime.now)
    # 是否发送到汇聚地址， 0， 未发送， 1， 发送
    is_pushed = db.Column(db.SmallInteger)

    __table_args__ = (db.UniqueConstraint('account_key', 'tx_id', name='account_key_unite_tx_id'), {'extend_existing': True})

    def __init__(self, account_key, amount, coin_name, tx_id, block_number,
                 need_confirm_num, confirmed=0):
        self.account_key = account_key
        self.amount = float(amount)
        self.coin_name = coin_name
        self.tx_id = tx_id
        self.status = DEPOSIT_CONFIRMING
        self.is_pushed = 0
        self.block_number = block_number
        self.need_confirm_num = need_confirm_num
        self.confirmed = confirmed
        self.pushed_confirm = -1

    def __setattr__(self, key, value):
        super(DepositTranscation, self).__setattr__(key, value)
        if key != "update_time":
            self.update_time = datetime.now()

    def to_dict(self):
        transaction_dict = {
            "account_key": self.account_key,
            "amount": self.amount,
            "coin_name": self.coin_name,
            "tx_id": self.tx_id,
            "block_number": self.block_number,
            "need_confirm_num": self.need_confirm_num,
            "confirmed": self.confirmed,
            "status": self.status,
            "create_time": str(self.create_time),
            "update_time": str(self.update_time),

        }
        return transaction_dict


