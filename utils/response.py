# encoding=utf-8

"""
    @author: lyz
    @date: 2019/5/29
"""
from flask import make_response, json

from rpc.authproxy import encode_python_object


def make_resp(code=200, success=True, message='', **kwargs):
    result = {
        "success": success,
    }
    if success:
        result.setdefault("data", kwargs)
    else:
        result.setdefault("message", message)

    resp = make_response(json.dumps(result, default=encode_python_object), code)
    resp.headers['Content-Type'] = "application/json; charset=utf-8"
    return resp