**About:
**------**
eventgen is a generic JSON based event generation tool. It facilitates the
configuration and triggering of user defined events.

**Prerequisites:
--------------**
eventgen uses python requests module to invoke  ReST calls. Please install this
package by:

pip install -i requirements.txt

**Event definition:
-----------------**
eventgen tool uses event.json file to construct an event. The JSON definition of
event is as follows:
```json
{
    "request_type": "post",                   -->the request type(POST,GET,PUT)
    "service_url": "http://localhost:5000",   -->url of the ecaaf api service
    "event": {                                -->event dictionary
        "event_name": "test_event.1",         -->event name <event_name>.<source_id>
        "params": {                           -->payload dict, any user defined
            "cust_name": "test_101"              go here.
            }
    }
}
```
**Usage:
------**
1. Update the event structure in event.json as per the requirement.
2. Save the event.json file
3. Execute: python eventgen
