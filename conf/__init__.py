# encoding=utf-8

"""
    @author: anzz
    @date: 2019/5/13
"""
import os

WORKDIR = os.path.join(os.getcwd(), os.path.pardir)

python_env = os.getenv('python_env', True)

if python_env in ('0', False, 'prod', "PRODUCTION"):
    GLOBAL_DEBUG = False
    from .conf_prod import *
elif python_env == '144':
    GLOBAL_DEBUG = True
    from .conf_144 import *
else:
    GLOBAL_DEBUG = True
    from .conf_debug import *


"""the same configure between debug and prod"""
PRIVATE_TOKEN = b"<O\\wbUn%S~e`@T888@]cyb.,:GanzziM"

PRIVATE_TOKEN_IV = b"zmI666&s_2{+sTuT"

"""
平台账单，记录所有资产转移记录。
目前包括type：
充提
1、充值，
2、提现，
划转
3、余额->抵押
4、抵押->余额
挖矿收益
5、合作
6、非合作
7、活动奖励
"""
DEPOSIT = 1
WITHDRAWAL = 2
BALANCE_2_PLEDGE = 3
PLEDGE_2_BALANCE = 4
MINING_COOPERATION = 5
MINING_NO_COOP = 6
ACTIVITY_REWORD = 7
