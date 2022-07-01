# FROM docker.io/library/python:3.9.12-slim-buster
FROM docker.io/openv2x/v2x-algo-base:latest

LABEL purpose="V2X AI Algorithm Service"

WORKDIR /home/www/v2x_ai_algorithm
COPY . /home/www/v2x_ai_algorithm

RUN cp /home/www/v2x_ai_algorithm/start.sh /usr/local/bin/start.sh \
    && mv /etc/apt/sources.list /etc/apt/sources.list.bak \
    && cp /home/www/v2x_ai_algorithm/sources.list /etc/apt/ \
    && apt-get update \
    && apt-get install -y wget libgl1-mesa-glx libglib2.0-dev libgeos-dev curl build-essential

RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r /home/www/v2x_ai_algorithm/requirements.txt \
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r /home/www/v2x_ai_algorithm/requirements/algo.txt \
    && pip install /home/www/v2x_ai_algorithm

CMD ["sh", "/usr/local/bin/start.sh"]
