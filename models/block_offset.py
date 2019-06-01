# encoding=utf-8

"""
    @author: anzz
    @date: 2019/5/29
"""

from datetime import datetime

from models import db


class BlockOffset(db.Model):
    __tablename__ = 'pool_block_offset'

    offset_name = db.Column(db.String(32), primary_key=True)
    offset_value = db.Column(db.Integer)
    create_time = db.Column(db.TIMESTAMP(), default=datetime.now)
    update_time = db.Column(db.TIMESTAMP(), default=datetime.now)

    def __init__(self, offset_name, offset_value):
        self.offset_name = offset_name
        self.offset_value = offset_value

    def __setattr__(self, key, value):
        super(BlockOffset, self).__setattr__(key, value)
        if key != "update_time":
            self.update_time = datetime.now()
