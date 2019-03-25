FROM python:3.5.5
MAINTAINER Swanand Rao <swanand.rao@gmail.com>

RUN mkdir /ecaaf && mkdir /host && pip install requests ast

ADD * /ecaaf/
WORKDIR /ecaaf
ENTRYPOINT python master.py

CMD ["{'event_name':'DUMMY'}"]
