"""Execution engine to process events for the storage domain"""

from confluent_kafka import Consumer, KafkaError
import json

from dmisc import ecaaf_config, ecaaf_logger, ecaaf_utils

__author__      = "Swanand Rao"
__copyright__   = ""
__credits__     = ["Swanand Rao"]
__license__     = ""
__version__     = "0.1"
__maintainer__  = "Swanand Rao"
__email__       = "swanand.rao@gmail.com"
__status__      = "pre-alpha"

logger = ecaaf_logger.get_logger('ecaaf_event_exec')

__c=None
def config_consumer(groupid, clientid):
    try:
        settings=ecaaf_config.get_kafka_consumer_config(groupid,clientid)
        c = Consumer(settings)
        c.subscribe([clientid])
    except:
        logger.error("Could not subscribe consumer",exc_info=True)
    return c

def start_platform_consumer():
    try:
        while True:
            #TODO:change the poll records
            msg = __c.poll(0.1)
            if msg is None:
                continue
            elif not msg.error():
                payload = str(msg.value())
                ecaaf_utils.run_image(payload)
                #elastic event - in execution
            elif msg.error().code() == KafkaError._PARTITION_EOF:
                logger.warn('End of partition reached {0}/{1}'\
                .format(msg.topic(), msg.partition()))
            else:
                logger.error('Error occured: {0}'.format(msg.error().str()))

    except:
        logger.error('Error occured..', exc_info=True)

    finally:
        __c.close()

if __name__ == '__main__':
    __c=config_consumer('event-executor','event-exec-1')
    if not __c:
        logger.error("Could not start storage executor")
    else:
        start_platform_consumer()
