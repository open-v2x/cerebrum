FROM docker.io/openv2x/cerebrum-base:latest

LABEL purpose="cerebrum"

WORKDIR /home/www/cerebrum
COPY . /home/www/cerebrum

RUN cp /home/www/cerebrum/start.sh /usr/local/bin/start.sh \
    && pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r /home/www/cerebrum/requirements.txt \
    && pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r /home/www/cerebrum/requirements/algo.txt \
    && pip install /home/www/cerebrum

CMD ["sh", "/usr/local/bin/start.sh"]
