""" Master script for python container environment."""
import sys
import json
import os
import ast

import dconfig
import dlogger
import ddb

import ecaaf_action_pre
import ecaaf_action_post
import ecaaf_action_handler
import ecaaf_generic_handler

__author__      = "Swanand Rao"
__copyright__   = ""
__credits__     = ["Swanand Rao"]
__license__     = ""
__version__     = "0.1"
__maintainer__  = "Swanand Rao"
__email__       = "swanand.rao@gmail.com"
__status__      = "pre-alpha"

__logger = dlogger.get_logger('master')
event={'event_name':'DUMMY',
    'event_id':'DUMMY'}
if (os.path.isfile('requirements.txt')):
    os.system('pip install -r requirements.txt')
try:
    if 'event' in os.environ:
        instr=ast.literal_eval(os.environ['event'])
        event=json.loads(instr)
    #t=event['binding']['target_url']
    __logger.info("Executing event: %s "%event['event_name'])
    ecaaf_action_pre.ecaaf_pre_action_funclet(event)
    ecaaf_action_handler.ecaaf_action_funclet(event)
    #elastic event- sucess or failed check return val of ecaaf_action_funclet
    ecaaf_action_post.ecaaf_post_action_funclet(event)
    ecaaf_generic_handler.ecaaf_generic_funclet(event)
except:
    __logger.error("Error in main", exc_info=True)
