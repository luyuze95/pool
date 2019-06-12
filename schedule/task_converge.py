# encoding=utf-8

"""
    @author: anzz
    @date: 2019/6/6
"""
from app import celery, db

from conf import MIN_CONVERGE_AMOUNT, MIN_CONFIRMED, BHD_COIN_NAME, \
    BHD_MINER_ADDRESS, POUNDAGE_BAlANCE, BHD_CONVERGE
from logs import celery_logger
from models.bhd_address import BhdAddress
from models.billings import Billings
from rpc.bhd_rpc import bhd_client


@celery.task
def bhd_converge():
    # listunspent 获取用户地址未消费收益
    addresses = db.session.query(BhdAddress.address).all()
    addresses = [address[0] for address in addresses]
    unspents = bhd_client.list_unspent(addresses=addresses, minimumAmount=MIN_CONVERGE_AMOUNT)
    account_balance = {}
    account_address = {}
    # 统计地址未花费交易总额
    for unspent_trx in unspents:
        address = unspent_trx['address']
        account = unspent_trx['account']
        amount = unspent_trx['amount']
        confirmations = unspent_trx['confirmations']
        spendable = unspent_trx['spendable']
        total_amount = account_balance.get(account, 0)
        if not spendable:
            continue
        if confirmations < MIN_CONFIRMED[BHD_COIN_NAME]:
            continue
        account_balance[account] = total_amount + amount
        account_address[account] = address

    celery_logger.info("account_address: %s" % account_address)
    celery_logger.info("account_balance: %s" % account_balance)

    for account, balance in account_balance.items():
        converge_amount = balance-POUNDAGE_BAlANCE
        address = account_address.get(account)
        account_key = ''
        bhd_address = BhdAddress.query.filter_by(address=address).first()
        if bhd_address:
            account_key = bhd_address.account_key
        try:
            tx_id = bhd_client.withdrawal(BHD_MINER_ADDRESS, converge_amount, account)
            billing = Billings(account_key, converge_amount, address, BHD_MINER_ADDRESS, BHD_CONVERGE, tx_id)
            db.session.add(billing)
            db.session.commit()
            celery_logger.info("bhd_converge account_key:%s, amount:%s, from:%s, to:%s, "
                               % (account_key, converge_amount, address, BHD_MINER_ADDRESS))
        except Exception as e:
            db.session.rollback()
            celery_logger.error("bhd_converge %s" % e)
