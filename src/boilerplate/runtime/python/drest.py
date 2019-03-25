""" Add description """
import json
import requests
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning

__author__      = "Swanand Rao"
__copyright__   = ""
__credits__     = ["Swanand Rao"]
__license__     = ""
__version__     = "0.1"
__maintainer__  = "Swanand Rao"
__email__       = "swanand.rao@gmail.com"
__status__      = "pre-alpha"


import dlogger

def ecaaf_rest(url, e, type):
    r=None
    params={}
    data={}
    username='root'
    password='l1a'
    headers = {'Content-type':'application/json', 'Accept':'application/json'}
    __logger = dlogger.get_logger(__name__)
    ##This is probably not the best way to handle ssl certification errors
    ##need to revaluate it. The same applies to verify=False for put,get,post,delete
    ##calls.
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    if 'binding' in e:
        if 'target_username' in e['binding']:
            username=e['binding']['target_username']
        if 'target_password' in e['binding']:
            password=e['binding']['target_password']
    else:
        __logger.info('No binding object found...')
    if 'params' in e:
        params=e['params']
    else:
        __logger.info('No param object found...')
    if 'data' in e:
        data=e['data']
    else:
        __logger.info('No data object found...')
    auth=HTTPBasicAuth(username, password)
    try:
        if (type=='get'):
            r = requests.get(url, auth=auth, \
                            params=params,data=json.dumps(data), headers=headers, \
                            verify=False)
        if (type=='post'):
            r = requests.post(url, auth=auth, \
                            params=params,data=json.dumps(data), headers=headers, \
                            verify=False)
        if (type=='delete'):
            r = requests.delete(url, auth=auth, \
                            params=params,data=json.dumps(data), headers=headers, \
                            verify=False)
        if (type=='put'):
            r = requests.put(url, auth=auth, \
                            params=params,data=json.dumps(data), headers=headers, \
                            verify=False)
        e['action_response']=r
        __logger.info("Event: %s"%(json.dumps(data)))
    except:
        __logger.error('Could not process rest request', exc_info=True)

    if r:
        if r.status_code in [200,201]:
            __logger.info("Event %s completed with return code %s" %(e['event_id'], str(r.status_code)))
    else:
        __logger.error("Event %s failed with return code %s" %(e['event_id'], str(r.status_code)), exc_info=True)
    return r
