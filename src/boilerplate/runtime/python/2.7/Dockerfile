FROM python:2.7
MAINTAINER Swanand Rao <swanand.rao@gmail.com>

#When using proxies uncomment the lines below.
#ENV http_proxy=www-proxy:80
#ENV https_proxy=www-proxy:80

RUN mkdir /ecaaf && mkdir /host && pip install requests ast redis

ADD * /ecaaf/

WORKDIR /ecaaf

ENTRYPOINT python master.py

CMD ["{'event_name':'DUMMY'}"]
