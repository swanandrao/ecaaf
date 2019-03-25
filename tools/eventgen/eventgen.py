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

def fire_event(u,p,e,type):
    r=None
    params={}
    data={}
    username='admin'
    password='admin'
    service_url='http://localhost:5000'
    if 'service_url' in e:
        service_url=e['service_url']
    url=service_url+'/ecaaf/api/v1.0/events'

    headers = {'Content-type':'application/json', 'Accept':'application/json'}
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    if 'event' in e:
        data=e['event']
    else:
        print('No data object found...')

    auth=HTTPBasicAuth(username, password)

    try:
        print("Sending event to %s"%e['service_url'])
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
    except:
        print('Could not process rest request...')

    if r:
        if r.status_code in [200,201]:
            print("Event delivered with return code %s" %(str(r.status_code)))
    else:
        print("Event delivery failed with return code %s" %(str(r.status_code)))
    return r

e={}
with open('event.json', 'r') as f:
    e = json.load(f)
fire_event("", "", e, e["request_type"])
