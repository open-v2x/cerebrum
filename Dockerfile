FROM docker.io/openv2x/cerebrum-base:latest

ARG GIT_BRANCH
ARG GIT_COMMIT
ARG RELEASE_VERSION
ARG REPO_URL

LABEL cerebrum.build_branch=${GIT_BRANCH} \
      cerebrum.build_commit=${GIT_COMMIT} \
      cerebrum.release_version=${RELEASE_VERSION} \
      cerebrum.repo_url=${REPO_URL}

WORKDIR /home/www/cerebrum
COPY . /home/www/cerebrum

RUN cp /home/www/cerebrum/start.sh /usr/local/bin/start.sh \
    && pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r /home/www/cerebrum/requirements.txt \
    && pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r /home/www/cerebrum/requirements/algo.txt \
    && pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r /home/www/cerebrum/overspeed_warning_service/requirements.txt \
    && pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r /home/www/cerebrum/reverse_driving_service/requirements.txt \
    && pip install /home/www/cerebrum

CMD ["sh", "/usr/local/bin/start.sh"]