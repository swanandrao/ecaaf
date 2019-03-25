""""This module is responsible for the management of all database connections
    and mappings. Currently redis is the key-value database and postgre is the
    planned sql db.
"""

import dlogger
import redis
import json

__author__      = "Swanand Rao"
__copyright__   = ""
__credits__     = ["Swanand Rao"]
__license__     = ""
__version__     = "0.1"
__maintainer__  = "Swanand Rao"
__email__       = "swanand.rao@gmail.com"
__status__      = "pre-alpha"

__logger = dlogger.get_logger('master_db')

try:
    r = redis.StrictRedis(host='http://docker.for.mac.host.internal', port=6379, db=0)
except:
    __logger.error("redis is not reachable...", exc_info=True)

def kvdb_set(key, val):
    r.set(key, json.dumps(val))

def kvdb_get(key):
    ret=r.get(key)
    if ret:
        return json.loads(ret)
    return ret

def kvdb_rpush(key, val):
    print key
    r.rpush(key, json.dumps(val))

def kvdb_get_list(key):
    ret=[]
    for i in range(0, r.llen(key)):
        ret.append(jason.loads(r.lindex(key, i)))
    return ret

def kvdb_delete(key):
    r.delet(key)

def kvdb_del(key):
    return r.delete(key)
