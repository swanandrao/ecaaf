About:
------
eventgen is a generic JSON based event generation tool. It facilitates the
configuration and triggering of user defined events.

Prerequisites:
--------------
eventgen uses python requests module to invoke  ReST calls. Please install this
package by:

pip install -i requirements.txt

Event definition:
-----------------
eventgen tool uses event.json file to construct an event. The JSON definition of
event is as follows:
```json
{
    "request_type": "the request type(POST,GET,PUT)",                   
    "service_url": "url of the ecaaf api service(default: http://localhost:5000)",   
    "event": {                                
        "event_name": "event name : <event_name>.<source_id>",         
        "params": {  
            "user_param":"value",
            "cust_name": "test_101"           
            }
    }
}
```
Usage:
------
1. Update the event structure in event.json as per the requirement.
2. Save the event.json file
3. Execute: python eventgen
