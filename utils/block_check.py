# encoding=utf-8

"""
    @author: an
    @date: 19-8-6
"""
from conf import MIN_DEPOSIT_AMOUNT, MIN_CONFIRMED


# 检查是否大于最小充值要求
def check_deposit_amount(coin_code, amount):
    return False if float(amount) < MIN_DEPOSIT_AMOUNT.get(coin_code,
                                                           1) else True


# 检查是否大于最小确认数
def check_min_confirmed(coin_name, confirmed):
    return False if confirmed < MIN_CONFIRMED.get(coin_name, 1) else True
