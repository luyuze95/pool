# encoding=utf-8

"""
    @author: lyz
    @date: 2019/6/17
"""


from datetime import datetime
from models import db
from models.base import BaseModel


class ActivityReward(BaseModel):
    __tablename__ = 'pool_capacity_winning_record_activity'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    account_key = db.Column(db.String(64), index=True)
    email = db.Column(db.String(128))
    amount = db.Column(db.DECIMAL(32, 16))
    grade = db.Column(db.String(32))
    update_time = db.Column(db.TIMESTAMP(), default=datetime.now)
    create_time = db.Column(db.TIMESTAMP(), default=datetime.now)
    is_add_asset = db.Column(db.SmallInteger)

    def to_dict(self):
        activity_reward_dict = {
            "account_key": self.account_key,
            "amount": self.amount,
            "is_add_asset": self.is_add_asset,
            "create_time": self.create_time,
        }
        return activity_reward_dict


