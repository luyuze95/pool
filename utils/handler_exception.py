# encoding=utf-8

"""
    @author: lyz
    @date: 2019/5/29
"""

from traceback import format_exc

from flask import request
from flask_restful import Api

from logs import api_logger
from utils.response import make_resp


class APIHandleError(Api):

    def handle_error(self, error):
        msg = "API_ERROR>>>url:%s, method:[%s], data:%s" % (
        request.url, request.method, request.form)
        from models import db
        db.session.rollback()
        api_logger.error(msg)
        api_logger.error(format_exc())
        return make_resp(500, False, message="error")
