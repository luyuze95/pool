# encoding=utf-8

"""
    @author: anzz
    @date: 2019/6/25
"""

from app import celery
from conf import *
from logs import celery_logger
from models import db
from models.billings import Billings
from models.remote_pledge_lhd import LHDRemotePledgeAddress, LHDRemotePledgeTransaction, LHDTeamWorkRecordActivity
from models.user_asset import UserAsset
from rpc import lhd_client
from schedule.distributed_lock_decorator import distributed_lock


@celery.task
@distributed_lock
def lhd_statistic_pledges():
    """
    检查链上借贷交易，并给用户添加借贷资产
    :return:
    """
    pledges = lhd_client.list_pledges()
    if not pledges:
        return
    for pledge in pledges:
        amount = pledge['amount']
        blockheight = pledge['blockheight']
        category = pledge['category']
        from_address = pledge['from']
        to_address = pledge['to']
        txid = pledge['txid']
        valid = pledge['valid']

        if not valid:
            continue
        if category != "point-to" and category != "point-from":
            continue
        if to_address != LHD_MINER_ADDRESS:
            continue
        remote_pledge_address = LHDRemotePledgeAddress.query.filter_by(address=from_address).first()
        if not remote_pledge_address:
            celery_logger.info("pledge address not found: %s" % from_address)
            continue
        pledge_tr = LHDRemotePledgeTransaction.query.filter_by(
            pledge_txid=txid).first()
        if pledge_tr:
            continue
        account_key = remote_pledge_address.account_key
        user_asset = UserAsset.query.filter_by(
            account_key=account_key, coin_name=LHD_NAME).with_for_update(
            read=True).first()
        if not user_asset:
            raise Exception("account_key:%s not found, address:%s" %
                            (account_key, from_address))
        pledge_margin = user_asset.get_available_margin_amount()
        if amount * 3 / 7 > pledge_margin:
            # 抵押保证金不足，不予抵押
            continue
        try:
            # 添加远程抵押记录
            user_asset.remote_freeze_asset += amount
            pledge_tr = LHDRemotePledgeTransaction(account_key,
                                                from_address,
                                                amount, blockheight, txid)
            db.session.add(pledge_tr)
            db.session.commit()
            celery_logger.info("pledge success %s" % pledge_tr.to_dict())
        except Exception as e:
            db.session.rollback()
            celery_logger.error("pledge failed %s" % e)


@celery.task
@distributed_lock
def lhd_check_pledges():
    """
    对比库中和链上数据，检查抵押状态的交易是否撤销，并处理。
    :return:
    """
    remote_pledges = LHDRemotePledgeTransaction.query.filter_by(
        status=DEBITING).all()
    pledges = lhd_client.list_pledges()
    if not remote_pledges:
        return
    pledges_txids = [pledge["txid"] for pledge in pledges]
    for remote_pledge in remote_pledges:
        if remote_pledge.pledge_txid in pledges_txids:
            # 抵押状态正常
            continue
        try:
            user_asset = UserAsset.query.filter_by(
                account_key=remote_pledge.account_key,
                coin_name=LHD_NAME).with_for_update(
                read=False).first()

            if not user_asset:
                continue
            celery_logger.info("user_asset before deduct %s" % user_asset.to_dict())
            coop_freeze_asset = user_asset.coop_freeze_asset
            total_pledge_amount = user_asset.get_pledge_amount()
            remote_pledge_amount = remote_pledge.pledge_amount
            # 首先扣掉远程借贷总数
            reside_no_debit_amount = user_asset.get_remote_avai_amount()
            user_asset.remote_freeze_asset -= remote_pledge_amount
            if reside_no_debit_amount >= remote_pledge_amount:
                remote_pledge.status = DEBIT_UNDONE
                db.session.commit()
                continue

            # 远程抵押中剩余可用不够扣除的。需要扣除远程合作和远程抵押中的资金
            remote_deduct = remote_pledge_amount - reside_no_debit_amount
            # 如果可用的能覆盖，不需要改动合作冻结资金
            if user_asset.available_asset >= remote_deduct:
                # 从可用中扣除全部
                user_asset.available_asset -= remote_deduct
                # 从远程合作和远程抵押中扣
                if user_asset.remote_4coop_asset >= remote_deduct:
                    # 从合作中直接扣除
                    user_asset.remote_4coop_asset -= remote_deduct
                else:
                    # 远程合作中扣除全部，抵押中扣除一部分。合作总额、抵押总额不变，可用补足
                    deduct_pledge_amount = remote_deduct - user_asset.remote_4coop_asset
                    user_asset.remote_4pledge_asset -= deduct_pledge_amount
                    user_asset.pledge_asset += deduct_pledge_amount
                    user_asset.remote_4coop_asset = 0
            # 如果可用余额不能覆盖，可用余额优先补足抵押
            else:
                if user_asset.remote_4coop_asset >= remote_deduct:
                    # 只扣远程合作中的余额
                    user_asset.remote_4coop_asset -= remote_deduct
                    deduct_coop_freeze = remote_deduct - user_asset.available_asset
                    user_asset.coop_freeze_asset -= deduct_coop_freeze
                else:
                    # 扣完远程合作中余额，扣远程抵押中余额. 远程抵押中要扣除
                    deduct_pledge_amount = remote_deduct - user_asset.remote_4coop_asset
                    if user_asset.available_asset >= deduct_pledge_amount:
                        # 如果远程可用资产中能覆盖远程抵押扣除。添加本地抵押余额，减去远程抵押余额
                        user_asset.pledge_asset += deduct_pledge_amount
                        user_asset.remote_4pledge_asset -= deduct_pledge_amount
                    else:
                        user_asset.pledge_asset += user_asset.available_asset
                        user_asset.remote_4pledge_asset = user_asset.remote_freeze_asset
                    user_asset.coop_freeze_asset -= user_asset.remote_4coop_asset
                    user_asset.remote_4coop_asset = 0
                user_asset.available_asset = 0

            # 合作冻结资金修改，检查是否违约
            if coop_freeze_asset != user_asset.coop_freeze_asset:
                # 进行中的订单
                team_works = LHDTeamWorkRecordActivity.query.filter_by(
                    account_key=remote_pledge.account_key,
                    status=TeamWorking).order_by(
                    LHDTeamWorkRecordActivity.create_time.asc()
                ).with_for_update(read=True).all()

                # 合作违约金额= 用户需要金额-剩余金额
                gap_amount = coop_freeze_asset - user_asset.coop_freeze_asset

                if gap_amount > 0:
                    # 实际抵押金额不满足需要金额
                    if team_works:
                        security_deposit = remote_pledge_amount * 3 / 7
                        gap_amount += security_deposit
                        for team_work in team_works:
                            if gap_amount > 0:
                                # 扣除违约订单，部分扣除的返还剩余部分。
                                team_work.status = BadTeamWork
                                gap_amount -= team_work.coo_amount
                            else:
                                break
                        # 扣除违约金 可用>合作>抵押
                        # 合作冻结中可扣 = 合作冻结 - 远程借贷合作
                        margin_in_coop = user_asset.coop_freeze_asset - user_asset.remote_4coop_asset
                        deduct_local_pledge_amount = security_deposit - margin_in_coop
                        if deduct_local_pledge_amount > 0:
                            user_asset.pledge_asset -= deduct_local_pledge_amount
                            user_asset.coop_freeze_asset = 0
                        else:
                            user_asset.coop_freeze_asset -= security_deposit
                        user_asset.total_asset -= security_deposit
                        # 返还剩余部分
                        if gap_amount < 0:
                            refund_amount = -gap_amount
                            local_asset_in_coop = user_asset.get_local_in_coop()
                            #　少的那一部分，全部返还到本地
                            refund_local = min(refund_amount, local_asset_in_coop)
                            deduct_remote_pledge_asset = total_pledge_amount - user_asset.get_pledge_amount()
                            if deduct_remote_pledge_asset >= refund_local:
                                user_asset.pledge_asset += refund_local
                            else:
                                user_asset.pledge_asset += deduct_remote_pledge_asset
                                user_asset.available_asset += (refund_local - deduct_remote_pledge_asset)
                            # 合作中本地部分少于返还部分，远程用于合作中返还
                            if local_asset_in_coop < refund_amount:
                                user_asset.remote_4coop_asset -= (refund_amount - local_asset_in_coop)
                                
                            # 减去订单中多扣除部分
                            user_asset.coop_freeze_asset -= refund_amount

                        billing = Billings(user_asset.account_key, security_deposit, '', '', COOP_FINE)
                        db.session.add(billing)
                        celery_logger.info("deduct security deposit %s " % billing.to_dict())
            celery_logger.info(
                "user_asset after deduct %s" % user_asset.to_dict())
            remote_pledge.status = DEBIT_UNDONE
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            celery_logger.error("check pledge failed %s" % e)


if __name__ == '__main__':
    lhd_check_pledges.delay()
