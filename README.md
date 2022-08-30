# Cerebrum：OpenV2X Data Processing

## 1. 本地调试

```bash
# 创建 python 虚拟环境
python3 -m virtualenv .venv
# 进入 python 虚拟环境
. .venv/bin/activate

# 安装依赖
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements/algo.txt
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 安装测试相关依赖
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple -r test-requirements.txt
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements/bandit.txt
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements/docstyle.txt
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements/pep8.txt
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements/typecheck.txt

# 配置环境变量
export redis_host='127.0.0.1'
export mqtt_host='127.0.0.1'
export mysql_host='127.0.0.1'
export cloud_url='http://127.0.0.1:28300/api/v1'
export mysql_user='root'
export mysql_password=password
export emqx_password=password
export redis_password=password

# 启动数据处理服务
python main.py
```

## 2. 单元测试和代码格式检查

```bash
tox
```

## 3. 容器镜像制作和部署

```bash
# pytorch 基础镜像镜
# docker build -t 99cloud/v2x-algo-base -f Dockerfile-algo-base .

CONTAINER_NAME=cerebrum
DOCKER_IMAGE=openv2x/${CONTAINER_NAME}

docker build -t ${DOCKER_IMAGE} .
docker stop ${CONTAINER_NAME}; docker rm ${CONTAINER_NAME}

docker run -d --net=host --name ${CONTAINER_NAME} -e redis_host=127.0.0.1 -e mqtt_host=127.0.0.1 -e mysql_host=127.0.0.1 -e cloud_url=http://127.0.0.1:28300/api/v1 -e mysql_user=root -e mysql_password=password -e emqx_password=password -e redis_password=password ${DOCKER_IMAGE}
```

## Notice

1. Please run "[`dprint fmt`](https://dprint.dev/)" to format markdown files before creating PR.
