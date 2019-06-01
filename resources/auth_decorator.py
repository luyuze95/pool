# encoding=utf-8

"""
    @author: anzz
    @date: 2019/5/29
"""
from functools import wraps

import jwt
from flask import request, g

from conf import JWT_SECRET
from logs import api_logger
from models.user import User
from utils.response import make_resp


def login_required(f):

    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get("token")
        if token is None:
            return make_resp(401, False, message="token not found")
        try:
            auth_dict = jwt.decode(token, JWT_SECRET, audience='pool')
        except Exception as e:
            api_logger.error("auth failed %s" % str(e))
            return make_resp(401, False, message="auth failed")

        account_key = auth_dict.get("accountKey")
        userid = auth_dict.get("userid")
        user = User.query.filter_by(account_key=account_key).first()
        if not user or user.account_key != account_key:
            return make_resp(401, False, message="account key not found")
        g.account_key = account_key
        g.user = user
        return f(*args, **kwargs)
    return wrapper


