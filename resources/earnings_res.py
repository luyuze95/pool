# encoding=utf-8

"""
    @author: lyz
    @date: 2019/5/30
"""

import time
from datetime import datetime

from flask import g
from flask_restful import Resource, reqparse
from sqlalchemy import func, and_

from models.activity_reward import ActivityReward
from models.income_record import IncomeRecord, NBIncomeRecord, LHDIncomeRecord, DISKIncomeRecord, HDDIncomeRecord
from models.remote_pledge import TeamWorkRecordActivity, TeamWorkActivity
from models.remote_pledge_lhd import LHDTeamWorkRecordActivity, LHDTeamWorkActivity
from resources.auth_decorator import login_required
from rpc import get_rpc
from utils.response import make_resp
from conf import *


class EarningsTotalApi(Resource):
    decorators = [login_required]

    def get(self):
        """
        获取用户总收益
        :return:
        """

        parse = reqparse.RequestParser()
        parse.add_argument('coin_name', type=str, required=False)
        args = parse.parse_args()
        coin_name = args.get('coin_name')
        if not coin_name:
            coin_name = BHD_COIN_NAME

        if coin_name == BHD_COIN_NAME:
            model = IncomeRecord
        elif coin_name == LHD_NAME:
            model = LHDIncomeRecord
        elif coin_name == DISK_NAME:
            model = DISKIncomeRecord
        elif coin_name == HDD_NAME:
            model = HDDIncomeRecord
        elif coin_name == NEWBI_NAME:
            model = NBIncomeRecord
        else:
            return make_resp(400, False, message="请求币种错误")

        account_key = g.account_key
        # 合作-裸挖-挖矿总收入
        mining_total_amount = model.query.filter_by(
            account_key=account_key
        ).filter(
            model.type.in_([IncomeTypeMining, IncomeTYpeMiningEcol])
        ).with_entities(func.sum(model.amount)).first()[0]

        # 昨天挖矿所得
        mining_last_day = model.query.filter_by(
            account_key=account_key
        ).filter(
            func.to_days(model.create_time) == func.to_days(func.now())-1
        ).filter(
            model.type.in_([IncomeTypeMining, IncomeTYpeMiningEcol])
        ).with_entities(
            func.sum(model.amount)).first()[0]

        if coin_name == NEWBI_NAME:
            return make_resp(mining_total_amount=mining_total_amount,
                             mining_last_day=mining_last_day)

        # 合作所得总
        coop_total_amount = model.query.filter_by(
            account_key=account_key, type=IncomeTYpeCoopReward
        ).with_entities(func.sum(model.amount)).first()[0]
        # 昨日合作所得
        coop_last_day = model.query.filter_by(
            account_key=account_key, type=IncomeTYpeCoopReward
        ).filter(
            func.to_days(model.create_time) == func.to_days(func.now())-1
        ).with_entities(func.sum(model.amount)).first()[0]

        if coin_name == LHD_NAME:
            return make_resp(mining_total_amount=mining_total_amount,
                             mining_last_day=mining_last_day,
                             coop_total_amount=coop_total_amount,
                             coop_last_day=coop_last_day,)
        # 理财收益
        manage_money_amount = model.query.filter_by(
            account_key=account_key, type=IncomeTYpemanagemoney
        ).with_entities(func.sum(model.amount)).first()[0]

        # 活动总收益
        activity_rewards_total_amount = ActivityReward.query.filter_by(
            account_key=account_key
        ).filter(ActivityReward.amount>0
                 ).with_entities(func.sum(ActivityReward.amount)).first()[0]
        # 昨日活动收益
        activity_rewards_last_day = ActivityReward.query.filter_by(
            account_key=account_key
        ).filter(
            func.to_days(ActivityReward.create_time) == func.to_days(func.now())-1
        ).filter(ActivityReward.amount>0
                 ).with_entities(func.sum(ActivityReward.amount)).first()[0]

        return make_resp(mining_total_amount=mining_total_amount,
                         mining_last_day=mining_last_day,
                         coop_total_amount=coop_total_amount,
                         coop_last_day=coop_last_day,
                         activity_rewards_total_amount=activity_rewards_total_amount,
                         activity_rewards_last_day=activity_rewards_last_day,
                         manage_money_amount=manage_money_amount)


class DayEarningsApi(Resource):

    decorators = [login_required]

    def get(self):
        """
        按天获取收益列表
        :return:
        """
        account_key = g.account_key
        parse = reqparse.RequestParser()
        now = int(time.time())
        parse.add_argument('limit', type=int, required=False, default=10)
        parse.add_argument('offset', type=int, required=False, default=0)
        parse.add_argument('from', type=int, required=False, default=0)
        parse.add_argument('end', type=int, required=False, default=now)
        parse.add_argument('coin_name', type=str, required=False)
        parse.add_argument('status', type=int, required=False)
        args = parse.parse_args()
        limit = args.get('limit')
        offset = args.get('offset')
        from_ts = args.get('from')
        end_ts = args.get('end')
        coin_name = args.get('coin_name')
        status = args.get('status')
        from_dt = datetime.fromtimestamp(from_ts)
        end_dt = datetime.fromtimestamp(end_ts)
        kwargs = {"account_key": account_key}
        if not coin_name:
            coin_name = BHD_COIN_NAME
        if coin_name == BHD_COIN_NAME:
            model = IncomeRecord
        elif coin_name == LHD_NAME:
            model = LHDIncomeRecord
        elif coin_name == DISK_NAME:
            model = DISKIncomeRecord
        elif coin_name == HDD_NAME:
            model = HDDIncomeRecord
        elif coin_name == NEWBI_NAME:
            model = NBIncomeRecord
        else:
            return make_resp(400, False, message="请求币种错误")

        # manage_money_amount = model.query.filter_by(
        #     account_key=account_key, type=IncomeTYpemanagemoney
        # ).filter(
        #     and_(model.create_time > from_dt,
        #          model.create_time < end_dt)
        # ).with_entities(func.sum(model.amount)).first()[0]

        infos = model.query.filter_by(
            **kwargs
        ).with_entities(       # 查询指定的列
            model.type, func.sum(model.amount), func.date(model.create_time),
            func.avg(model.capacity),
        ).filter(
            and_(model.create_time > from_dt,
                 model.create_time < end_dt)
        ).order_by(
            model.create_time.desc()
        ).group_by(
            model.type,
            func.date(model.create_time)
        ).limit(limit).offset(offset).all()

        total_records = model.query.filter_by(
            **kwargs
        ).group_by(
            func.to_days(model.create_time)
        ).count()

        date_incomes = {}
        for income_type, amount, create_time, capacity in infos:
            create_time = str(create_time)
            if create_time not in date_incomes:
                date_incomes[create_time] = {'coop_income': 0,
                                             'mining_income': 0,
                                             "manage_money_income": 0,
                                             'capacity': 0}
            day_income = date_incomes[create_time]
            filed_name = "coop_income"
            if income_type == IncomeTypeMining:
                filed_name = "mining_income"
                day_income["capacity"] = capacity
            elif income_type == IncomeTYpemanagemoney:
                filed_name = "manage_money_income"
            day_income[filed_name] = amount
            day_income["total_income"] = day_income.get("total_income",
                                                        0) + amount
        records = sorted(date_incomes.items(), key=lambda k: k[0], reverse=True)
        return make_resp(records=records, total_records=total_records)


class MiningIncomeApi(Resource):
    decorators = [login_required]

    def get(self):
        account_key = g.account_key
        parse = reqparse.RequestParser()
        now = int(time.time())
        parse.add_argument('limit', type=int, required=False, default=10)
        parse.add_argument('offset', type=int, required=False, default=0)
        parse.add_argument('from', type=int, required=False, default=0)
        parse.add_argument('end', type=int, required=False, default=now)
        parse.add_argument('coin_name', type=str, required=False)
        parse.add_argument('status', type=int, required=False)
        parse.add_argument('type', type=int, required=False)
        args = parse.parse_args()
        limit = args.get('limit')
        offset = args.get('offset')
        from_ts = args.get('from')
        end_ts = args.get('end')
        coin_name = args.get('coin_name')
        status = args.get('status')
        mining_type = args.get('type')
        if mining_type in [IncomeTypeMining, IncomeTYpeMiningEcol]:
            mining_type = [mining_type]
        else:
            mining_type = [IncomeTypeMining, IncomeTYpeMiningEcol]
        from_dt = datetime.fromtimestamp(from_ts)
        end_dt = datetime.fromtimestamp(end_ts)
        kwargs = {"account_key": account_key}
        if not coin_name:
            coin_name = BHD_COIN_NAME
        if coin_name == BHD_COIN_NAME:
            model = IncomeRecord
        elif coin_name == LHD_NAME:
            model = LHDIncomeRecord
        elif coin_name == DISK_NAME:
            model = DISKIncomeRecord
        elif coin_name == HDD_NAME:
            model = HDDIncomeRecord
        elif coin_name == NEWBI_NAME:
            model = NBIncomeRecord
        else:
            return make_resp(400, False, message="请求币种错误")
        infos = model.query.filter_by(
            **kwargs
        ).filter(
            model.type.in_(mining_type)
        ).filter(
            and_(model.create_time > from_dt,
                 model.create_time < end_dt)
        ).order_by(
            model.create_time.desc()
        ).limit(limit).offset(offset).all()

        total_records = model.query.filter_by(
            **kwargs
        ).filter(
            model.type.in_(mining_type)
        ).count()

        records = [info.to_dict() for info in infos]

        client = get_rpc(coin_name)
        latest_height = client.get_latest_block_number()
        return make_resp(records=records, total_records=total_records, latest_height=latest_height)


class CoopIncomeApi(Resource):
    decorators = [login_required]

    def get(self):
        account_key = g.account_key
        parse = reqparse.RequestParser()
        now = int(time.time())
        parse.add_argument('limit', type=int, required=False, default=10)
        parse.add_argument('offset', type=int, required=False, default=0)
        parse.add_argument('from', type=int, required=False, default=0)
        parse.add_argument('end', type=int, required=False, default=now)
        parse.add_argument('coin_name', type=str, required=False)
        parse.add_argument('status', type=int, required=False)
        args = parse.parse_args()
        limit = args.get('limit')
        offset = args.get('offset')
        from_ts = args.get('from')
        end_ts = args.get('end')
        coin_name = args.get('coin_name') or BHD_COIN_NAME
        status = args.get('status')
        from_dt = datetime.fromtimestamp(from_ts)
        end_dt = datetime.fromtimestamp(end_ts)
        kwargs = {"account_key": account_key}
        if coin_name == LHD_NAME:
            model = LHDIncomeRecord
        elif coin_name == DISK_NAME:
            model = DISKIncomeRecord
        elif coin_name == HDD_NAME:
            model = HDDIncomeRecord
        else:
            model = IncomeRecord
        infos = model.query.filter_by(
            **kwargs
        ).filter(
            model.type.in_([IncomeTYpeCoopReward])
        ).filter(
            and_(model.create_time > from_dt,
                 model.create_time < end_dt)
        ).order_by(
            model.create_time.desc()
        ).limit(limit).offset(offset).all()

        total_records = model.query.filter_by(
            **kwargs
        ).filter(
            model.type.in_([IncomeTYpeCoopReward])
        ).count()

        records = [info.to_dict() for info in infos]

        client = get_rpc(coin_name)
        latest_height = client.get_latest_block_number()
        return make_resp(records=records, total_records=total_records, latest_height=latest_height)


class ManageIncomeApi(Resource):
    """
    理财数据
    """
    decorators = [login_required]

    def get(self):
        account_key = g.account_key
        parse = reqparse.RequestParser()
        now = int(time.time())
        parse.add_argument('limit', type=int, required=False, default=10)
        parse.add_argument('offset', type=int, required=False, default=0)
        parse.add_argument('from', type=int, required=False, default=0)
        parse.add_argument('end', type=int, required=False, default=now)
        parse.add_argument('coin_name', type=str, required=False)
        parse.add_argument('status', type=int, required=False)
        args = parse.parse_args()
        limit = args.get('limit')
        offset = args.get('offset')
        from_ts = args.get('from')
        end_ts = args.get('end')
        coin_name = args.get('coin_name') or BHD_COIN_NAME
        status = args.get('status')
        from_dt = datetime.fromtimestamp(from_ts)
        end_dt = datetime.fromtimestamp(end_ts)

        # 获取model
        model_record = TeamWorkRecordActivity
        model = TeamWorkActivity
        if coin_name == "lhd":
            model_record = LHDTeamWorkRecordActivity
            model = LHDTeamWorkActivity

        # 联表查询
        infos = model_record.query.filter_by(
            account_key=account_key, type=2     # 筛选用户，筛选活动类型为理财类型
        ).join(
            model, model_record.cooperation_id == model.id   # 通过合作id字段与活动表id联表
        ).with_entities(
            model.rate, model_record.coo_amount, model_record.income,
            model.deadline, model_record.create_time, model_record.end_time,
            model_record.status        # 筛选所需列，（年化，投入金额，收益，周期，开始时间，结束时间，目前状态）
        ).filter(
            and_(model_record.create_time > from_dt,
                 model_record.create_time < end_dt)
        ).order_by(
            model_record.create_time.desc()
        ).limit(limit).offset(offset).all()

        # 理财数据数量
        total_records = model_record.query.filter_by(
            account_key=account_key, type=2
        ).join(
            model, model_record.cooperation_id == model.id
        ).with_entities(
            model.rate, model_record.coo_amount, model_record.income,
            model.deadline, model_record.create_time, model_record.end_time,
            model_record.status
        ).count()

        records = []
        for info in infos:
            dict_pro = {}
            dict_pro["rate"] = info.rate
            dict_pro["coo_amount"] = info.coo_amount
            dict_pro["income"] = info.income
            dict_pro["deadline"] = info.deadline
            dict_pro["create_time"] = info.create_time
            dict_pro["end_time"] = info.end_time
            dict_pro["status"] = info.status
            records.append(dict_pro)

        return make_resp(records=records, total_records=total_records)





