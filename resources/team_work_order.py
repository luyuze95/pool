# encoding=utf-8

"""
    @author: lyz
    @date: 2019/8/29
"""
import time
from datetime import datetime

from flask import g
from flask_restful import Resource, reqparse
from sqlalchemy import and_

from conf import *
from models.remote_pledge import TeamWorkRecordActivity
from models.remote_pledge_lhd import LHDTeamWorkRecordActivity
from resources.auth_decorator import login_required
from utils.response import make_resp


class TeamWorkOrderApi(Resource):
    decorators = [login_required]

    def get(self):
        """
        用户合作订单信息
        :return:
        """
        account_key = g.account_key
        parse = reqparse.RequestParser()
        now = int(time.time())
        parse.add_argument('coin_name', type=str, required=False)
        parse.add_argument('limit', type=int, required=False, default=10)
        parse.add_argument('offset', type=int, required=False, default=0)
        parse.add_argument('from', type=int, required=False, default=0)
        parse.add_argument('end', type=int, required=False, default=now)
        args = parse.parse_args()
        coin_name = args.get('coin_name') or BHD_COIN_NAME
        limit = args.get('limit')
        offset = args.get('offset')
        from_ts = args.get('from')
        end_ts = args.get('end')
        from_dt = datetime.fromtimestamp(from_ts)
        end_dt = datetime.fromtimestamp(end_ts)
        coin_name = coin_name.lower()
        kwargs = {"account_key": account_key}
        if coin_name == LHD_NAME:
            model = LHDTeamWorkRecordActivity
        else:
            model = TeamWorkRecordActivity
        teamworkorders = model.query.filter_by(
            **kwargs
        ).filter(
            and_(model.create_time > from_dt,
                 model.create_time < end_dt)
        ).limit(limit).offset(offset).all()

        total_records = model.query.filter_by(
            **kwargs
        ).count()
        records = [teamworkorder.to_dict() for teamworkorder in teamworkorders]
        return make_resp(records=records, total_records=total_records)




