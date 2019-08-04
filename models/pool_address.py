# encoding=utf-8

"""
    @author: anzz
    @date: 2019/5/29
"""
from datetime import datetime

from models import db
from conf import BHD_COIN_NAME
from models.base import BaseModel
from utils.crypto import crypto


class PoolAddress(BaseModel):
    __tablename__ = 'pool_address'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    account_key = db.Column(db.String(64), index=True)
    coin_name = db.Column(db.String(64), default=BHD_COIN_NAME, nullable=False)
    address = db.Column(db.String(42), index=True, nullable=False)
    private_key_crypto = db.Column(db.BLOB(1024), nullable=False)
    create_time = db.Column(db.TIMESTAMP(), default=datetime.now)
    update_time = db.Column(db.TIMESTAMP(), default=datetime.now)

    def __init__(self, account_key, address, private_key,
                 coin_name=BHD_COIN_NAME) -> None:
        self.account_key = account_key
        self.address = address
        self.private_key = private_key
        self.coin_name = coin_name

    @property
    def private_key(self):
        if self.private_key_crypto is None:
            return
        pk = crypto.decrypt(self.private_key_crypto)
        return pk.decode()

    @private_key.setter
    def private_key(self, v):
        if v is None:
            self.private_key_crypto = None
            return
        pkc = crypto.encrypt(v)
        self.private_key_crypto = pkc

    def to_dict(self):
        dict_addr = {
            "account_key": self.account_key,
            "address": self.address,
            "coin_name": self.coin_name,
            "create_time": str(self.create_time),
            "update_time": str(self.update_time),
        }

        return dict_addr

    def __setattr__(self, key, value):
        super(PoolAddress, self).__setattr__(key, value)
        if key != "update_time":
            self.update_time = datetime.now()
