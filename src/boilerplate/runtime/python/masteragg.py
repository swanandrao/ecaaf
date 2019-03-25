import threading
import time
import sys
import json
import os
import ast

import dconfig
import dlogger
import ddb

import ecaaf_modules


__author__      = "Swanand Rao"
__copyright__   = ""
__credits__     = ["Swanand Rao"]
__license__     = ""
__version__     = "0.1"
__maintainer__  = "Swanand Rao"
__email__       = "swanand.rao@gmail.com"
__status__      = "pre-alpha"


__logger = dlogger.get_logger('master_opt')

class masterThread (threading.Thread):
    def __init__(self, modname, functionname, event):
      threading.Thread.__init__(self)
      self.modname = modname
      self.functionname = functionname
      self.event=event

    def run(self):
      self.process_data(self.modname, self.functionname, self.event)

    def process_data(self, modname, functionname, event):
        getattr(modname, functionname)(event)

if (os.path.isfile('requirements.txt')):
    os.system('pip install -r requirements.txt')

threads = []
event={'event_name':'DUMMY',
    'event_id':'DUMMY'}
functionList=[ecaaf_modules]
try:
    if 'event' in os.environ:
         instr=ast.literal_eval(os.environ['event'])
         event=json.loads(instr)
         #t=event['binding']['target_url']
    __logger.info("Executing event: %s "%event['event_name'])

    # Create new threads
    for  modname in functionList:
        thread = masterThread(modname, 'ecaaf_action_funclet', event)
        thread.start()
        threads.append(thread)
    # Wait for all threads to complete
    for t in threads:
        t.join()
except:
    __logger.error("Error in master aggregator", exc_info=True)
