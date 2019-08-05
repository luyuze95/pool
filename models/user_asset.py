# encoding=utf-8

"""
    @author: anzz
    @date: 2019/5/29
"""

from datetime import datetime

from sqlalchemy import func

from conf import *
from models import db
from models.base import BaseModel


class UserAsset(BaseModel):
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
    # 可用资产， 可用来提现,交易，远程抵押保证金
    available_asset = db.Column(db.DECIMAL(32, 16), default='0')
    # 提现冻结资产
    frozen_asset = db.Column(db.DECIMAL(32, 16), default='0')
    # 交易冻结资产
    trading_asset = db.Column(db.DECIMAL(32, 16), default='0')
    # 合作挖矿冻结资产
    coop_freeze_asset = db.Column(db.DECIMAL(32, 16), default='0')
    # 远程抵押资产总额
    remote_freeze_asset = db.Column(db.DECIMAL(32, 16), default='0')
    # 远程抵押资产-抵押金额
    remote_4pledge_asset = db.Column(db.DECIMAL(32, 16), default='0')
    # 远程抵押资产-合作金额
    remote_4coop_asset = db.Column(db.DECIMAL(32, 16), default='0')
    # 总资产 = 可用+抵押+交易冻结+提现冻结+合作冻结中不包含远程合作
    total_asset = db.Column(db.DECIMAL(32, 16), default='0')
    # 理论抵押
    # theory_asset = db.Column(db.BigInteger)

    # 收益率
    # yield_rate = db.Column(db.DECIMAL(32, 16))
    # 抵押率
    # pledge_rate = db.Column(db.DECIMAL(32, 16))

    create_time = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())
    update_time = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())

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
            "available_asset": self.available_asset,
            "total_asset": self.total_asset,
            "frozen_asset": self.frozen_asset,
            "trading_asset": self.trading_asset,
            "create_time": str(self.create_time),
        }
        if self.coin_name == BHD_COIN_NAME:
            user_asset_dict.update({
                # 矿池抵押
                "pledge_asset": self.get_pledge_amount(),
                # 指向抵押
                "remote_freeze_asset": self.remote_freeze_asset,
                # 合作冻结
                "coop_freeze_asset": self.coop_freeze_asset,
                # 指向用于抵押
                "remote_4pledge_asset": self.remote_4pledge_asset,
                # 指向用于合作
                "remote_4coop_asset": self.remote_4coop_asset,
                # 可用抵押资产
                "available_pledge_asset": self.get_available_pledge_amount(),
                # 可用保证金
                "available_margin_asset": self.get_available_margin_amount(),
            })
        return user_asset_dict

    # 保证金
    def get_available_margin_amount(self):
        # 充值+收益=可用+抵押+合作冻结-远程借贷合作部分
        amount = self.available_asset + self.pledge_asset + self.coop_freeze_asset - self.remote_4coop_asset
        # 抵押金
        margin_amount = self.remote_freeze_asset/9

        available_margin_asset = amount - margin_amount
        return available_margin_asset

    def get_available_pledge_amount(self):
        return self.available_asset+self.remote_freeze_asset-self.remote_4pledge_asset-self.remote_4coop_asset

    def get_pledge_amount(self):
        return self.pledge_asset + self.remote_4pledge_asset

    def get_can_deduct(self):
        return self.coop_freeze_asset - self.remote_4coop_asset

    def get_remote_avai_amount(self):
        return self.remote_freeze_asset - self.remote_4pledge_asset - self.remote_4coop_asset

    def get_total_available_pledge_amount(self):
        return self.get_remote_avai_amount() + self.available_asset

    def get_available_withdrawal_amount(self):
        available_asset = self.available_asset + self.get_remote_avai_amount()
        total_asset = available_asset + self.coop_freeze_asset + self.get_pledge_amount()
        available_withdrawal_asset = total_asset - self.remote_freeze_asset/9*10
        return available_withdrawal_asset


