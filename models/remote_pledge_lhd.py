# encoding=utf-8

"""
    @author: anzz
    @date: 2019/6/25
"""

from sqlalchemy import func

from models import db
from conf import *
from models.base import BaseModel


class LHDRemotePledgeAddress(db.Model):
    __tablename__ = 'pool_lhd_pledge_ro'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    # 用户account_key
    account_key = db.Column(db.String(64), index=True)
    # 用户远程抵押地址
    address = db.Column(db.String(64), index=True)
    # 1可用，0禁止
    status = db.Column(db.Integer)

    create_time = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())
    update_time = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())

    def to_dict(self):
        remote_pledge_dict = {
            "account_key": self.account_key,
            "address": self.address,
            "status": self.status,
            "create_time": str(self.create_time),
        }
        return remote_pledge_dict


class LHDRemotePledgeTransaction(BaseModel):
    __tablename__ = 'pool_lhd_remote_pledge_transaction'
    __table_args__ = {'extend_existing': True}
    # id
    id = db.Column(db.Integer, primary_key=True)
    # 用户account_key
    account_key = db.Column(db.String(64), index=True)
    # 用户远程抵押地址
    pledge_address = db.Column(db.String(64), index=True)
    # 抵押数量
    pledge_amount = db.Column(db.DECIMAL(32, 16))
    # 抵押高度
    pledge_height = db.Column(db.Integer)
    # 抵押交易id
    pledge_txid = db.Column(db.String(64), unique=True)

    # 抵押状态, 抵押状态。1，抵押撤销，0
    status = db.Column(db.Integer)

    create_time = db.Column(db.TIMESTAMP(),
                            server_default=func.current_timestamp())
    update_time = db.Column(db.TIMESTAMP(),
                            server_default=func.current_timestamp())

    def __init__(self, account_key, pledge_address, pledge_amount, pledge_height,
                 pledge_txid):
        self.account_key = account_key
        self.pledge_address = pledge_address
        self.pledge_amount = pledge_amount
        self.pledge_height = pledge_height
        self.pledge_txid = pledge_txid
        self.status = DEBITING

    def to_dict(self):
        remote_pledge_tr_dict = {
            "account_key": self.account_key,
            "pledge_address": self.pledge_address,
            "pledge_amount": self.pledge_amount,
            "pledge_height": self.pledge_height,
            "pledge_txid": self.pledge_txid,
            "status": self.status,
            "create_time": str(self.create_time),
        }
        return remote_pledge_tr_dict


class LHDTeamWorkRecordActivity(BaseModel):
    __tablename__ = 'pool_lhd_team_work_record_activity'
    __table_args__ = {'extend_existing': True}
    # id
    id = db.Column(db.Integer, primary_key=True)
    account_key = db.Column(db.String(64), index=True)
    order_id = db.Column(db.BigInteger)
    income = db.Column(db.DECIMAL(32, 16))
    coo_amount = db.Column(db.DECIMAL(32, 16))
    # 1进行中，0已结束
    status = db.Column(db.Integer)
    is_foul = db.Column(db.Integer)
    cooperation_id = db.Column(db.Integer)

    release_time = db.Column(db.TIMESTAMP(),
                             server_default=func.current_timestamp())
    begin_time = db.Column(db.TIMESTAMP(),
                           server_default=func.current_timestamp())
    end_time = db.Column(db.TIMESTAMP(),
                         server_default=func.current_timestamp())
    create_time = db.Column(db.TIMESTAMP(),
                            server_default=func.current_timestamp())
    update_time = db.Column(db.TIMESTAMP(),
                            server_default=func.current_timestamp())

    def to_dict(self):
        tr_dict = {
            "account_key": self.account_key,
            "order_id": self.order_id,
            "income": self.income,
            "coo_amount": self.coo_amount,
            "status": self.status,
            "cooperation_id": self.cooperation_id,
            "is_foul": self.is_foul,
            "create_time": str(self.create_time),
        }
        return tr_dict


class LHDTeamWorkActivity(BaseModel):
    __tablename__ = 'pool_lhd_team_work_activity'
    __table_args__ = {'extend_existing': True}
    # id
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    total_amount = db.Column(db.DECIMAL(32, 16))
    distribution = db.Column(db.DECIMAL(32, 16))
    available_amount = db.Column(db.DECIMAL(32, 16))
    deadline = db.Column(db.DECIMAL(32, 16))
    min_amount = db.Column(db.DECIMAL(32, 16))
    type = db.Column(db.INTEGER)
    rate = db.Column(db.DECIMAL(32, 16))

    create_time = db.Column(db.TIMESTAMP(),
                            server_default=func.current_timestamp())
    update_time = db.Column(db.TIMESTAMP(),
                            server_default=func.current_timestamp())
    end_time = db.Column(db.TIMESTAMP(),
                         server_default=func.current_timestamp())

    def to_dict(self):
        tr_dict = {
            "title": self.title,
            "total_amount": self.total_amount,
            "distribution": self.distribution,
            "available_amount": self.available_amount,
            "deadline": self.deadline,
            "min_amount": self.min_amount,
            "type": self.type,
            "rate": self.rate,
            "create_time": str(self.create_time),
            "end_time": str(self.end_time),
        }
        return tr_dict
