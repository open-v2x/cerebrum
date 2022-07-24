# V2X-Data-Processing

## 1. 本地调试

```bash
# 创建 python 虚拟环境
python3 -m virtualenv .venv
# 进入 python 虚拟环境
. .venv/bin/activate

# 安装依赖
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements/algo.txt
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

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

CONTAINER_NAME=v2x-data-processing
DOCKER_IMAGE=openv2x/${CONTAINER_NAME}

docker build -t ${DOCKER_IMAGE} .
docker stop ${CONTAINER_NAME}; docker rm ${CONTAINER_NAME}
docker run -d --name ${CONTAINER_NAME} ${DOCKER_IMAGE}
```

## 4. 手动更新

### 4.1 手动制作和上传容器镜像

如果容器镜像已存在，可以跳过此步骤

```bash
docker build -t cereburm .
docker tag cereburm openv2x/cereburm:latest
docker push openv2x/cereburm:latest
```

### 4.2 手动将容器镜像部署到测试环境

```bash
DEPLOY_HOST=v2x-server
# DEPLOY_HOST=v2x-test

cat .drone.yml | grep v2x-server | grep -v -E "^\s*#" | grep -E '^\s*-' | sed "s/v2x-server/${DEPLOY_HOST}/g"| sed 's/-//' > /tmp/deploy-cereburm.sh

# 然后检查一下 /tmp/deploy-cereburm.sh 是否有需要修改的地方
cat /tmp/deploy-cereburm.sh
bash /tmp/deploy-cereburm.sh
```

## Notice

1. Please run "[`dprint fmt`](https://dprint.dev/)" to format markdown files before creating PR.
