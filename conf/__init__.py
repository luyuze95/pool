# encoding=utf-8

"""
    @author: lyz
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
PRIVATE_TOKEN = b"<O\\wbUn%S~e`@T888@]cyb.,:GlyziM"

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
5、合作池
6、非合作池
7、活动奖励
8、聚合到挖矿地址
9、usdt汇聚手续费
10、usdt汇聚
11、合作违约罚金
12、合作挖矿收益
13、生态挖矿收益
"""
DEPOSIT = 1
WITHDRAWAL = 2
BALANCE_2_PLEDGE = 3
PLEDGE_2_BALANCE = 4
MINING_COOPERATION = 5
MINING_NO_COOP = 6
ACTIVITY_REWORD = 7
BHD_CONVERGE = 8
USDT_CONVERGE_FEE = 9
USDT_CONVERGE = 10
COOP_FINE = 11
COOP_MINE_EARNINGS = 12
ECOL_MINE_EARNINGS = 13


""" 
 提现交易状态
"""
# 用户发起提现申请
WITHDRAWAL_APPLY = 1
# 后台审核通过
WITHDRAWAL_PASS = 2
# 等待发送
WITHDRAWAL_WAIT_SEND = 3
# 发送中
WITHDRAWAL_SENDING = 4
# 已发送
WITHDRAWAL_SENDED = 5
# 发送失败
WITHDRAWAL_FAILED = 6
# 审核失败
WITHDRAWAL_NOT_PASS = 7
# 已撤销
WITHDRAWAL_UNDO = 8

"""
充值交易状态
"""
# 确认中
DEPOSIT_CONFIRMING = 1
# 已确认
DEPOSIT_CONFIRMED = 2
# 已到账
DEPOSIT_ADDED = 3
# 充值失败
DEPOSIT_FAILED = 4

# 提现手续费率
WITHDRAWAL_FEE = Decimal("0.001")
WITHDRAWAL_ACTUAL = Decimal("0.999")
DISK_WITHDRAWAL_ACTUAL = Decimal("0.99")

"""
合作池、生态池
"""
COOP_POOL = "coop"
ECOLOGY_POOL = "ecol"

"""
远程借贷状态
"""
# 正常借贷状态
DEBITING = 1
# 借贷已撤销
DEBIT_UNDONE = 0

"""
合作投放状态
"""
# 违约
BadTeamWork = 2
# 进行中
TeamWorking = 1
# 结束
TeamWorkEnd = 0

BHD_RATE_KEY = "bhd:ratio"


"""
收益类型
"""
IncomeTypeMining = 0
IncomeTYpeCoopReward = 1
IncomeTYpeMiningEcol = 2

# 理财收益类型
IncomeTYpemanagemoney = 3
