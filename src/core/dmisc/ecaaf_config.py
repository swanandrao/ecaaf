"""
Configuration file. It holds the base configuration for installation of the
ecaaf service. Make changes to this file after installation and before using the
service.
"""
__author__      = "Swanand Rao"
__copyright__   = ""
__credits__     = ["Swanand Rao"]
__license__     = ""
__version__     = "0.1"
__maintainer__  = "Swanand Rao"
__email__       = "swanand.rao@gmail.com"
__status__      = "pre-alpha"
__paths={
    'install_dir':'/home/user',
    'event_upload_folder':'/tmp/trials/bindings/uploads',
    'host_vol_dir':'/tmp/trials',
    'ecaaf_logging':'/tmp/trials/logs',
    'action_config':'action.ecaaf',
    'boilerplate_path':'/ecaaf/src/boilerplate',
    'domain_folder':'/ecaaf/.catalog',
    'image_config_file':'config',
    'app_folder':'/ecaaf/.catalog/apps'
}
__kafa_consumer = {
    'bootstrap.servers': 'localhost:9092',
    'group.id':'DUMMY',
    'client.id':'DUMMY',
    'enable.auto.commit': True,
    'session.timeout.ms': 6000,
    'default.topic.config': {'auto.offset.reset': 'smallest'}
}
__redis={
    'host':'localhost',
    'port':6379
}
__apigateway={
    'host':'0.0.0.0',
    'port':5000,
    'secret':'skunksworks'
}
__uploadextensions = ['zip','yml']

def get_log_path():
    return __paths['ecaaf_logging']

def get_path_config(name):
    return __paths[name]

def get_app_path():
    return __paths['app_folder']

def get_upload_extensions():
    return __uploadextensions

def get_redis_conf():
    return __redis

def get_kafka_consumer_config(groupid, clientid):
    __kafa_consumer['group.id']=groupid
    __kafa_consumer['client.id']=clientid
    return __kafa_consumer

def get_api_gateway_config():
    return (__apigateway['host'],__apigateway['port'],__apigateway['secret'])
