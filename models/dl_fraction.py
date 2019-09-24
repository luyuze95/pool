# encoding=utf-8

"""
    @author: anzz
    @date: 2019/6/10
"""

from datetime import datetime
from models import db


class DeadlineFractionMixin(object):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    account_key = db.Column(db.String(64), index=True)
    plotter_id = db.Column(db.String(64), index=True)
    miner_name = db.Column(db.String(64), index=True)
    fraction = db.Column(db.DECIMAL(32, 16))
    capacity = db.Column(db.DECIMAL(32, 16))
    height = db.Column(db.INTEGER)
    create_time = db.Column(db.TIMESTAMP(), default=datetime.now)
    deadline = db.Column(db.BigInteger)

    def to_dict(self):
        dl_fraction_dict = {
            "account_key": self.account_key,
            "plotter_id": self.plotter_id,
            "miner_name": self.miner_name,
            "fraction": self.fraction,
            "capacity": self.capacity,
            "height": self.height,
            "create_time": str(self.create_time),
            "deadline": self.deadline,
        }

        return dl_fraction_dict


class DeadlineFraction(DeadlineFractionMixin, db.Model):
    __tablename__ = 'pool_bhd_fraction_record'


class DeadlineFractionEcology(DeadlineFractionMixin, db.Model):
    __tablename__ = 'pool_bhd_ecology_fraction_record'


class NBDeadlineFraction(DeadlineFractionMixin, db.Model):
    __tablename__ = 'pool_newbi_fraction_record'


class LHDDeadlineFraction(DeadlineFractionMixin, db.Model):
    __tablename__ = 'pool_lhd_fraction_record'


class LHDDeadlineFractionMain(DeadlineFractionMixin, db.Model):
    __tablename__ = 'pool_lhd_main_fraction_record'


class DISKDeadlineFraction(DeadlineFractionMixin, db.Model):
    __tablename__ = 'pool_disk_fraction_record'


class HDDECOLDeadlineFraction(DeadlineFractionMixin, db.Model):
    __tablename__ = 'pool_hdd_ecol_fraction_record'
