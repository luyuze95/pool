# encoding=utf-8

"""
    @author: anzz
    @date: 2019/5/13
"""
import os

python_env = os.getenv('python_env', True)

if python_env in ('0', False, 'prod', "PRODUCTION"):
    GLOBAL_DEBUG = False
    from .conf_prod import *
else:
    GLOBAL_DEBUG = True
    from .conf_debug import *


"""the same configure between debug and prod"""
PRIVATE_TOKEN = b"<O\\wbUn%S~e`@T888@]cyb.,:GanzziM"

PRIVATE_TOKEN_IV = b"zmI666&s_2{+sTuT"

