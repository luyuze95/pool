# encoding=utf-8

"""
    @author: anzz
    @date: 2019/6/6
"""

from app import celery, db

from conf import *
from logs import celery_logger
from models.pool_address import PoolAddress
from models.billings import Billings
from rpc import lhd_client
from rpc.bhd_rpc import bhd_client
from rpc.usdt_rpc import usdt_client
from rpc.disk_rpc import disk_client
from rpc.hdd_rpc import hdd_client
from schedule.distributed_lock_decorator import distributed_lock


@celery.task
@distributed_lock
def bhd_converge():
    # listunspent 获取用户地址未消费收益
    addresses = db.session.query(PoolAddress.address).filter_by(coin_name=BHD_COIN_NAME).all()
    addresses = [address[0] for address in addresses]
    unspents = bhd_client.list_unspent(addresses=addresses, minimumAmount=MIN_CONVERGE_AMOUNT_BHD)

    if not unspents:
        return

    account_balance = {}
    account_address = {}
    # 统计地址未花费交易总额
    for unspent_trx in unspents:
        address = unspent_trx['address']
        # 老大地址，因为和primary 在一个account，特殊处理。
        if address == BHD_MINER_ADDRESS:
            continue
        account = unspent_trx['account']
        amount = unspent_trx['amount']
        confirmations = unspent_trx['confirmations']
        spendable = unspent_trx.get('spendable', False)
        total_amount = account_balance.get(account, 0)
        if not spendable:
            continue
        if confirmations < MIN_CONFIRMED[BHD_COIN_NAME]:
            continue
        account_balance[account] = total_amount + amount
        account_address[account] = address

    all_total_amount = bhd_client.get_balance() - MIN_FEE
    tx_id = bhd_client.withdrawal(BHD_MINER_ADDRESS, all_total_amount)

    for account, balance in account_balance.items():
        converge_amount = balance - POUNDAGE_BALANCE
        address = account_address.get(account)
        bhd_address = PoolAddress.query.filter_by(address=address).first()
        if not bhd_address:
            continue
        account_key = bhd_address.account_key
        try:
            # todo 添加记录，但是最后，直接获取总额，转账到提现地址。
            billing = Billings(account_key, converge_amount, address, BHD_MINER_ADDRESS, BHD_CONVERGE, tx_id)
            db.session.add(billing)
            db.session.commit()
            celery_logger.info("bhd_converge %s" % billing.to_dict())
        except Exception as e:
            db.session.rollback()
            celery_logger.error("bhd_converge %s" % e)
    # 添加地址


@celery.task
@distributed_lock
def lhd_converge():
    addresses = db.session.query(PoolAddress.address).filter_by(coin_name=LHD_NAME).all()
    addresses = [address[0] for address in addresses]
    unspents = lhd_client.list_unspent(addresses=addresses, minimumAmount=MIN_CONVERGE_AMOUNT_LHD)

    if not unspents:
        return
    all_total_amount = lhd_client.get_balance() - MIN_FEE - LHD_ECOL_REMAIN
    tx_id = lhd_client.withdrawal(LHD_MINER_ADDRESS, all_total_amount)


@celery.task
@distributed_lock
def disk_converge():
    addresses = db.session.query(PoolAddress.address).filter_by(coin_name=DISK_NAME).all()
    addresses = [address[0] for address in addresses]
    unspents = disk_client.list_unspent(addresses=addresses)

    if not unspents:
        return
    all_total_amount = disk_client.get_balance() - MIN_FEE - DISK_ECOL_REMAIN
    if int(all_total_amount) <= 0:
        return
    tx_id = disk_client.withdrawal(DISK_MINER_ADDRESS, all_total_amount)


@celery.task
@distributed_lock
def hdd_converge():
    addresses = db.session.query(PoolAddress.address).filter_by(coin_name=HDD_NAME).all()
    addresses = [address[0] for address in addresses]
    unspents = hdd_client.list_unspent(addresses=addresses)

    if not unspents:
        return
    all_total_amount = hdd_client.get_balance() - MIN_FEE - HDD_ECOL_REMAIN
    if int(all_total_amount) <= 0:
        return
    tx_id = hdd_client.withdrawal(HDD_MINER_ADDRESS, all_total_amount)


@celery.task
@distributed_lock
def usdt_converge():
    addresses_balance = usdt_client.get_all_addresses_balance()
    for address_balance in addresses_balance:
        try:
            address = address_balance['address']
            token_balance = address_balance['balances']
            property_id = token_balance[0]['propertyid']
            balance = Decimal(token_balance[0]['balance'])
            if property_id != 31:
                continue
            if address == USDT_WITHDRAWAL_ADDRESS:
                continue
            if balance < MIN_CONVERGE_AMOUNT_USDT:
                continue
            account_key = ''
            bhd_address = PoolAddress.query.filter_by(address=address).first()
            if bhd_address:
                account_key = bhd_address.account_key
            btc_unspent = len(usdt_client.list_unspent(address))
            if btc_unspent == 0:
                tx_id = usdt_client.withdrawal(address, POUNDAGE_BALANCE, is_btc=True)
                celery_logger.info("%s converge task,gas txid: %s" % (USDT_NAME, tx_id))
                billing = Billings(account_key, POUNDAGE_BALANCE, usdt_client.address, address, USDT_CONVERGE_FEE, tx_id)
            else:
                tx_id = usdt_client.funded_sendall(address)
                celery_logger.info("%s converge task, txid: %s" % (USDT_NAME, tx_id))
                billing = Billings(account_key, balance, address, usdt_client.address, USDT_CONVERGE, tx_id)
            db.session.add(billing)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            celery_logger.warning('%s converge error:%s' % (USDT_NAME, e))