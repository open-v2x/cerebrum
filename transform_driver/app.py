#   Copyright 99Cloud, Inc. All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

"""Listen for messages and process data."""

import aioredis as redis
import asyncio
import paho.mqtt.client as mqtt  # type: ignore
from post_process_algo import post_process
from pre_process_ai_algo.pre_process import Cfg
from pre_process_ai_algo.pre_process import DataProcessing
import re
from scenario_algo.scenario_service import Service
import signal
from transform_driver import consts
from transform_driver import db
from transform_driver.driver_lib import drivers
from transform_driver.log import Loggings
from transform_driver.rsi_service import RSI
import uuid

logger = Loggings()


class App:
    """Listen for messages and process data."""

    def __init__(self, config) -> None:
        """Class initialization."""
        self.config = config
        self.msg_dispatch = {
            consts.topic_replace(
                "V2X/RSU/+/RSM/UP", self.config.DELIMITER
            ): self._mqtt_on_rsm_msg,
            consts.topic_replace(
                "V2X/RSU/+/RSM/UP/+", self.config.DELIMITER
            ): self._mqtt_on_rsm_msg,
            consts.topic_replace(
                "V2X/RSU/+/RSI/UP/+", self.config.DELIMITER
            ): self._mqtt_on_rsi,
            consts.topic_replace(
                "V2X/DEVICE/+/RSI/UP", self.config.DELIMITER
            ): self._mqtt_on_rsi,
            consts.topic_replace(
                "V2X/RSU/+/VIR/UP", self.config.DELIMITER
            ): self._mqtt_on_vir,
            consts.topic_replace(
                "V2X/RSU/+/PIP/CFG", self.config.DELIMITER
            ): self._mqtt_on_cfg,
            consts.topic_replace(
                "V2X/RSU/REG/TICE", self.config.DELIMITER
            ): self._mqtt_on_db,
        }
        self.rsm_topic_driver_re = re.compile(
            consts.topic_replace(
                r"V2X/RSU/(?P<rsuid>[^/]+)/RSM/UP/(?P<driver>[^/]+)",
                self.config.DELIMITER,
            )
        )
        self.rsm_topic_std_re = re.compile(
            consts.topic_replace(
                r"V2X/RSU/(?P<rsuid>[^/]+)/RSM/UP", self.config.DELIMITER
            )
        )
        self.rsi_topic_driver_re = re.compile(
            consts.topic_replace(
                r"V2X/RSU/(?P<rsuid>[^/]+)/RSI/UP/(?P<driver>[^/]+)",
                self.config.DELIMITER,
            )
        )
        self.rsi_topic_std_re = re.compile(
            consts.topic_replace(
                r"V2X/DEVICE/(?P<rsuid>[^/]+)/RSI/UP", self.config.DELIMITER
            )
        )
        self.vir_topic_re = re.compile(
            consts.topic_replace(
                r"V2X/RSU/(?P<rsuid>[^/]+)/VIR/UP", self.config.DELIMITER
            )
        )
        self.rsi_topic_re = re.compile(
            consts.topic_replace(
                r"V2X/RSU/(?P<rsuid>[^/]+)/RSI/UP", self.config.DELIMITER
            )
        )
        self.cfg_topic_re = re.compile(
            consts.topic_replace(
                r"V2X/RSU/(?P<rsuid>[^/]+)/PIP/CFG", self.config.DELIMITER
            )
        )
        self.stop = False

    def run(self):
        """External call function."""
        asyncio.run(self._run())

    async def _run(self):
        self.loop = asyncio.get_running_loop()
        await self._setup()
        while not self.stop:
            await asyncio.sleep(1)
        await self._stop()

    def _handle_sigstop(self):
        self.stop = True

    async def _setup(self) -> bool:
        self.kv = db.KVStore(await redis.Redis(**self.config.redis))
        mcfg = self.config.mqtt
        self.mqtt = mqtt.Client(mcfg["client_id"])
        self.mqtt.on_connect = self._mqtt_on_connect
        self.mqtt.on_socket_open = self._mqtt_on_socket_open
        self.mqtt.on_socket_close = self._mqtt_on_socket_close
        self.mqtt.on_socket_register_write = (
            self._mqtt_on_socket_register_write
        )
        self.mqtt.on_socket_unregister_write = (
            self._mqtt_on_socket_unregister_write
        )

        self.mqtt.username_pw_set(mcfg["username"], mcfg["password"])
        self.mqtt.connect(mcfg["host"], mcfg["port"])
        try:
            mcfg_conn = db.get_mqtt_config()
            self.mqtt_conn = mqtt.Client(client_id=uuid.uuid4().hex)
            self.mqtt_conn.username_pw_set(
                mcfg_conn["username"], mcfg_conn["password"]
            )
            self.mqtt_conn.connect(mcfg_conn["host"], mcfg_conn["port"])
            self.process = DataProcessing(self.mqtt, self.kv, self.mqtt_conn)
            self.svc = Service(self.mqtt, self.kv, self.mqtt_conn)
        except Exception:
            self.process = DataProcessing(self.mqtt, self.kv)
            self.svc = Service(self.mqtt, self.kv)
        self.rsi = RSI(self.mqtt, self.kv)
        self.cfg = Cfg(self.kv)

        for sig in ("SIGINT", "SIGTERM", "SIGUSR2"):
            self.loop.add_signal_handler(
                getattr(signal, sig), self._handle_sigstop
            )
        return True

    async def _stop(self):
        await self.kv.redis.close()
        self.mqtt.disconnect()

    def _mqtt_on_socket_open(self, client, userdata, sock):
        logger.trace("Socket opened")

        def cb():
            logger.trace("Socket is readable, calling loop_read")
            client.loop_read()

        self.loop.add_reader(sock, cb)
        self.misc = self.loop.create_task(self._misc_loop())

    def _mqtt_on_socket_close(self, client, userdata, sock):
        logger.trace("Socket closed")
        self.loop.remove_reader(sock)
        self.misc.cancel()

    def _mqtt_on_socket_register_write(self, client, userdata, sock):
        logger.trace("Watching socket for writability.")

        def cb():
            logger.trace("Socket is writable, calling loop_write")
            client.loop_write()

        self.loop.add_writer(sock, cb)

    def _mqtt_on_socket_unregister_write(self, client, userdata, sock):
        logger.trace("Stop watching socket for writability.")
        self.loop.remove_writer(sock)

    async def _misc_loop(self):
        logger.trace("misc_loop started")
        while self.mqtt.loop_misc() == mqtt.MQTT_ERR_SUCCESS:
            try:
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                break
        logger.trace("misc_loop finished")

    def _mqtt_on_connect(self, client, userdata, flags, rc):
        for topic, cb in self.msg_dispatch.items():
            client.subscribe(topic)
            client.message_callback_add(topic, cb)

    def _mqtt_on_rsm_msg(self, client, userdata, msg):
        driver_name, rsu_id = self._driver_name(msg.topic, "rsm")
        driver = getattr(drivers, driver_name)
        miss_flag, rsm, miss_info = driver(msg.payload)
        if self._is_valid_rsu_id(rsu_id):
            self.loop.create_task(
                self.process.run(rsu_id, rsm, miss_flag, miss_info)
            )
        else:
            logger.error("RSU is not registered")

    def _mqtt_on_vir(self, client, userdata, msg):
        m = self.vir_topic_re.search(msg.topic)
        rsu_id = m.groupdict()["rsuid"]
        if self._is_valid_rsu_id(rsu_id):
            self.loop.create_task(self.svc.run(rsu_id, msg.payload))
        else:
            logger.error("Target RSU is not registered")

    def _mqtt_on_rsi(self, client, userdata, msg):
        driver_name, rsu_id = self._driver_name(msg.topic, "rsi")
        driver = getattr(drivers, driver_name)
        rsi, congestion_info = driver(msg.payload)
        if self._is_valid_rsu_id(rsu_id):
            self.loop.create_task(self.rsi.run(rsu_id, rsi, congestion_info))
        else:
            logger.error("RSU is not registered")

    def _mqtt_on_cfg(self, client, userdata, msg):
        m = self.cfg_topic_re.search(msg.topic)
        rsu_id = m.groupdict()["rsuid"]
        if self._is_valid_rsu_id(rsu_id):
            self.loop.create_task(self.cfg.run(rsu_id, msg.payload))
        else:
            logger.error("RSU is not registered")

    def _mqtt_on_db(self, client, userdata, msg):
        db.get_rsu_info(msg.payload)

    def _driver_name(self, topic, msg_type):
        if topic[-2:] == "UP":
            m = getattr(self, "{}_topic_std_re".format(msg_type)).search(topic)
            rsu_id = m.groupdict()["rsuid"]
            driver_name = msg_type + "_std"
        else:
            m = getattr(self, "{}_topic_driver_re".format(msg_type)).search(
                topic
            )
            rsu_id = m.groupdict()["rsuid"]
            driver_name = msg_type + "_" + m.groupdict()["driver"].lower()
        return driver_name, rsu_id

    def _is_valid_rsu_id(self, rsu_id):
        if rsu_id in post_process.rsu_info:
            return True
        return False
