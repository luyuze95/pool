# encoding=utf-8

"""
    @author: anzz
    @date: 2019/6/17
"""
import time
from datetime import datetime

from flask import g
from flask_restful import Resource, reqparse
from sqlalchemy import and_

from models.activity_reward import ActivityReward
from resources.auth_decorator import login_required
from utils.response import make_resp


class ActivityRewards(Resource):
    decorators = [login_required]

    def get(self):
        account_key = g.account_key
        parse = reqparse.RequestParser()
        now = int(time.time())
        ten_days = now - 864000
        parse.add_argument('limit', type=int, required=False, default=10)
        parse.add_argument('offset', type=int, required=False, default=0)
        parse.add_argument('from', type=int, required=False, default=ten_days)
        parse.add_argument('end', type=int, required=False, default=now)
        parse.add_argument('coin_name', type=str, required=False)
        parse.add_argument('status', type=int, required=False)
        args = parse.parse_args()
        limit = args.get('limit')
        offset = args.get('offset')
        from_ts = args.get('from')
        end_ts = args.get('end')
        from_dt = datetime.fromtimestamp(from_ts)
        end_dt = datetime.fromtimestamp(end_ts)
        kwargs = {"account_key": account_key}

        infos = ActivityReward.query.filter_by(
            **kwargs
        ).filter(
            and_(ActivityReward.create_time > from_dt,
                 ActivityReward.create_time < end_dt)
        ).filter(
            ActivityReward.amount > 0
        ).order_by(
            ActivityReward.create_time.desc()
        ).limit(limit).offset(offset).all()

        total_records = ActivityReward.query.filter_by(
            **kwargs
        ).filter(ActivityReward.amount > 0).count()

        records = [info.to_dict() for info in infos]
        return make_resp(records=records, total_records=total_records)
