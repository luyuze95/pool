# encoding=utf-8

"""
    @author: anzz
    @date: 2019/7/11
"""

import time
from datetime import datetime

from flask import g
from flask_restful import Resource, reqparse
from sqlalchemy import and_, literal

from models import db
from models.bhd_burst import BurstBlock, EcolBurstBlock, NBBurstBlock, \
    LHDBurstBlock, DISKBurstBlock, LHDMainBurstBlock, HDDECOLBurstBlock
from resources.auth_decorator import login_required
from utils.response import make_resp
from conf import *


class BurstBlockApi(Resource):
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
        coin_name = args.get('coin_name')
        status = args.get('status')
        from_dt = datetime.fromtimestamp(from_ts)
        end_dt = datetime.fromtimestamp(end_ts)
        kwargs = {"account_key": account_key}

        if not coin_name:
            coin_name = BHD_COIN_NAME

        if coin_name == BHD_COIN_NAME:
            model = BurstBlock
            query_deadline = model.deadline
        elif coin_name == LHD_NAME:
            model = LHDBurstBlock
            query_deadline = model.deadline
        elif coin_name == DISK_NAME:
            model = DISKBurstBlock
            query_deadline = model.deadline
        elif coin_name == HDD_NAME:
            model = HDDECOLBurstBlock
            query_deadline = model.deadline
        else:
            model = NBBurstBlock
            query_deadline = literal("0")
        if coin_name == BHD_COIN_NAME:
            coop_query = db.session.query(model.plotter_id, model.height,
                                          query_deadline,
                                          model.create_time.label(
                                              'create_time'),
                                          literal("coop")
                                          ).filter_by(account_key=account_key
                                                      ).filter(
                and_(model.create_time > from_dt,
                     model.create_time < end_dt))
        else:   # coin_name == LHD_NAME:
            coop_query = db.session.query(model.plotter_id, model.height,
                                          query_deadline,
                                          model.create_time.label(
                                              'create_time'),
                                          literal("ecol")
                                          ).filter_by(account_key=account_key
                                                      ).filter(
                and_(model.create_time > from_dt,
                     model.create_time < end_dt))
        # else:
        #     coop_query = db.session.query(model.plotter_id, model.height,
        #                                   query_deadline,
        #                                   model.create_time.label(
        #                                       'create_time'),
        #                                   literal("ecol")
        #                                   ).filter_by(account_key=account_key
        #                                               ).filter(
        #         and_(model.create_time > from_dt,
        #              model.create_time < end_dt))


        if coin_name == NEWBI_NAME:
            coops = coop_query.limit(limit).offset(offset).all()
            coops = [coop.to_dict() for coop in coops]
            return make_resp(records=coops, total_records=len(coops))
        ecol_query = None
        if coin_name == BHD_COIN_NAME:
            ecol_query = db.session.query(EcolBurstBlock.plotter_id,
                                          EcolBurstBlock.height,
                                          EcolBurstBlock.deadline,
                                          EcolBurstBlock.create_time.label(
                                              'create_time'),
                                          literal("ecol")
                                          ).filter_by(account_key=account_key
                                                      ).filter(
                and_(EcolBurstBlock.create_time > from_dt,
                     EcolBurstBlock.create_time < end_dt))
        elif coin_name == LHD_NAME:
            ecol_query = db.session.query(LHDMainBurstBlock.plotter_id,
                                          LHDMainBurstBlock.height,
                                          LHDMainBurstBlock.deadline,
                                          LHDMainBurstBlock.create_time.label(
                                              'create_time'),
                                          literal("coop")
                                          ).filter_by(account_key=account_key
                                                      ).filter(
                and_(LHDMainBurstBlock.create_time > from_dt,
                     LHDMainBurstBlock.create_time < end_dt))
        all_burst = None
        if coin_name in [BHD_COIN_NAME, LHD_NAME]:
            all_burst = coop_query.union_all(ecol_query).order_by(
                'create_time').all()[::-1][offset:limit]
        elif coin_name in [DISK_NAME, HDD_NAME]:
            all_burst = coop_query.order_by(
                'create_time').all()[::-1][offset:limit]
        total_records = len(all_burst)
        return make_resp(records=all_burst, total_records=total_records)
