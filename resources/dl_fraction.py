# encoding=utf-8

"""
    @author: anzz
    @date: 2019/7/16
"""
import time
from datetime import datetime

from flask import g
from flask_restful import Resource, reqparse
from sqlalchemy import and_, literal

from models import db

from models.dl_fraction import DeadlineFraction, DeadlineFractionEcology, NBDeadlineFraction
from resources.auth_decorator import login_required
from utils.response import make_resp
from conf import *


class DeadlineFractionApi(Resource):

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
        coin_name = args.get('coin_name', BHD_COIN_NAME)
        status = args.get('status')
        from_dt = datetime.fromtimestamp(from_ts)
        end_dt = datetime.fromtimestamp(end_ts)
        kwargs = {"account_key": account_key}

        if coin_name == BHD_COIN_NAME:
            model = DeadlineFraction
        else:
            model = NBDeadlineFraction

        coop_query = db.session.query(model.height,
                                      literal("coop"),
                                      model.fraction,
                                      model.deadline,
                                      model.miner_name,
                                      model.plotter_id,
                                      model.create_time.label('create_time'),
                                      ).filter_by(account_key=account_key
                                                  ).filter(
            and_(model.create_time > from_dt,
                 model.create_time < end_dt))

        if coin_name == NEWBI_NAME:
            all_dls = coop_query.limit(limit).offset(offset).all()
            dls = [dl.to_dict() for dl in all_dls]
            return make_resp(records=dls, total_records=len(dls))

        ecol_query = db.session.query(DeadlineFractionEcology.height,
                                      literal("ecol"),
                                      DeadlineFractionEcology.fraction,
                                      DeadlineFractionEcology.deadline,
                                      DeadlineFractionEcology.miner_name,
                                      DeadlineFractionEcology.plotter_id,
                                      DeadlineFractionEcology.create_time.label('create_time'),
                                      ).filter_by(account_key=account_key
                                                  ).filter(
            and_(DeadlineFractionEcology.create_time > from_dt,
                 DeadlineFractionEcology.create_time < end_dt))

        all_dls = coop_query.union_all(ecol_query).order_by('create_time').all()[::-1][offset:limit]
        total_records = len(all_dls)
        return make_resp(records=all_dls, total_records=total_records)

