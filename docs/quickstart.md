## Prerequisites:

Server
  1. Docker - [get it](https://docs.docker.com/install/)
  2. Kafka - [get it](https://kafka.apache.org/quickstart)
  3. Redshift - [get it](https://redis.io/topics/quickstart)
  4. [Python dependencies](/install/server/requirements.txt)

Cli
  1. [Python dependencies](/install/cli/requirements.txt)

## Initial setup:

## Configurations:

Configuration settings are defined in the [ecaaf_config.py](/src/core/dmisc/ecaaf_config.py), the following are the tunables that can be changed:

# Path configurations:
```
  __paths={
    'install_dir':'/home/user',
    'event_upload_folder':'/tmp/trials/bindings/uploads',
    'host_vol_dir':'/tmp/trials',
    'ecaaf_logging':'/tmp/trials/logs',
    
     # DONOT change the configs below
     
    'action_config':'action.ecaaf',
    'boilerplate_path':'/ecaaf/src/boilerplate',
    'domain_folder':'/ecaaf/.catalog',
    'image_config_file':'config',
    'app_folder':'/ecaaf/.catalog/apps'
}

# Kafka configurations:

__kafa_consumer = {
    'bootstrap.servers': 'localhost:9092',
    'group.id':'DUMMY',
    'client.id':'DUMMY',
    'enable.auto.commit': True,
    'session.timeout.ms': 6000,
    'default.topic.config': {'auto.offset.reset': 'smallest'}
}

# Redis configurations:

__redis={
    'host':'localhost',
    'port':6379
}

# API gateway configurations:

__apigateway={
    'host':'0.0.0.0',
    'port':5000,
    'secret':'skunksworks'
}
```
## Sanity test:

## CLI setup:

## Deploying a funclet:

## Create an event-funclet binding:

## Testing the event-funclet:

For further reading refer to the [user manual](/docs/manual/USERGUIDE.md).
