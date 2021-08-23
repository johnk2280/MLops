FROM ubuntu:focal

RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.8 python3.8-dev python3-pip \

WORKDIR /app
COPY requirements.txt .
RUN rm -f /user/bin/python && ln -s /usr/bin/python3.8 /usr/bin/python
RUN rm -f /user/bin/python3 && ln -s /usr/bin/python3.8 /usr/bin/python3

RUN pip3 install -r requirements.txt
RUN pip3 install gunicorn==20.1.0

ADD ./backend /app/backend
ADD ./docker /app/backend/docker
ADD ./research /app/backend/research

RUN mkdir -p /app/backend/server/static