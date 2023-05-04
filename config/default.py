import os
from pathlib import Path
from urllib.parse import quote_plus
import uuid

DEFAULT_MQTT_HOST = "172.17.0.1"
DEFAULT_MQTT_PASSWORD = "v2x2022"  # user define
DEFAULT_REDIS_HOST = "172.17.0.1"
DEFAULT_REDIS_PASSWORD = "v2x2022"  # user define
DEFAULT_MYSQL_HOST = "172.17.0.1"
DEFAULT_MYSQL_USER = "dandelion"
DEFAULT_MYSQL_PASSWORD = "v2x2022"  # user define
DEFAULT_CLOUD_URL = "http://172.17.0.1:28300/api/v1"
DEFAULT_ALGORITHM_YAML_PATH = "/etc/cerebrum/algorithm.yaml"
DEFAULT_ALGORITHM_YAML = """
rsi_formatter:
  algos:
    rsi_formatter:
      enable: true
      module: "transform_driver.rsi_service"
      algo: "rsi"
      version:
      - rsi
pre_process_ai_algo:
  algos:
    complement:
      enable: true
      module: "pre_process_ai_algo.algo_lib.complement"
      algo: "interpolation"
      version:
      - interpolation
      - lstm_predict
    fusion:
      enable: false
      module: "pre_process_ai_algo.algo_lib.fusion"
      algo: "fusion"
      version:
      - fusion
    smooth:
      enable: true
      module: "pre_process_ai_algo.algo_lib.smooth"
      algo: "exponential"
      version:
      - exponential
      - polynomial
    visual:
      enable: true
      module: "pre_process_ai_algo.pipelines.visualization"
      algo: "visual"
      version:
      - visual
scenario_algo:
  algos:
    collision_warning:
      enable: true
      module: "scenario_algo.algo_lib.collision_warning"
      algo: "collision_warning"
      version:
      - collision_warning
    cooperative_lane_change:
      enable: true
      module: "scenario_algo.algo_lib.cooperative_lane_change"
      algo: "cooperative_lane_change"
      version:
      - cooperative_lane_change
    do_not_pass_warning:
      enable: true
      module: "scenario_algo.algo_lib.do_not_pass_warning"
      algo: "do_not_pass_warning"
      version:
      - do_not_pass_warning
    sensor_data_sharing:
      enable: true
      module: "scenario_algo.algo_lib.sensor_data_sharing"
      algo: "sensor_data_sharing"
      version:
      - sensor_data_sharing
    reverse_driving_warning:
      enable: true
      module: "scenario_algo.algo_lib.reverse_driving_warning"
      algo: "reverse_driving_warning"
      version:
      - reverse_driving_warning
    congestion_warning:
      enable: true
      module: "scenario_algo.algo_lib.congestion_warning"
      algo: "congestion_warning"
      version:
      - congestion_warning
    overspeed_warning:
      enable: true
      module: "scenario_algo.algo_lib.overspeed_warning"
      algo: "overspeed_warning"
      version:
      - overspeed_warning
    slowspeed_warning:
      enable: true
      module: "scenario_algo.algo_lib.slowspeed_warning"
      algo: "slowspeed_warning"
      version:
      - slowspeed_warning
post_process_algo:
  algos:
    post_process:
      enable: true
      module: "post_process_algo.post_process"
      algo: "post_process"
      version:
      - post_process
"""
DELIMITER = "/"

db_server = os.getenv("db_server") or "mariadb"

sqlalchemy_w = {
    "url": "sqlite:///:memory:",
    "echo": True,
    "pool_recycle": 3600,
    "encoding": "utf-8",
}

if db_server == "mariadb":
    DB_HOST = os.getenv("mysql_host") or DEFAULT_MYSQL_HOST
    DB_PORT = 3306
    DB_USERNAME = os.getenv("mysql_user") or DEFAULT_MYSQL_USER
    DB_PASSWORD = os.getenv("mysql_password") or DEFAULT_MYSQL_PASSWORD
    sqlalchemy_w = {
        "url": f"mariadb+pymysql://{DB_USERNAME}:{quote_plus(DB_PASSWORD)}"
        f"@{DB_HOST}:{DB_PORT}/dandelion?charset=utf8",
        "echo": True,
    }

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

dandelion = {
    "endpoint": os.getenv("DANDELION_ENDPOINT", "http://127.0.0.1:28300/"),
    "edge_id_url": os.getenv("SYSTEM_CONFIG_URL", "api/v1/system_configs/1"),
    "login_url": os.getenv("LOGIN_URL", "api/v1/login"),
    "username": os.getenv("USERNAME", "admin"),
    "password": os.getenv("PASSWORD", "dandelion"),
    "rsu_get_url": os.getenv("RSU_GET_URL", "api/v1/rsus?pageSize=-1"),
    "get_algo_all_url": os.getenv("ALGO_GET_URL", "api/v1/algos?pageSize=-1"),
}

cloud_server = os.getenv("cloud_url") or DEFAULT_CLOUD_URL
algorithm_yaml = os.getenv("algorithm_yaml") or DEFAULT_ALGORITHM_YAML_PATH


if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent.parent
    example = os.path.join(BASE_DIR, "etc", "algorithm.yaml.example")
    with open(example, "w") as f:
        f.write(DEFAULT_ALGORITHM_YAML.strip() + "\n")
