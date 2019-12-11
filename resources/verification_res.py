# encoding=utf-8

"""
    @author: lyz
    @date: 2019/6/3
"""

from random import randint

from flask import g
from flask_restful import Resource, reqparse

from resources.auth_decorator import login_required
from utils.redis_ins import redis_auth
from utils.response import make_resp


class VerifyApi(Resource):
    decorators = [login_required]

    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('code_type', type=str, required=False, trim=True, default='withdrawal')
        args = parse.parse_args()
        code_type = args.get('code_type').lower()
        account_key = g.account_key

        pass_code = randint(0, 999999)
        key = "%s:seccode:%s" % (code_type, account_key)
        redis_auth.set(key, pass_code, ex=5 * 60)
        from schedule.task_email import email_sender_task
        email_sender_task.delay(g.user.email, pass_code, g.token)

        return make_resp(200, True)
