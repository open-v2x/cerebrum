import os
import uuid

DEFAULT_HOST_MQTT = "139.196.13.9"
DEFAULT_PASSOWRD_MQTT = "v2x2022" # user define
DEFAULT_HOST_REDIS = "139.196.13.9"
DEFAULT_PASSWORD_REDIS = "v2x2022" # user define
DEFAULT_HOST_MYSQL = "139.196.13.9"
DEFAULT_PASSOWRD_MYSQL = "v2x2022" # user define
DEFAULT_CLOUD_URL = "http://139.196.13.9:28300/api/v1"
DELIMITER = "/"

redis = {
    "host": os.getenv("redis_host") or DEFAULT_HOST_REDIS,
    "port": 6379,
    "password": os.getenv("redis_password") or DEFAULT_PASSWORD_REDIS,
    "db": 1,
}

mqtt = {
    "host": os.getenv("mqtt_host") or DEFAULT_HOST_MQTT,
    "port": 1883,
    "client_id": uuid.uuid4().hex,
    "username": "root",
    "password": os.getenv("emqx_password") or DEFAULT_PASSOWRD_MQTT,
}

mysql = {
    "host": os.getenv("mysql_host") or DEFAULT_HOST_MYSQL,
    "port": 3306,
    "user": "root",
    "password": os.getenv("mysql_root_password") or DEFAULT_PASSOWRD_MYSQL,
    "charset": "utf8",
    "db": "dandelion",
}
cloud_server = os.getenv("cloud_url") or DEFAULT_CLOUD_URL
