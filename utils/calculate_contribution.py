# encoding=utf-8

"""
    @author: lyz
    @date: 2019/5/23
"""
from utils.msyql_ins import do_select_all

get_all_account_id = "select DISTINCT(plotter_id) from pool_bhd_nonce_record"

get_deadline_by_account = """SELECT height, MIN(deadline) from pool_bhd_nonce_record where plotter_id=%s and height>85793 GROUP BY height"""

get_height_count = "SELECT count(DISTINCT(height)) from pool_bhd_nonce_record "

all_account = do_select_all(get_all_account_id)


print(all_account)

all_height_count = do_select_all(get_height_count)[0][0]

print(all_height_count)


all_theory_submit = 0
account_id_theory_submit = {}
for account_id in all_account:
    deadline_sum = 0
    all_record = do_select_all(get_deadline_by_account, account_id)
    # if account_id[0] == '12883486922922612657':
    #     all_record = [(84572, 971)]
    # if account_id[0] == '7547073369825669068':
    #     all_record = [(84572, 4146)]
    for height, deadline in all_record:
        deadline_sum += deadline
    deadline_avg = deadline_sum / len(all_record)

    one_day_submit = 86400/deadline_avg

    theory_submit = one_day_submit*len(all_record)/100

    print(theory_submit)
    account_id_theory_submit[account_id] = theory_submit
    all_theory_submit += theory_submit

for account_id, theory_submit in account_id_theory_submit.items():
    print(account_id, theory_submit/all_theory_submit*25)
    # print(account_id, theory_submit/all_theory_submit*all_height_count*25)

