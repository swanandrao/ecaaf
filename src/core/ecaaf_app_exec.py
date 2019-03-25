""" Processor for bind reqeuests and new action funclets"""

from confluent_kafka import Consumer, KafkaError
import json
import sys

from dmisc import ecaaf_config, ecaaf_db, ecaaf_logger, ecaaf_utils

__author__      = "Swanand Rao"
__copyright__   = ""
__credits__     = ["Swanand Rao"]
__license__     = ""
__version__     = "0.1"
__maintainer__  = "Swanand Rao"
__email__       = "swanand.rao@gmail.com"
__status__      = "pre-alpha"

__logger = ecaaf_logger.get_logger('ecaaf_app_exec')

__c=None
def config_consumer(groupid, clientid):
    try:
        settings=ecaaf_config.get_kafka_consumer_config(groupid,clientid)
        c = Consumer(settings)
        c.subscribe([clientid])
    except:
        __logger.error("Could not subscribe consumer",exc_info=True)
    return c

def start_platform_consumer():
    try:
        while True:
            #TODO:change the number of poll records
            msg = __c.poll(0.1)
            if msg is None:
                continue
            elif not msg.error():
                __logger.info(msg.value())
                payload = json.loads(msg.value())
                tag=ecaaf_utils.exec_app(payload)
                __logger.info("Image with tag %s created"%tag)
#                payload["itag"]=tag
#                ecaaf_db.kvdb_set(payload["ename"], payload)
            elif msg.error().code() == KafkaError._PARTITION_EOF:
                __logger.warn('End of partition reached {0}/{1}'\
                .format(msg.topic(), msg.partition()))
            else:
                __logger.error('Error occured: {0}'.format(msg.error().str()), exc_info=True)

    except:
        __logger.error('Error occured...', exc_info=True)

    finally:
        __c.close()

if __name__ == '__main__':
    __c=config_consumer('core','analyzer')
    if not __c:
        __logger.error("Could not start core event binder")
    else:
        start_platform_consumer()
