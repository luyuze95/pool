# encoding=utf-8

"""
    @author: anzz
    @date: 2019/5/29
"""
from app import celery
from conf import *
from logs import celery_logger
from models import db
from models.deposit_transaction import DepositTranscation
from models.pool_address import PoolAddress
from models.user_asset import UserAsset
from rpc import usdt_client, get_rpc, nb_client, lhd_client
from rpc.bhd_rpc import bhd_client
from rpc.disk_rpc import disk_client
from schedule.distributed_lock_decorator import distributed_lock
from utils.block_check import check_deposit_amount, check_min_confirmed


@celery.task
@distributed_lock
def bhd_deposit_scan():
    # 获取所有地址收款交易
    addresses_transactions = bhd_client.list_received_by_address()
    for address_recevied in addresses_transactions:
        address = address_recevied.get("address")
        account = address_recevied.get("account")
        total_amount = address_recevied.get("amount")
        txids = address_recevied.get("txids")
        # 挖矿地址的交易暂时忽略
        if address == BHD_MINER_ADDRESS:
            continue
        # 根据地址查询用户资产信息
        asset = PoolAddress.query.filter_by(address=address).first()
        if asset is None:
            continue
        for txid in txids:
            # 检查交易是否已经存在
            deposit_tx = DepositTranscation.query.filter_by(
                tx_id=txid, account_key=asset.account_key).first()
            if deposit_tx:
                continue

            # 获取交易详情
            transaction = bhd_client.get_transaction_detail(txid)
            tx_outs = transaction.get('vout', [])
            confirmed = transaction['confirmations']
            height = transaction['locktime']
            for tx_out in tx_outs:
                amount = tx_out['value']
                tx_type = tx_out['scriptPubKey']['type']
                if tx_type != 'scripthash':
                    continue

                address_vout = tx_out['scriptPubKey']['addresses'][0]
                if address_vout == BHD_MINER_ADDRESS or address_vout != asset.address:
                    continue
                if not check_deposit_amount(BHD_COIN_NAME, amount):
                    celery_logger.info("bhd deposit too small, transaction:%s"
                                       % transaction)
                    continue
                need_confirmed = MIN_CONFIRMED.get(BHD_COIN_NAME)

                tr = DepositTranscation(asset.account_key, amount,
                                        asset.coin_name,
                                        txid, height,
                                        need_confirmed, confirmed)
                celery_logger.info("deposit transaction: %s" % tr.to_dict())
                db.session.add(tr)
                db.session.commit()


@celery.task
@distributed_lock
def lhd_deposit_scan():
    # 获取所有地址收款交易
    addresses_transactions = lhd_client.list_received_by_address()
    for address_recevied in addresses_transactions:
        address = address_recevied.get("address")
        account = address_recevied.get("account")
        total_amount = address_recevied.get("amount")
        txids = address_recevied.get("txids")
        # 挖矿地址的交易暂时忽略
        if address == LHD_MINER_ADDRESS:
            continue
        # 根据地址查询用户资产信息
        asset = PoolAddress.query.filter_by(address=address).first()
        if asset is None:
            continue
        for txid in txids:
            # 检查交易是否已经存在
            deposit_tx = DepositTranscation.query.filter_by(
                tx_id=txid, account_key=asset.account_key).first()
            if deposit_tx:
                continue

            # 获取交易详情
            transaction = lhd_client.get_transaction_detail(txid)
            tx_outs = transaction.get('vout', [])
            confirmed = transaction['confirmations']
            height = transaction['locktime']
            for tx_out in tx_outs:
                amount = tx_out['value']
                tx_type = tx_out['scriptPubKey']['type']
                if tx_type != 'scripthash':
                    continue

                address_vout = tx_out['scriptPubKey']['addresses'][0]
                if address_vout == LHD_MINER_ADDRESS or address_vout != asset.address:
                    continue
                if not check_deposit_amount(LHD_NAME, amount):
                    celery_logger.info("lhd_deposit too small, transaction:%s"
                                       % transaction)
                    continue
                need_confirmed = MIN_CONFIRMED.get(LHD_NAME)

                tr = DepositTranscation(asset.account_key, amount,
                                        asset.coin_name,
                                        txid, height,
                                        need_confirmed, confirmed)
                celery_logger.info("lhd_deposit transaction: %s" % tr.to_dict())
                db.session.add(tr)
                db.session.commit()


@celery.task
@distributed_lock
def disk_deposit_scan():
    transactions = disk_client.get_transactions(50, 0)[::-1]
    if transactions == []:
        return
    celery_logger.info("=== disk deposit task start === %s " % transactions)
    for transaction in transactions:
        tx_id = transaction["txid"]
        tr = DepositTranscation.query.filter_by(tx_id=tx_id).first()
        if tr:
            continue
        else:
            transaction_detail = disk_client.get_transaction_detail(tx_id)
            confirmed = transaction_detail['confirmations']
            tx_outs = transaction_detail.get('vout', [])
            height = transaction_detail['locktime']
            for tx_out in tx_outs:
                amount = tx_out['value']
                tx_type = tx_out['scriptPubKey']['type']
                if tx_type != 'pubkeyhash':
                    continue
                address_vout = tx_out['scriptPubKey']['addresses'][0]
                need_confirmed = MIN_CONFIRMED.get(DISK_NAME)
                asset = PoolAddress.query.filter_by(address=address_vout, coin_name=DISK_NAME).first()
                if asset:

                    tr = DepositTranscation(asset.account_key, amount,
                                            DISK_NAME,
                                            tx_id, height,
                                            need_confirmed, confirmed)
                    celery_logger.info("deposit transaction: %s" % tr.to_dict())
                    db.session.add(tr)
                    db.session.commit()


@celery.task
def usdt_deposit_scan():
    data = usdt_client.get_transactions()
    celery_logger.info("=== usdt deposit task start === %s " % data)
    for wallet_tr in data:
        tr_type = wallet_tr.get('type')
        if tr_type != "Simple Send":
            continue
        address = wallet_tr['referenceaddress']
        amount = float(wallet_tr.get('amount', 0))
        confirm = wallet_tr['confirmations']
        block = wallet_tr['block']
        valid = wallet_tr.get('valid')
        if not check_deposit_amount(USDT_NAME, amount) or not valid:
            continue
        tx_id = wallet_tr['txid']
        tr = DepositTranscation.query.filter_by(tx_id=tx_id).first()
        # 如果充值记录已经存在并且status是3 ，表示读取充值记录完毕， 返回
        if tr and tr.status in (DEPOSIT_CONFIRMED, DEPOSIT_ADDED):
            return
        # 如果入库但未确认
        elif tr and tr.status == DEPOSIT_CONFIRMING:
            # 设置确认数
            tr.confirmed = confirm
            # 判断确认数
            if check_min_confirmed(USDT_NAME, confirm):
                celery_logger.info("usdt deposit, confirmed %s" % tr.to_dict())
                tr.status = DEPOSIT_CONFIRMED
            db.session.commit()
        # 未入库的
        else:
            # 判断是否存在这个地址
            asset = PoolAddress.query.filter_by(address=address,
                                                coin_name=USDT_NAME).first()
            # 如果存在
            if asset:
                # 创建充值记录
                tr = DepositTranscation(asset.account_key, amount, USDT_NAME,
                                        tx_id, block, MIN_CONFIRMED[USDT_NAME],
                                        confirm)
                db.session.add(tr)
                celery_logger.info("usdt deposit, insert into deposit_transaction: %s" % tr.to_dict())
                db.session.commit()


@celery.task
@distributed_lock
def nb_deposit_scan():
    addresses = PoolAddress.query.filter_by(coin_name=NEWBI_NAME).all()
    for address in addresses:
        transactions = nb_client.get_account_transactions(address.address_rs)
        for transaction in transactions:
            tx_id = transaction.get("transaction")
            confirmations = transaction.get("confirmations")
            amountNQT = Decimal(transaction.get("amountNQT", 0))/100000000
            height = transaction.get("height")
            recipient = transaction.get("recipient")
            subtype = transaction.get("subtype")
            a_type = transaction.get("type")

            if subtype != 0 or a_type != 0:
                # 充值交易
                continue
            if amountNQT < MIN_DEPOSIT_AMOUNT[NEWBI_NAME]:
                celery_logger.info("nb_deposit,amount small %s" % transaction)
                continue

            if address.address != recipient:
                celery_logger.info("nb_deposit, not deposit transaction %s" %
                                   transaction)
                continue

            tx_id_first = DepositTranscation.query.filter_by(tx_id=tx_id).first()
            if tx_id_first:
                continue
            need_confirmed = MIN_CONFIRMED.get(NEWBI_NAME)

            tr = DepositTranscation(address.account_key, amountNQT,
                                    address.coin_name,
                                    tx_id, height,
                                    need_confirmed, confirmations)
            celery_logger.info("nb_deposit transaction: %s" % tr.to_dict())
            db.session.add(tr)
            db.session.commit()


@celery.task
@distributed_lock
def confirm_deposit_transaction():
    confirming_deposit_transactions = DepositTranscation.query.filter_by(
        status=DEPOSIT_CONFIRMING).all()
    for transaction in confirming_deposit_transactions:
        client = get_rpc(transaction.coin_name)
        transaction_info = client.get_transaction_detail(transaction.tx_id)
        confirmed = transaction_info['confirmations']

        if check_min_confirmed(transaction.coin_name, confirmed):
            transaction.status = DEPOSIT_CONFIRMED
        if confirmed != transaction.confirmed:
            transaction.confirmed = confirmed
        celery_logger.info(
            "deposit update confirmed %s " % transaction.to_dict())
        db.session.commit()


@celery.task
@distributed_lock
def deposit_add_asset():
    confirmed_deposit_transactions = DepositTranscation.query.filter_by(
        status=DEPOSIT_CONFIRMED).all()
    if not confirmed_deposit_transactions:
        return
    for transaction in confirmed_deposit_transactions:
        try:
            user_asset = UserAsset.query.filter_by(
                account_key=transaction.account_key,
                coin_name=transaction.coin_name).with_for_update(
                read=True).first()
            user_asset.available_asset += transaction.amount
            user_asset.total_asset += transaction.amount
            transaction.status = DEPOSIT_ADDED
            celery_logger.info(
                "deposit update asset %s " % transaction.to_dict())
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            celery_logger.error("deposit_add_asset task, error %s" % str(e))
            continue


