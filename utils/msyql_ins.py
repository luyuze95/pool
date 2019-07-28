# encoding=utf-8

"""
    @author: anzz
    @date: 2019/5/23
"""

import threading
import pymysql

from conf import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB
from models import db
from models.block_offset import BlockOffset


class MysqlSingleton(object):
    lock = threading.Lock()
    MAX_CONNECTION = 10

    @staticmethod
    def get_instance(database="wallet"):
        if hasattr(MysqlSingleton, "_instance"):
            return MysqlSingleton._instance

        MysqlSingleton.lock.acquire()
        try:
            if not hasattr(MysqlSingleton, "_instance"):
                conn = pymysql.connect(host=MYSQL_HOST,
                                       port=MYSQL_PORT,
                                       user=MYSQL_USER,
                                       password=MYSQL_PASSWORD,
                                       db=database)
                MysqlSingleton._instance = conn
        finally:
            MysqlSingleton.lock.release()
        return MysqlSingleton._instance


def do_select_all(sql, args=None, database=MYSQL_DB):
    conn = MysqlSingleton.get_instance(database)
    conn.connect()
    result = []
    try:
        cursor = conn.cursor()

        cursor.execute(sql, args)
        rows = cursor.fetchall()
        for row in rows:
            result.append(row)
        cursor.close()
    except Exception as e:
        print(e, "exception")
    finally:
        if conn:
            conn.close()
    return result


def initialize_offset(offset_name, offset, latest_block_number=0):
    if offset is None:
        init_offset = latest_block_number
        offset = BlockOffset(offset_name, init_offset)
        db.session.add(offset)
        db.session.commit()
    return offset
