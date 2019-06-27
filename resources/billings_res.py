# encoding=utf-8

"""
    @author: anzz
    @date: 2019/6/27
"""

import time
from datetime import datetime

from flask import g
from flask_restful import Resource, reqparse
from sqlalchemy import and_

from models.billings import Billings
from resources.auth_decorator import login_required
from utils.response import make_resp


class OthersBill(Resource):
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
        parse.add_argument('type', type=list, required=False)
        args = parse.parse_args()
        limit = args.get('limit')
        offset = args.get('offset')
        from_ts = args.get('from')
        end_ts = args.getlist('end')
        billing_types = args.get('type')
        billing_types = [int(billing_type) for billing_type in billing_types if
                         billing_type.isalnum()]
        from_dt = datetime.fromtimestamp(from_ts)
        end_dt = datetime.fromtimestamp(end_ts)

        infos = Billings.query.filter_by(
            account_key=account_key,
        ).filter(
            Billings.type.in_(billing_types),
        ).filter(
            and_(Billings.create_time > from_dt,
                 Billings.create_time < end_dt)
        ).order_by(
            Billings.create_time.desc()
        ).limit(limit).offset(offset).all()

        total_records = Billings.query.filter_by(
            account_key=account_key,
        ).filter(
            Billings.type.in_(billing_types), ).count()

        records = [info.to_dict() for info in infos]

        return make_resp(records=records, total_records=total_records)
