# encoding=utf-8

"""
    @author: anzz
    @date: 2019/6/10
"""

from datetime import datetime
from models import db


class BurstBlock(db.Model):
    """
        平台爆块记录
    """
    __tablename__ = 'pool_bhd_burst'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    account_key = db.Column(db.String(255), index=True)
    plotter_id = db.Column(db.String(255))
    block_hash = db.Column(db.String(256), default='')
    nonce = db.Column(db.String(256), default='')
    height = db.Column(db.INTEGER)
    deadline = db.Column(db.INTEGER)
    burst_block_time = db.Column(db.BIGINT)
    create_time = db.Column(db.TIMESTAMP(), default=datetime.now)

    def to_dict(self):
        burst_dict = {
            "account_key": self.account_key,
            "plotter_id": self.plotter_id,
            "block_hash": self.block_hash,
            "nonce": self.nonce,
            "height": self.height,
            "deadline": self.deadline,
            "create_time": str(self.create_time),
            "burst_block_time": self.burst_block_time,
        }

        return burst_dict
