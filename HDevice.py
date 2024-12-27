#!/bin/python3
import inspect
import json
import socket
import threading
import random
from datetime import datetime

import paho.mqtt.client as mqtt
from paho.mqtt import client as mqtt_client
import time

import HStategrid
import HHhdlist
import HSyslog


def hhd_init(host="127.0.0.1", port=1883):
    try:
        client = HMqttClient(host, port)
        client.connect()
        do_mqtt_net_period()
        do_platform_device_data()
        if HHhdlist.device_mqtt_status:
            # net_status = {
            #     "net_type": HHhdlist.net_type.no_net.value,
            #     "net_sig_val": 0,
            #     "net_id": HHhdlist.net_id.unknow.value
            # }
            # HHhdlist.platform_device_data.put([HHhdlist.topic_hqc_sys_network_state, net_status])
            get_param = {
                "param_list": [104, 110, 111, 113, 114, 115, 117, 121, 122],
                "device_type": HHhdlist.device_param_type.chargeSys.value,
                "device_num": 0
            }
            HHhdlist.platform_device_data.put([HHhdlist.topic_hqc_main_event_notify_read_param, get_param])
            time.sleep(5)
            get_param = {
                "param_list": [169, 172, 209, 215, 216, 226, 222, 223, 224, 225],
                "device_type": HHhdlist.device_param_type.gun.value,
            }
            HHhdlist.platform_device_data.put([HHhdlist.topic_hqc_main_event_notify_read_param, get_param])
            get_param = {
                "device_type": [HHhdlist.device_ctrl_type.DTU.value, HHhdlist.device_ctrl_type.TIU.value]
            }
            HHhdlist.platform_device_data.put([HHhdlist.topic_hqc_sys_upgrade_notify_version, get_param])
            time.sleep(3)
            HHhdlist.gun_num = HStategrid.get_DeviceInfo("00110")
            for i in range(HHhdlist.gun_num):
                instance = HStategrid.Gun_info(i)
                HStategrid.Gun_list.append(instance)
            HHhdlist.Device_ready = True
    except Exception as e:
        HSyslog.log_error(f"hhd_init error. {e}")


'''################################################### 数据接收发送队列初始化 ####################################################'''


class HMqttClient:
    def __init__(self, broker_address, broker_port, keepalive=60, client_id="Device_MQTT"):
        self.broker_address = broker_address
        self.broker_port = broker_port
        self.keepalive = keepalive
        self.client_id = client_id
        self.client = mqtt.Client(client_id=self.client_id)
        self.send_thread = None

    def connect(self, isReady=False):
        """连接到MQTT服务器"""
        try:
            try:
                # 设置回调函数
                self.client.on_connect = self._on_connect
                self.client.on_disconnect = self._on_disconnect
                self.client.on_message = self._on_message

                self.client.connect(self.broker_address, self.broker_port, self.keepalive)
                self.subscribe()
                self.client.loop_start()  # 启动网络循环以处理连接
                isReady = True
                HSyslog.log_info(f"Connected to Device MQTT broker at {self.broker_address}:{self.broker_port}")
            except Exception as e:
                HSyslog.log_error(f"Failed to Device Connect to broker: {e}")

            if isReady:
                self.start_send_thread()
        except socket.error as e:
            HSyslog.log_error(f"connect_device: {e}")
            time.sleep(5)

    def start_send_thread(self):
        if not self.send_thread or not self.send_thread.is_alive():
            self.send_thread = threading.Thread(target=self._send_messages, daemon=True)
            self.send_thread.start()

    def disconnect(self):
        """断开与MQTT服务器的连接"""
        self.client.loop_stop()
        self.client.disconnect()
        HSyslog.log_info("Disconnected from Device MQTT broker")

    def _on_connect(self, client, userdata, flags, rc):
        """连接成功时的回调函数"""
        if rc == 0:
            HHhdlist.device_mqtt_status = True
            HSyslog.log_info("Connected to Device MQTT Broker!")
        else:
            HHhdlist.device_mqtt_status = False
            HSyslog.log_info(f"Failed to device connect, return code {rc}")

    def _on_disconnect(self, client, userdata, rc):
        """断开连接时的回调函数"""
        HSyslog.log_info("check device connection is closed! rc = {}".format(rc))
        HHhdlist.device_mqtt_status = False
        # 断线自动重连
        try:
            if rc != 0:
                HSyslog.log_info("Attempting to device reconnect...")
                self.reconnect()
        except Exception as e:
            HSyslog.log_error(f"Device MQTT.close: {e}")

    def reconnect(self):
        """重新连接到MQTT服务器"""
        try:
            self.client.reconnect()
            HSyslog.log_info("Reconnected to Device MQTT broker")
        except Exception as e:
            HSyslog.log_error(f"Device Reconnection failed: {e}")
        time.sleep(10)

    def subscribe(self):
        """订阅主题"""
        for topic, topic_dict in app_func_dict.items():
            if topic_dict.get("isSubscribe"):
                self.client.subscribe(topic)
                HSyslog.log_info(f"{topic}")

    def _on_message(self, client, userdata, msg):
        """接收消息时的回调函数"""
        try:
            receive_msg = msg.payload.decode('utf-8', 'ignore')
            topic = msg.topic
            if receive_msg and topic:
                if topic in app_func_dict.keys():
                    receive_dict = json.loads(receive_msg)
                    app_func_dict[topic]["func"](receive_dict.get("body", {}))
                    # HSyslog.log_info(f"Received Device message: '{receive_msg}' on topic {topic}")
                    if topic != HHhdlist.topic_hqc_main_telemetry_notify_info:
                        HSyslog.log_info(f"Received Device message: '{receive_msg}' on topic {topic}")
        except Exception as e:
            HSyslog.log_error(f"device _receive_messages: '{msg}' {e}")

    def _send_messages(self):
        """向主题发送消息"""
        while True:
            if HHhdlist.device_mqtt_status:
                if not HHhdlist.hd_send_data:
                    time.sleep(0.1)
                else:
                    try:
                        if HHhdlist.hd_send_data.empty():
                            time.sleep(0.1)
                        else:
                            msg = dict(HHhdlist.hd_send_data.get())
                            topic = msg.get("topic")
                            send_data = msg.get("msg", "")
                            qos = msg.get("qos", 0)
                            result = self.client.publish(topic, send_data, qos)
                            if result.rc == mqtt_client.MQTT_ERR_SUCCESS:
                                if topic != HHhdlist.topic_hqc_sys_network_state:
                                    HSyslog.log_info(f"Send_to_Device {send_data} to topic: {topic}")
                            else:
                                HSyslog.log_info(f"Failed to send device message, result code: {result.rc}")
                            time.sleep(0.02)
                    except Exception as e:
                        HSyslog.log_error(f"Send_to_Device: {e}")
            else:
                if not HHhdlist.hd_send_data:
                    time.sleep(0.1)
                else:
                    if HHhdlist.hd_send_data.empty():
                        time.sleep(0.1)
                    else:
                        msg = HHhdlist.hd_send_data.get()
                        HSyslog.log_info(f"Send_to_Device Faild: {msg}")


def app_publish(topic: str, msg_body: dict):
    HHhdlist.package_num += 1
    msg_dict = {'version': '1.1.1',
                'package_num': HHhdlist.package_num,  # 包序号
                'package_seq': 1,  # 包头序号
                'sub_pkt_num': 1,  # 分包数量
                'need_response': False,  # 消息是否需要确认
                'body': msg_body
                }
    if topic == HHhdlist.topic_hqc_main_event_notify_control_charge:
        msg_dict["body"].update({"package_num": HHhdlist.package_num})
    msg = json.dumps(msg_dict)
    qos = app_func_dict.get(topic).get("qos")
    send_msg = {"topic": topic, "msg": msg, "qos": qos}
    if msg_body.get("info_id", -1) != -1:
        if msg_body.get("info_id", -1) == HHhdlist.control_charge.start_charge.value:
            HStategrid.Gun_list[msg_body.get("gun_id")].set_gun_charge(
                {"start_package_num": msg_dict.get("package_num")})
        if msg_body.get("info_id", -1) == HHhdlist.control_charge.stop_charge.value:
            HStategrid.Gun_list[msg_body.get("gun_id")].set_gun_charge(
                {"stop_package_num": msg_dict.get("package_num")})
        if msg_body.get("info_id", -1) == HHhdlist.control_charge.rev_charge.value:
            HStategrid.Gun_list[msg_body.get("gun_id")].set_gun_charge(
                {"res_package_num": msg_dict.get("package_num")})
        if msg_body.get("info_id", -1) == HHhdlist.control_charge.rev_not_charge.value:
            HStategrid.Gun_list[msg_body.get("gun_id")].set_gun_charge(
                {"resnot_package_num": msg_dict.get("package_num")})

    HHhdlist.hd_send_data.put(send_msg)


def __mqtt_net_event():
    period_time = time.time()
    while True:
        if int(time.time()) - int(period_time) > 5:
            HHhdlist.get_net()
            if HStategrid.connect_status and HHhdlist.Device_ready:
                net_status = {
                    "netType": HHhdlist.net_status.get("netType"),
                    "netSigVal": HHhdlist.net_status.get("sigVal"),
                    "netId": HHhdlist.net_status.get("netId")
                }
                _hqc_sys_network_state(net_status)
            else:
                net_status = {
                    "netType": HHhdlist.net_type.no_net.value,
                    "netSigVal": 0,
                    "netId": HHhdlist.net_id.unknow.value
                }
                _hqc_sys_network_state(net_status)
            period_time = time.time()
        time.sleep(1)


def do_mqtt_net_period():
    mqttPeriodThread = threading.Thread(target=__mqtt_net_event)
    mqttPeriodThread.start()
    HSyslog.log_info("do_mqtt_net_period")


def __platform_device_data():
    while True:
        if not HHhdlist.platform_device_data:
            time.sleep(0.1)
        else:
            try:
                if HHhdlist.platform_device_data.empty():
                    time.sleep(0.1)
                else:
                    msg = HHhdlist.platform_device_data.get()
                    topic = msg[0]
                    app_func_dict[topic]["func"](msg[1])
            except Exception as e:
                HSyslog.log_error(f"__platform_device_data Faild: {msg}, {e}")


def do_platform_device_data():
    p_d = threading.Thread(target=__platform_device_data)
    p_d.start()
    HSyslog.log_info("do_platform_device_data")


'''################################################### 数据接收发送队列初始化 ####################################################'''

'''############################################### 接收数据处理 ##############################################'''


def _hqc_sys_network_state(msg_body_dict: dict):  # 网络状态消息
    netType = msg_body_dict.get("netType", -1)
    netSigVal = msg_body_dict.get("netSigVal", -1)
    netId = msg_body_dict.get("netId", -1)
    try:
        if netType != -1 and netSigVal != -1 and netId != -1:
            info = {
                "netType": netType,
                "netSigVal": netSigVal,
                "netId": netId
            }
            topic = HHhdlist.topic_hqc_sys_network_state
            app_publish(topic, info)
    except Exception as e:
        HSyslog.log_error(f"_hqc_sys_network_state error: {e}")


def _hqc_sys_time_sync(msg_body_dict: dict):  # 时间同步消息
    year = msg_body_dict.get("year", -1)
    try:
        if year == -1:
            unix_time = msg_body_dict.get("unix_time")
            dt_object = datetime.fromtimestamp(unix_time)
            time_info = {
                "year": dt_object.year - 2000,
                "month": dt_object.month,
                "day": dt_object.day,
                "hour": dt_object.hour,
                "minute": dt_object.minute,
                "second": dt_object.second
            }
        else:
            time_info = {
                "year": msg_body_dict.get("year", -1) - 2000,
                "month": msg_body_dict.get("month", -1),
                "day": msg_body_dict.get("day", -1),
                "hour": msg_body_dict.get("hour", -1),
                "minute": msg_body_dict.get("minute", -1),
                "second": msg_body_dict.get("second", -1)
            }
        topic = HHhdlist.topic_hqc_sys_time_sync
        app_publish(topic, time_info)
    except Exception as e:
        HSyslog.log_error(f"_hqc_sys_time_sync error: {e}")


def _hqc_main_telemetry_notify_fault(msg_body_dict: dict):  # 设备故障消息
    faultSum = msg_body_dict.get('faultSum', -1)  # int
    warnSum = msg_body_dict.get('warnSum', -1)  # int
    faultVal = msg_body_dict.get('faultVal', [])  # array
    warnVal = msg_body_dict.get('warnVal', [])  # array
    try:
        fault_code = {}  # {"device_num":[]}
        warn_code = {}
        for i in range(0, HStategrid.get_DeviceInfo("00110")):
            fault_code.update({i: {}})  # {"device_num":[]}
            warn_code.update({i: {}})  # {"device_num":[]}
        if warnSum < 0 or faultSum < 0:
            HSyslog.log_info("故障告警信息错误")
        elif warnSum > 0 or faultSum > 0:
            for info in faultVal:
                for p_fault_id, p_fault_info in HHhdlist.stop_fault_code.items():
                    gun_id = int(info.get("device_num"))
                    fault_id = info.get("fault_id")
                    if fault_id in p_fault_info:
                        fault_info = {
                            "fault_id": p_fault_id,
                            "start_time": info.get("start_time"),
                            "desc": info.get("desc"),
                            "status": 0
                        }
                        if gun_id >= HHhdlist.gun_num:
                            gun_id = random.randint(0, HHhdlist.gun_num - 1)
                            fault_code[gun_id].update({p_fault_id: fault_info})
                        else:
                            fault_code[gun_id].update({p_fault_id: fault_info})

            for info in warnVal:
                for p_fault_id, p_fault_info in HHhdlist.stop_fault_code.items():
                    gun_id = int(info.get("device_num"))
                    fault_id = info.get("fault_id")
                    if fault_id in p_fault_info:
                        fault_info = {
                            "warn_id": p_fault_id,
                            "start_time": info.get("start_time"),
                            "desc": info.get("desc"),
                            "status": 0
                        }
                        if gun_id >= HHhdlist.gun_num:
                            gun_id = random.randint(0, HHhdlist.gun_num - 1)
                            warn_code[gun_id].update({p_fault_id: fault_info})
                        else:
                            warn_code[gun_id].update({p_fault_id: fault_info})
        else:
            HSyslog.log_info("故障告警数量为零")

        for gun_info in HStategrid.Gun_list:
            HStategrid.Gun_list[gun_info.gun_id].set_gun_fault(fault_code.get(gun_info.gun_id))
            HStategrid.Gun_list[gun_info.gun_id].set_gun_warn(warn_code.get(gun_info.gun_id))

        HHhdlist.device_platform_data.put([HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_118.value, {}])
        HHhdlist.device_platform_data.put([HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_120.value, {}])
    except Exception as e:
        HSyslog.log_error(f"_hqc_main_telemetry_notify_fault error: {e}")


def _hqc_cloud_event_notify_fault(msg_body_dict: dict):  # 设备故障查询消息
    try:
        info = {
            "type": 0x00
        }
        topic = HHhdlist.topic_hqc_cloud_event_notify_fault
        app_publish(topic, info)
    except Exception as e:
        HSyslog.log_error(f"_hqc_cloud_event_notify_fault error: {e}")


def _hqc_main_telemetry_notify_info(msg_body_dict: dict):  # 遥测遥信消息
    dev_type = msg_body_dict.get('dcCharger')  # 设备类型
    chargeSys = {}
    cabinet = {}
    gun = {}
    pdu = {}
    module = {}
    bms = {}
    meter = {}
    parkLock = {}
    try:
        if dev_type != -1:
            for sub_dev_type, sub_dev_data in dev_type.items():  # 子设备遍历
                if sub_dev_type == "chargeSys":
                    for gun_id, gun_data in sub_dev_data.items():
                        gun_id = int(gun_id)
                        chargeSys[gun_id] = {}
                        for key, value in gun_data.items():
                            chargeSys[gun_id][int(key)] = value
                        if gun_id not in HHhdlist.chargeSys.keys():
                            HHhdlist.chargeSys[gun_id] = {}
                        HHhdlist.chargeSys[gun_id].update(chargeSys[gun_id])
                if sub_dev_type == "cabinet":
                    for gun_id, gun_data in sub_dev_data.items():
                        gun_id = int(gun_id)
                        cabinet[gun_id] = {}
                        for key, value in gun_data.items():
                            if key != "extend":
                                cabinet[gun_id][int(key)] = value
                        if gun_id not in HHhdlist.cabinet.keys():
                            HHhdlist.cabinet[gun_id] = {}
                        HHhdlist.cabinet[gun_id].update(cabinet[gun_id])
                if sub_dev_type == "gun":
                    for gun_id, gun_data in sub_dev_data.items():
                        gun_id = int(gun_id)
                        gun[gun_id] = {}
                        for key, value in gun_data.items():
                            gun[gun_id][int(key)] = value
                        if gun_id not in HHhdlist.gun.keys():
                            HHhdlist.gun[gun_id] = {}
                        HHhdlist.gun[gun_id].update(gun[gun_id])
                if sub_dev_type == "pdu":
                    for gun_id, gun_data in sub_dev_data.items():
                        gun_id = int(gun_id)
                        pdu[gun_id] = {}
                        for key, value in gun_data.items():
                            pdu[gun_id][int(key)] = value
                        if gun_id not in HHhdlist.pdu.keys():
                            HHhdlist.pdu[gun_id] = {}
                        HHhdlist.pdu[gun_id].update(pdu[gun_id])
                if sub_dev_type == "module":
                    for gun_id, gun_data in sub_dev_data.items():
                        gun_id = int(gun_id)
                        module[gun_id] = {}
                        for key, value in gun_data.items():
                            module[gun_id][int(key)] = value
                        if gun_id not in HHhdlist.module.keys():
                            HHhdlist.module[gun_id] = {}
                        HHhdlist.module[gun_id].update(module[gun_id])
                if sub_dev_type == "bms":
                    for gun_id, gun_data in sub_dev_data.items():
                        gun_id = int(gun_id)
                        bms[gun_id] = {}
                        for key, value in gun_data.items():
                            bms[gun_id][int(key)] = value
                        if gun_id not in HHhdlist.bms.keys():
                            HHhdlist.bms[gun_id] = {}
                        HHhdlist.bms[gun_id].update(bms[gun_id])
                if sub_dev_type == "meter":
                    for gun_id, gun_data in sub_dev_data.items():
                        gun_id = int(gun_id)
                        meter[gun_id] = {}
                        for key, value in gun_data.items():
                            meter[gun_id][int(key)] = value
                        if gun_id not in HHhdlist.meter.keys():
                            HHhdlist.meter[gun_id] = {}
                        HHhdlist.meter[gun_id].update(meter[gun_id])
                if sub_dev_type == "parkLock":
                    for gun_id, gun_data in sub_dev_data.items():
                        gun_id = int(gun_id)
                        parkLock[gun_id] = {}
                        for key, value in gun_data.items():
                            parkLock[gun_id][int(key)] = value
                        if gun_id not in HHhdlist.parkLock.keys():
                            HHhdlist.parkLock[gun_id] = {}
                        HHhdlist.parkLock[gun_id].update(parkLock[gun_id])

        if HStategrid.Platform_ready:
            for gun_id in HHhdlist.gun.keys():
                if HHhdlist.gun.get(gun_id).get(6) == 1 and HStategrid.Gun_list[gun_id].get_gun_connect_status() == HStategrid.Gun_Connect_Status.Not_Connect.value:
                    HStategrid.Gun_list[gun_id].set_gun_status(HStategrid.Gun_Status.Plugged_in_not_charging.value)
                    HStategrid.Gun_list[gun_id].set_gun_connect_status(HStategrid.Gun_Connect_Status.Connect.value)
                    HStategrid.Gun_list[gun_id].set_gun_car_connect_status(1)
                    info = {
                        "gun_id": gun_id,
                        "cmd_addr": HStategrid.Gun_Connect_Status.Connect.value,
                        "addr_data": "0000",
                        "charge_id": ""
                    }
                    HHhdlist.device_platform_data.put([HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_108.value, info])
                elif HHhdlist.gun.get(gun_id).get(6) == 0 and HStategrid.Gun_list[gun_id].get_gun_connect_status() == HStategrid.Gun_Connect_Status.Connect.value:
                    HStategrid.Gun_list[gun_id].set_gun_status(HStategrid.Gun_Status.Idle.value)
                    HStategrid.Gun_list[gun_id].set_gun_connect_status(HStategrid.Gun_Connect_Status.Not_Connect.value)
                    HStategrid.Gun_list[gun_id].set_gun_charge_gun_id([gun_id])
                    # HStategrid.Gun_list[gun_id] = HStategrid.Gun_info(gun_id)
                    HStategrid.Gun_list[gun_id].set_gun_car_connect_status(0)
                    info = {
                        "gun_id": gun_id,
                        "cmd_addr": HStategrid.Gun_Connect_Status.Not_Connect.value,
                        "addr_data": "0000",
                        "charge_id": ""
                    }
                    HHhdlist.device_platform_data.put([HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_108.value, info])
    except Exception as e:
        HSyslog.log_error(f"_hqc_main_telemetry_notify_info error: {e}")

    # HSyslog.log_info(f"chargeSys: {HHhdlist.chargeSys}")
    # HSyslog.log_info(f"cabinet: {HHhdlist.cabinet}")
    # HSyslog.log_info(f"gun: {HHhdlist.gun}")
    # HSyslog.log_info(f"pdu: {HHhdlist.pdu}")
    # HSyslog.log_info(f"module: {HHhdlist.module}")
    # HSyslog.log_info(f"bms: {HHhdlist.bms}")
    # HSyslog.log_info(f"meter: {HHhdlist.meter}")
    # HSyslog.log_info(f"parkLock: {HHhdlist.parkLock}")


def _hqc_cloud_event_notify_info(msg_body_dict: dict):  # 遥测遥信查询消息
    device_type = msg_body_dict.get("device_type", -1)
    try:
        info = {
            "dcCharger": device_type,
        }
        topic = HHhdlist.topic_hqc_cloud_event_notify_info
        app_publish(topic, info)
    except Exception as e:
        HSyslog.log_error(f"_hqc_cloud_event_notify_info error: {e}")


def _hqc_main_event_notify_request_charge(msg_body_dict: dict):  # 充电请求消息
    gun_id = msg_body_dict.get('gun_id', -1)  # int
    session_id = msg_body_dict.get('session_id', '')  # string
    start_source = msg_body_dict.get('start_source', -1)  # int
    charge_type = msg_body_dict.get('charge_type', -1)  # int
    stop_type = msg_body_dict.get('stop_type', -1)  # int
    stop_condition = msg_body_dict.get('stop_condition', -1)  # int
    try:
        HStategrid.Gun_list[gun_id].set_gun_charge({"device_session_id": session_id})
        HStategrid.Gun_list[gun_id].set_gun_charge({"start_source": start_source})
        HStategrid.Gun_list[gun_id].set_gun_charge({"charge_type": charge_type})
        HStategrid.Gun_list[gun_id].set_gun_charge({"stop_type": stop_type})
        HStategrid.Gun_list[gun_id].set_gun_charge({"stop_condition": stop_condition})
        info = {
            'gun_id': gun_id,
        }
        _hqc_main_event_reply_request_charge(info)
    except Exception as e:
        HSyslog.log_error(f"_hqc_main_event_notify_request_charge error: {e}")


def _hqc_main_event_reply_request_charge(msg_body_dict: dict):  # 充电请求应答消息
    gun_id = msg_body_dict.get("gun_id")
    try:
        info = {
            'gun_id': gun_id,
            'cloud_session_id': "",
            'device_session_id': HStategrid.Gun_list[gun_id].get_gun_charge("device_session_id"),
            'request_result': 1,
            'failure_reason': 0,
            'temp_strategy': {
                'delay_time': -1,
                'stop_type': HStategrid.Gun_list[gun_id].get_gun_charge("stop_type"),
                'stop_condition': HStategrid.Gun_list[gun_id].get_gun_charge("stop_condition")
            },
            'temp_rate': {
                'rate_id': "",
                'count': 0,
                'items': []
            }
        }
        topic = HHhdlist.topic_hqc_main_event_reply_request_charge
        app_publish(topic, info)

        HStategrid.Gun_list[gun_id].set_gun_charge({"failure_reason": info.get("failure_reason")})
        HStategrid.Gun_list[gun_id].set_gun_charge({"delay_time": info.get("temp_strategy").get("delay_time")})
    except Exception as e:
        HSyslog.log_error(f"_hqc_main_event_reply_request_charge error: {e}")


def _hqc_main_event_notify_control_charge(msg_body_dict: dict):  # 充电控制消息
    info = msg_body_dict.get("control_type", "")
    try:
        if info == HHhdlist.control_charge.start_charge.value:
            gun_id = msg_body_dict.get("gun_id")
            msg = {
                'control_type': info,
                'gun_id': gun_id,
                'command_type': 0,
                'start_source': HStategrid.Gun_list[gun_id].get_gun_charge("start_source"),
                'aux_power_type': 0xFF,
                'multi_mode': 0xFF,
                'user_id': HStategrid.Gun_list[gun_id].get_gun_charge("user_phone"),
                'appointment_time': 0,
                'cloud_session_id': HStategrid.Gun_list[gun_id].get_gun_charge("charge_id"),
                'account_info': {
                    'stop_code': HStategrid.Gun_list[gun_id].get_gun_charge("user_phone"),
                    'balance': 0,
                    'billing': 0,
                    'overdraft_limit': 0,
                    'electric_discount': 0,
                    'service_discount': 0,
                    'multi_charge': 0,
                },
                'temp_strategy': {
                    'delay_time': -1,
                    'stop_type': HStategrid.Gun_list[gun_id].get_gun_charge("stop_type"),
                    'stop_condition': HStategrid.Gun_list[gun_id].get_gun_charge("stop_condition"),
                },
                'temp_rate': {
                    'rate_id': "",
                    'count': 0,
                    'items': []
                }
            }
            topic = HHhdlist.topic_hqc_main_event_notify_control_charge
            app_publish(topic, msg)

            HStategrid.Gun_list[gun_id].set_gun_charge({"start_source": msg.get("start_source")})
            HStategrid.Gun_list[gun_id].set_gun_charge({"aux_power_type": msg.get("aux_power_type")})
            HStategrid.Gun_list[gun_id].set_gun_charge({"cloud_session_id": msg.get("cloud_session_id")})
            HStategrid.Gun_list[gun_id].set_gun_charge({"appointment_time": msg.get("appointment_time")})
            HStategrid.Gun_list[gun_id].set_gun_charge({"multi_mode": msg.get("multi_mode")})

            HStategrid.Gun_list[gun_id].set_gun_charge({"delay_time": msg.get("temp_strategy").get("delay_time")})
            HStategrid.Gun_list[gun_id].set_gun_charge({"stop_type": msg.get("temp_strategy").get("stop_type")})
            HStategrid.Gun_list[gun_id].set_gun_charge({"stop_condition": msg.get("temp_strategy").get("stop_condition")})
            HStategrid.Gun_list[gun_id].set_gun_charge({"balance": msg.get("account_info").get("balance")})
            HStategrid.Gun_list[gun_id].set_gun_charge({"billing": msg.get("account_info").get("billing")})
            HStategrid.Gun_list[gun_id].set_gun_charge({"stop_code": msg.get("account_info").get("stop_code")})
            HStategrid.Gun_list[gun_id].set_gun_charge({"overdraft_limit": msg.get("account_info").get("overdraft_limit")})
            HStategrid.Gun_list[gun_id].set_gun_charge({"electric_discount": msg.get("account_info").get("electric_discount")})
            HStategrid.Gun_list[gun_id].set_gun_charge({"service_discount": msg.get("account_info").get("service_discount")})
            HStategrid.Gun_list[gun_id].set_gun_charge({"multi_charge": msg.get("account_info").get("multi_charge")})
            HStategrid.Gun_list[gun_id].set_gun_charge({"user_id": msg.get("user_id")})
        elif info == HHhdlist.control_charge.stop_charge.value:
            gun_id = msg_body_dict.get("gun_id")
            msg = {
                'info_id': info,
                'gun_id': gun_id,
                'command_type': 1,
                'start_source': HStategrid.Gun_list[gun_id].get_gun_charge("start_source"),
                'aux_power_type': HStategrid.Gun_list[gun_id].get_gun_charge("aux_power_type"),
                'multi_mode': HStategrid.Gun_list[gun_id].get_gun_charge("multi_mode"),
                'user_id': HStategrid.Gun_list[gun_id].get_gun_charge("user_id"),
                'appointment_time': HStategrid.Gun_list[gun_id].get_gun_charge("appointment_time"),
                'cloud_session_id': HStategrid.Gun_list[gun_id].get_gun_charge("charge_id"),
                'account_info': {
                    'stop_code': HStategrid.Gun_list[gun_id].get_gun_charge("stop_code"),
                    'balance': HStategrid.Gun_list[gun_id].get_gun_charge("balance"),
                    'billing': HStategrid.Gun_list[gun_id].get_gun_charge("billing"),
                    'overdraft_limit': HStategrid.Gun_list[gun_id].get_gun_charge("overdraft_limit"),
                    'electric_discount': HStategrid.Gun_list[gun_id].get_gun_charge("electric_discount"),
                    'service_discount': HStategrid.Gun_list[gun_id].get_gun_charge("service_discount"),
                    'multi_charge': HStategrid.Gun_list[gun_id].get_gun_charge("multi_charge"),
                },
                'temp_strategy': {
                    'delay_time': HStategrid.Gun_list[gun_id].get_gun_charge("delay_time"),
                    'stop_type': HStategrid.Gun_list[gun_id].get_gun_charge("stop_type"),
                    'stop_condition': HStategrid.Gun_list[gun_id].get_gun_charge("stop_condition"),
                },
                'temp_rate': {
                    'rate_id': "",
                    'count': 0,
                    'items': []
                }
            }
            topic = HHhdlist.topic_hqc_main_event_notify_control_charge
            app_publish(topic, msg)
        elif info == HHhdlist.control_charge.rev_charge.value:
            gun_id = msg_body_dict.get("gun_id")
            msg = {
                'control_type': info,
                'gun_id': gun_id,
                'command_type': 5,
                'start_source': 2,
                'user_id': HStategrid.get_DeviceInfo("Device_ID"),
                'appointment_time': msg_body_dict.get("start_rev_time"),
                'cloud_session_id': "",
                'multi_charge_mode': 0,
                'account_info': {
                    'stop_code': "",
                    'balance': 0,
                    'billing': 0,
                    'overdraft_limit': 0,
                    'electric_discount': 0,
                    'service_discount': 0,
                    'multi_charge': 0,
                },
                'temp_strategy': {
                    'delay_time': -1,
                    'stop_type': 0,
                    'stop_condition': 0,
                },
                'temp_rate': {
                    'rate_id': "",
                    'count': 0,
                    'items': []
                }
            }
            topic = HHhdlist.topic_hqc_main_event_notify_control_charge
            app_publish(topic, msg)

            HStategrid.Gun_list[gun_id].set_gun_charge({"start_source": msg.get("start_source")})
            HStategrid.Gun_list[gun_id].set_gun_charge({"aux_power_type": msg.get("aux_power_type")})
            HStategrid.Gun_list[gun_id].set_gun_charge({"cloud_session_id": msg.get("cloud_session_id")})
            HStategrid.Gun_list[gun_id].set_gun_charge({"appointment_time": msg.get("appointment_time")})
            HStategrid.Gun_list[gun_id].set_gun_charge({"multi_mode": msg.get("multi_mode")})
            HStategrid.Gun_list[gun_id].set_gun_charge({"delay_time": msg.get("temp_strategy").get("delay_time")})
            HStategrid.Gun_list[gun_id].set_gun_charge({"stop_type": msg.get("temp_strategy").get("stop_type")})
            HStategrid.Gun_list[gun_id].set_gun_charge({"stop_condition": msg.get("temp_strategy").get("stop_condition")})
            HStategrid.Gun_list[gun_id].set_gun_charge({"balance": msg.get("account_info").get("balance")})
            HStategrid.Gun_list[gun_id].set_gun_charge({"billing": msg.get("account_info").get("billing")})
            HStategrid.Gun_list[gun_id].set_gun_charge({"stop_code": msg.get("account_info").get("stop_code")})
            HStategrid.Gun_list[gun_id].set_gun_charge({"overdraft_limit": msg.get("account_info").get("overdraft_limit")})
            HStategrid.Gun_list[gun_id].set_gun_charge({"electric_discount": msg.get("account_info").get("electric_discount")})
            HStategrid.Gun_list[gun_id].set_gun_charge({"service_discount": msg.get("account_info").get("service_discount")})
            HStategrid.Gun_list[gun_id].set_gun_charge({"multi_charge": msg.get("account_info").get("multi_charge")})
            HStategrid.Gun_list[gun_id].set_gun_charge({"user_id": msg.get("user_id")})
        elif info == HHhdlist.control_charge.rev_not_charge.value:
            gun_id = msg_body_dict.get("gun_id")
            msg = {
                'info_id': info,
                'gun_id': gun_id,
                'command_type': 6,
                'start_source': HStategrid.Gun_list[gun_id].get_gun_charge("start_source"),
                'user_id': HStategrid.Gun_list[gun_id].get_gun_charge("user_id"),
                'appointment_time': HStategrid.Gun_list[gun_id].get_gun_charge("appointment_time"),
                'cloud_session_id': "",
                'multi_charge_mode': HStategrid.Gun_list[gun_id].get_gun_charge("multi_charge_mode"),
                'account_info': {
                    'stop_code': HStategrid.Gun_list[gun_id].get_gun_charge("stop_code"),
                    'balance': HStategrid.Gun_list[gun_id].get_gun_charge("balance"),
                    'billing': HStategrid.Gun_list[gun_id].get_gun_charge("billing"),
                    'overdraft_limit': HStategrid.Gun_list[gun_id].get_gun_charge("overdraft_limit"),
                    'electric_discount': HStategrid.Gun_list[gun_id].get_gun_charge("electric_discount"),
                    'service_discount': HStategrid.Gun_list[gun_id].get_gun_charge("service_discount"),
                    'multi_charge': HStategrid.Gun_list[gun_id].get_gun_charge("multi_charge"),
                },
                'temp_strategy': {
                    'delay_time': HStategrid.Gun_list[gun_id].get_gun_charge("delay_time"),
                    'stop_type': HStategrid.Gun_list[gun_id].get_gun_charge("stop_type"),
                    'stop_condition': HStategrid.Gun_list[gun_id].get_gun_charge("stop_condition"),
                },
                'temp_rate': {
                    'rate_id': "",
                    'count': 0,
                    'items': []
                }
            }
            topic = HHhdlist.topic_hqc_main_event_notify_control_charge
            app_publish(topic, msg)
        else:
            HSyslog.log_info(f"_hqc_main_event_notify_control_charge' control_charge error: {info}")
    except Exception as e:
        HSyslog.log_error(f"_hqc_main_event_notify_control_charge error: {e}")


def _hqc_main_event_reply_control_charge(msg_body_dict: dict):  # 充电控制应答消息
    gun_id = msg_body_dict.get('gun_id', -1)  # int
    package_num = msg_body_dict.get('package_num', -1)  # int
    result = msg_body_dict.get('result', -1)  # int
    reason = msg_body_dict.get('reason', -1)  # int
    time = msg_body_dict.get('time', -1)  # int
    try:
        pass
    except Exception as e:
        HSyslog.log_error(f"_hqc_main_event_reply_control_charge error: {e}")


def _hqc_ui_event_notify_auth_gun(msg_body_dict: dict):  # 鉴权绑定消息
    gun_id = msg_body_dict.get('gun_id', -1)  # int
    type = msg_body_dict.get('type', -1)  # int
    try:
        info = {
            "gun_id": gun_id,
            "auth_time": 60,
            "type": type
        }
        topic = HHhdlist.topic_hqc_ui_event_notify_auth_gun
        app_publish(topic, info)
    except Exception as e:
        HSyslog.log_error(f"_hqc_ui_event_notify_auth_gun error: {e}")


def _hqc_main_event_notify_check_vin(msg_body_dict: dict):  # 车辆VIN鉴权消息
    gun_id = msg_body_dict.get('gun_id', -1)  # int
    type = msg_body_dict.get('type', -1)  # int
    content = msg_body_dict.get('content', '')  # string
    start_source = msg_body_dict.get('start_source', -1)  # int
    extras = msg_body_dict.get('extras', '')  # string

    try:
        if not HStategrid.hand_status or not HStategrid.connect_status:
            info = {
                "gun_id": gun_id,
                "result": 0,
                "reason": 0x04,
            }
            _hqc_main_event_reply_check_vin(info)
            return True

        HStategrid.Gun_list[gun_id].set_gun_charge({"car_vin": content})
        HStategrid.Gun_list[gun_id].set_gun_charge({"card_id": extras})

        if start_source == 4 and start_source == HStategrid.Gun_list[gun_id].get_gun_charge("start_source"):
            info = {
                "gun_id": gun_id,
                "result": 1,
                "reason": 0x04,
            }
            _hqc_main_event_reply_check_vin(info)
        elif start_source == 5 and start_source == HStategrid.Gun_list[gun_id].get_gun_charge("start_source"):
            auth_data = {
                "gun_id": gun_id,
            }
            HHhdlist.device_platform_data.put([HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_34.value, auth_data])
        elif start_source == 7 and start_source == HStategrid.Gun_list[gun_id].get_gun_charge("start_source"):
            auth_data = {
                "gun_id": gun_id,
            }
            HHhdlist.device_platform_data.put([HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_40.value, auth_data])
        elif start_source == 0x0B:
            info = {
                "gun_id": gun_id,
                "result": 1,
                "reason": 0x04,
            }
            _hqc_main_event_reply_check_vin(info)
            pass
    except Exception as e:
        HSyslog.log_error(f"_hqc_main_event_notify_check_vin error: {e}")


def _hqc_main_event_reply_check_vin(msg_body_dict: dict):  # 车辆VIN鉴权应答消息
    gun_id = msg_body_dict.get("gun_id")
    start_source = HStategrid.Gun_list[gun_id].get_gun_charge("start_source")
    try:
        if start_source == 4:
            info = {
                "gun_id": gun_id,
                "result": msg_body_dict.get("result"),
                "failure_reason": msg_body_dict.get("reason"),
                "account_info": {
                    "stop_code": HStategrid.Gun_list[gun_id].get_gun_charge("stop_code"),
                    "balance": HStategrid.Gun_list[gun_id].get_gun_charge("balance"),
                    "billing": HStategrid.Gun_list[gun_id].get_gun_charge("billing"),
                    "overdraft_limit": HStategrid.Gun_list[gun_id].get_gun_charge("overdraft_limit"),
                    "electric_discount": HStategrid.Gun_list[gun_id].get_gun_charge("electric_discount"),
                    "service_discount": HStategrid.Gun_list[gun_id].get_gun_charge("service_discount"),
                    "multi_charge": HStategrid.Gun_list[gun_id].get_gun_charge("multi_charge"),
                }
            }
        elif start_source == 5:
            info = {
                "gun_id": gun_id,
                "result": msg_body_dict.get("result"),
                "failure_reason": msg_body_dict.get("reason"),
                "account_info": {
                    "stop_code": "",
                    "balance": msg_body_dict.get("balance"),
                    "billing": 1,
                    "overdraft_limit": 0,
                    "electric_discount": 0,
                    "service_discount": 0,
                    "multi_charge": 0,
                }
            }
        elif start_source == 7:
            info = {
                "gun_id": gun_id,
                "result": msg_body_dict.get("result"),
                "failure_reason": msg_body_dict.get("reason"),
                "account_info": {
                    "stop_code": msg_body_dict.get("stop_code"),
                    "balance": msg_body_dict.get("balance"),
                    "billing": 0,
                    "overdraft_limit": 0,
                    "electric_discount": 0,
                    "service_discount": 0,
                    "multi_charge": 0,
                }
            }
        else:
            info = {}
        topic = HHhdlist.topic_hqc_main_event_reply_check_vin
        app_publish(topic, info)

        gun_charge_mode = HHhdlist.gun.get(gun_id, {}).get(7, 0)
        if gun_charge_mode == 0:
            HStategrid.Gun_list[gun_id].set_gun_charge_gun_id([gun_id])
        elif gun_charge_mode == 1:
            HStategrid.Gun_list[gun_id + 1].copy_gun_charge(gun_id)
            HStategrid.Gun_list[gun_id].set_gun_charge_gun_id([gun_id, gun_id + 1])
            HStategrid.Gun_list[gun_id + 1].set_gun_charge_gun_id([gun_id, gun_id + 1])
        elif gun_charge_mode == 2:
            HStategrid.Gun_list[gun_id + 1].copy_gun_charge(gun_id)
            HStategrid.Gun_list[gun_id + 2].copy_gun_charge(gun_id)
            HStategrid.Gun_list[gun_id].set_gun_charge_gun_id([gun_id, gun_id + 1, gun_id + 2])
            HStategrid.Gun_list[gun_id + 1].set_gun_charge_gun_id([gun_id, gun_id + 1, gun_id + 2])
            HStategrid.Gun_list[gun_id + 2].set_gun_charge_gun_id([gun_id, gun_id + 1, gun_id + 2])

        gun_list = HStategrid.Gun_list[gun_id].get_gun_charge_gun_id()
        for gun in gun_list:
            if HStategrid.Gun_list[gun].get_gun_charge("charge_id") is not None and HStategrid.Gun_list[gun].get_gun_charge("device_session_id") is not None:
                update_charge_id = {
                    "gun_id": gun,
                    "device_session_id": HStategrid.Gun_list[gun_id].get_gun_charge("device_session_id"),
                    "cloud_session_id": HStategrid.Gun_list[gun_id].get_gun_charge("charge_id"),
                }
                _hqc_cloud_event_notify_update_charge_order_id(update_charge_id)
                HStategrid.Gun_list[gun].set_gun_charge({"cloud_session_id": HStategrid.Gun_list[gun_id].get_gun_charge("charge_id")})

        # for gun_info in HStategrid.Gun_list:
        #     HSyslog.log_info(f"{gun_info.gun_id}: {gun_info.get_gun_charge()}")
    except Exception as e:
        HSyslog.log_error(f"_hqc_main_event_reply_check_vin error: {e}")


def _hqc_main_event_notify_charge_record(msg_body_dict: dict):  # 充电记录消息
    gun_id = msg_body_dict.get('gun_id')
    device_session_id = msg_body_dict.get("device_session_id", "")
    cloud_session_id = msg_body_dict.get("cloud_session_id", "")
    try:
        if cloud_session_id == HStategrid.Gun_list[gun_id].get_gun_charge("cloud_session_id") and HStategrid.Gun_list[gun_id].get_gun_charge("cloud_session_id") is not None:
            HStategrid.Gun_list[gun_id].set_gun_status(HStategrid.Gun_Status.Stopping.value)
            charge_stop_reason = HHhdlist.get_stop_reason(msg_body_dict.get("stop_reason"))
            info = {
                "gun_id": gun_id,
                "cmd_addr": HStategrid.Gun_Connect_Status.Stop_Charge.value,
                "addr_data": charge_stop_reason,
                "charge_id": cloud_session_id,
            }
            HHhdlist.device_platform_data.put([HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_108.value, info])
            info = {
                "gun_id": gun_id,
            }
            HHhdlist.device_platform_data.put([HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_104.value, info])
            HStategrid.Gun_list[gun_id].set_gun_charge_order(msg_body_dict)
            HStategrid.Gun_list[gun_id].set_gun_charge_reserve()
            HHhdlist.device_platform_data.put([HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_312.value, info])
            HHhdlist.device_platform_data.put([HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_202.value, info])
            info = {
                "gun_id": gun_id,
                "cloud_session_id": cloud_session_id,
            }
            _hqc_main_event_notify_charge_account(info)
        else:
            info = {
                "gun_id": gun_id,
                "cloud_session_id": cloud_session_id,
                "device_session_id": device_session_id,
                "result": 0
            }
            HHhdlist.platform_device_data.put([HHhdlist.topic_hqc_main_event_reply_charge_record, info])
    except Exception as e:
        HSyslog.log_error(f"_hqc_main_event_notify_charge_record error: {e}")


def _hqc_main_event_reply_charge_record(msg_body_dict: dict):  # 充电记录应答消息
    gun_id = msg_body_dict.get("gun_id")
    try:
        info = {
            "cloud_session_id": msg_body_dict.get("cloud_session_id"),
            "device_session_id": msg_body_dict.get("device_session_id"),
            "result": msg_body_dict.get("result")
        }
        topic = HHhdlist.topic_hqc_main_event_reply_charge_record
        app_publish(topic, info)
    except Exception as e:
        HSyslog.log_error(f"_hqc_main_event_reply_charge_record error: {e}")


def _hqc_main_event_notify_charge_cost(msg_body_dict: dict):  # 充电费用消息
    gun_id = msg_body_dict.get("gun_id")
    try:
        if HStategrid.Gun_list[gun_id].get_gun_charge("device_session_id") == msg_body_dict.get("device_session_id"):
            HStategrid.Gun_list[gun_id].set_gun_charge({"charge_time": msg_body_dict.get('charge_time', -1)})
            HStategrid.Gun_list[gun_id].set_gun_charge({"cusp_energy": msg_body_dict.get('cusp_energy', -1)})
            HStategrid.Gun_list[gun_id].set_gun_charge({"cusp_electric_cost": msg_body_dict.get('cusp_electric_cost', -1)})
            HStategrid.Gun_list[gun_id].set_gun_charge({"cusp_service_cost": msg_body_dict.get('cusp_service_cost', -1)})
            HStategrid.Gun_list[gun_id].set_gun_charge({"peak_energy": msg_body_dict.get('peak_energy', -1)})
            HStategrid.Gun_list[gun_id].set_gun_charge({"peak_electric_cost": msg_body_dict.get('peak_electric_cost', -1)})
            HStategrid.Gun_list[gun_id].set_gun_charge({"peak_service_cost": msg_body_dict.get('peak_service_cost', -1)})
            HStategrid.Gun_list[gun_id].set_gun_charge({"normal_energy": msg_body_dict.get('normal_energy', -1)})
            HStategrid.Gun_list[gun_id].set_gun_charge({"normal_electric_cost": msg_body_dict.get('normal_electric_cost', -1)})
            HStategrid.Gun_list[gun_id].set_gun_charge({"normal_service_cost": msg_body_dict.get('normal_service_cost', -1)})
            HStategrid.Gun_list[gun_id].set_gun_charge({"valley_energy": msg_body_dict.get('valley_energy', -1)})
            HStategrid.Gun_list[gun_id].set_gun_charge({"valley_electric_cost": msg_body_dict.get('valley_electric_cost', -1)})
            HStategrid.Gun_list[gun_id].set_gun_charge({"valley_service_cost": msg_body_dict.get('valley_service_cost', -1)})
            HStategrid.Gun_list[gun_id].set_gun_charge({"deep_valley_energy": msg_body_dict.get('deep_valley_energy', -1)})
            HStategrid.Gun_list[gun_id].set_gun_charge({"deep_valley_electric_cost": msg_body_dict.get('deep_valley_electric_cost', -1)})
            HStategrid.Gun_list[gun_id].set_gun_charge({"deep_valley_service_cost": msg_body_dict.get('deep_valley_service_cost', -1)})
            HStategrid.Gun_list[gun_id].set_gun_charge({"total_energy": msg_body_dict.get('total_energy', -1)})
            HStategrid.Gun_list[gun_id].set_gun_charge({"total_electric_cost": msg_body_dict.get('total_electric_cost', -1)})
            HStategrid.Gun_list[gun_id].set_gun_charge({"total_service_cost": msg_body_dict.get('total_service_cost', -1)})
            HStategrid.Gun_list[gun_id].set_gun_charge({"total_cost": msg_body_dict.get('total_cost', -1)})

            HStategrid.Gun_list[gun_id].gun_charge_cost = True

        # for gun_info in HStategrid.Gun_list:
        #     HSyslog.log_info(f"{gun_info.gun_id}: {gun_info.get_gun_charge()}")
    except Exception as e:
        HSyslog.log_error(f"_hqc_main_event_notify_charge_cost error: {e}")


def _hqc_main_event_notify_charge_elec(msg_body_dict: dict):  # 充电电量冻结消息
    gun_id = msg_body_dict.get('gun_id', -1)  # int
    cloud_session_id = msg_body_dict.get('cloud_session_id', '')  # string
    device_session_id = msg_body_dict.get('device_session_id', '')  # string
    count = msg_body_dict.get('count', -1)  # int
    items = msg_body_dict.get('items', [])  # array
    try:
        pass
    except Exception as e:
        HSyslog.log_error(f"_hqc_main_event_notify_charge_elec error: {e}")


def _hqc_main_event_notify_charge_account(msg_body_dict: dict):  # 充电结算消息
    gun_id = msg_body_dict.get('gun_id', -1)  # int
    cloud_session_id = msg_body_dict.get('cloud_session_id', '')  # string
    try:
        info = {
            "gun_id": gun_id,
            "cloud_session_id": cloud_session_id,
            "user_id": HStategrid.Gun_list[gun_id].get_gun_charge_order("user_id"),
            "balance": 0,
            "energy": HStategrid.Gun_list[gun_id].get_gun_charge_order("total_energy"),
            "electric_cost": HStategrid.Gun_list[gun_id].get_gun_charge_order("total_electric_cost"),
            "service_cost": HStategrid.Gun_list[gun_id].get_gun_charge_order("total_service_cost"),
            "total_cost": HStategrid.Gun_list[gun_id].get_gun_charge_order("total_cost"),
        }
        topic = HHhdlist.topic_hqc_cloud_event_notify_recharge
        app_publish(topic, info)
    except Exception as e:
        HSyslog.log_error(f"_hqc_main_event_notify_charge_account error: {e}")


def _hqc_cloud_event_notify_recharge(msg_body_dict: dict):  # 账户充值消息
    gun_id = msg_body_dict.get('gun_id', -1)  # int
    try:
        info = {
            "gun_id": gun_id,
            "device_session_id": HStategrid.Gun_list[gun_id].set_gun_charge("charge_id"),
            "user_id": HStategrid.Gun_list[gun_id].set_gun_charge("user_id"),
            "card_id": HStategrid.Gun_list[gun_id].set_gun_charge("card_id"),
            "balance": HStategrid.Gun_list[gun_id].set_gun_charge("balance"),
        }
        topic = HHhdlist.topic_hqc_cloud_event_notify_recharge
        app_publish(topic, info)
    except Exception as e:
        HSyslog.log_error(f"_hqc_cloud_event_notify_recharge error: {e}")


def _hqc_cloud_event_reply_recharge(msg_body_dict: dict):  # 账户充值应答消息
    result = msg_body_dict.get('result', -1)  # int
    reason = msg_body_dict.get('reason', -1)  # int
    try:
        info = {
            "result": result,
            "reason": reason
        }
    except Exception as e:
        HSyslog.log_error(f"_hqc_cloud_event_reply_recharge error: {e}")


def _hqc_cloud_event_notify_balance_query(msg_body_dict: dict):  # 账户余额查询消息
    gun_id = msg_body_dict.get('gun_id', -1)  # int
    account_type = msg_body_dict.get('account_type', -1)  # int
    account_content_len = msg_body_dict.get('account_content_len', -1)  # int
    account_content = msg_body_dict.get('account_content', -1)  # int
    try:
        info = {
            "gun_id": gun_id,
            "card_id": account_type[0:16],
            "random_id": account_type[16:],
            "phy_id": account_type,
        }
        HStategrid.Gun_list[gun_id].set_gun_charge({"total_cost": msg_body_dict.get('total_cost', -1)})
    except Exception as e:
        HSyslog.log_error(f"_hqc_cloud_event_notify_balance_query error: {e}")


def _hqc_cloud_event_reply_balance_query(msg_body_dict: dict):  # 账户余额查询结果消息
    gun_id = msg_body_dict.get('gun_id', -1)  # int
    account_type = msg_body_dict.get('account_type', -1)  # int
    balance = msg_body_dict.get('balance', -1)  # i
    try:
        info = {
            "gun_id": gun_id,
            "account_type": account_type,
            "balance": balance
        }
        topic = HHhdlist.topic_hqc_cloud_event_reply_balance_query
        app_publish(topic, info)
    except Exception as e:
        HSyslog.log_error(f"_hqc_cloud_event_reply_balance_query error: {e}")


def _hqc_cloud_event_notify_request_rate(msg_body_dict: dict):  # 充电系统费率请求消息
    count = msg_body_dict.get('count', -1)  # int
    items = msg_body_dict.get('items', [])  # array
    try:
        if items:
            fee_id = items[0].get("id")
            if fee_id == HStategrid.get_DeviceInfo("fee_model_id"):
                info = {
                    "result": 0
                }
            else:
                info = {
                    "result": 1
                }
        else:
            info = {
                "result": 1
            }
        _hqc_main_event_notify_update_rate(info)
        _hqc_cloud_event_reply_request_rate({})
    except Exception as e:
        HSyslog.log_error(f"_hqc_cloud_event_notify_request_rate error: {e}")


def _hqc_cloud_event_reply_request_rate(msg_body_dict: dict):  # 充电系统费率请求应答消息
    try:
        info = {
            "result": 0
        }
        topic = HHhdlist.topic_hqc_cloud_event_reply_request_rate
        app_publish(topic, info)
    except Exception as e:
        HSyslog.log_error(f"_hqc_cloud_event_reply_request_rate error: {e}")


def _hqc_cloud_event_notify_query_rate(msg_body_dict: dict):  # 充电系统费率查询消息
    try:
        info = {}
        topic = HHhdlist.topic_hqc_cloud_event_notify_query_rate
        app_publish(topic, info)
    except Exception as e:
        HSyslog.log_error(f"_hqc_cloud_event_notify_query_rate error: {e}")


def _hqc_cloud_event_reply_query_rate(msg_body_dict: dict):  # 充电系统费率查询结果消息
    count = msg_body_dict.get('count', -1)  # int
    items = msg_body_dict.get('items', [])  # array
    try:
        if items:
            info = {
                "fee_id": items[0].get("id")
            }
        else:
            info = {
                "fee_id": ""
            }
    except Exception as e:
        HSyslog.log_error(f"_hqc_cloud_event_reply_query_rate error: {e}")


def _hqc_cloud_event_notify_request_gunrate(msg_body_dict: dict):  # 充电枪费率请求消息
    gun_id = msg_body_dict.get("gun_id", -1)
    count = msg_body_dict.get('count', -1)  # int
    items = msg_body_dict.get('items', [])  # array
    try:
        if items:
            info = {
                "gun_id": gun_id,
                "fee_id": items[0].get("id")
            }
        else:
            info = {
                "gun_id": gun_id,
                "fee_id": ""
            }
        _hqc_cloud_event_reply_request_gunrate({"gun_id": gun_id})
    except Exception as e:
        HSyslog.log_error(f"_hqc_cloud_event_notify_request_gunrate error: {e}")


def _hqc_cloud_event_reply_request_gunrate(msg_body_dict: dict):  # 充电枪费率请求应答消息
    gun_id = msg_body_dict.get("gun_id", -1)
    try:
        info = {
            "gun_id": gun_id,
            "result": 0
        }
        topic = HHhdlist.topic_hqc_cloud_event_reply_request_gunrate
        app_publish(topic, info)
    except Exception as e:
        HSyslog.log_error(f"_hqc_cloud_event_reply_request_gunrate error: {e}")


def _hqc_cloud_event_notify_query_gunrate(msg_body_dict: dict):  # 充电枪费率查询消息
    gun_id = msg_body_dict.get("gun_id", -1)
    try:
        info = {
            "gun_id": gun_id,
        }
        topic = HHhdlist.topic_hqc_cloud_event_notify_query_gunrate
        app_publish(topic, info)
    except Exception as e:
        HSyslog.log_error(f"_hqc_cloud_event_notify_query_gunrate error: {e}")


def _hqc_cloud_event_reply_query_gunrate(msg_body_dict: dict):  # 充电枪费率查询结果消息
    gun_id = msg_body_dict.get("gun_id", -1)
    count = msg_body_dict.get('count', -1)  # int
    items = msg_body_dict.get('items', [])  # array
    try:
        if items:
            info = {
                "gun_id": gun_id,
                "fee_id": items[0].get("id")
            }
        else:
            info = {
                "gun_id": gun_id,
                "fee_id": ""
            }
    except Exception as e:
        HSyslog.log_error(f"_hqc_cloud_event_reply_query_gunrate error: {e}")


def _hqc_cloud_event_notify_request_startup(msg_body_dict: dict):  # 充电启动策略请求消息
    count = msg_body_dict.get('count', -1)  # int
    items = msg_body_dict.get('items', [])  # array
    try:
        if items:
            info = {
                "startup_id": items[0].get("id")
            }
        else:
            info = {
                "startup_id": ""
            }
        _hqc_cloud_event_reply_request_gunrate({})
    except Exception as e:
        HSyslog.log_error(f"_hqc_cloud_event_notify_request_startup error: {e}")


def _hqc_cloud_event_reply_request_startup(msg_body_dict: dict):  # 充电启动策略请求应答消息
    try:
        info = {
            "result": 0
        }
        topic = HHhdlist.topic_hqc_cloud_event_reply_request_startup
        app_publish(topic, info)
    except Exception as e:
        HSyslog.log_error(f"_hqc_cloud_event_reply_request_startup error: {e}")


def _hqc_cloud_event_notify_query_startup(msg_body_dict: dict):  # 充电启动策略查询消息
    try:
        info = {}
        topic = HHhdlist.topic_hqc_cloud_event_notify_query_startup
        app_publish(topic, info)
    except Exception as e:
        HSyslog.log_error(f"_hqc_cloud_event_notify_query_startup error: {e}")


def _hqc_cloud_event_reply_query_startup(msg_body_dict: dict):  # 充电启动策略查询结果消息
    count = msg_body_dict.get('count', -1)  # int
    items = msg_body_dict.get('items', [])  # array
    try:
        if items:
            info = {
                "startup_id": items[0].get("id")
            }
        else:
            info = {
                "startup_id": ""
            }
    except Exception as e:
        HSyslog.log_error(f"_hqc_cloud_event_reply_query_startup error: {e}")


def _hqc_cloud_event_notify_request_dispatch(msg_body_dict: dict):  # 功率分配策略请求消息
    count = msg_body_dict.get('count', -1)  # int
    items = msg_body_dict.get('items', [])  # array
    try:
        if items:
            info = {
                "dispatch_id": items[0].get("id")
            }
        else:
            info = {
                "dispatch_id": ""
            }
        _hqc_cloud_event_reply_request_dispatch({})
    except Exception as e:
        HSyslog.log_error(f"_hqc_cloud_event_notify_request_dispatch error: {e}")


def _hqc_cloud_event_reply_request_dispatch(msg_body_dict: dict):  # 功率分配策略请求应答消息
    try:
        info = {
            "result": 0
        }
        topic = HHhdlist.topic_hqc_cloud_event_reply_request_dispatch
        app_publish(topic, info)
    except Exception as e:
        HSyslog.log_error(f"_hqc_cloud_event_reply_request_dispatch error: {e}")


def _hqc_cloud_event_notify_query_dispatch(msg_body_dict: dict):  # 功率分配策略查询消息
    try:
        info = {}
        topic = HHhdlist.topic_hqc_cloud_event_notify_query_dispatch
        app_publish(topic, info)
    except Exception as e:
        HSyslog.log_error(f"_hqc_cloud_event_notify_query_dispatch error: {e}")


def _hqc_cloud_event_reply_query_dispatch(msg_body_dict: dict):  # 功率分配策略查询结果消息
    count = msg_body_dict.get('count', -1)  # int
    items = msg_body_dict.get('items', [])  # array
    try:
        if items:
            info = {
                "dispatch_id": items[0].get("id")
            }
        else:
            info = {
                "dispatch_id": ""
            }
    except Exception as e:
        HSyslog.log_error(f"_hqc_cloud_event_reply_query_dispatch error: {e}")


def _hqc_cloud_event_notify_request_offlinelist(msg_body_dict: dict):  # 离线名单版本请求消息
    count = msg_body_dict.get('count', -1)  # int
    items = msg_body_dict.get('items', [])  # array
    try:
        if items:
            offlinelist = {
                "offlinelist_id": items[0].get("id")
            }
        else:
            offlinelist = {
                "offlinelist_id": ""
            }
        _hqc_cloud_event_reply_request_offlinelist({})
    except Exception as e:
        HSyslog.log_error(f"_hqc_cloud_event_notify_request_offlinelist error: {e}")


def _hqc_cloud_event_reply_request_offlinelist(msg_body_dict: dict):  # 离线名单版本应答消息
    try:
        info = {
            "result": 0
        }
        topic = HHhdlist.topic_hqc_cloud_event_reply_request_offlinelist
        app_publish(topic, info)
    except Exception as e:
        HSyslog.log_error(f"_hqc_cloud_event_reply_request_offlinelist error: {e}")


def _hqc_main_event_notify_charge_session(msg_body_dict: dict):  # 充电会话消息
    gun_id = msg_body_dict.get('gun_id', -1)  # int
    cloud_session_id = msg_body_dict.get('cloud_session_id', '')  # string
    device_session_id = msg_body_dict.get('device_session_id', '')  # string
    user_id = msg_body_dict.get('user_id', '')  # string
    card_id = msg_body_dict.get('card_id', '')  # string
    connect_time = msg_body_dict.get('connect_time', -1)  # int
    start_charge_time = msg_body_dict.get('start_charge_time', -1)  # int
    start_meter_value = msg_body_dict.get('start_meter_value', -1)  # int
    start_soc = msg_body_dict.get('start_soc', -1)  # int
    start_source = msg_body_dict.get('start_source', -1)  # int
    stop_type = msg_body_dict.get('stop_type', -1)  # int
    stop_condition = msg_body_dict.get('stop_condition', -1)  # int
    offline_mode = msg_body_dict.get('offline_mode', -1)  # int
    charge_mode = msg_body_dict.get('charge_mode', -1)  # int
    main_gun = msg_body_dict.get('main_gun', -1)  # int

    try:
        if HStategrid.Gun_list[gun_id].get_gun_charge("charge_id") == cloud_session_id:
            HStategrid.Gun_list[gun_id].set_gun_status(HStategrid.Gun_Status.Charging.value)
            HStategrid.Gun_list[gun_id].set_gun_charge({"connect_time": connect_time})
            HStategrid.Gun_list[gun_id].set_gun_charge({"device_session_id": device_session_id})
            HStategrid.Gun_list[gun_id].set_gun_charge({"start_charge_time": start_charge_time})
            HStategrid.Gun_list[gun_id].set_gun_charge({"start_meter_value": start_meter_value})
            HStategrid.Gun_list[gun_id].set_gun_charge({"start_soc": start_soc})
            HStategrid.Gun_list[gun_id].set_gun_charge({"offline_mode": offline_mode})
            HStategrid.Gun_list[gun_id].set_gun_charge({"charge_mode": charge_mode})
            HStategrid.Gun_list[gun_id].set_gun_charge({"main_gun": main_gun})

            if HStategrid.Gun_list[gun_id].get_gun_charge("start_source") == start_source:
                info = {
                    "gun_id": gun_id,
                    "cmd_addr": HStategrid.Gun_Connect_Status.Start_Charge.value,
                    "addr_data": "0000",
                    "charge_id": cloud_session_id,
                }
                HHhdlist.device_platform_data.put([HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_108.value, info])
                info = {
                    "gun_id": gun_id,
                }
                HHhdlist.device_platform_data.put([HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_104.value, info])
                HHhdlist.device_platform_data.put([HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_304.value, info])
                HHhdlist.device_platform_data.put([HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_306.value, info])

            HStategrid.Gun_list[gun_id].gun_charge_session = True

        else:
            if main_gun == gun_id:
                pass
            else:
                if HStategrid.Gun_list[gun_id].get_gun_charge("device_session_id") == HStategrid.Gun_list[main_gun].get_gun_charge("device_session_id"):
                    HStategrid.Gun_list[gun_id].set_gun_status(HStategrid.Gun_Status.Charging.value)
                    HStategrid.Gun_list[gun_id].set_gun_charge({"connect_time": connect_time})
                    HStategrid.Gun_list[gun_id].set_gun_charge({"device_session_id": device_session_id})
                    HStategrid.Gun_list[gun_id].set_gun_charge({"start_charge_time": start_charge_time})
                    HStategrid.Gun_list[gun_id].set_gun_charge({"start_meter_value": start_meter_value})
                    HStategrid.Gun_list[gun_id].set_gun_charge({"start_soc": start_soc})
                    HStategrid.Gun_list[gun_id].set_gun_charge({"offline_mode": offline_mode})
                    HStategrid.Gun_list[gun_id].set_gun_charge({"charge_mode": charge_mode})
                    HStategrid.Gun_list[gun_id].set_gun_charge({"main_gun": main_gun})

                    if HStategrid.Gun_list[gun_id].get_gun_charge("start_source") == start_source:
                        info = {
                            "gun_id": gun_id,
                            "cmd_addr": HStategrid.Gun_Connect_Status.Start_Charge.value,
                            "addr_data": "0000",
                            "charge_id": cloud_session_id,
                        }
                        HHhdlist.device_platform_data.put([HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_108.value, info])
                        info = {
                            "gun_id": gun_id,
                        }
                        HHhdlist.device_platform_data.put([HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_104.value, info])
                        HHhdlist.device_platform_data.put([HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_304.value, info])
                        HHhdlist.device_platform_data.put([HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_306.value, info])

                    HStategrid.Gun_list[gun_id].gun_charge_session = True

        reply_charge_session_info = {
            "gun_id": gun_id,
        }
        _hqc_main_event_reply_charge_session(reply_charge_session_info)

        # for gun_info in HStategrid.Gun_list:
        #     HSyslog.log_info(f"{gun_info.gun_id}: {gun_info.get_gun_charge()}")
    except Exception as e:
        HSyslog.log_error(f"_hqc_cloud_event_reply_request_offlinelist error: {e}")


def _hqc_main_event_reply_charge_session(msg_body_dict: dict):  # 充电会话应答消息
    try:
        msg_body = {
            'result': 0x00
        }
        topic = HHhdlist.topic_hqc_main_event_reply_charge_session
        app_publish(topic, msg_body)
    except Exception as e:
        HSyslog.log_error(f"_hqc_main_event_reply_charge_session error: {e}")


def _hqc_main_event_notify_update_param(msg_body_dict: dict):  # 设置参数消息
    device_type = msg_body_dict.get("device_type", -1)
    param_list = msg_body_dict.get("param_list", [])
    device_num = msg_body_dict.get("gun_id", -1)
    try:
        topic = HHhdlist.topic_hqc_main_event_notify_update_param
        if device_type == HHhdlist.device_param_type.chargeSys.value:
            param_dict = {
                'device_type': device_type,
                'device_num': 0,
                'count': len(param_list),
                "source": 0,
                'items': []
            }
            for param in param_list:
                param_id = param.get("param_id")
                param_value = param.get("param_value")
                if isinstance(param_value, int):
                    param_dict['items'].append({"id": param_id, "type": 0, "intvalue": param.get("param_value")})
                    HStategrid.save_DeviceInfo(f"{device_type}0{param_id}", HStategrid.DB_Data_Type.DATA_INT.value, "", param_value)
                elif isinstance(param_value, bool):
                    param_dict['items'].append({"id": param_id, "type": 1, "boolvalue": param.get("param_value")})
                    HStategrid.save_DeviceInfo(f"{device_type}0{param_id}", HStategrid.DB_Data_Type.DATA_INT.value, "", param_value)
                elif isinstance(param_value, float):
                    param_dict['items'].append({"id": param_id, "type": 2, "floatvalue": param.get("param_value")})
                    HStategrid.save_DeviceInfo(f"{device_type}0{param_id}", HStategrid.DB_Data_Type.DATA_INT.value, "", param_value)
                elif isinstance(param_value, str):
                    param_dict['items'].append({"id": param_id, "type": 3, "strvalue": param.get("param_value")})
                    HStategrid.save_DeviceInfo(f"{device_type}0{param_id}", HStategrid.DB_Data_Type.DATA_STR.value, param_value, 0)
            app_publish(topic, param_dict)
            HHhdlist.write_param_is = False
        if device_type == HHhdlist.device_param_type.cabinet.value:
            if device_num == -1:
                for ccu_id in range(0, HStategrid.get_DeviceInfo("00122")):
                    param_dict = {
                        'device_type': device_type,
                        'device_num': ccu_id,
                        'count': len(param_list),
                        "source": 0,
                        'items': []
                    }
                    for param in param_list:
                        param_id = param.get("param_id")
                        param_value = param.get("param_value")
                        if isinstance(param_value, int):
                            param_dict['items'].append({"id": param_id, "type": 0, "intvalue": param.get("param_value")})
                            HStategrid.save_DeviceInfo(f"{device_type}0{param_id}", HStategrid.DB_Data_Type.DATA_INT.value, "", param_value)
                        elif isinstance(param_value, bool):
                            param_dict['items'].append({"id": param_id, "type": 1, "boolvalue": param.get("param_value")})
                            HStategrid.save_DeviceInfo(f"{device_type}0{param_id}", HStategrid.DB_Data_Type.DATA_INT.value, "", param_value)
                        elif isinstance(param_value, float):
                            param_dict['items'].append({"id": param_id, "type": 2, "floatvalue": param.get("param_value")})
                            HStategrid.save_DeviceInfo(f"{device_type}0{param_id}", HStategrid.DB_Data_Type.DATA_INT.value, "", param_value)
                        elif isinstance(param_value, str):
                            param_dict['items'].append({"id": param_id, "type": 3, "strvalue": param.get("param_value")})
                            HStategrid.save_DeviceInfo(f"{device_type}0{param_id}", HStategrid.DB_Data_Type.DATA_STR.value, param_value, 0)
                    app_publish(topic, param_dict)
                    HHhdlist.write_param_is = False
            else:
                param_dict = {
                    'device_type': device_type,
                    'device_num': device_num,
                    'count': len(param_list),
                    "source": 0,
                    'items': []
                }
                for param in param_list:
                    param_id = param.get("param_id")
                    param_value = param.get("param_value")
                    if isinstance(param_value, int):
                        param_dict['items'].append({"id": param_id, "type": 0, "intvalue": param.get("param_value")})
                        HStategrid.save_DeviceInfo(f"{device_type}0{param_id}", HStategrid.DB_Data_Type.DATA_INT.value, "", param_value)
                    elif isinstance(param_value, bool):
                        param_dict['items'].append({"id": param_id, "type": 1, "boolvalue": param.get("param_value")})
                        HStategrid.save_DeviceInfo(f"{device_type}0{param_id}", HStategrid.DB_Data_Type.DATA_INT.value, "", param_value)
                    elif isinstance(param_value, float):
                        param_dict['items'].append({"id": param_id, "type": 2, "floatvalue": param.get("param_value")})
                        HStategrid.save_DeviceInfo(f"{device_type}0{param_id}", HStategrid.DB_Data_Type.DATA_INT.value, "", param_value)
                    elif isinstance(param_value, str):
                        param_dict['items'].append({"id": param_id, "type": 3, "strvalue": param.get("param_value")})
                        HStategrid.save_DeviceInfo(f"{device_type}0{param_id}", HStategrid.DB_Data_Type.DATA_STR.value, param_value, 0)
                app_publish(topic, param_dict)
                HHhdlist.write_param_is = False
        if device_type == HHhdlist.device_param_type.gun.value:
            if device_num == -1:
                for gun_info in HStategrid.Gun_list:
                    param_dict = {
                        'device_type': device_type,
                        'device_num': gun_info.gun_id,
                        'count': len(param_list),
                        "source": 0,
                        'items': []
                    }
                    for param in param_list:
                        param_id = param.get("param_id")
                        param_value = param.get("param_value")
                        if isinstance(param_value, int):
                            param_dict['items'].append({"id": param_id, "type": 0, "intvalue": param.get("param_value")})
                            HStategrid.save_DeviceInfo(f"{device_type}0{param_id}", HStategrid.DB_Data_Type.DATA_INT.value, "", param_value)
                        elif isinstance(param_value, bool):
                            param_dict['items'].append({"id": param_id, "type": 1, "boolvalue": param.get("param_value")})
                            HStategrid.save_DeviceInfo(f"{device_type}0{param_id}", HStategrid.DB_Data_Type.DATA_INT.value, "", param_value)
                        elif isinstance(param_value, float):
                            param_dict['items'].append({"id": param_id, "type": 2, "floatvalue": param.get("param_value")})
                            HStategrid.save_DeviceInfo(f"{device_type}0{param_id}", HStategrid.DB_Data_Type.DATA_INT.value, "", param_value)
                        elif isinstance(param_value, str):
                            param_dict['items'].append({"id": param_id, "type": 3, "strvalue": param.get("param_value")})
                            HStategrid.save_DeviceInfo(f"{device_type}0{param_id}", HStategrid.DB_Data_Type.DATA_STR.value, param_value, 0)
                    app_publish(topic, param_dict)
                    HHhdlist.write_param_is = False
            else:
                param_dict = {
                    'device_type': device_type,
                    'device_num': device_num,
                    'count': len(param_list),
                    "source": 0,
                    'items': []
                }
                for param in param_list:
                    param_id = param.get("param_id")
                    param_value = param.get("param_value")
                    if isinstance(param_value, int):
                        param_dict['items'].append({"id": param_id, "type": 0, "intvalue": param.get("param_value")})
                        HStategrid.save_DeviceInfo(f"{device_type}0{param_id}", HStategrid.DB_Data_Type.DATA_INT.value, "", param_value)
                    elif isinstance(param_value, bool):
                        param_dict['items'].append({"id": param_id, "type": 1, "boolvalue": param.get("param_value")})
                        HStategrid.save_DeviceInfo(f"{device_type}0{param_id}", HStategrid.DB_Data_Type.DATA_INT.value, "", param_value)
                    elif isinstance(param_value, float):
                        param_dict['items'].append({"id": param_id, "type": 2, "floatvalue": param.get("param_value")})
                        HStategrid.save_DeviceInfo(f"{device_type}0{param_id}", HStategrid.DB_Data_Type.DATA_INT.value, "", param_value)
                    elif isinstance(param_value, str):
                        param_dict['items'].append({"id": param_id, "type": 3, "strvalue": param.get("param_value")})
                        HStategrid.save_DeviceInfo(f"{device_type}0{param_id}", HStategrid.DB_Data_Type.DATA_STR.value, param_value, 0)
                app_publish(topic, param_dict)
                HHhdlist.write_param_is = False
        if device_type == HHhdlist.device_param_type.parkLock.value:
            if device_num == -1:
                for gun_info in HStategrid.Gun_list:
                    param_dict = {
                        'device_type': device_type,
                        'device_num': gun_info.gun_id,
                        'count': len(param_list),
                        "source": 0,
                        'items': []
                    }
                    for param in param_list:
                        param_id = param.get("param_id")
                        param_value = param.get("param_value")
                        if isinstance(param_value, int):
                            param_dict['items'].append({"id": param_id, "type": 0, "intvalue": param.get("param_value")})
                            HStategrid.save_DeviceInfo(f"{device_type}0{param_id}", HStategrid.DB_Data_Type.DATA_INT.value, "", param_value)
                        elif isinstance(param_value, bool):
                            param_dict['items'].append({"id": param_id, "type": 1, "boolvalue": param.get("param_value")})
                            HStategrid.save_DeviceInfo(f"{device_type}0{param_id}", HStategrid.DB_Data_Type.DATA_INT.value, "", param_value)
                        elif isinstance(param_value, float):
                            param_dict['items'].append({"id": param_id, "type": 2, "floatvalue": param.get("param_value")})
                            HStategrid.save_DeviceInfo(f"{device_type}0{param_id}", HStategrid.DB_Data_Type.DATA_INT.value, "", param_value)
                        elif isinstance(param_value, str):
                            param_dict['items'].append({"id": param_id, "type": 3, "strvalue": param.get("param_value")})
                            HStategrid.save_DeviceInfo(f"{device_type}0{param_id}", HStategrid.DB_Data_Type.DATA_STR.value, param_value, 0)
                    app_publish(topic, param_dict)
                    HHhdlist.write_param_is = False
            else:
                param_dict = {
                    'device_type': device_type,
                    'device_num': device_num,
                    'count': len(param_list),
                    "source": 0,
                    'items': []
                }
                for param in param_list:
                    param_id = param.get("param_id")
                    param_value = param.get("param_value")
                    if isinstance(param_value, int):
                        param_dict['items'].append({"id": param_id, "type": 0, "intvalue": param.get("param_value")})
                        HStategrid.save_DeviceInfo(f"{device_type}0{param_id}", HStategrid.DB_Data_Type.DATA_INT.value, "", param_value)
                    elif isinstance(param_value, bool):
                        param_dict['items'].append({"id": param_id, "type": 1, "boolvalue": param.get("param_value")})
                        HStategrid.save_DeviceInfo(f"{device_type}0{param_id}", HStategrid.DB_Data_Type.DATA_INT.value, "", param_value)
                    elif isinstance(param_value, float):
                        param_dict['items'].append({"id": param_id, "type": 2, "floatvalue": param.get("param_value")})
                        HStategrid.save_DeviceInfo(f"{device_type}0{param_id}", HStategrid.DB_Data_Type.DATA_INT.value, "", param_value)
                    elif isinstance(param_value, str):
                        param_dict['items'].append({"id": param_id, "type": 3, "strvalue": param.get("param_value")})
                        HStategrid.save_DeviceInfo(f"{device_type}0{param_id}", HStategrid.DB_Data_Type.DATA_STR.value, param_value, 0)
                app_publish(topic, param_dict)
                HHhdlist.write_param_is = False
    except Exception as e:
        HSyslog.log_error(f"_hqc_main_event_notify_update_param error: {e}")


def _hqc_main_event_reply_update_param(msg_body_dict: dict):  # 设置参数应答消息
    device_type = msg_body_dict.get("device_type")
    device_num = msg_body_dict.get("device_num")
    source = msg_body_dict.get("source")
    count = msg_body_dict.get("count")
    valid_id = msg_body_dict.get("valid_id")
    invalid_id = msg_body_dict.get("invalid_id")
    try:
        HHhdlist.write_param_is = True
    except Exception as e:
        HSyslog.log_error(f"_hqc_main_event_reply_update_param error: {e}")


def _hqc_main_event_notify_update_qrcode(msg_body_dict: dict):  # 二维码更新消息
    gun_id = msg_body_dict.get("gun_id", [])
    qrcode = msg_body_dict.get("qrcode", [])

    try:
        if isinstance(qrcode, list) and isinstance(gun_id, list):
            if len(gun_id) == len(qrcode):
                for gun in range(0, len(gun_id)):
                    info = {
                        "gun_id": gun_id[gun],
                        "source": gun_id[gun],
                        "content": qrcode[gun]
                    }
                    topic = HHhdlist.topic_hqc_main_event_notify_update_qrcode
                    app_publish(topic, info)
            else:
                HSyslog.log_info(f"gun_id != qrcode error: {gun_id}--{qrcode}")
        elif isinstance(qrcode, str) and isinstance(gun_id, int):
            info = {
                "gun_id": gun_id,
                "source": gun_id,
                "content": qrcode
            }
            topic = HHhdlist.topic_hqc_main_event_notify_update_qrcode
            app_publish(topic, info)
        else:
            HSyslog.log_info(f"gun_id != qrcode error: {gun_id}--{qrcode}")
    except Exception as e:
        HSyslog.log_error(f"_hqc_main_event_notify_update_qrcode error: {e}")


def _hqc_main_event_reply_update_qrcode(msg_body_dict: dict):  # 二维码更新应答消息
    gun_id = msg_body_dict.get('gun_id', -1)  # int
    source = msg_body_dict.get('source', -1)  # int
    result = msg_body_dict.get('result', -1)  # int
    reason = msg_body_dict.get('reason', -1)  # int
    try:
        info = {
            "gun_id": gun_id,
            "result": result,
            "reason": reason
        }
    except Exception as e:
        HSyslog.log_error(f"_hqc_main_event_reply_update_qrcode error: {e}")


def _hqc_main_event_notify_reserve_count_down(msg_body_dict: dict):  # 预约延时启动倒计时消息
    gun_id = msg_body_dict.get('gun_id', -1)  # int
    command_type = msg_body_dict.get('command_type', -1)  # int
    remain_time = msg_body_dict.get('remain_time', -1)  # int
    try:
        info = {
            "gun_id": gun_id,
            "command_type": command_type,
            "remain_time": remain_time
        }
        topic = HHhdlist.topic_hqc_main_event_notify_reserve_count_down
        app_publish(topic, info)
    except Exception as e:
        HSyslog.log_error(f"_hqc_main_event_notify_reserve_count_down error: {e}")


def _hqc_cloud_event_notify_m1_secret(msg_body_dict: dict):  # M1卡密钥更新消息
    secret_key = msg_body_dict.get('secret_key', "")  # int
    try:
        info = {
            "secret_key": secret_key,
        }
        topic = HHhdlist.topic_hqc_cloud_event_notify_m1_secret
        app_publish(topic, info)
    except Exception as e:
        HSyslog.log_error(f"_hqc_cloud_event_notify_m1_secret error: {e}")


def _hqc_cloud_event_reply_m1_secret(msg_body_dict: dict):  # M1卡密钥更新结果消息
    result = msg_body_dict.get('result', -1)  # int
    try:
        info = {
            "result": result,
        }
    except Exception as e:
        HSyslog.log_error(f"_hqc_cloud_event_reply_m1_secret error: {e}")


def _hqc_cloud_event_notify_pos_pre_transaction(msg_body_dict: dict):  # POS机预交易信息消息
    gun_id = msg_body_dict.get('gun_id', -1)  # int
    credit_card = msg_body_dict.get('credit_card', "")  # int
    pos_transaction_id = msg_body_dict.get('pos_transaction_id', "")  # int
    pos_transaction_data = msg_body_dict.get('pos_transaction_data', "")  # int
    try:
        info = {
            "gun_id": gun_id,
            "credit_card": credit_card,
            "pos_transaction_id": pos_transaction_id,
            "pos_transaction_data": pos_transaction_data,
        }
        topic = HHhdlist.topic_hqc_cloud_event_notify_pos_pre_transaction
        app_publish(topic, info)
    except Exception as e:
        HSyslog.log_error(f"_hqc_cloud_event_notify_pos_pre_transaction error: {e}")


def _hqc_cloud_event_notify_pos_charge_cost(msg_body_dict: dict):  # POS机扣费消息
    gun_id = msg_body_dict.get('gun_id', -1)  # int
    total_cost = msg_body_dict.get('total_cost', -1)  # int
    pos_transaction_id = msg_body_dict.get('pos_transaction_id', "")  # int
    pos_transaction_data = msg_body_dict.get('pos_transaction_data', "")  # in
    try:
        info = {
            "gun_id": gun_id,
            "total_cost": total_cost,
            "pos_transaction_id": pos_transaction_id,
            "pos_transaction_data": pos_transaction_data,
        }
    except Exception as e:
        HSyslog.log_error(f"_hqc_cloud_event_notify_pos_charge_cost error: {e}")


def _hqc_cloud_event_reply_pos_charge_cost(msg_body_dict: dict):  # POS机扣费结果消息
    gun_id = msg_body_dict.get('gun_id', -1)  # int
    result = msg_body_dict.get('result', -1)  # int
    pos_transaction_id = msg_body_dict.get('pos_transaction_id', "")  # int
    try:
        info = {
            "gun_id": gun_id,
            "result": result,
            "pos_transaction_id": pos_transaction_id,
        }
        topic = HHhdlist.topic_hqc_cloud_event_reply_pos_charge_cost
        app_publish(topic, info)
    except Exception as e:
        HSyslog.log_error(f"_hqc_cloud_event_reply_pos_charge_cost error: {e}")


def _hqc_cloud_event_notify_update_charge_order_id(msg_body_dict: dict):  # 充电订单ID更新消息
    gun_id = msg_body_dict.get('gun_id', -1)  # int
    device_session_id = msg_body_dict.get('device_session_id', -1)  # int
    cloud_session_id = msg_body_dict.get('cloud_session_id', "")  # int
    try:
        info = {
            "gun_id": gun_id,
            "device_session_id": device_session_id,
            "cloud_session_id": cloud_session_id,
        }
        topic = HHhdlist.topic_hqc_cloud_event_notify_update_charge_order_id
        app_publish(topic, info)
    except Exception as e:
        HSyslog.log_error(f"_hqc_cloud_event_notify_update_charge_order_id error: {e}")


def _hqc_cloud_event_reply_update_charge_order_id(msg_body_dict: dict):  # 充电订单ID更新结果消息
    gun_id = msg_body_dict.get('gun_id', -1)  # int
    device_session_id = msg_body_dict.get('device_session_id', -1)  # int
    result = msg_body_dict.get('result', "")  # int
    try:
        info = {
            "gun_id": gun_id,
            "device_session_id": device_session_id,
            "result": result,
        }
    except Exception as e:
        HSyslog.log_error(f"_hqc_cloud_event_reply_update_charge_order_id error: {e}")


def _hqc_main_event_notify_update_rate(msg_body_dict: dict):  # 充电系统费率同步消息
    fee_model_id = msg_body_dict.get("fee_model_id", "")
    contents = msg_body_dict.get("contents", [])

    result = msg_body_dict.get("result", -1)
    try:
        if contents and result == -1:
            info = {
                "type": 1,  # 1:全量下发
                "count": 1,  # [0-8]
                "items": [],
            }
            info_items = {
                "num": 1,  # 从1开始
                "id": str(fee_model_id),
                "count": len(contents),  # [1-16]
                "contents": contents,
                "commencement_date": HStategrid.get_datetime_timestamp(),
                "last_updated": HStategrid.get_datetime_timestamp(),
                "charge_type": 0,
            }
            info["items"].append(info_items)
            topic = HHhdlist.topic_hqc_main_event_notify_update_rate
            app_publish(topic, info)
        elif result != -1 and result == 1:
            contents = HStategrid.get_FeeModel()
            if contents:
                info = {
                    "type": 1,  # 1:全量下发
                    "count": 1,  # [0-8]
                    "items": [],
                }
                info_items = {
                    "num": 1,  # 从1开始
                    "id": str(fee_model_id),
                    "count": len(contents),  # [1-16]
                    "contents": contents,
                    "commencement_date": HStategrid.get_datetime_timestamp(),
                    "last_updated": HStategrid.get_datetime_timestamp(),
                    "charge_type": 0,
                }
                info["items"].append(info_items)
                topic = HHhdlist.topic_hqc_main_event_notify_update_rate
                app_publish(topic, info)
        else:
            pass
    except Exception as e:
        HSyslog.log_error(f"_hqc_main_event_notify_update_rate error: {e}")


def _hqc_main_event_reply_update_rate(msg_body_dict: dict):  # 充电系统费率同步应答消息
    id = msg_body_dict.get('id', '')  # string
    result = msg_body_dict.get('result', -1)  # int
    reason = msg_body_dict.get('reason', -1)  # int
    try:
        info = {
            "fee_id": id,
            "result": result,
            "reason": reason,
        }
        HHhdlist.device_platform_data.put([HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_1310.value, info])
        # if id == HStategrid.get_DeviceInfo("fee_model_id") and result == 0x01:
        #     _hqc_main_event_notify_update_rate(info)
        # elif id != HStategrid.get_DeviceInfo("fee_model_id"):
        #     pass
        # else:
        #     pass
    except Exception as e:
        HSyslog.log_error(f"_hqc_main_event_reply_update_rate error: {e}")


def _hqc_main_event_notify_update_gunrate(msg_body_dict: dict):  # 充电枪费率同步消息
    gun_id = msg_body_dict.get("gun_id")
    gun_fee_id = msg_body_dict.get("fee_model_id")
    list_items = msg_body_dict.get("contents")

    result = msg_body_dict.get("result", -1)
    try:
        if list_items and result == -1:
            info_items = {
                "num": 1,  # 从1开始
                "id": str(gun_fee_id),
                "count": len(list_items),  # [1-16]
                "contents": list_items,
                "commencement_date": HStategrid.get_datetime_timestamp(),
                "last_updated": HStategrid.get_datetime_timestamp(),
                "charge_type": 0,
            }
            info = {
                "gun_id": gun_id,
                "type": 1,
                "count": len(list_items),
                "items": info_items,
            }
            topic = HHhdlist.topic_hqc_main_event_notify_update_gunrate
            app_publish(topic, info)
        elif result != -1:
            list_items = HStategrid.get_FeeModel()
            if list_items:
                info_items = {
                    "num": 1,  # 从1开始
                    "id": str(gun_fee_id),
                    "count": len(list_items),  # [1-16]
                    "contents": list_items,
                    "commencement_date": HStategrid.get_datetime_timestamp(),
                    "last_updated": HStategrid.get_datetime_timestamp(),
                    "charge_type": 0,
                }
                info = {
                    "gun_id": gun_id,
                    "type": 1,
                    "count": len(list_items),
                    "items": info_items,
                }
                topic = HHhdlist.topic_hqc_main_event_notify_update_gunrate
                app_publish(topic, info)
        else:
            pass
    except Exception as e:
        HSyslog.log_error(f"_hqc_main_event_notify_update_gunrate error: {e}")


def _hqc_main_event_reply_update_gunrate(msg_body_dict: dict):  # 充电枪费率同步应答消息
    gun_id = msg_body_dict.get('gun_id', '')  # string
    id = msg_body_dict.get('id', -1)  # int
    result = msg_body_dict.get('result', -1)  # int
    reason = msg_body_dict.get('reason', -1)  # int
    try:
        info = {
            "gun_id": gun_id,
            "id": id,
            "result": result,
            "reason": reason,
        }
        if id == HStategrid.get_DeviceInfo("gun_fee_id") and result == 0x01:
            _hqc_main_event_notify_update_gunrate(info)
        elif id != HStategrid.get_DeviceInfo("gun_fee_if"):
            _hqc_main_event_notify_update_gunrate(info)
        else:
            pass
    except Exception as e:
        HSyslog.log_error(f"_hqc_main_event_reply_update_gunrate error: {e}")


def _hqc_main_event_notify_update_startup(msg_body_dict: dict):  # 充电启动策略同步消息
    command_type = msg_body_dict.get("command_type")
    list_items = msg_body_dict.get("list_items")
    try:
        if list_items:
            info = {
                "type": command_type,
                "count": len(list_items),
                "items": list_items,
            }
            topic = HHhdlist.topic_hqc_main_event_notify_update_startup
            app_publish(topic, info)
    except Exception as e:
        HSyslog.log_error(f"_hqc_main_event_notify_update_startup error: {e}")


def _hqc_main_event_reply_update_startup(msg_body_dict: dict):  # 充电启动策略同步应答消息
    id = msg_body_dict.get('id', '')  # string
    last_updated = msg_body_dict.get('last_updated', -1)  # int
    result = msg_body_dict.get('result', -1)  # int
    reason = msg_body_dict.get('reason', -1)  # int
    try:
        info = {
            "id": id,
            "result": result,
            "reason": reason,
        }
    except Exception as e:
        HSyslog.log_error(f"_hqc_main_event_reply_update_startup error: {e}")


def _hqc_main_event_notify_update_dispatch(msg_body_dict: dict):  # 功率分配策略同步消息
    command_type = msg_body_dict.get("command_type")
    list_items = msg_body_dict.get("list_items")
    try:
        if list_items:
            info = {
                "type": command_type,
                "count": len(list_items),
                "items": list_items,
            }
            topic = HHhdlist.topic_hqc_main_event_notify_update_dispatch
            app_publish(topic, info)
    except Exception as e:
        HSyslog.log_error(f"_hqc_main_event_notify_update_dispatch error: {e}")


def _hqc_main_event_reply_update_dispatch(msg_body_dict: dict):  # 功率分配策略同步应答消息
    id = msg_body_dict.get('id', '')  # string
    last_updated = msg_body_dict.get('last_updated', -1)  # int
    result = msg_body_dict.get('result', -1)  # int
    reason = msg_body_dict.get('reason', -1)  # int
    try:
        info = {
            "id": id,
            "result": result,
            "reason": reason,
        }
    except Exception as e:
        HSyslog.log_error(f"_hqc_main_event_reply_update_dispatch error: {e}")


def _hqc_main_event_notify_update_offlinelist(msg_body_dict: dict):  # 离线名单版本同步消息
    command_type = msg_body_dict.get("command_type")
    list_items = msg_body_dict.get("list_items")
    try:
        if list_items:
            info = {
                "type": command_type,
                "count": len(list_items),
                "items": list_items,
            }
            topic = HHhdlist.topic_hqc_main_event_notify_update_offlinelist
            app_publish(topic, info)
    except Exception as e:
        HSyslog.log_error(f"_hqc_main_event_notify_update_offlinelist error: {e}")


def _hqc_main_event_reply_update_offflinelist(msg_body_dict: dict):  # 离线名单版本同步应答消息
    result = msg_body_dict.get('result', -1)  # int
    reason = msg_body_dict.get('reason', -1)  # int
    try:
        info = {
            "result": result,
            "reason": reason,
        }
    except Exception as e:
        HSyslog.log_error(f"_hqc_main_event_reply_update_offflinelist error: {e}")


def _hqc_main_event_notify_offlinelist_log(msg_body_dict: dict):  # 离线名单项操作日志消息
    list_id = msg_body_dict.get("id")
    list_items = msg_body_dict.get("list_items")
    try:
        if list_items:
            info = {
                "id": list_id,
                "count": len(list_items),
                "items": list_items,
            }
            topic = HHhdlist.topic_hqc_main_event_notify_offlinelist_log
            app_publish(topic, info)
    except Exception as e:
        HSyslog.log_error(f"_hqc_main_event_notify_offlinelist_log error: {e}")


def _hqc_main_event_reply_offlinelist_log(msg_body_dict: dict):  # 离线名单项操作日志应答消息
    id = msg_body_dict.get('id', '')  # string
    type = msg_body_dict.get('type', -1)  # int
    version = msg_body_dict.get('version', -1)  # int
    result = msg_body_dict.get('result', -1)  # int
    reason = msg_body_dict.get('reason', -1)  # int
    try:
        info = {
            "list_id": id,
            "result": result,
            "reason": reason,
        }
    except Exception as e:
        HSyslog.log_error(f"_hqc_main_event_reply_offlinelist_log error: {e}")


def _hqc_main_event_notify_clear(msg_body_dict: dict):  # 清除故障、事件消息
    command_type = msg_body_dict.get("type")
    try:
        info = {
            "type": command_type,
        }
        topic = HHhdlist.topic_hqc_main_event_notify_clear
        app_publish(topic, info)
    except Exception as e:
        HSyslog.log_error(f"_hqc_main_event_notify_clear error: {e}")


def _hqc_main_event_reply_clear(msg_body_dict: dict):  # 清除故障、事件应答消息
    type = msg_body_dict.get('type', -1)  # int
    result = msg_body_dict.get('result', -1)  # int
    try:
        info = {
            "command_type": type,
            "result": result,
        }
    except Exception as e:
        HSyslog.log_error(f"_hqc_main_event_reply_clear error: {e}")


def _hqc_sys_upgrade_notify_notify(msg_body_dict: dict):  # 升级控制消息
    device_type = msg_body_dict.get("device_type")
    device_id = msg_body_dict.get("device_id")
    command = msg_body_dict.get("command")
    soft_version = msg_body_dict.get("soft_version")
    hard_version = msg_body_dict.get("hard_version")
    location = msg_body_dict.get("location")
    try:
        info = {
            "mode": 0,
            "type": device_type,
            "device_id": device_id,
            "command": command,
            "auto_exit": 1,
            "soft_version": soft_version,
            "hard_version": hard_version,
            "location": location,
        }
        topic = HHhdlist.topic_hqc_sys_upgrade_notify_notify
        app_publish(topic, info)
    except Exception as e:
        HSyslog.log_error(f"_hqc_sys_upgrade_notify_notify error: {e}")


def _hqc_sys_upgrade_reply_notify(msg_body_dict: dict):  # 升级控制应答消息
    type = msg_body_dict.get('type', -1)  # int
    device_id = msg_body_dict.get('device_id', -1)  # int
    command = msg_body_dict.get('command', -1)  # int
    result = msg_body_dict.get('result', -1)  # int
    try:
        info = {
            "device_type": type,
            "device_id": device_id,
            "result": result,
        }
    except Exception as e:
        HSyslog.log_error(f"_hqc_sys_upgrade_reply_notify error: {e}")


def _hqc_sys_upgrade_notify_process(msg_body_dict: dict):  # 升级进度消息
    type = msg_body_dict.get('type', -1)  # int
    device_id = msg_body_dict.get('device_id', -1)  # int
    process = msg_body_dict.get('process', -1)  # int
    try:
        info = {
            "device_type": type,
            "device_id": device_id,
            "process": process,
        }
    except Exception as e:
        HSyslog.log_error(f"_hqc_sys_upgrade_notify_process error: {e}")


def _hqc_sys_upgrade_notify_result(msg_body_dict: dict):  # 升级结果消息
    type = msg_body_dict.get('type', -1)  # int
    device_id = msg_body_dict.get('device_id', -1)  # int
    result = msg_body_dict.get('result', -1)  # int
    try:
        info = {
            "device_type": type,
            "device_id": device_id,
            "result": result,
        }
    except Exception as e:
        HSyslog.log_error(f"_hqc_sys_upgrade_notify_result error: {e}")


def _hqc_sys_upload_notify_notify(msg_body_dict: dict):  # 日志文件上传请求消息
    file_type = msg_body_dict.get('type', -1)  # int
    device_type = msg_body_dict.get('device_id', -1)  # int
    device_id = msg_body_dict.get('process', -1)  # int
    file_name = msg_body_dict.get('type', -1)  # int
    file_len = msg_body_dict.get('device_id', -1)  # int
    crc32_value = msg_body_dict.get('process', -1)  # int
    try:
        pass
    except Exception as e:
        HSyslog.log_error(f"_hqc_sys_upload_notify_notify error: {e}")


def _hqc_sys_upload_reply_notify(msg_body_dict: dict):  # 日志文件上传请求应答消息
    result = msg_body_dict.get('result', -1)  # int
    try:
        info = {
            "allow": result,
        }
        topic = HHhdlist.topic_hqc_sys_upload_reply_notify
        app_publish(topic, info)
    except Exception as e:
        HSyslog.log_error(f"_hqc_sys_upload_reply_notify error: {e}")


def _hqc_sys_upgrade_notify_version(msg_body_dict: dict):  # 读取版本号消息
    device_type_list = msg_body_dict.get("device_type", [])
    try:
        for device_type in device_type_list:
            info = {
                "type": device_type,
                "device_id": 255
            }
            topic = HHhdlist.topic_hqc_sys_upgrade_notify_version
            app_publish(topic, info)
    except Exception as e:
        HSyslog.log_error(f"_hqc_sys_upgrade_notify_version error: {e}")


def _hqc_sys_upgrade_reply_version(msg_body_dict: dict):  # 读取版本号应答消息
    type = msg_body_dict.get('type', -1)  # int
    device_id = msg_body_dict.get('device_id', -1)  # int
    soft_version = msg_body_dict.get('soft_version', [])  # string
    hard_version = msg_body_dict.get('hard_version', [])  # string
    try:
        if type == HHhdlist.device_ctrl_type.DTU.value:
            if hard_version[0] != "" and soft_version[0] != "":
                HStategrid.save_VerInfoEvt(device_id, 4, hard_version[0], soft_version[0])
        if type == HHhdlist.device_ctrl_type.TIU.value:
            if hard_version[0] != "" and soft_version[0] != "":
                HStategrid.save_VerInfoEvt(device_id, 0, hard_version[0], soft_version[0])
        if type == HHhdlist.device_ctrl_type.CCU.value:
            if hard_version[0] != "" and soft_version[0] != "":
                HStategrid.save_VerInfoEvt(device_id, 3, hard_version[0], soft_version[0])
        if type == HHhdlist.device_ctrl_type.GCU.value:
            if hard_version[0] != "" and soft_version[0] != "":
                HStategrid.save_VerInfoEvt(device_id, 1, hard_version[0], soft_version[0])
        if type == HHhdlist.device_ctrl_type.PDU.value:
            if hard_version[0] != "" and soft_version[0] != "":
                HStategrid.save_VerInfoEvt(device_id, 2, hard_version[0], soft_version[0])
    except Exception as e:
        HSyslog.log_error(f"_hqc_sys_upgrade_reply_version error: {e}")


def _hqc_sys_upgrade_notify_control_command(msg_body_dict: dict):  # 远程控制命令消息
    device_type = msg_body_dict.get('device_type', -1)  # int
    try:
        info = {
            "type": device_type,
            "device_id": 0xFF,
            "command": 0,
        }
        topic = HHhdlist.topic_hqc_sys_upgrade_notify_control_command
        app_publish(topic, info)
    except Exception as e:
        HSyslog.log_error(f"_hqc_sys_upgrade_notify_control_command error: {e}")


def _hqc_sys_upgrade_reply_control_command(msg_body_dict: dict):  # 远程控制命令应答消息
    type = msg_body_dict.get('type', -1)  # int
    device_id = msg_body_dict.get('device_id', -1)  # int
    command = msg_body_dict.get('command', -1)  # int
    result = msg_body_dict.get('result', -1)  # int
    try:
        info = {
            "device_type": type,
            "command": command,
            "result": result
        }
    except Exception as e:
        HSyslog.log_error(f"_hqc_sys_upgrade_reply_control_command error: {e}")


def _hqc_main_event_notify_read_param(msg_body_dict: dict):  # 参数读取消息
    param_list = msg_body_dict.get("param_list")
    device_type = msg_body_dict.get("device_type")
    device_num = msg_body_dict.get("device_num", -1)
    try:
        topic = HHhdlist.topic_hqc_main_event_notify_read_param
        if device_type == HHhdlist.device_param_type.chargeSys.value:
            info = {
                "device_type": device_type,
                "device_num": 0,
                "source": 0,
                "model": 0,
                "count": len(param_list),
                "param_id": param_list,
            }
            app_publish(topic, info)
            HHhdlist.read_param_is = False
        if device_type == HHhdlist.device_param_type.cabinet.value:
            if device_num == -1:
                for ccu_id in range(0, HStategrid.get_DeviceInfo("00122")):
                    info = {
                        'device_type': device_type,
                        'device_num': ccu_id,
                        "source": 0,
                        "model": 0,
                        'count': len(param_list),
                        "param_id": param_list,
                    }
                    app_publish(topic, info)
                    HHhdlist.read_param_is = False
            else:
                info = {
                    'device_type': device_type,
                    'device_num': device_num,
                    "source": 0,
                    "model": 0,
                    'count': len(param_list),
                    "param_id": param_list,
                }
                app_publish(topic, info)
                HHhdlist.read_param_is = False
        if device_type == HHhdlist.device_param_type.gun.value:
            if device_num == -1:
                for gun_id in range(0, HStategrid.get_DeviceInfo("00110")):
                    info = {
                        'device_type': device_type,
                        'device_num': gun_id,
                        "source": 0,
                        "model": 0,
                        'count': len(param_list),
                        "param_id": param_list,
                    }
                    app_publish(topic, info)
                    HHhdlist.read_param_is = False
            else:
                info = {
                    'device_type': device_type,
                    'device_num': device_num,
                    "source": 0,
                    "model": 0,
                    'count': len(param_list),
                    "param_id": param_list,
                }
                app_publish(topic, info)
                HHhdlist.read_param_is = False
    except Exception as e:
        HSyslog.log_error(f"_hqc_main_event_notify_read_param error: {e}")


def _hqc_main_event_reply_read_param(msg_body_dict: dict):  # 参数读取应答消息
    device_type = msg_body_dict.get('device_type', -1)  # int
    device_num = msg_body_dict.get('device_num', -1)  # int
    invalid_id = msg_body_dict.get('device_num', [])  # array
    count = msg_body_dict.get('count', -1)  # int
    param_info = msg_body_dict.get('param_info', [])  # array

    try:
        for i in range(0, count):
            param_info_id = param_info[i].get("id")
            data_type = param_info[i].get("type", -1)

            if data_type == 0:
                param_info_value = param_info[i].get("intvalue")
                HStategrid.save_DeviceInfo(str(device_type) + str(device_num) + str(param_info_id), HStategrid.DB_Data_Type.DATA_INT.value, "null", param_info_value)
            if data_type == 1:
                param_info_value = param_info[i].get("boolvalue")
                HStategrid.save_DeviceInfo(str(device_type) + str(device_num) + str(param_info_id), HStategrid.DB_Data_Type.DATA_INT.value, "null", param_info_value)
            if data_type == 2:
                param_info_value = param_info[i].get("floatvalue")
                HStategrid.save_DeviceInfo(str(device_type) + str(device_num) + str(param_info_id), HStategrid.DB_Data_Type.DATA_INT.value, "null", param_info_value)
            if data_type == 3:
                param_info_value = param_info[i].get("strvalue")
                HStategrid.save_DeviceInfo(str(device_type) + str(device_num) + str(param_info_id), HStategrid.DB_Data_Type.DATA_STR.value, param_info_value, 0)

        HHhdlist.read_param_is = True
        return 0
    except Exception as e:
        HSyslog.log_error(f"app_parameter_fetch_response's error: {e}")


def _hqc_main_event_notify_read_fault(msg_body_dict: dict):  # 当前/历史故障读取消息
    read_flaut_type = msg_body_dict.get("read_event_type")
    read_flaut = msg_body_dict.get("read_flaut")
    try:
        if read_flaut_type == 0x00:
            info = {
                "type": read_flaut,
                "model": 0x00,
                "param1": msg_body_dict.get("start_intex"),
                "param2": msg_body_dict.get("stop_intex"),
            }
        elif read_flaut_type == 0x01:
            info = {
                "type": read_flaut,
                "model": 0x01,
                "param1": msg_body_dict.get("start_time"),
                "param2": msg_body_dict.get("stop_time"),
            }
        else:
            info = {
                "type": read_flaut,
                "model": 0x00,
                "param1": 0,
                "param2": 0,
            }
        topic = HHhdlist.topic_hqc_main_event_notify_read_fault
        app_publish(topic, info)
    except Exception as e:
        HSyslog.log_error(f"_hqc_main_event_notify_read_fault error: {e}")


def _hqc_main_event_reply_read_fault(msg_body_dict: dict):  # 当前/历史读取应答消息
    total = msg_body_dict.get('total', -1)  # int
    count = msg_body_dict.get('count', -1)  # int
    type = msg_body_dict.get('type', -1)  # int
    faults = msg_body_dict.get('faults', [])  # array
    try:
        pass
    except Exception as e:
        HSyslog.log_error(f"_hqc_main_event_reply_read_fault error: {e}")


def _hqc_main_event_notify_read_event(msg_body_dict: dict):  # 事件读取消息
    read_event_type = msg_body_dict.get("read_event_type")
    try:
        if read_event_type == 0x00:
            info = {
                "model": 0x00,
                "param1": msg_body_dict.get("start_intex"),
                "param2": msg_body_dict.get("stop_intex"),
            }
        elif read_event_type == 0x01:
            info = {
                "model": 0x01,
                "param1": msg_body_dict.get("start_time"),
                "param2": msg_body_dict.get("stop_time"),
            }
        else:
            info = {
                "model": 0x00,
                "param1": 0,
                "param2": 0,
            }
        topic = HHhdlist.topic_hqc_main_event_notify_read_event
        app_publish(topic, info)
    except Exception as e:
        HSyslog.log_error(f"_hqc_main_event_notify_read_event error: {e}")


def _hqc_main_event_reply_read_event(msg_body_dict: dict):  # 事件读取应答消息
    total = msg_body_dict.get('total', -1)  # int
    count = msg_body_dict.get('count', -1)  # int
    events = msg_body_dict.get('events', [])  # array
    try:
        pass
    except Exception as e:
        HSyslog.log_error(f"_hqc_main_event_reply_read_event error: {e}")


app_func_dict = {
    '/hqc/sys/network-state': {'name': '/hqc/sys/network-state', 'isSubscribe': False, 'qos': 0, 'func': _hqc_sys_network_state},  # 网络状态消息
    '/hqc/sys/time-sync': {'name': '/hqc/sys/time-sync', 'isSubscribe': False, 'qos': 2, 'func': _hqc_sys_time_sync},  # 时间同步消息
    '/hqc/main/telemetry-notify/fault': {'name': '/hqc/main/telemetry-notify/fault', 'isSubscribe': True, 'qos': 1, 'func': _hqc_main_telemetry_notify_fault},  # 设备故障消息
    '/hqc/cloud/event-notify/fault': {'name': '/hqc/cloud/event-notify/fault', 'isSubscribe': False, 'qos': 2, 'func': _hqc_cloud_event_notify_fault},  # 设备故障查询消息
    '/hqc/main/telemetry-notify/info': {'name': '/hqc/main/telemetry-notify/info', 'isSubscribe': True, 'qos': 0, 'func': _hqc_main_telemetry_notify_info},  # 遥测遥信消息
    '/hqc/cloud/event-notify/info': {'name': '/hqc/cloud/event-notify/info', 'isSubscribe': False, 'qos': 2, 'func': _hqc_cloud_event_notify_info},  # 遥测遥信查询消息
    '/hqc/main/event-notify/request-charge': {'name': '/hqc/main/event-notify/request-charge', 'isSubscribe': True, 'qos': 2, 'func': _hqc_main_event_notify_request_charge},  # 充电请求消息
    '/hqc/main/event-reply/request-charge': {'name': '/hqc/main/event-reply/request-charge', 'isSubscribe': False, 'qos': 2, 'func': _hqc_main_event_reply_request_charge},  # 充电请求应答消息
    '/hqc/main/event-notify/control-charge': {'name': '/hqc/main/event-notify/control-charge', 'isSubscribe': False, 'qos': 2, 'func': _hqc_main_event_notify_control_charge},  # 充电控制消息
    '/hqc/main/event-reply/control-charge': {'name': '/hqc/main/event-reply/control-charge', 'isSubscribe': True, 'qos': 2, 'func': _hqc_main_event_reply_control_charge},  # 充电控制应答消息
    '/hqc/ui/event-notify/auth-gun': {'name': '/hqc/ui/event-notify/auth-gun', 'isSubscribe': False, 'qos': 2, 'func': _hqc_ui_event_notify_auth_gun},  # 鉴权绑定消息
    '/hqc/main/event-notify/check-vin': {'name': '/hqc/main/event-notify/check-vin', 'isSubscribe': True, 'qos': 2, 'func': _hqc_main_event_notify_check_vin},  # 车辆VIN鉴权消息
    '/hqc/main/event-reply/check-vin': {'name': '/hqc/main/event-reply/check-vin', 'isSubscribe': False, 'qos': 2, 'func': _hqc_main_event_reply_check_vin},  # 车辆VIN鉴权应答消息
    '/hqc/main/event-notify/charge-record': {'name': '/hqc/main/event-notify/charge-record', 'isSubscribe': True, 'qos': 2, 'func': _hqc_main_event_notify_charge_record},  # 充电记录消息
    '/hqc/main/event-reply/charge-record': {'name': '/hqc/main/event-reply/charge-record', 'isSubscribe': False, 'qos': 2, 'func': _hqc_main_event_reply_charge_record},  # 充电记录应答消息
    '/hqc/main/event-notify/charge-cost': {'name': '/hqc/main/event-notify/charge-cost', 'isSubscribe': True, 'qos': 2, 'func': _hqc_main_event_notify_charge_cost},  # 充电费用消息
    '/hqc/main/event-notify/charge-elec': {'name': '/hqc/main/event-notify/charge-elec', 'isSubscribe': True, 'qos': 2, 'func': _hqc_main_event_notify_charge_elec},  # 充电电量冻结消息
    '/hqc/main/event-notify/charge-account': {'name': '/hqc/main/event-notify/charge-account', 'isSubscribe': False, 'qos': 1, 'func': _hqc_main_event_notify_charge_account},  # 充电结算消息
    '/hqc/cloud/event-notify/recharge': {'name': '/hqc/cloud/event-notify/recharge', 'isSubscribe': False, 'qos': 2, 'func': _hqc_cloud_event_notify_recharge},  # 账户充值消息
    '/hqc/cloud/event-reply/recharge': {'name': '/hqc/cloud/event-reply/recharge', 'isSubscribe': True, 'qos': 2, 'func': _hqc_cloud_event_reply_recharge},  # 账户充值应答消息
    '/hqc/cloud/event-notify/balance-query': {'name': '/hqc/cloud/event-notify/balance-query', 'isSubscribe': True, 'qos': 2, 'func': _hqc_cloud_event_notify_balance_query},  # 账户余额查询消息
    '/hqc/cloud/event-reply/balance-query': {'name': '/hqc/cloud/event-reply/balance-query', 'isSubscribe': False, 'qos': 2, 'func': _hqc_cloud_event_reply_balance_query},  # 账户余额查询结果消息
    '/hqc/cloud/event-notify/request-rate': {'name': '/hqc/cloud/event-notify/request-rate', 'isSubscribe': True, 'qos': 2, 'func': _hqc_cloud_event_notify_request_rate},  # 充电系统费率请求消息
    '/hqc/cloud/event-reply/request-rate': {'name': '/hqc/cloud/event-reply/request-rate', 'isSubscribe': False, 'qos': 2, 'func': _hqc_cloud_event_reply_request_rate},  # 充电系统费率请求应答消息
    '/hqc/cloud/event-notify/query-rate': {'name': '/hqc/cloud/event-notify/query-rate', 'isSubscribe': False, 'qos': 2, 'func': _hqc_cloud_event_notify_query_rate},  # 充电系统费率查询消息
    '/hqc/cloud/event-reply/query-rate': {'name': '/hqc/cloud/event-reply/query-rate', 'isSubscribe': True, 'qos': 2, 'func': _hqc_cloud_event_reply_query_rate},  # 充电系统费率查询结果消息
    '/hqc/cloud/event-notify/request-gunrate': {'name': '/hqc/cloud/event-notify/request-gunrate', 'isSubscribe': True, 'qos': 2, 'func': _hqc_cloud_event_notify_request_gunrate},  # 充电枪费率请求消息
    '/hqc/cloud/event-reply/request-gunrate': {'name': '/hqc/cloud/event-reply/request-gunrate', 'isSubscribe': False, 'qos': 2, 'func': _hqc_cloud_event_reply_request_gunrate},  # 充电枪费率请求应答消息
    '/hqc/cloud/event-notify/query-gunrate': {'name': '/hqc/cloud/event-notify/query-gunrate', 'isSubscribe': False, 'qos': 2, 'func': _hqc_cloud_event_notify_query_gunrate},  # 充电枪费率查询消息
    '/hqc/cloud/event-reply/query-gunrate': {'name': '/hqc/cloud/event-reply/query-gunrate', 'isSubscribe': True, 'qos': 2, 'func': _hqc_cloud_event_reply_query_gunrate},  # 充电枪费率查询结果消息
    '/hqc/cloud/event-notify/request-startup': {'name': '/hqc/cloud/event-notify/request-startup', 'isSubscribe': False, 'qos': 2, 'func': _hqc_cloud_event_notify_request_startup},  # 充电启动策略请求消息
    '/hqc/cloud/event-reply/request-startup': {'name': '/hqc/cloud/event-reply/request-startup', 'isSubscribe': False, 'qos': 2, 'func': _hqc_cloud_event_reply_request_startup},  # 充电启动策略请求应答消息
    '/hqc/cloud/event-notify/query-startup': {'name': '/hqc/cloud/event-notify/query-startup', 'isSubscribe': False, 'qos': 2, 'func': _hqc_cloud_event_notify_query_startup},  # 充电启动策略查询消息
    '/hqc/cloud/event-reply/query-startup': {'name': '/hqc/cloud/event-reply/query-startup', 'isSubscribe': False, 'qos': 2, 'func': _hqc_cloud_event_reply_query_startup},  # 充电启动策略查询结果消息
    '/hqc/cloud/event-notify/request-dispatch': {'name': '/hqc/cloud/event-notify/request-dispatch', 'isSubscribe': False, 'qos': 2, 'func': _hqc_cloud_event_notify_request_dispatch},  # 功率分配策略请求消息
    '/hqc/cloud/event-reply/request-dispatch': {'name': '/hqc/cloud/event-reply/request-dispatch', 'isSubscribe': False, 'qos': 2, 'func': _hqc_cloud_event_reply_request_dispatch},  # 功率分配策略请求应答消息
    '/hqc/cloud/event-notify/query-dispatch': {'name': '/hqc/cloud/event-notify/query-dispatch', 'isSubscribe': False, 'qos': 2, 'func': _hqc_cloud_event_notify_query_dispatch},  # 功率分配策略查询消息
    '/hqc/cloud/event-reply/query-dispatch': {'name': '/hqc/cloud/event-reply/query-dispatch', 'isSubscribe': False, 'qos': 2, 'func': _hqc_cloud_event_reply_query_dispatch},  # 功率分配策略查询结果消息
    '/hqc/cloud/event-notify/request-offlinelist': {'name': '/hqc/cloud/event-notify/request-offlinelist', 'isSubscribe': False, 'qos': 2, 'func': _hqc_cloud_event_notify_request_offlinelist},  # 离线名单版本请求消息
    '/hqc/cloud/event-reply/request-offlinelist': {'name': '/hqc/cloud/event-reply/request-offlinelist', 'isSubscribe': False, 'qos': 2, 'func': _hqc_cloud_event_reply_request_offlinelist},  # 离线名单版本应答消息
    '/hqc/main/event-notify/charge-session': {'name': '/hqc/main/event-notify/charge-session', 'isSubscribe': True, 'qos': 1, 'func': _hqc_main_event_notify_charge_session},  # 充电会话消息
    '/hqc/main/event-reply/charge-session': {'name': '/hqc/main/event-reply/charge-session', 'isSubscribe': False, 'qos': 1, 'func': _hqc_main_event_reply_charge_session},  # 充电会话应答消息
    '/hqc/main/event-notify/update-param': {'name': '/hqc/main/event-notify/update-param', 'isSubscribe': False, 'qos': 2, 'func': _hqc_main_event_notify_update_param},  # 设置参数消息
    '/hqc/main/event-reply/update-param': {'name': '/hqc/main/event-reply/update-param', 'isSubscribe': True, 'qos': 2, 'func': _hqc_main_event_reply_update_param},  # 设置参数应答消息
    '/hqc/main/event-notify/update-qrcode': {'name': '/hqc/main/event-notify/update-qrcode', 'isSubscribe': False, 'qos': 2, 'func': _hqc_main_event_notify_update_qrcode},  # 二维码更新消息
    '/hqc/main/event-notify/reserve-count-down': {'name': '/hqc/main/event-notify/reserve-count-down', 'isSubscribe': False, 'qos': 2, 'func': _hqc_main_event_notify_reserve_count_down},  # 预约延时启动倒计时消息
    '/hqc/cloud/event-notify/m1-secret': {'name': '/hqc/cloud/event-notify/m1-secret', 'isSubscribe': False, 'qos': 2, 'func': _hqc_cloud_event_notify_m1_secret},  # M1卡密钥更新消息
    '/hqc/cloud/event-reply/m1-secret': {'name': '/hqc/cloud/event-reply/m1-secret', 'isSubscribe': True, 'qos': 2, 'func': _hqc_cloud_event_reply_m1_secret},  # M1卡密钥更新结果消息
    '/hqc/main/event-reply/update-qrcode': {'name': '/hqc/main/event-reply/update-qrcode', 'isSubscribe': True, 'qos': 2, 'func': _hqc_main_event_reply_update_qrcode},  # 二维码更新应答消息
    '/hqc/cloud/event-notify/pos-pre-transaction': {'name': '/hqc/cloud/event-notify/pos-pre-transaction', 'isSubscribe': False, 'qos': 2, 'func': _hqc_cloud_event_notify_pos_pre_transaction},  # POS机预交易信息消息
    '/hqc/cloud/event-notify/pos-charge-cost': {'name': '/hqc/cloud/event-notify/pos-charge-cost', 'isSubscribe': False, 'qos': 2, 'func': _hqc_cloud_event_notify_pos_charge_cost},  # POS机扣费消息
    '/hqc/cloud/event-reply/pos-charge-cost': {'name': '/hqc/cloud/event-reply/pos-charge-cost', 'isSubscribe': False, 'qos': 2, 'func': _hqc_cloud_event_reply_pos_charge_cost},  # POS机扣费结果消息
    '/hqc/cloud/event-notify/update-charge-order-id': {'name': '/hqc/cloud/event-notify/update-charge-order-id', 'isSubscribe': False, 'qos': 2, 'func': _hqc_cloud_event_notify_update_charge_order_id},  # 充电订单ID更新消息
    '/hqc/cloud/event-reply/update-charge-order-id': {'name': '/hqc/cloud/event-reply/update-charge-order-id', 'isSubscribe': False, 'qos': 2, 'func': _hqc_cloud_event_reply_update_charge_order_id},  # 充电订单ID更新结果消息
    '/hqc/main/event-notify/update-rate': {'name': '/hqc/main/event-notify/update-rate', 'isSubscribe': False, 'qos': 2, 'func': _hqc_main_event_notify_update_rate},  # 充电系统费率同步消息
    '/hqc/main/event-reply/update-rate': {'name': '/hqc/main/event-reply/update-rate', 'isSubscribe': True, 'qos': 2, 'func': _hqc_main_event_reply_update_rate},  # 充电系统费率同步应答消息
    '/hqc/main/event-notify/update-gunrate': {'name': '/hqc/main/event-notify/update-gunrate', 'isSubscribe': False, 'qos': 2, 'func': _hqc_main_event_notify_update_gunrate},  # 充电枪费率同步消息
    '/hqc/main/event-reply/update-gunrate': {'name': '/hqc/main/event-reply/update-gunrate', 'isSubscribe': True, 'qos': 2, 'func': _hqc_main_event_reply_update_gunrate},  # 充电枪费率同步应答消息
    '/hqc/main/event-notify/update-startup': {'name': '/hqc/main/event-notify/update-startup', 'isSubscribe': False, 'qos': 2, 'func': _hqc_main_event_notify_update_startup},  # 充电启动策略同步消息
    '/hqc/main/event-reply/update-startup': {'name': '/hqc/main/event-reply/update-startup', 'isSubscribe': False, 'qos': 2, 'func': _hqc_main_event_reply_update_startup},  # 充电启动策略同步应答消息
    '/hqc/main/event-notify/update-dispatch': {'name': '/hqc/main/event-notify/update-dispatch', 'isSubscribe': False, 'qos': 2, 'func': _hqc_main_event_notify_update_dispatch},  # 功率分配策略同步消息
    '/hqc/main/event-reply/update-dispatch': {'name': '/hqc/main/event-reply/update-dispatch', 'isSubscribe': False, 'qos': 2, 'func': _hqc_main_event_reply_update_dispatch},  # 功率分配策略同步应答消息
    '/hqc/main/event-notify/update-offlinelist': {'name': '/hqc/main/event-notify/update-offlinelist', 'isSubscribe': False, 'qos': 2, 'func': _hqc_main_event_notify_update_offlinelist},  # 离线名单版本同步消息
    '/hqc/main/event-reply/update-offflinelist': {'name': '/hqc/main/event-reply/update-offflinelist', 'isSubscribe': False, 'qos': 2, 'func': _hqc_main_event_reply_update_offflinelist},  # 离线名单版本同步应答消息
    '/hqc/main/event-notify/offlinelist-log': {'name': '/hqc/main/event-notify/offlinelist-log', 'isSubscribe': False, 'qos': 2, 'func': _hqc_main_event_notify_offlinelist_log},  # 离线名单项操作日志消息
    '/hqc/main/event-reply/offlinelist-log': {'name': '/hqc/main/event-reply/offlinelist-log', 'isSubscribe': False, 'qos': 2, 'func': _hqc_main_event_reply_offlinelist_log},  # 离线名单项操作日志应答消息
    '/hqc/main/event-notify/clear': {'name': '/hqc/main/event-notify/clear', 'isSubscribe': False, 'qos': 2, 'func': _hqc_main_event_notify_clear},  # 清除故障、事件消息
    '/hqc/main/event-reply/clear': {'name': '/hqc/main/event-reply/clear', 'isSubscribe': False, 'qos': 2, 'func': _hqc_main_event_reply_clear},  # 清除故障、事件应答消息
    '/hqc/sys/upgrade-notify/notify': {'name': '/hqc/sys/upgrade-notify/notify', 'isSubscribe': False, 'qos': 1, 'func': _hqc_sys_upgrade_notify_notify},  # 升级控制消息
    '/hqc/sys/upgrade-reply/notify': {'name': '/hqc/sys/upgrade-reply/notify', 'isSubscribe': False, 'qos': 1, 'func': _hqc_sys_upgrade_reply_notify},  # 升级控制应答消息
    '/hqc/sys/upgrade-notify/process': {'name': '/hqc/sys/upgrade-notify/process', 'isSubscribe': False, 'qos': 0, 'func': _hqc_sys_upgrade_notify_process},  # 升级进度消息
    '/hqc/sys/upgrade-notify/result': {'name': '/hqc/sys/upgrade-notify/result', 'isSubscribe': False, 'qos': 1, 'func': _hqc_sys_upgrade_notify_result},  # 升级结果消息
    '/hqc/sys/upload-notify/notify': {'name': '/hqc/sys/upload-notify/notify', 'isSubscribe': False, 'qos': 1, 'func': _hqc_sys_upload_notify_notify},  # 日志文件上传请求消息
    '/hqc/sys/upload-reply/notify': {'name': '/hqc/sys/upload-reply/notify', 'isSubscribe': False, 'qos': 1, 'func': _hqc_sys_upload_reply_notify},  # 日志文件上传请求应答消息
    '/hqc/sys/upgrade-notify/version': {'name': '/hqc/sys/upgrade-notify/version', 'isSubscribe': False, 'qos': 1, 'func': _hqc_sys_upgrade_notify_version},  # 读取版本号消息
    '/hqc/sys/upgrade-reply/version': {'name': '/hqc/sys/upgrade-reply/version', 'isSubscribe': True, 'qos': 1, 'func': _hqc_sys_upgrade_reply_version},  # 读取版本号应答消息
    '/hqc/sys/upgrade-notify/control_command': {'name': '/hqc/sys/upgrade-notify/control_command', 'isSubscribe': False, 'qos': 1, 'func': _hqc_sys_upgrade_notify_control_command},  # 远程控制命令消息
    '/hqc/sys/upgrade-reply/control_command': {'name': '/hqc/sys/upgrade-reply/control_command', 'isSubscribe': False, 'qos': 1, 'func': _hqc_sys_upgrade_reply_control_command},  # 远程控制命令应答消息
    '/hqc/main/event-notify/read-param': {'name': '/hqc/main/event-notify/read-param', 'isSubscribe': False, 'qos': 1, 'func': _hqc_main_event_notify_read_param},  # 参数读取消息
    '/hqc/main/event-reply/read-param': {'name': '/hqc/main/event-reply/read-param', 'isSubscribe': True, 'qos': 1, 'func': _hqc_main_event_reply_read_param},  # 参数读取应答消息
    '/hqc/main/event-notify/read-fault': {'name': '/hqc/main/event-notify/read-fault', 'isSubscribe': False, 'qos': 1, 'func': _hqc_main_event_notify_read_fault},  # 当前/历史故障读取消息
    '/hqc/main/event-reply/read-fault': {'name': '/hqc/main/event-reply/read-fault', 'isSubscribe': False, 'qos': 1, 'func': _hqc_main_event_reply_read_fault},  # 当前/历史读取应答消息
    '/hqc/main/event-notify/read-event': {'name': '/hqc/main/event-notify/read-event', 'isSubscribe': False, 'qos': 1, 'func': _hqc_main_event_notify_read_event},  # 事件读取消息
    '/hqc/main/event-reply/read-event': {'name': '/hqc/main/event-reply/read-event', 'isSubscribe': False, 'qos': 1, 'func': _hqc_main_event_reply_read_event},  # 事件读取应答消息
}
