# encoding=utf-8

"""
    @author: anzz
    @date: 2019/5/30
"""

from flask import g, request
from flask_restful import Resource, reqparse

from models.income_record import IncomeRecord
from resources.auth_decorator import login_required
from utils.redis_ins import redis_capacity
from utils.response import make_resp


class EarningsApi(Resource):
    decorators = [login_required]

    def get(self):
        """
        获取收益列表
        :return:
        """
        parse = reqparse.RequestParser()
        parse.add_argument('limit', type=int, required=False)
        parse.add_argument('offset', type=int, required=False)
        parse.add_argument('t', type=int, required=False)
        args = parse.parse_args()
        limit = args.get('limit')
        offset = args.get('offset')
        account_key = g.account_key
        # incomes = IncomeRecord.query.filter_by(account_key=account_key, is_add_asset=1).order_by(IncomeRecord.create_time.desc()).limit(limit).offset(offset).all()
        incomes = IncomeRecord.query.filter_by(account_key=account_key, is_add_asset=0).order_by(IncomeRecord.create_time.desc()).limit(limit).offset(offset).all()

        for index, income in enumerate(incomes):
            income_dict = income.to_dict()
            keys_pattern = "miner:%s:*" % income.account_key
            miners_capacity_keys = redis_capacity.keys(keys_pattern)
            total_capacity = sum([int(redis_capacity.get(miner_capacity_key).split(":")[0]) for miner_capacity_key in miners_capacity_keys])
            income_dict["total_capacity"] = total_capacity
            incomes[index] = income_dict

        return make_resp(incomes=incomes)
