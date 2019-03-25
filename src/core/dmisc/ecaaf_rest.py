"""This file can be marked for removal..."""

import requests

__author__      = "Swanand Rao"
__copyright__   = ""
__credits__     = ["Swanand Rao"]
__license__     = ""
__version__     = "0.1"
__maintainer__  = "Swanand Rao"
__email__       = "swanand.rao@gmail.com"
__status__      = "pre-alpha"

__basedir=''
__ecaaf_api_gateway=""

def ecaaf_api_gateway_upload_file(data):
    url = __ecaaf_api_gateway+'uploads'
    headers = {'Content-type': 'multipart/form-data'}
    fileobj = open(data['fpath']+'/'+data['fname'], 'rb')
    r = requests.post(url, data = data, files={"file": (fname, fileobj)})

def ecaaf_api_get_event_binding(ename):
    return

def ecaaf_api_get_event_binding_all():
    return

def ecaaf_target_rest_put(data):
    return

def ecaaf_target_rest_get(data):
    return

def ecaaf_target_rest_delete(data):
    return

def ecaaf_target_rest_post(data):
    return
