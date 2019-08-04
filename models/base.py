# encoding=utf-8

"""
    @author: anzz
    @date: 2019/8/4
"""

from datetime import datetime

from models import db


class BaseModel(db.Model):

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        if key != "update_time":
            self.update_time = datetime.now()
