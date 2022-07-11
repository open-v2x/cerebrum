# FROM docker.io/library/python:3.9.12-slim-buster
FROM docker.io/openv2x/v2x-algo-base:latest

LABEL purpose="cerebrum"

WORKDIR /home/www/cerebrum
COPY . /home/www/cerebrum

RUN cp /home/www/cerebrum/start.sh /usr/local/bin/start.sh \
    && mv /etc/apt/sources.list /etc/apt/sources.list.bak \
    && cp /home/www/cerebrum/sources.list /etc/apt/ \
    && apt-get update \
    && apt-get install -y wget libgl1-mesa-glx libglib2.0-dev libgeos-dev curl build-essential

RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r /home/www/cerebrum/requirements.txt \
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r /home/www/cerebrum/requirements/algo.txt \
    && pip install /home/www/cerebrum

CMD ["sh", "/usr/local/bin/start.sh"]
