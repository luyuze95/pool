# encoding=utf-8

"""
    @author: anzz
    @date: 2019/6/10
"""

from datetime import datetime
from models import db


class DeadlineFraction(db.Model):
    __tablename__ = 'pool_bhd_fraction_record'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    account_key = db.Column(db.String(64), index=True)
    plotter_id = db.Column(db.String(64), index=True)
    miner_name = db.Column(db.String(64), index=True)
    fraction = db.Column(db.DECIMAL(32, 16))
    capacity = db.Column(db.DECIMAL(32, 16))
    height = db.Column(db.INTEGER)
    create_time = db.Column(db.TIMESTAMP(), default=datetime.now)

    def to_dict(self):
        dl_fraction_dict = {
            "account_key": self.account_key,
            "plotter_id": self.plotter_id,
            "miner_name": self.miner_name,
            "fraction": self.fraction,
            "capacity": self.capacity,
            "height": self.height,
            "create_time": str(self.create_time),
        }

        return dl_fraction_dict
