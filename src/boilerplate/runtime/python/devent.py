""" This file is packed in the container and acts as a helper function to make
outbound ReST calls """
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
import dconfig
__logger = dlogger.get_logger(__name__)
def ecaaf_fire_event(name, params):
    r=None
    params={}
    data={}
    username='admin'
    password='admin'
    url=dconfig.apigateway()
    headers = {'Content-type':'application/json', 'Accept':'application/json'}
    data['event_name']=name
    data['params']=params
    ##This is probably not the best way to handle ssl certification errors
    ##need to revaluate it. The same applies to verify=False for put,get,post,delete
    ##calls.
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    auth=HTTPBasicAuth(username, password)
    try:
        r = requests.post(url, auth=auth,data=json.dumps(data), \
                        headers=headers, verify=False)
    except:
        __logger.error('Could not process rest request', exc_info=True)

    if r:
        if r.status_code in [200,201]:
            __logger.info("Event fired with return code %s" %(str(r.status_code)))
    else:
        __logger.error("Event failed with return code %s" %(str(r.status_code)), exc_info=True)
    return r
