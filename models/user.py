# encoding=utf-8

"""
    @author: lyz
    @date: 2019/5/29
"""

from datetime import datetime

from models import db


class User(db.Model):
    __tablename__ = 'pool_user'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    # 用户id
    account_key = db.Column(db.String(64), index=True)
    # 用户密码
    password = db.Column(db.String(256))
    # 用户邮箱
    email = db.Column(db.String(64))
    # 是否冻结
    is_freeze = db.Column(db.SmallInteger)
    # token
    # token = db.Column(db.String(256))

    create_time = db.Column(db.TIMESTAMP(), default=datetime.now)
    update_time = db.Column(db.TIMESTAMP(), default=datetime.now)

    def __setattr__(self, key, value):
        super(User, self).__setattr__(key, value)
        if key != "update_time":
            self.update_time = datetime.now()

    def to_dict(self):
        user_dict = {
            "account_key": self.account_key,
            "email": self.email,
            "is_freeze": self.is_freeze,
            "create_time": str(self.create_time),
        }
        return user_dict
