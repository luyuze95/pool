# encoding=utf-8

"""
    @author: anzz
    @date: 2019/5/29
"""
from app import celery
from conf import *
from logs import celery_logger
from models import db
from models.block_offset import BlockOffset
from models.deposit_transaction import DepositTranscation
from models.pool_address import PoolAddress
from models.user_asset import UserAsset
from rpc import usdt_client
from rpc.bhd_rpc import bhd_client
from utils.msyql_ins import initialize_offset


@celery.task
def bhd_block_scan():
    buffer_window = CELERY_MAX_CHILDREN_TASK
    # 获取最新区块高度
    latest_block_number = bhd_client.get_latest_block_number()
    bhd_offset = BlockOffset.query.filter_by(offset_name=BHD_COIN_NAME).first()
    # 如果之前没有bhd，初始化最新区块到数据库
    bhd_offset = initialize_offset(BHD_COIN_NAME, bhd_offset,
                                   latest_block_number)
    wait_scan_block_size = latest_block_number - bhd_offset.offset_value
    if wait_scan_block_size < buffer_window:
        buffer_window = wait_scan_block_size
    # 根据高度差，下发最新的扫描任务
    for block_number in range(bhd_offset.offset_value,
                              bhd_offset.offset_value + buffer_window):
        bhd_block_number_deposit_task.apply_async((block_number, BHD_COIN_NAME),
                                                  expires=20)

    # 更新区块高度
    bhd_offset.offset_value += buffer_window
    db.session.commit()


@celery.task
def bhd_block_number_deposit_task(block_number, series):
    # 获取每个地址收取的详情 listreceivedbyaddress
    transaction_hashs = bhd_client.get_transaction_hashs(block_number)
    if not transaction_hashs:
        return True
    for transaction_hash in transaction_hashs:
        try:
            #todo 获取交易详情,更换为gettransaction。
            transaction_info = bhd_client.get_transaction_detail(
                transaction_hash)
        except Exception as e:
            celery_logger.error(
                "failed block_number:%s, transaction_hash:%s, error:%s"
                % (block_number, transaction_hash, str(e)))
            continue
        tx_outs = transaction_info['vout']
        for tx_out in tx_outs:
            amount = tx_out['value']
            tx_type = tx_out['scriptPubKey']['type']
            if tx_type != 'scripthash':
                continue

            address = tx_out['scriptPubKey']['addresses'][0]
            # 不满足最小充值数，跳过检查
            if not check_deposit_amount(series, amount):
                celery_logger.info("bhd deposit too small, transaction:%s"
                                   % transaction_info)
                continue
            # 查询是否充向用户的地址
            asset = PoolAddress.query.filter_by(address=address).first()
            if asset is None:
                continue
            # 查询是否已经存在，防止重复
            deposit_tx = DepositTranscation.query.filter_by(
                tx_id=transaction_hash, account_key=asset.account_key).first()
            if deposit_tx:
                continue
            # 记录确认数
            confirmed = transaction_info['confirmations']
            need_confirmed = MIN_CONFIRMED.get(BHD_COIN_NAME)

            tr = DepositTranscation(asset.account_key, amount, asset.coin_name,
                                    transaction_hash, block_number,
                                    need_confirmed, confirmed)
            celery_logger.info("deposit transaction: %s" % tr.to_dict())
            db.session.add(tr)
            db.session.commit()


@celery.task
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
            if check_min_confirmed(BHD_COIN_NAME, confirm):
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
def confirm_deposit_transaction():
    confirming_deposit_transactions = DepositTranscation.query.filter_by(
        status=DEPOSIT_CONFIRMING).all()
    for transaction in confirming_deposit_transactions:
        transaction_info = bhd_client.get_transaction_detail(transaction.tx_id)
        confirmed = transaction_info['confirmations']

        if check_min_confirmed(BHD_COIN_NAME, confirmed):
            transaction.status = DEPOSIT_CONFIRMED
        if confirmed != transaction.confirmed:
            transaction.confirmed = confirmed
        celery_logger.info(
            "deposit update confirmed %s " % transaction.to_dict())
        db.session.commit()


@celery.task
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


# 检查是否大于最小充值要求
def check_deposit_amount(coin_code, amount):
    return False if float(amount) < MIN_DEPOSIT_AMOUNT.get(coin_code,
                                                           1) else True


# 检查是否大于最小确认数
def check_min_confirmed(coin_name, confirmed):
    return False if confirmed < MIN_CONFIRMED.get(coin_name, 1) else True
