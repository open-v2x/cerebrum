import os
import uuid


DEFAULT_MQTT_HOST = "139.196.13.9"
DEFAULT_MQTT_PASSWORD = "v2x2022"  # user define
DEFAULT_REDIS_HOST = "139.196.13.9"
DEFAULT_REDIS_PASSWORD = "v2x2022"  # user define
DEFAULT_MYSQL_HOST = "139.196.13.9"
DEFAULT_MYSQL_USER = "dandelion"
DEFAULT_MYSQL_PASSWORD = "v2x2022"  # user define
DEFAULT_CLOUD_URL = "http://139.196.13.9:28300/api/v1"
DELIMITER = "/"

redis = {
    "host": os.getenv("redis_host") or DEFAULT_REDIS_HOST,
    "port": 6379,
    "password": os.getenv("redis_password") or DEFAULT_REDIS_PASSWORD,
    "db": 1,
}

mqtt = {
    "host": os.getenv("mqtt_host") or DEFAULT_MQTT_HOST,
    "port": 1883,
    "client_id": uuid.uuid4().hex,
    "username": "root",
    "password": os.getenv("emqx_password") or DEFAULT_MQTT_PASSWORD,
}

mysql = {
    "host": os.getenv("mysql_host") or DEFAULT_MYSQL_HOST,
    "port": 3306,
    "user": os.getenv("mysql_user") or DEFAULT_MYSQL_USER,
    "password": os.getenv("mysql_password") or DEFAULT_MYSQL_PASSWORD,
    "charset": "utf8",
    "db": "dandelion",
}
cloud_server = os.getenv("cloud_url") or DEFAULT_CLOUD_URL
