# encoding=utf-8

"""
    @author: anzz
    @date: 2019/5/30
"""

from datetime import datetime

from sqlalchemy import func

from models import db


class MinerPlotter(db.Model):
    __tablename__ = 'pool_miner_plotter'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    # 用户id
    account_key = db.Column(db.String(64), index=True)
    # 用户id
    plotter_id = db.Column(db.String(64))
    # 矿工名
    miner_name = db.Column(db.String(256))
    # 矿机容量
    capacity = db.Column(db.BigInteger)

    create_time = db.Column(db.TIMESTAMP(), default=datetime.now)
    update_time = db.Column(db.TIMESTAMP(), default=datetime.now)

    def __setattr__(self, key, value):
        super(MinerPlotter, self).__setattr__(key, value)
        if key != "update_time":
            self.update_time = datetime.now()

    def to_dict(self):
        miner_plotter_dict = {
            "account_key": self.account_key,
            "miner_name": self.miner_name,
            "capacity": self.capacity,
            "create_time": self.create_time,
            "update_time": self.update_time,
        }
        return miner_plotter_dict
