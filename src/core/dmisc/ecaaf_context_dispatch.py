"""The dispatcher interface to forward events and bind requests to the
respective kafka queues"""

from confluent_kafka import Producer
import json
import ecaaf_logger

__author__      = "Swanand Rao"
__copyright__   = ""
__credits__     = ["Swanand Rao"]
__license__     = ""
__version__     = "0.1"
__maintainer__  = "Swanand Rao"
__email__       = "swanand.rao@gmail.com"
__status__      = "pre-alpha"

__logger = ecaaf_logger.get_logger('ecaaf_context_dispatch')
p = Producer({'bootstrap.servers': 'localhost:9092'})

def ack(err, msg):
    if err is not None:
        print("Failed to deliver message: {0}: {1}"
              .format(msg.value(), err.str()))
    else:
        print(str(msg.value()))

def dispatch_event_req(msg):
    try:
        __logger.info("Queuing message {0} in topic :{1}".format(str(msg),'event-exec-1'))
        #elastic store the event -  queued
        p.produce('event-exec-1', value=json.dumps(msg), callback=ack)
    except:
        __logger.error("Error dispatching {0} in topic :{1}".format(str(msg),'event-exec-1'))

def dispatch_bind_req(msg):
    try:
        __logger.info("Queuing message {0} in topic :{1}".format(str(msg),'binder'))
        p.produce('binder', value=json.dumps(msg), callback=ack)
    except:
        __logger.error("Error dispatching {0} in topic :{1}".format(str(msg),'binder'))

def dispatch_analyzer_req(msg):
    try:
        __logger.info("Queuing message {0} in topic :{1}".format(str(msg),'analyzer'))
        p.produce('analyzer', value=json.dumps(msg), callback=ack)
    except:
        __logger.error("Error dispatching {0} in topic :{1}".format(str(msg),'analyzer'))
