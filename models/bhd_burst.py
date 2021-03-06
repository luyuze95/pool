# encoding=utf-8

"""
    @author: lyz
    @date: 2019/6/10
"""

from datetime import datetime
from models import db


class BurstBlockMixin(object):
    """
        平台爆块记录
    """
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    account_key = db.Column(db.String(255), index=True)
    plotter_id = db.Column(db.String(255))
    block_hash = db.Column(db.String(256), default='')
    nonce = db.Column(db.String(256), default='')
    height = db.Column(db.INTEGER)

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


class BurstBlock(BurstBlockMixin, db.Model):
    __tablename__ = 'pool_bhd_burst'
    deadline = db.Column(db.INTEGER)


class EcolBurstBlock(BurstBlockMixin, db.Model):
    __tablename__ = 'pool_bhd_ecology_burst'
    deadline = db.Column(db.INTEGER)


class NBBurstBlock(BurstBlockMixin, db.Model):
    __tablename__ = 'pool_newbi_burst'

    def to_dict(self):
        burst_dict = {
            "account_key": self.account_key,
            "plotter_id": self.plotter_id,
            "block_hash": self.block_hash,
            "nonce": self.nonce,
            "height": self.height,
            "create_time": str(self.create_time),
            "burst_block_time": self.burst_block_time,
        }

        return burst_dict


class LHDBurstBlock(BurstBlockMixin, db.Model):
    __tablename__ = 'pool_lhd_burst'
    deadline = db.Column(db.INTEGER)


class LHDMainBurstBlock(BurstBlockMixin, db.Model):
    __tablename__ = 'pool_lhd_main_burst'
    deadline = db.Column(db.INTEGER)


class DISKBurstBlock(BurstBlockMixin, db.Model):
    __tablename__ = 'pool_disk_burst'
    deadline = db.Column(db.INTEGER)


class HDDECOLBurstBlock(BurstBlockMixin, db.Model):
    __tablename__ = 'pool_hdd_ecol_burst'
    deadline = db.Column(db.INTEGER)
