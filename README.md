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

> 注意：[如果是 Ubuntu 环境，需要先安装 libgl 头文件支持](https://github.com/open-v2x/cerebrum/issues/61)

> `apt-get install libgl1-mesa-glx`

简单执行 tox 就行：

```bash
tox
```

## 3. 替换算法

默认的内置算法列表参考：[algorithm.yaml.example](/etc/algorithm.yaml.example)

### 3.1 替换算法模块

您可以替换某一个算法模块，比如：

1. `pip install` 一个新的 fusion 算法模块 'new_fusion'
2. 复制 `algorithm.yaml.example` 到 `/etc/cerebrum/algorithm.yaml`
3. 将 yaml 文件中的 `pre_process_ai_algo.algo_lib.fusion` 改成 `new_fusion`
4. 重启 cerebrum 服务，cerebrum 服务在启动时会尝试访问 `/etc/cerebrum/algorithm.yaml` 配置文件，动态加载对应的算法模块

这样就可以可使用 `new_fusion` 算法模块代替内置的 `pre_process_ai_algo.algo_lib.fusion` 算法模块。

### 3.2 替换使用模块中的某个具体算法

您也可以替换某一算法模块中的不同算法，比如：

1. 将 yaml 文件中的 `pre_process_ai_algo.algo_lib.complement.enable` 改成 false，这样该模块会禁用
2. 将 yaml 文件中的 `pre_process_ai_algo.algo_lib.complement.algo` 改成 `lstm_predict`，这样该算法会代替原来的
   `interpolation`

您也可以发配置消息，动态替换模块中的具体算法（发送 `V2X/RSU/(?P<rsuid>[^/]+)/PIP/CFG` 消息，里面带 cfg 字段）：

```json
"cfg": {
    "fusion": "disable",
    "complement": "interpolation",
    "smooth": "exponential",
    "collision": "collision_warning",
    "visual": "visual"
}
```

## 4. 容器镜像制作和部署

```bash
# pytorch 基础镜像镜
# docker build -t 99cloud/v2x-algo-base -f Dockerfile-algo-base .

CONTAINER_NAME=cerebrum
DOCKER_IMAGE=openv2x/${CONTAINER_NAME}

docker build -t ${DOCKER_IMAGE} .
docker stop ${CONTAINER_NAME}; docker rm ${CONTAINER_NAME}

docker run -d --net=host --name ${CONTAINER_NAME} -e redis_host=127.0.0.1 -e mqtt_host=127.0.0.1 -e mysql_host=127.0.0.1 -e cloud_url=http://127.0.0.1:28300/api/v1 -e mysql_user=root -e mysql_password=password -e emqx_password=password -e redis_password=password ${DOCKER_IMAGE}
# docker run -d --name ${CONTAINER_NAME} -e redis_host=172.17.0.1 -e mqtt_host=172.17.0.1 -e mysql_host=172.17.0.1 -e cloud_url=http://172.17.0.1:28300/api/v1 -e mysql_user=root -e mysql_password=password -e emqx_password=password -e redis_password=password ${DOCKER_IMAGE}
```

## 5. 算法功能自动化测试

```bash
# 安装依赖
pip3 install -r test-function-requirements.txt

# 执行
export ip='127.0.0.1'
export emqx_root=password
sh ./function_test/function_test.sh
```

## Notice

1. Please run "[`dprint fmt`](https://dprint.dev/)" to format markdown files before creating PR.
