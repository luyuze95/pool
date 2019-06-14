# encoding=utf-8

"""
    @author: anzz
    @date: 2019/5/30
"""
import json
import time
from datetime import datetime

from flask import g
from flask_restful import Resource, reqparse
from sqlalchemy import func

from models import db
from models.income_record import IncomeRecord, IncomeEcologyRecord
from resources.auth_decorator import login_required
from rpc.authproxy import encode_python_object
from utils.response import make_resp


class EarningsTotalApi(Resource):
    decorators = [login_required]

    def get(self):
        """
        获取用户总收益
        :return:
        """
        account_key = g.account_key
        coop_total_amount = IncomeRecord.query.filter_by(account_key=account_key).with_entities(func.sum(IncomeRecord.amount)).first()[0]
        ecol_total_amount = IncomeEcologyRecord.query.filter_by(account_key=account_key).with_entities(func.sum(IncomeEcologyRecord.amount)).first()[0]
        if not coop_total_amount:
            coop_total_amount = 0
        if not ecol_total_amount:
            ecol_total_amount = 0
        return make_resp(coop_total_amount=coop_total_amount, ecol_total_amount=ecol_total_amount)


class DayEarningsApi(Resource):

    decorators = [login_required]

    def get(self):
        """
        按天获取收益列表
        :return:
        """
        parse = reqparse.RequestParser()

        now = int(time.time())
        ten_days = now - 864000
        parse.add_argument('limit', type=int, required=False, default=10)
        parse.add_argument('offset', type=int, required=False, default=0)
        parse.add_argument('from', type=int, required=False, default=ten_days)
        parse.add_argument('end', type=int, required=False, default=now)
        parse.add_argument('status', type=int, required=False)
        args = parse.parse_args()
        limit = args.get('limit')
        offset = args.get('offset')
        from_ts = args.get('from')
        end_ts = args.get('end')
        status = args.get('status')
        from_dt = datetime.fromtimestamp(from_ts)
        end_dt = datetime.fromtimestamp(end_ts)

        account_key = g.account_key
        results = db.session.execute("""
            SELECT
	        SUM(amount),
	        MAX(create_time),
	        AVG(capacity)
            FROM
	        pool_bhd_income_record 
            WHERE
	        is_add_asset=1 and account_key = '%s'
            GROUP BY
            TO_DAYS( create_time )
            ORDER BY 
            create_time
            DESC 
            LIMIT %s, %s
            """ % (account_key, offset, limit)).fetchall()
        if not results:
            return make_resp(200, True)
        for index, result in enumerate(results):
            results[index] = json.loads(json.dumps(list(result), default=encode_python_object))
        return make_resp(200, True, days_earnings=results)



