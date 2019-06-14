# encoding=utf-8

"""
    @author: anzz
    @date: 2019/5/29
"""

from datetime import datetime

from sqlalchemy import func

from models import db


class UserAsset(db.Model):
    __tablename__ = 'pool_user_asset'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    # 用户account_key
    account_key = db.Column(db.String(64), index=True)
    # 用户id
    user_id = db.Column(db.INTEGER)
    # 资产id
    asset_id = db.Column(db.INTEGER)
    # 币种名
    coin_name = db.Column(db.String(32), default='0')
    # 抵押资产
    pledge_asset = db.Column(db.DECIMAL(32, 16), default='0')
    # 可用资产
    available_asset = db.Column(db.DECIMAL(32, 16), default='0')
    # 提现冻结资产
    frozen_asset = db.Column(db.DECIMAL(32, 16), default='0')
    # 交易冻结资产
    trading_asset = db.Column(db.DECIMAL(32, 16), default='0')
    # 总资产
    total_asset = db.Column(db.DECIMAL(32, 16), default='0')
    # 理论抵押
    # theory_asset = db.Column(db.BigInteger)

    # 收益率
    # yield_rate = db.Column(db.DECIMAL(32, 16))
    # 抵押率
    # pledge_rate = db.Column(db.DECIMAL(32, 16))

    create_time = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())
    update_time = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())

    def __init__(self, account_key, coin_name, pledge_asset, available_asset,
                 total_asset, theory_asset, yield_rate):
        self.account_key = account_key
        self.coin_name = coin_name
        self.pledge_asset = pledge_asset
        self.available_asset = available_asset
        self.total_asset = total_asset
        self.yield_rate = yield_rate

    def __setattr__(self, key, value):
        super(UserAsset, self).__setattr__(key, value)
        if key != "update_time":
            self.update_time = datetime.now()

    def to_dict(self):
        user_asset_dict = {
            "account_key": self.account_key,
            "user_id": self.user_id,
            "coin_name": self.coin_name,
            "asset_id": self.asset_id,
            "pledge_asset": self.pledge_asset,
            "available_asset": self.available_asset,
            "total_asset": self.total_asset,
            "frozen_asset": self.frozen_asset,
            "trading_asset": self.trading_asset,
            "create_time": str(self.create_time),
        }
        return user_asset_dict