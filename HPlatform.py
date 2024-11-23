import datetime
import hashlib
import inspect
import json
import queue
import random
import socket
import ssl
import struct
import subprocess
import threading
import time
import urllib.request

from paho.mqtt import client as mqtt_client
import paho.mqtt.client as mqtt
import HHhdlist
import HStategrid
from HHhdlist import *
import HSyslog


def tpp_init(host, port):
    try:
        while True:
            if not HHhdlist.Device_ready:
                time.sleep(1)
            else:
                break
        HStategrid.save_VerInfoEvt(0, HHhdlist.device_ctrl_type.SDK.value, "20.0.2", "A.0.1")
        device_start_time = HStategrid.get_datetime_timestamp()
        HStategrid.save_DeviceInfo("device_start_time", HStategrid.DB_Data_Type.DATA_INT.value, "", device_start_time)
        device_start_nums = HStategrid.get_DeviceInfo("device_start_nums")
        charge_record_num = HStategrid.get_DeviceInfo("charge_record_num")
        if device_start_nums is None:
            HStategrid.device_start_nums += 1
            HStategrid.save_DeviceInfo("device_start_nums", HStategrid.DB_Data_Type.DATA_INT.value, "", HStategrid.device_start_nums)
        else:
            device_start_nums += 1
            HStategrid.device_start_nums = device_start_nums
            HStategrid.save_DeviceInfo("device_start_nums", HStategrid.DB_Data_Type.DATA_INT.value, "", device_start_nums)

        if charge_record_num is None:
            HStategrid.save_DeviceInfo("charge_record_num", HStategrid.DB_Data_Type.DATA_INT.value, "", HStategrid.charge_record_num)
        HStategrid.save_DeviceInfo("device_charge_time", HStategrid.DB_Data_Type.DATA_INT.value, "", device_start_time)
        client = Client(host, port)
        client.connect()
        do_mqtt_resv_data()
        do_device_platform_data()
        do_mqtt_period()

        HStategrid.Platform_ready = True
    except Exception as e:
        HSyslog.log_info(f"tpp_init error. {e}")


class Client:
    def __init__(self, broker_address, broker_port, keepalive=30, client_id=HStategrid.Device_ID):
        self.broker_address = broker_address
        self.broker_port = broker_port
        self.keepalive = keepalive
        self.client_id = client_id
        self.client = mqtt.Client(client_id=self.client_id)
        self.send_thread = None
        self.client.username_pw_set("91110113MA01CF8F83", "JvL8so96zyM6ppaTPfEe2JRt9lsnJ07EhT/oQhcCAyuE7Eyo5RoQ0MXBIXyyD13cNN2LqK3ViHLKCFbE/IkKXpeDfIMpCWt8niVn29Vpaf38gtVf0ne7RWPpHC4PlP+gIWLPRVUV1ei1RSeCWfJ4GtDJ0fuOuq7ij0gq/4BIiKU=")

    def connect(self, isReady=False):
        """连接到MQTT服务器"""
        try:
            try:
                # 设置回调函数
                self.client.on_connect = self._on_connect
                self.client.on_disconnect = self._on_disconnect
                self.client.on_message = self._on_message

                self.client.connect(self.broker_address, self.broker_port, self.keepalive)
                time.sleep(2)  # 等待连接结果
                self.subscribe(HStategrid.Device_ID)
                self.client.loop_start()  # 启动网络循环以处理连接

                isReady = True
                HSyslog.log_info(f"Connected to MQTT broker at {self.broker_address}:{self.broker_port}")
            except Exception as e:
                HSyslog.log_info(f"Failed to connect to broker: {e}")

            if isReady:
                self.start_send_thread()
        except socket.error as e:
            HSyslog.log_info(f"{HStategrid.red_char}connect_tpp: {e}{HStategrid.init_char}")
            time.sleep(5)

    def start_send_thread(self):
        if not self.send_thread or not self.send_thread.is_alive():
            self.send_thread = threading.Thread(target=self._send_messages, daemon=True)
            self.send_thread.start()

    def disconnect(self):
        """断开与MQTT服务器的连接"""
        self.client.loop_stop()
        self.client.disconnect()
        HSyslog.log_info("Disconnected from MQTT broker")

    def _on_connect(self, client, userdata, flags, rc):
        """连接成功时的回调函数"""
        if rc == 0:
            HStategrid.hand_status = True
            hhd_to_tpp_106({})
            HSyslog.log_info("Connected to MQTT Broker!")
        else:
            HStategrid.connect_status = False
            HStategrid.hand_status = False
            HSyslog.log_info(f"Failed to connect, return code {rc}")

    def _on_disconnect(self, client, userdata, rc):
        """断开连接时的回调函数"""
        try:
            HSyslog.log_info("check connection is closed! rc = {}".format(rc))
            HStategrid.connect_status = False
            HStategrid.hand_status = False
            # 断线自动重连
            if rc != 0:
                HSyslog.log_info("Attempting to reconnect...")
                self.reconnect()
        except Exception as e:
            HSyslog.log_info(f"MQTT.close: {e}")

    def reconnect(self):
        """重新连接到MQTT服务器"""
        try:
            self.client.reconnect()
            HSyslog.log_info("Reconnected to MQTT broker")
        except Exception as e:
            HSyslog.log_info(f"Reconnection failed: {e}")
        time.sleep(10)

    def subscribe(self, topic):
        """订阅主题"""
        self.client.subscribe(topic)
        HSyslog.log_info(f"Subscribed to topic: {topic}")

    def _on_message(self, client, userdata, msg):
        """接收消息时的回调函数"""
        if HStategrid.hand_status:
            try:
                receive_msg = msg.payload
                topic = msg.topic
                if receive_msg:
                    result = HStategrid.unpack(receive_msg)
                    # HSyslog.log_info(f"Received message: '{receive_msg}' on topic {topic}")
            except Exception as e:
                HSyslog.log_info(f"_receive_messages: '{msg}' {e}")

    def _send_messages(self):
        """向主题发送消息"""
        HSyslog.log_info(f"start send msg")
        while True:
            if HStategrid.hand_status:
                if not HStategrid.tpp_send_data:
                    time.sleep(0.1)
                else:
                    try:
                        if HStategrid.tpp_send_data.empty():
                            time.sleep(0.1)
                        else:
                            msg = HStategrid.tpp_send_data.get()
                            topic = HStategrid.Device_ID
                            result = self.client.publish(topic, msg)
                            if result.rc == mqtt_client.MQTT_ERR_SUCCESS:
                                HSyslog.log_info(f"Send_to_Platform: {msg} to topic: {topic}")
                                pass
                            else:
                                HSyslog.log_info(f"Failed to send message, result code: {result.rc}")
                            time.sleep(0.02)
                    except Exception as e:
                        HSyslog.log_info(f"Send_to_Platform: {e}")
            else:
                if not HStategrid.tpp_send_data:
                    time.sleep(0.1)
                else:
                    if HStategrid.tpp_send_data.empty():
                        time.sleep(0.1)
                    else:
                        msg = HStategrid.tpp_send_data.get()
                        HSyslog.log_info(f"Send_to_Platform Faild: {msg}")


def __mqtt_resv_data():
    while True:
        if HStategrid.hand_status:
            if not HStategrid.tpp_resv_data:
                time.sleep(0.1)
            else:
                try:
                    if HStategrid.tpp_resv_data.empty():
                        time.sleep(0.1)
                    else:
                        msg = HStategrid.tpp_resv_data.get()
                        if msg[0] in tpp_to_hhd.keys():
                            tpp_to_hhd[msg[0]](msg[1])
                        else:
                            HSyslog.log_info(f"__mqtt_resv_data： 参数错误--{msg}")
                except Exception as e:
                    HSyslog.log_info(f"__mqtt_resv_data error: {e}")
        else:
            if not HStategrid.tpp_resv_data:
                time.sleep(0.1)
            else:
                if HStategrid.tpp_resv_data.empty():
                    time.sleep(0.1)
                else:
                    msg = HStategrid.tpp_resv_data.get()
                    HSyslog.log_info(f"__mqtt_resv_data Faild: {msg}")


def do_mqtt_resv_data():
    mqttSendThread = threading.Thread(target=__mqtt_resv_data)
    mqttSendThread.start()
    HSyslog.log_info("do_mqtt_resv_data")


def __device_platform_data():
    while True:
        if not HHhdlist.device_platform_data:
            time.sleep(0.1)
        else:
            try:
                if HHhdlist.device_platform_data.empty():
                    time.sleep(0.1)
                else:
                    msg = HHhdlist.device_platform_data.get()
                    if msg[0] in hhd_to_tpp.keys():
                        hhd_to_tpp[msg[0]](msg[1])
                    else:
                        HSyslog.log_info(f"__device_platform_data： 参数错误--{msg}")
            except Exception as e:
                HSyslog.log_info(f"__device_platform_data error: {e}")


def do_device_platform_data():
    d_p = threading.Thread(target=__device_platform_data)
    d_p.start()
    HSyslog.log_info("__device_platform_data")


def __mqtt_period_event(interval_102, interval_104, interval_106):
    period_time_102 = HStategrid.get_datetime_timestamp()
    period_time_104 = HStategrid.get_datetime_timestamp()
    period_time_106 = HStategrid.get_datetime_timestamp()
    while True:
        if HStategrid.connect_status and HStategrid.hand_status:
            if int(time.time()) - int(period_time_102) >= interval_102:
                period_time_102 = HStategrid.get_datetime_timestamp()
                hhd_to_tpp_102({})
            if int(time.time()) - int(period_time_104) >= interval_104:
                period_time_104 = HStategrid.get_datetime_timestamp()
                hhd_to_tpp_104()
                hhd_to_tpp_306()
            if int(time.time()) - int(period_time_106) >= interval_106:
                period_time_106 = HStategrid.get_datetime_timestamp()
                hhd_to_tpp_106({})
            time.sleep(1)
        else:
            time.sleep(1)


def do_mqtt_period():
    interval_102 = HStategrid.get_DeviceInfo("report_102_interval")
    interval_104 = HStategrid.get_DeviceInfo("report_104_interval") // 2
    interval_106 = HStategrid.get_DeviceInfo("report_106_interval") * 60
    if interval_102 is None or interval_102 == 0:
        interval_102 = 30
    if interval_104 is None or interval_104 == 0:
        interval_104 = 30 // 2
    if interval_106 is None or interval_106 == 0:
        interval_106 = 30 * 60
    mqttPeriodThread = threading.Thread(target=__mqtt_period_event, args=(interval_102, interval_104, interval_106))
    mqttPeriodThread.start()
    HSyslog.log_info("do_mqtt_period")


'''################################################### 接收数据处理 ####################################################'''


def tpp_to_hhd_1(msg):
    try:
        cmd_type = msg.get("cmd_type")
        data_addr = msg.get("data_addr")
        data = msg.get("data", -1)
        if data_addr in HStategrid.cleck_code_1.keys():
            if cmd_type == 0:
                datainfo = HStategrid.get_DeviceInfo(HStategrid.cleck_code_1.get(data_addr).get("param_id"))
                if datainfo is not None:
                    info = {
                        "data_addr": data_addr,
                        "cmd_type": cmd_type,
                        "datainfo": HStategrid.get_DeviceInfo(HStategrid.cleck_code_1.get(data_addr).get("param_id")),
                        "result": 0
                    }
                else:
                    info = {
                        "data_addr": data_addr,
                        "cmd_type": cmd_type,
                        "datainfo": 0,
                        "result": 1
                    }
            elif cmd_type == 1:
                if data != -1:
                    HStategrid.save_DeviceInfo(HStategrid.cleck_code_1.get(data_addr).get("param_id"), HStategrid.DB_Data_Type.DATA_INT, "", data)
                    info = {
                        "data_addr": data_addr,
                        "cmd_type": cmd_type,
                        "datainfo": HStategrid.get_DeviceInfo(HStategrid.cleck_code_1.get(data_addr).get("param_id")),
                        "result": 0
                    }
                else:
                    info = {
                        "data_addr": data_addr,
                        "cmd_type": cmd_type,
                        "datainfo": 0,
                        "result": 1
                    }
            else:
                info = {
                    "data_addr": data_addr,
                    "cmd_type": cmd_type,
                    "datainfo": 0,
                    "result": 1
                }
        else:
            info = {
                "data_addr": data_addr,
                "cmd_type": cmd_type,
                "datainfo": 0,
                "result": 1
            }
        hhd_to_tpp_2(info)
    except Exception as e:
        HSyslog.log_info(f"tpp_to_hhd_1'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_3(msg):
    try:
        cmd_type = msg.get("cmd_type")
        data_addr = msg.get("data_addr")
        data = msg.get("data", -1)
        if data_addr in HStategrid.cleck_code_3.keys():
            if cmd_type == 0:
                datainfo = HStategrid.get_DeviceInfo(HStategrid.cleck_code_3.get(data_addr).get("param_id"))
                if datainfo is not None:
                    info = {
                        "data_addr": data_addr,
                        "cmd_type": cmd_type,
                        "datainfo": HStategrid.get_DeviceInfo(HStategrid.cleck_code_3.get(data_addr).get("param_id")),
                        "result": 0
                    }
                else:
                    info = {
                        "data_addr": data_addr,
                        "cmd_type": cmd_type,
                        "datainfo": 0,
                        "result": 1
                    }
            elif cmd_type == 1:
                if data != -1:
                    HStategrid.save_DeviceInfo(HStategrid.cleck_code_3.get(data_addr).get("param_id"), HStategrid.DB_Data_Type.DATA_INT, "", data)
                    info = {
                        "data_addr": data_addr,
                        "cmd_type": cmd_type,
                        "datainfo": HStategrid.get_DeviceInfo(HStategrid.cleck_code_3.get(data_addr).get("param_id")),
                        "result": 0
                    }
                else:
                    info = {
                        "data_addr": data_addr,
                        "cmd_type": cmd_type,
                        "datainfo": 0,
                        "result": 1
                    }
            else:
                info = {
                    "data_addr": data_addr,
                    "cmd_type": cmd_type,
                    "datainfo": 0,
                    "result": 1
                }
        else:
            info = {
                "data_addr": data_addr,
                "cmd_type": cmd_type,
                "datainfo": 0,
                "result": 1
            }
        hhd_to_tpp_4(info)
    except Exception as e:
        HSyslog.log_info(f"tpp_to_hhd_3'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_501(msg):
    try:
        data_dict = msg.get("data_dict")
        suss_num = 0
        for data_addr, data in data_dict.items():
            if data_addr in HStategrid.cleck_code_501.keys():
                if data_addr != 6:
                    param_id = HStategrid.cleck_code_501.get(data_addr).get("param_id")
                    param_type = HStategrid.cleck_code_501.get(data_addr).get("param_type")
                    if param_type == HStategrid.DB_Data_Type.DATA_INT.value:
                        HStategrid.save_DeviceInfo(param_id, param_type, "", data)
                    else:
                        HStategrid.save_DeviceInfo(param_id, param_type, data, 0)
                    suss_num += 1
                else:
                    param_id = HStategrid.cleck_code_501.get(data_addr).get("param_id")
                    param_type = HStategrid.cleck_code_501.get(data_addr).get("param_type")
                    gun_id = data.split(':')[0]
                    gun_qrcode = data.split(':')[1]
                    HStategrid.save_DeviceInfo(f"{param_id}_{gun_id}", param_type, gun_qrcode, 0)
                    suss_num += 1
            else:
                suss_num += 0

        if suss_num == len(data_dict):
            info = {
                "suss_num": suss_num,
                "result": 0
            }
        else:
            info = {
                "suss_num": suss_num,
                "result": 2
            }
        hhd_to_tpp_502(info)
    except Exception as e:
        HSyslog.log_info(f"tpp_to_hhd_501'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_505(msg):
    try:
        info = {
            "charge_id": msg.get("charge_id"),
            "gun_id": msg.get("gun_id"),
            "result": 0,
        }
        hhd_to_tpp_506(info)
    except Exception as e:
        HSyslog.log_info(f"tpp_to_hhd_505'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_507(msg):
    try:
        data_dict = msg.get("data_dict")
        suss_num = 0
        fail_num = 0
        fail_data_info = {}
        for data_addr, data in data_dict.items():
            if data_addr in HStategrid.cleck_code_507.keys():
                param_id = HStategrid.cleck_code_501.get(data_addr).get("param_id")
                param_type = HStategrid.cleck_code_501.get(data_addr).get("param_type")
                if param_type == HStategrid.DB_Data_Type.DATA_INT.value:
                    HStategrid.save_DeviceInfo(param_id, param_type, "", data)
                else:
                    HStategrid.save_DeviceInfo(param_id, param_type, data, 0)
                suss_num += 1
            else:
                fail_num += 1
                fail_data_info.update({data_addr: 2})

        info = {
            "suss_num": suss_num,
            "fail_num": fail_num,
            "fail_data_info": fail_data_info,
            "result": 0
        }
        hhd_to_tpp_508(info)
    except Exception as e:
        HSyslog.log_info(f"tpp_to_hhd_507'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_511(msg):
    try:
        ctrl_cmd = msg.get("ctrl_cmd")  # 命令
        cmd_addr = msg.get("cmd_addr")  # 枪号
        cmd_ctrl = msg.get("cmd_ctrl")  # 控制
        if ctrl_cmd == 0:
            update_param = {
                "device_type": HHhdlist.device_param_type.parkLock.value,
                "param_list": [{"param_id": 90, "param_value": 0}],
                "gun_id": cmd_addr,
            }
        elif ctrl_cmd == 1:
            if cmd_addr == 0:
                update_param = {
                    "device_type": HHhdlist.device_param_type.gun.value,
                    "param_list": [{"param_id": 30, "param_value": cmd_ctrl}],
                    "gun_id": cmd_addr,
                }

            if cmd_addr == 1:
                update_param = {
                    "device_type": HHhdlist.device_param_type.gun.value,
                    "param_list": [{"param_id": 31, "param_value": cmd_ctrl}],
                    "gun_id": cmd_addr,
                }
        elif ctrl_cmd == 2:
            if cmd_addr == 0:
                subprocess.run(['supervisorctl', 'restart', 'internal'])
            if cmd_addr == 1:
                subprocess.run(['supervisorctl', 'restart', 'internal_ocpp'])
        elif ctrl_cmd == 3:
            update_param = {
                "device_type": HHhdlist.device_param_type.chargeSys.value,
                "param_list": [{"param_id": 186, "param_value": cmd_ctrl}],
                "gun_id": cmd_addr,
            }
        elif ctrl_cmd == 4:
            pass
        else:
            info = {
                "result": 1,
                "fail_reason": 0
            }
            hhd_to_tpp_512(info)
        info = {
            "result": 0,
            "fail_reason": 0
        }
        hhd_to_tpp_512(info)
    except Exception as e:
        HSyslog.log_info(f"tpp_to_hhd_511'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_513(msg):
    try:
        cmd_num = msg.get("cmd_num")
        data_list = msg.get("data_list")
        data_info = {}
        for cmd in data_list:
            if cmd in HStategrid.cleck_code_507.keys():
                param_id = HStategrid.cleck_code_507.get(cmd).get("param_id")
                param_data = HStategrid.get_DeviceInfo(param_id)
                if param_data is not None:
                    data_info.update({
                        cmd: {
                            "data_result": 0,
                            "data_len": 1,
                            "data": param_data
                        }
                    })
                else:
                    data_info.update({
                        cmd: {
                            "data_result": 1,
                            "data_len": 1,
                            "data": 0
                        }
                    })
            else:
                data_info.update({
                    cmd: {
                        "data_result": 1,
                        "data_len": 1,
                        "data": 0
                    }
                })

        info = {
            "data_num": cmd_num,
            "data_info": data_info
        }
        hhd_to_tpp_514(info)
    except Exception as e:
        HSyslog.log_info(f"tpp_to_hhd_513'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_515(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_info(f"tpp_to_hhd_515'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_5(msg):
    try:
        gun_id = msg.get("gun_id")
        data_addr = msg.get("data_addr")
        data = msg.get("data")
        cmd_num = msg.get("cmd_num")
        if data_addr == 1:  # 模块开机
            pass
        elif data_addr == 2:  # 停止充电
            pass
        elif data_addr == 3 or data_addr == 5 or data_addr == 6:  # 预留
            pass
        elif data_addr == 4:  # 充电控制方式
            pass
        elif data_addr == 7:  # 充电电压
            pass
        elif data_addr == 8:  # 充电电流
            pass
        elif data_addr == 9:  # 充电模式
            pass
        elif data_addr == 10:  # 取消充电预约
            pass
        elif data_addr == 11:  # 设备重启
            if data == 0x55:
                subprocess.run(['supervisorctl', 'reboot'])
        elif data_addr == 12:  # 恢复出厂设置
            if data == 0x55:
                subprocess.run(['supervisorctl', 'reboot'])
        elif data_addr == 13:  # 上锁
            if data == 0x55:
                update_param = {
                    "device_type": HHhdlist.device_param_type.parkLock.value,
                    "param_list": [{"param_id": 90, "param_value": 1}],
                    "gun_id": gun_id - 1,
                }
        elif data_addr == 14:  # 解锁
            if data == 0x55:
                update_param = {
                    "device_type": HHhdlist.device_param_type.parkLock.value,
                    "param_list": [{"param_id": 90, "param_value": 0}],
                    "gun_id": gun_id - 1,
                }
        elif data_addr == 15:  # 升级
            pass
        elif data_addr == 16:  # 正常
            pass
        elif data_addr == 17:  # 106
            hhd_to_tpp_106({})
        elif data_addr == 18:  # 104
            hhd_to_tpp_104()
        elif data_addr == 19:  # 扫描支付
            pass
        elif data_addr == 20:  # 重连
            pass
        else:
            pass

        info = {
            "gun_id": gun_id,
            "data_addr": data_addr,
            "cmd_num": cmd_num,
            "result": "0000",
        }
        hhd_to_tpp_6(info)
    except Exception as e:
        HSyslog.log_info(f"tpp_to_hhd_5'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_7(msg):
    try:
        user_phone = msg.get("user_phone")
        gun_id = msg.get("gun_id") - 1
        charge_type = msg.get("charge_type")
        charge_policy = msg.get("charge_policy")
        charge_policy_param = msg.get("charge_policy_param")
        book_time = msg.get("book_time")
        book_timeout = msg.get("book_timeout")
        charge_id = msg.get("charge_id")
        allow_offline_charge = msg.get("allow_offline_charge")
        allow_offline_charge_kw_amout = msg.get("allow_offline_charge_kw_amout")
        charge_delay_cost_is = msg.get("charge_delay_cost_is")
        charge_delay_cost_time = msg.get("charge_delay_cost_time")

        if HStategrid.Gun_list[gun_id].get_gun_charge() == {} and HStategrid.Gun_list[gun_id].get_gun_charge_order() == {}:
            HStategrid.Gun_list[gun_id].set_gun_status(HStategrid.Gun_Status.Self_checking.value)
            HStategrid.Gun_list[gun_id].set_gun_charge({"user_phone": str(user_phone)})
            HStategrid.Gun_list[gun_id].set_gun_charge({"charge_type": charge_type})
            HStategrid.Gun_list[gun_id].set_gun_charge({"charge_policy": charge_policy})
            HStategrid.Gun_list[gun_id].set_gun_charge({"charge_policy_param": charge_policy_param})
            HStategrid.Gun_list[gun_id].set_gun_charge({
                "stop_type": {
                    0: [0x00, charge_policy_param],
                    1: [0x03, charge_policy_param],
                    2: [0x02, charge_policy_param * 10],
                    3: [0x01, charge_policy_param * 10],
                    4: [0x04, charge_policy_param]
                }.get(charge_policy)[0]})
            HStategrid.Gun_list[gun_id].set_gun_charge({
                "stop_condition": {
                    0: [0x00, charge_policy_param],
                    1: [0x03, charge_policy_param],
                    2: [0x02, charge_policy_param * 10],
                    3: [0x01, charge_policy_param * 10],
                    4: [0x04, charge_policy_param]
                }.get(charge_policy)[1]})
            HStategrid.Gun_list[gun_id].set_gun_charge({"book_time": book_time})
            HStategrid.Gun_list[gun_id].set_gun_charge({"book_timeout": book_timeout})
            HStategrid.Gun_list[gun_id].set_gun_charge({"charge_id": charge_id})
            HStategrid.Gun_list[gun_id].set_gun_charge({"allow_offline_charge": allow_offline_charge})
            HStategrid.Gun_list[gun_id].set_gun_charge({"allow_offline_charge_kw_amout": allow_offline_charge_kw_amout})
            HStategrid.Gun_list[gun_id].set_gun_charge({"charge_delay_cost_is": charge_delay_cost_is})
            HStategrid.Gun_list[gun_id].set_gun_charge({"charge_delay_cost_time": charge_delay_cost_time})

            if HStategrid.Gun_list[gun_id].get_gun_charge("start_source") is None:
                HStategrid.Gun_list[gun_id].set_gun_charge({"start_source": 4})
                if charge_type == 0:
                    info = {
                        "gun_id": gun_id,
                        "control_type": HHhdlist.control_charge.start_charge.value
                    }
                    HHhdlist.platform_device_data.put([HHhdlist.topic_hqc_main_event_notify_control_charge, info])
                    info = {
                        "gun_id": gun_id,
                        "result": "0000",
                        "charge_id": HStategrid.Gun_list[gun_id].get_gun_charge("charge_id"),
                    }
                    hhd_to_tpp_8(info)
                elif charge_type == 1:
                    info = {
                        "gun_id": gun_id,
                        "result": "100D",
                        "charge_id": HStategrid.Gun_list[gun_id].get_gun_charge("charge_id"),
                    }
                    hhd_to_tpp_8(info)
                else:
                    info = {
                        "gun_id": gun_id,
                        "result": "100D",
                        "charge_id": HStategrid.Gun_list[gun_id].get_gun_charge("charge_id"),
                    }
                    hhd_to_tpp_8(info)
            elif HStategrid.Gun_list[gun_id].get_gun_charge("start_source") == 5:
                info = {
                    "gun_id": gun_id,
                    "result": 1,
                    "reason": 0x03,
                    "balance": 0
                }
                HHhdlist.platform_device_data.put([HHhdlist.topic_hqc_main_event_reply_check_vin, info])
                info = {
                    "gun_id": gun_id,
                    "result": "0000",
                    "charge_id": HStategrid.Gun_list[gun_id].get_gun_charge("charge_id"),
                }
                hhd_to_tpp_8(info)
        else:
            info = {
                "gun_id": gun_id,
                "result": "100D",
                "charge_id": HStategrid.Gun_list[gun_id].get_gun_charge("charge_id"),
            }
            hhd_to_tpp_8(info)
    except Exception as e:
        HSyslog.log_info(f"tpp_to_hhd_7'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_11(msg):
    try:
        gun_id = msg.get("gun_id") - 1
        charge_id = msg.get("charge_id")
        if charge_id == HStategrid.Gun_list[gun_id].get_gun_charge("charge_id"):
            info = {
                "gun_id": gun_id,
                "control_type": HHhdlist.control_charge.stop_charge.value
            }
            HHhdlist.platform_device_data.put([HHhdlist.topic_hqc_main_event_notify_control_charge, info])
            info = {
                "gun_id": gun_id,
                "result": "0000",
                "charge_id": charge_id,
            }
            hhd_to_tpp_12(info)
        else:
            pass
    except Exception as e:
        HSyslog.log_info(f"tpp_to_hhd_11'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_13(msg):
    try:
        info = {}
        hhd_to_tpp_14(info)
    except Exception as e:
        HSyslog.log_info(f"tpp_to_hhd_13'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_15(msg):
    try:
        gun_id = msg.get("gun_id") - 1
        charge_policy_date = msg.get("charge_policy_date")
        power_model_num = msg.get("power_model_num")
        power_out_nums = msg.get("power_out_nums")
        gun_power = HStategrid.get_DeviceInfo(f"2{gun_id}169")
        if gun_power is None or gun_power == 0:
            get_param = {
                "param_list": [169],
                "device_type": HHhdlist.device_param_type.gun.value,
                "device_num": gun_id
            }
            gun_power = HStategrid.get_DeviceInfo(f"2{gun_id}169")
        info = {
            "gun_id": gun_id,
            "result": "0000",
            "gun_power": gun_power,
        }
        hhd_to_tpp_16(info)
    except Exception as e:
        HSyslog.log_info(f"tpp_to_hhd_15'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_503(msg):
    try:
        max_power = msg.get("max_power")
        if len(max_power) <= HHhdlist.gun_num:
            param_list = []
            for gun_id, power in max_power.items():
                param_list.append({"param_id": 169, "param_value": power})
            updata_param = {
                "device_type": HHhdlist.device_param_type.gun.value,
                "param_list": param_list,
            }
            HHhdlist.platform_device_data.put([HHhdlist.topic_hqc_main_event_notify_update_param, updata_param])
            info = {
                "result": 0
            }
        else:
            info = {
                "result": 2
            }
        hhd_to_tpp_504(info)
    except Exception as e:
        HSyslog.log_info(f"tpp_to_hhd_503'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_17(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_info(f"tpp_to_hhd_17'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_19(msg):
    try:
        gun_id = msg.get("gun_id")
        max_gun_power = msg.get("max_gun_power")
        if gun_id > HHhdlist.gun_num:
            updata_param = {
                "device_type": HHhdlist.device_param_type.gun.value,
                "param_list": [{"param_id": 169, "param_value": max_gun_power}],
                "gun_id": gun_id - 1,
            }
            HHhdlist.platform_device_data.put([HHhdlist.topic_hqc_main_event_notify_update_param, updata_param])
            HStategrid.Gun_list[gun_id - 1].set_gun_charge({"max_gun_power": max_gun_power})
            info = {
                "gun_id": gun_id,
                "result": 0,
            }
        else:
            info = {
                "gun_id": gun_id,
                "result": 2,
            }
        hhd_to_tpp_20(info)
    except Exception as e:
        HSyslog.log_info(f"tpp_to_hhd_19'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_101(msg):
    try:
        heart_index = msg.get("heart_index")
        if HHhdlist.qrcode_nums <= 5:
            HHhdlist.qrcode_nums += 1
            update_qrcode = {
                "gun_id": [],
                "qrcode": []
            }
            for gun_info in HStategrid.Gun_list:
                qrcode = gun_info.get_gun_qr()
                if qrcode:
                    update_qrcode["gun_id"].append(gun_info.gun_id)
                    update_qrcode["qrcode"].append(gun_info.get_gun_qr())
                else:
                    pass
            HHhdlist.platform_device_data.put([HHhdlist.topic_hqc_main_event_notify_update_qrcode, update_qrcode])
    except Exception as e:
        HSyslog.log_info(f"tpp_to_hhd_101'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_103(msg):
    try:
        speed_charge = msg.get("speed_charge")
        gun_id = msg.get("gun_id")
        user_card_id = msg.get("user_card_id")
        user_card_balance = msg.get("user_card_balance")
        card_balance_is = msg.get("card_balance_is")
    except Exception as e:
        HSyslog.log_info(f"tpp_to_hhd_103'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_105(msg):
    try:
        system_time = msg.get("system_time")
        time_info = {
            "unix_time": system_time
        }
        HStategrid.connect_status = True
        HHhdlist.platform_device_data.put([HHhdlist.topic_hqc_sys_time_sync, time_info])
        hhd_to_tpp_206({})
    except Exception as e:
        HSyslog.log_info(f"tpp_to_hhd_105'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_113(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_info(f"tpp_to_hhd_113'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_301(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_info(f"tpp_to_hhd_301'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_303(msg):
    try:
        gun_id = msg.get("gun_id")
        device_id = msg.get("device_id")
        charge_id = msg.get("charge_id")
    except Exception as e:
        HSyslog.log_info(f"tpp_to_hhd_303'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_305(msg):
    try:
        gun_id = msg.get("gun_id")
        device_id = msg.get("device_id")
        charge_id = msg.get("charge_id")
    except Exception as e:
        HSyslog.log_info(f"tpp_to_hhd_305'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_307(msg):
    try:
        gun_id = msg.get("gun_id")
        device_id = msg.get("device_id")
        charge_id = msg.get("charge_id")
    except Exception as e:
        HSyslog.log_info(f"tpp_to_hhd_307'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_309(msg):
    try:
        gun_id = msg.get("gun_id")
        device_id = msg.get("device_id")
        charge_id = msg.get("charge_id")
    except Exception as e:
        HSyslog.log_info(f"tpp_to_hhd_309'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_311(msg):
    try:
        gun_id = msg.get("gun_id")
        device_id = msg.get("device_id")
        charge_id = msg.get("charge_id")
    except Exception as e:
        HSyslog.log_info(f"tpp_to_hhd_311'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_201(msg):
    try:
        gun_id = msg.get("gun_id") - 1
        user_card_id = msg.get("user_card_id")
        if user_card_id != "":
            info = {
                "gun_id": gun_id,
                "charge_id": user_card_id,
                "confirm_is": 1
            }
            HStategrid.set_HistoryOrder(info)
    except Exception as e:
        HSyslog.log_info(f"tpp_to_hhd_201'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_205(msg):
    try:
        gun_id = msg.get("gun_id") - 1
        user_card_id = msg.get("user_card_id")
        if user_card_id == HStategrid.Gun_list[gun_id].get_gun_charge("charge_id"):
            info = {
                "gun_id": gun_id,
                "cloud_session_id": HStategrid.Gun_list[gun_id].get_gun_charge("charge_id"),
                "device_session_id": HStategrid.Gun_list[gun_id].get_gun_charge("device_session_id"),
                "result": 0
            }
            HHhdlist.platform_device_data.put([HHhdlist.topic_hqc_main_event_reply_charge_record, info])
    except Exception as e:
        HSyslog.log_info(f"tpp_to_hhd_205'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_401(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_info(f"tpp_to_hhd_401'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_23(msg):
    try:
        gun_id = msg.get("gun_id")
        lock_ctrl = msg.get("lock_ctrl")
        update_param = {
            "device_type": HHhdlist.device_param_type.gun.value,
            "param_list": [{"param_id": 90, "param_value": lock_ctrl}],
            "gun_id": gun_id - 1
        }
        HHhdlist.platform_device_data.put([HHhdlist.topic_hqc_main_event_notify_update_param, update_param])
        info = {
            "gun_id": gun_id,
            "result": 0
        }
        hhd_to_tpp_24(info)
    except Exception as e:
        HSyslog.log_info(f"tpp_to_hhd_23'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_1303(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_info(f"tpp_to_hhd_1303'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_1305(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_info(f"tpp_to_hhd_1305'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_1307(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_info(f"tpp_to_hhd_1307'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_1309(msg):
    try:
        fee_model_num = msg.get("fee_model_num")
        fee_model_info = msg.get("fee_model_info")
        contents = []
        start_time = 0
        for fee_model in fee_model_info:
            for i in range(0, fee_model.get("fee_model_con_num")):
                content = {
                    "num": fee_model.get("fee_model_nums") + 1 + i,
                    "type": 3,
                    "start_time": start_time,
                    "stop_time": start_time + 1800,
                    "electric_rate": fee_model.get("fee_electricity") * 10000,
                    "service_rate": fee_model.get("fee_server") * 10000,
                    "delay_rate": fee_model.get("fee_delay") * 10000,
                }
                contents.append(content)
                start_time += 1800
        if 48 != len(contents):
            info = {
                "result": 2
            }
            hhd_to_tpp_1310(info)
        else:
            update_fee = {
                "contents": contents,
                "fee_model_id": f"{HStategrid.get_datetime_timestamp()}",
            }
            HHhdlist.platform_device_data.put([HHhdlist.topic_hqc_main_event_notify_update_rate, update_fee])
            HStategrid.save_DeviceInfo("fee_model_id", HStategrid.DB_Data_Type.DATA_STR.value, update_fee.get("fee_model_id"), 0)
            HStategrid.save_FeeModel(contents)
    except Exception as e:
        HSyslog.log_info(f"tpp_to_hhd_1309'msg error: {msg}. {e}")
        info = {
            "result": 1
        }
        hhd_to_tpp_1310(info)
        return False


def tpp_to_hhd_107(msg):
    try:
        gun_id = msg.get("gun_id")
        cmd_addr = msg.get("cmd_addr")
    except Exception as e:
        HSyslog.log_info(f"tpp_to_hhd_107'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_117(msg):
    try:
        gun_id = msg.get("gun_id")
        fault_code = msg.get("fault_code")
    except Exception as e:
        HSyslog.log_info(f"tpp_to_hhd_117'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_119(msg):
    try:
        gun_id = msg.get("gun_id")
        warn_code = msg.get("warn_code")
    except Exception as e:
        HSyslog.log_info(f"tpp_to_hhd_119'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_407(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_info(f"tpp_to_hhd_407'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_409(msg):
    try:
        log_file_nums = msg.get("log_file_nums")

    except Exception as e:
        HSyslog.log_info(f"tpp_to_hhd_409'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_1101(msg):
    try:
        ota_type = msg.get("ota_type")
        ota_param = msg.get("ota_param")
        ota_url = msg.get("ota_url")
        ota_md5 = msg.get("ota_md5")
        try:
            md5_hash = hashlib.md5()
            urllib.request.urlretrieve(ota_url, HStategrid.ota_path)
            HSyslog.log_info(f"文件已下载到: {HStategrid.ota_path}")
            with open(HStategrid.ota_path, 'rb') as file:
                for chunk in iter(lambda: file.read(8192), b""):
                    md5_hash.update(chunk)
            if md5_hash.hexdigest() == ota_md5:
                info = {
                    "ota_status": 0,
                    "ota_md5": ota_md5
                }
            else:
                info = {
                    "ota_status": 1,
                    "ota_md5": ota_md5
                }
        except Exception as e:
            HSyslog.log_info(f"下载失败: {e}")
            info = {
                "ota_status": 1,
                "ota_md5": ota_md5
            }
        hhd_to_tpp_1102(info)
    except Exception as e:
        HSyslog.log_info(f"tpp_to_hhd_1101'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_801(msg):
    try:
        encrypt_data_len = msg.get("encrypt_data_len")
        encrypt_data = msg.get("encrypt_data")
        device_id = msg.get("device_id")
        encrypt_type = msg.get("encrypt_type")
        encrypt_version = msg.get("encrypt_version")
        encrypt_version_nums = msg.get("encrypt_version_nums")
    except Exception as e:
        HSyslog.log_info(f"tpp_to_hhd_801'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_509(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_info(f"tpp_to_hhd_509'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_33(msg):
    try:
        gun_id = msg.get("gun_id")
        result = msg.get("result")
        balance = msg.get("balance")
        HStategrid.Gun_list[gun_id - 1].set_gun_charge({"card_balance": balance})
        if result == 0:
            info = {
                "gun_id": gun_id - 1,
            }
            hhd_to_tpp_36(info)
        elif result == 1:
            info = {
                "gun_id": gun_id - 1,
                "result": 0,
                "reason": 0x02,
                "balance": balance
            }
            HHhdlist.platform_device_data.put([HHhdlist.topic_hqc_main_event_reply_check_vin, info])
        elif result == 2:
            info = {
                "gun_id": gun_id - 1,
                "result": 0,
                "reason": 0x01,
                "balance": balance
            }
            HHhdlist.platform_device_data.put([HHhdlist.topic_hqc_main_event_reply_check_vin, info])
        elif result == 3:
            info = {
                "gun_id": gun_id - 1,
                "result": 0,
                "reason": 0x03,
                "balance": balance
            }
            HHhdlist.platform_device_data.put([HHhdlist.topic_hqc_main_event_reply_check_vin, info])
    except Exception as e:
        HSyslog.log_info(f"tpp_to_hhd_33'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_35(msg):
    try:
        gun_id = msg.get("gun_id")
        result = msg.get("result")
        user_card_id = msg.get("user_card_id")
        if result == 0:
            info = {
                "gun_id": gun_id - 1,
            }
        else:
            info = {
                "gun_id": gun_id - 1,
                "result": 0,
                "reason": 0x00,
                "balance": HStategrid.Gun_list[gun_id - 1].get_gun_charge("card_balance")
            }
            HHhdlist.platform_device_data.put([HHhdlist.topic_hqc_main_event_reply_check_vin, info])
    except Exception as e:
        HSyslog.log_info(f"tpp_to_hhd_35'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_37(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_info(f"tpp_to_hhd_37'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_331(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_info(f"tpp_to_hhd_331'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_41(msg):
    try:
        gun_id = msg.get("gun_id") - 1
        charge_id = msg.get("charge_id")
        car_vin = msg.get("car_vin")
        user_balance = msg.get("user_balance")
        result = msg.get("result")
        reason = msg.get("reason")
        remain_mile = msg.get("remain_mile")
        chargeable_power = msg.get("chargeable_power")
        remain_num = msg.get("remain_num")
        user_phone = msg.get("user_phone")

        HStategrid.Gun_list[gun_id].set_gun_charge({"charge_id": charge_id})
        HStategrid.Gun_list[gun_id].set_gun_charge({"user_balance": user_balance})
        HStategrid.Gun_list[gun_id].set_gun_charge({"remain_mile": remain_mile})
        HStategrid.Gun_list[gun_id].set_gun_charge({"chargeable_power": chargeable_power})
        HStategrid.Gun_list[gun_id].set_gun_charge({"remain_num": remain_num})
        HStategrid.Gun_list[gun_id].set_gun_charge({"user_phone": user_phone})
        HStategrid.Gun_list[gun_id].set_gun_charge({"charge_policy": 0})
        HStategrid.Gun_list[gun_id].set_gun_charge({"charge_policy_param": 0})

        if result == 0:
            info = {
                "gun_id": gun_id,
                "result": 1,
                "reason": 0,
                "balance": user_balance,
                "stop_code": user_phone,
            }
            HHhdlist.platform_device_data.put([HHhdlist.topic_hqc_main_event_reply_check_vin, info])
            info = {
                "gun_id": gun_id,
                "result": "0000",
                "charge_id": HStategrid.Gun_list[gun_id].get_gun_charge("charge_id"),
            }
            hhd_to_tpp_8(info)
        else:
            info = {
                "gun_id": gun_id,
                "result": 0,
                "reason": 0,
                "balance": user_balance,
                "stop_code": user_phone,
            }
            HHhdlist.platform_device_data.put([HHhdlist.topic_hqc_main_event_reply_check_vin, info])
            info = {
                "gun_id": gun_id,
                "result": "2008",
                "charge_id": HStategrid.Gun_list[gun_id].get_gun_charge("charge_id"),
            }
            hhd_to_tpp_8(info)
    except Exception as e:
        HSyslog.log_info(f"tpp_to_hhd_41'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_43(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_info(f"tpp_to_hhd_43'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_45(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_info(f"tpp_to_hhd_45'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_81(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_info(f"tpp_to_hhd_81'msg error: {msg}. {e}")
        return False


'''################################################### 发送数据处理 ####################################################'''


def hhd_to_tpp_2(msg):
    try:
        info = {
            "device_id": HStategrid.Device_ID,
            "cmd_type": msg.get("cmd_type"),
            "cmd_num": 1,
            "result": msg.get("result"),
            "data_addr": msg.get("data_addr"),
            "datainfo": msg.get("datainfo"),
            "reserved": 0,
        }
        HStategrid.tpp_cmd_2(info)
    except Exception as e:
        HSyslog.log_info(f"hhd_to_tpp_2'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_4(msg):
    try:
        info = {
            "device_id": HStategrid.Device_ID,
            "cmd_type": msg.get("cmd_type"),
            "result": msg.get("result"),
            "data_addr": msg.get("data_addr"),
            "datainfo": msg.get("datainfo"),
            "reserved": 0,
        }
        HStategrid.tpp_cmd_4(info)
    except Exception as e:
        HSyslog.log_info(f"hhd_to_tpp_4'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_502(msg):
    try:
        info = {
            "device_id": HStategrid.Device_ID,
            "suss_num": msg.get("suss_num"),
            "result": msg.get("result")
        }
        HStategrid.tpp_cmd_502(info)
    except Exception as e:
        HSyslog.log_info(f"hhd_to_tpp_502'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_506(msg):
    try:
        info = {
            "charge_id": msg.get("charge_id"),
            "gun_id": msg.get("gun_id"),
            "result": msg.get("result"),
        }
        HStategrid.tpp_cmd_506(info)
    except Exception as e:
        HSyslog.log_info(f"hhd_to_tpp_506'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_508(msg):
    try:
        info = {
            "device_id": HStategrid.Device_ID,
            "suss_num": msg.get("suss_num"),
            "fail_num": msg.get("fail_num"),
            "fail_data_info": msg.get("fail_data_info"),
            "result": msg.get("result"),
        }
        HStategrid.tpp_cmd_508(info)
    except Exception as e:
        HSyslog.log_info(f"hhd_to_tpp_508'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_512(msg):
    try:
        info = {
            "device_id": HStategrid.Device_ID,
            "result": msg.get("result"),
            "fail_reason": msg.get("fail_reason"),
        }
        HStategrid.tpp_cmd_512(info)
    except Exception as e:
        HSyslog.log_info(f"hhd_to_tpp_512'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_514(msg):
    try:
        info = {
            "device_id": HStategrid.Device_ID,
            "data_num": msg.get("data_num"),
            "data_info": msg.get("data_info")
        }
        HStategrid.tpp_cmd_514(info)
    except Exception as e:
        HSyslog.log_info(f"hhd_to_tpp_514'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_516(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_info(f"hhd_to_tpp_516'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_6(msg):
    try:
        info = {
            "device_id": HStategrid.Device_ID,
            "gun_id": msg.get("gun_id"),
            "data_addr": msg.get("data_addr"),
            "cmd_num": msg.get("cmd_num"),
            "result": msg.get("result"),
        }
        HStategrid.tpp_cmd_6(info)
    except Exception as e:
        HSyslog.log_info(f"hhd_to_tpp_6'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_8(msg):
    try:
        gun_id = msg.get("gun_id")
        if HStategrid.Gun_list[gun_id].get_gun_charge("start_source") == 4:
            device_id = HStategrid.Device_ID
            result = msg.get("result")
            charge_id = HStategrid.Gun_list[gun_id].get_gun_charge("charge_id")
            if result == 0x00:
                info = {
                    "gun_id": gun_id + 1,
                    "device_id": device_id,
                    "result": "0000",
                    "charge_id": charge_id
                }
                HStategrid.tpp_cmd_8(info)
            else:
                info = {
                    "gun_id": gun_id + 1,
                    "device_id": device_id,
                    "result": result,
                    "charge_id": charge_id
                }
                HStategrid.tpp_cmd_8(info)
        elif HStategrid.Gun_list[gun_id].get_gun_charge("start_source") == 5:
            device_id = HStategrid.Device_ID
            result = msg.get("result")
            charge_id = msg.get("charge_id")
            info = {
                "gun_id": gun_id + 1,
                "device_id": device_id,
                "result": result,
                "charge_id": charge_id
            }
            HStategrid.tpp_cmd_8(info)
        elif HStategrid.Gun_list[gun_id].get_gun_charge("start_source") == 7:
            device_id = HStategrid.Device_ID
            result = msg.get("result")
            charge_id = msg.get("charge_id")
            info = {
                "gun_id": gun_id + 1,
                "device_id": device_id,
                "result": result,
                "charge_id": charge_id
            }
            HStategrid.tpp_cmd_8(info)
        else:
            device_id = HStategrid.Device_ID
            result = msg.get("result")
            charge_id = msg.get("charge_id")
            info = {
                "gun_id": gun_id + 1,
                "device_id": device_id,
                "result": result,
                "charge_id": charge_id
            }
            HStategrid.tpp_cmd_8(info)
    except Exception as e:
        HSyslog.log_info(f"hhd_to_tpp_8'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_12(msg):
    try:
        gun_id = msg.get("gun_id")
        result = msg.get("result")
        reason = msg.get("reason")
        info = {
            "gun_id": gun_id + 1,
            "charge_id": HStategrid.Gun_list[gun_id].get_gun_charge("charge_id"),
            "device_id": HStategrid.Device_ID,
            "result": result,
        }
        HStategrid.tpp_cmd_12(info)
    except Exception as e:
        HSyslog.log_info(f"hhd_to_tpp_12'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_14(msg):
    try:
        power_model_list = []
        power_model_num = HStategrid.get_DeviceInfo("00111")
        device_power = HStategrid.get_DeviceInfo("00121")
        power_model_kw = HStategrid.get_DeviceInfo("00117")
        if power_model_num is None or power_model_num == 0 or device_power is None or device_power == 0 or power_model_kw is None or power_model_kw == 0:
            get_param = {
                "param_list": [111, 121, 117],
                "device_type": HHhdlist.device_param_type.chargeSys.value,
                "device_num": 0
            }
            power_model_num = HStategrid.get_DeviceInfo("00111")
            device_power = HStategrid.get_DeviceInfo("00121")
            power_model_kw = HStategrid.get_DeviceInfo("00117")

        for i in range(0, power_model_num):
            power_model_list.append({"power_model_status": 0, "power_model_kw": power_model_kw})
        info = {
            "device_id": HStategrid.Device_ID,
            "power_model_num": power_model_num,
            "device_power": device_power,
            "power_model_list": power_model_list,
        }
        HStategrid.tpp_cmd_14(info)
    except Exception as e:
        HSyslog.log_info(f"hhd_to_tpp_14'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_16(msg):
    try:
        info = {
            "device_id": HStategrid.Device_ID,
            "gun_id": msg.get("gun_id"),
            "result": msg.get("result"),
            "gun_power": msg.get("gun_power"),
        }
        HStategrid.tpp_cmd_16(info)
    except Exception as e:
        HSyslog.log_info(f"hhd_to_tpp_16'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_504(msg):
    try:
        info = {
            "device_id": HStategrid.Device_ID,
            "result": msg.get("result"),
        }
        HStategrid.tpp_cmd_504(info)
    except Exception as e:
        HSyslog.log_info(f"hhd_to_tpp_504'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_18(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_info(f"hhd_to_tpp_18'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_20(msg):
    try:
        info = {
            "device_id": HStategrid.Device_ID,
            "gun_id": msg.get("gun_id"),
            "result": msg.get("result"),
        }
        HStategrid.tpp_cmd_20(info)
    except Exception as e:
        HSyslog.log_info(f"hhd_to_tpp_20'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_102(msg):
    try:
        info = {
            "device_id": HStategrid.Device_ID,
            "heart_index": HStategrid.Heartbeat,
        }
        HStategrid.Heartbeat += 1
        HStategrid.tpp_cmd_102(info)
    except Exception as e:
        HSyslog.log_info(f"hhd_to_tpp_102'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_104(msg=None):
    try:
        if msg is None:
            for gun_info in HStategrid.Gun_list:
                gun_id = gun_info.gun_id
                charge_status = gun_info.get_gun_status()
                if charge_status in [HStategrid.Gun_Status.Idle.value, HStategrid.Gun_Status.Plugged_in_not_charging.value, HStategrid.Gun_Status.Self_checking.value]:
                    info = {
                        "device_id": HStategrid.Device_ID,
                        "gun_num": HHhdlist.gun_num,
                        "gun_id": gun_id + 1,
                        "gun_type": gun_info.get_gun_type(),
                        "charge_status": charge_status,
                        "soc_now": 0,
                        "fault_code": "0000",
                        "car_connection_status": gun_info.get_gun_car_connect_status(),
                        "charge_cost": 0,
                        "dc_charge_vol": HHhdlist.gun.get(gun_id, {}).get(112, 0),
                        "dc_charge_cur": HHhdlist.gun.get(gun_id, {}).get(113, 0),
                        "bms_need_vol": 0,
                        "bms_need_cur": 0,
                        "bms_charge_mode": 2,
                        "ac_a_vol": 3800,
                        "ac_b_vol": 3800,
                        "ac_c_vol": 3800,
                        "ac_a_cur": 0,
                        "ac_b_cur": 0,
                        "ac_c_cur": 0,
                        "charge_full_time": 0,
                        "charge_time": 0,
                        "charge_kw_amount": 0,
                        "start_meter": HHhdlist.meter.get(gun_id, {}).get(0, 0),
                        "now_meter": HHhdlist.meter.get(gun_id, {}).get(0, 0),
                        "start_charge_type": 0,
                        "charge_policy": 0,
                        "charge_policy_param": 0,
                        "book_flag": 0,
                        "charge_id": "",
                        "book_timeout": 0,
                        "book_start_time": 0,
                        "start_card_balance": 0,
                        "charge_mode": 0,
                        "charge_power_kw": 0,
                        "device_temperature": 0,
                    }
                    HStategrid.tpp_cmd_104(info)
                elif charge_status in [HStategrid.Gun_Status.Charging.value, HStategrid.Gun_Status.Stopping.value]:
                    gun_list = HStategrid.Gun_list[gun_id].get_gun_charge_gun_id()
                    start_charge_type = 1
                    if HStategrid.Gun_list[gun_id].get_gun_charge("start_source") == 5:
                        start_charge_type = 0
                    if len(gun_list) == 1:
                        charge_mode = 0
                    else:
                        charge_mode = 1
                    if HStategrid.Gun_list[gun_id].gun_charge_cost is True and HStategrid.Gun_list[gun_id].gun_charge_session is True:
                        info = {
                            "device_id": HStategrid.Device_ID,
                            "gun_num": HHhdlist.gun_num,
                            "gun_id": gun_id + 1,
                            "gun_type": gun_info.get_gun_type(),
                            "charge_status": charge_status,
                            "soc_now": HHhdlist.bms.get(gun_id, {}).get(106, 0),
                            "fault_code": "0000",
                            "car_connection_status": 2,
                            "charge_cost": 0,
                            "dc_charge_vol": HHhdlist.gun.get(gun_id, {}).get(112, 0),
                            "dc_charge_cur": 0,
                            "bms_need_vol": HHhdlist.bms.get(gun_id, {}).get(100, 0),
                            "bms_need_cur": 0,
                            "bms_charge_mode": HHhdlist.bms.get(gun_id, {}).get(102, 0),
                            "ac_a_vol": 3800,
                            "ac_b_vol": 3800,
                            "ac_c_vol": 3800,
                            "ac_a_cur": 0,
                            "ac_b_cur": 0,
                            "ac_c_cur": 0,
                            "charge_full_time": HHhdlist.bms.get(gun_id, {}).get(107, 0),
                            "charge_time": HStategrid.Gun_list[gun_id].get_gun_charge("charge_time"),
                            "charge_kw_amount": 0,
                            "start_meter": 0,
                            "now_meter": 0,
                            "start_charge_type": start_charge_type,
                            "charge_policy": HStategrid.Gun_list[gun_id].get_gun_charge("charge_policy"),
                            "charge_policy_param": HStategrid.Gun_list[gun_id].get_gun_charge("charge_policy_param"),
                            "book_flag": 0,
                            "charge_id": HStategrid.Gun_list[gun_id].get_gun_charge("charge_id"),
                            "book_timeout": 0,
                            "book_start_time": 0,
                            "start_card_balance": 0,
                            "charge_mode": charge_mode,
                            "charge_power_kw": 0,
                            "device_temperature": 800,
                        }
                        for gun in gun_list:
                            HSyslog.log_info(f"{gun}: {HStategrid.Gun_list[gun].get_gun_charge()}")
                            HSyslog.log_info(f"{gun}: {HHhdlist.gun.get(gun, {})}")
                            info["charge_cost"] += HStategrid.Gun_list[gun].get_gun_charge("total_cost") // 10
                            info["dc_charge_cur"] += HHhdlist.gun.get(gun, {}).get(113, 0)
                            info["charge_kw_amount"] += HStategrid.Gun_list[gun].get_gun_charge("total_energy")
                            info["bms_need_cur"] += HHhdlist.bms.get(gun, {}).get(101, 0)
                            info["start_meter"] += HStategrid.Gun_list[gun].get_gun_charge("start_meter_value")
                            info["now_meter"] += HHhdlist.meter.get(gun, {}).get(0, 0)
                            info["charge_power_kw"] += HHhdlist.gun.get(gun, {}).get(115, 0) // 100
                    else:
                        info = {
                            "device_id": HStategrid.Device_ID,
                            "gun_num": HHhdlist.gun_num,
                            "gun_id": gun_id + 1,
                            "gun_type": gun_info.get_gun_type(),
                            "charge_status": charge_status,
                            "soc_now": HHhdlist.bms.get(gun_id, {}).get(106, 0),
                            "fault_code": "0000",
                            "car_connection_status": 2,
                            "charge_cost": 0,
                            "dc_charge_vol": HHhdlist.gun.get(gun_id, {}).get(112, 0),
                            "dc_charge_cur": 0,
                            "bms_need_vol": HHhdlist.bms.get(gun_id, {}).get(100, 0),
                            "bms_need_cur": 0,
                            "bms_charge_mode": HHhdlist.bms.get(gun_id, {}).get(102, 0),
                            "ac_a_vol": 3800,
                            "ac_b_vol": 3800,
                            "ac_c_vol": 3800,
                            "ac_a_cur": 0,
                            "ac_b_cur": 0,
                            "ac_c_cur": 0,
                            "charge_full_time": HHhdlist.bms.get(gun_id, {}).get(107, 0),
                            "charge_time": 0,
                            "charge_kw_amount": 0,
                            "start_meter": 0,
                            "now_meter": 0,
                            "start_charge_type": start_charge_type,
                            "charge_policy": HStategrid.Gun_list[gun_id].get_gun_charge("charge_policy"),
                            "charge_policy_param": HStategrid.Gun_list[gun_id].get_gun_charge("charge_policy_param"),
                            "book_flag": 0,
                            "charge_id": HStategrid.Gun_list[gun_id].get_gun_charge("charge_id"),
                            "book_timeout": 0,
                            "book_start_time": 0,
                            "start_card_balance": 0,
                            "charge_mode": charge_mode,
                            "charge_power_kw": 0,
                            "device_temperature": 800,
                        }
                        for gun in gun_list:
                            HSyslog.log_info(f"{gun}: {HStategrid.Gun_list[gun].get_gun_charge()}")
                            HSyslog.log_info(f"{gun}: {HHhdlist.gun.get(gun, {})}")
                            info["dc_charge_cur"] += HHhdlist.gun.get(gun, {}).get(113, 0)
                            info["bms_need_cur"] += HHhdlist.bms.get(gun, {}).get(101, 0)
                            info["start_meter"] += HStategrid.Gun_list[gun].get_gun_charge("start_meter_value")
                            info["now_meter"] += HHhdlist.meter.get(gun, {}).get(0, 0)
                            info["charge_power_kw"] += HHhdlist.gun.get(gun, {}).get(115, 0) // 100
                    HStategrid.tpp_cmd_104(info)
                elif charge_status == HStategrid.Gun_Status.Charging_completed_not_unplugged.value:
                    gun_list = HStategrid.Gun_list[gun_id].get_gun_charge_gun_id()
                    start_source = HStategrid.Gun_list[gun_id].get_gun_charge_reserve("start_source")
                    start_charge_type = {
                        0: 0,
                        1: 1,
                        2: 2,
                        3: 2,
                    }.get(start_source, 1)
                    if len(gun_list) == 1:
                        charge_mode = 0
                    else:
                        charge_mode = 1
                    info = {
                        "device_id": HStategrid.Device_ID,
                        "gun_num": HHhdlist.gun_num,
                        "gun_id": gun_id + 1,
                        "gun_type": gun_info.get_gun_type(),
                        "charge_status": charge_status,
                        "soc_now": HHhdlist.bms.get(gun_id, {}).get(106, 0),
                        "fault_code": "0000",
                        "car_connection_status": 2,
                        "charge_cost": 0,
                        "dc_charge_vol": HHhdlist.gun.get(gun_id, {}).get(112, 0),
                        "dc_charge_cur": 0,
                        "bms_need_vol": HHhdlist.bms.get(gun_id, {}).get(100, 0),
                        "bms_need_cur": 0,
                        "bms_charge_mode": HHhdlist.bms.get(gun_id, {}).get(102, 0),
                        "ac_a_vol": 3800,
                        "ac_b_vol": 3800,
                        "ac_c_vol": 3800,
                        "ac_a_cur": 0,
                        "ac_b_cur": 0,
                        "ac_c_cur": 0,
                        "charge_full_time": HHhdlist.bms.get(gun_id, {}).get(107, 0),
                        "charge_time": HStategrid.Gun_list[gun_id].get_gun_charge_reserve("charge_time"),
                        "charge_kw_amount": 0,
                        "start_meter": 0,
                        "now_meter": 0,
                        "start_charge_type": start_charge_type,
                        "charge_policy": HStategrid.Gun_list[gun_id].get_gun_charge_reserve("charge_policy"),
                        "charge_policy_param": HStategrid.Gun_list[gun_id].get_gun_charge_reserve("charge_policy_param"),
                        "book_flag": 0,
                        "charge_id": HStategrid.Gun_list[gun_id].get_gun_charge_reserve("cloud_session_id"),
                        "book_timeout": 0,
                        "book_start_time": 0,
                        "start_card_balance": 0,
                        "charge_mode": charge_mode,
                        "charge_power_kw": 0,
                        "device_temperature": 800,
                    }
                    for gun in gun_list:
                        info["charge_cost"] += HStategrid.Gun_list[gun].get_gun_charge_reserve("total_cost") // 10
                        info["dc_charge_cur"] += HHhdlist.gun.get(gun, {}).get(113, 0)
                        info["charge_kw_amount"] += HStategrid.Gun_list[gun].get_gun_charge_reserve("total_energy")
                        info["bms_need_cur"] += HHhdlist.bms.get(gun, {}).get(101, 0)
                        info["start_meter"] += HStategrid.Gun_list[gun].get_gun_charge_reserve("start_meter_value")
                        info["now_meter"] += HHhdlist.meter.get(gun, {}).get(0, 0)
                        info["charge_power_kw"] += HHhdlist.gun.get(gun, {}).get(115, 0) // 100
                    HStategrid.tpp_cmd_104(info)
        else:
            gun_id = msg.get("gun_id")
            charge_status = HStategrid.Gun_list[gun_id].get_gun_status()
            if charge_status in [HStategrid.Gun_Status.Idle.value, HStategrid.Gun_Status.Plugged_in_not_charging.value, HStategrid.Gun_Status.Self_checking.value]:
                info = {
                    "device_id": HStategrid.Device_ID,
                    "gun_num": HHhdlist.gun_num,
                    "gun_id": gun_id + 1,
                    "gun_type": HStategrid.Gun_list[gun_id].get_gun_type(),
                    "charge_status": charge_status,
                    "soc_now": 0,
                    "fault_code": "0000",
                    "car_connection_status": HStategrid.Gun_list[gun_id].get_gun_car_connect_status(),
                    "charge_cost": 0,
                    "dc_charge_vol": HHhdlist.gun.get(gun_id, {}).get(112, 0),
                    "dc_charge_cur": HHhdlist.gun.get(gun_id, {}).get(113, 0),
                    "bms_need_vol": 0,
                    "bms_need_cur": 0,
                    "bms_charge_mode": 2,
                    "ac_a_vol": 3800,
                    "ac_b_vol": 3800,
                    "ac_c_vol": 3800,
                    "ac_a_cur": 0,
                    "ac_b_cur": 0,
                    "ac_c_cur": 0,
                    "charge_full_time": 0,
                    "charge_time": 0,
                    "charge_kw_amount": 0,
                    "start_meter": HHhdlist.meter.get(gun_id, {}).get(0, 0),
                    "now_meter": HHhdlist.meter.get(gun_id, {}).get(0, 0),
                    "start_charge_type": 0,
                    "charge_policy": 0,
                    "charge_policy_param": 0,
                    "book_flag": 0,
                    "charge_id": "",
                    "book_timeout": 0,
                    "book_start_time": 0,
                    "start_card_balance": 0,
                    "charge_mode": 0,
                    "charge_power_kw": 0,
                    "device_temperature": 0,
                }
                HStategrid.tpp_cmd_104(info)
            elif charge_status in [HStategrid.Gun_Status.Charging.value, HStategrid.Gun_Status.Stopping.value]:
                gun_list = HStategrid.Gun_list[gun_id].get_gun_charge_gun_id()
                start_charge_type = 1
                if HStategrid.Gun_list[gun_id].get_gun_charge("start_source") == 5:
                    start_charge_type = 0
                if len(gun_list) == 1:
                    charge_mode = 0
                else:
                    charge_mode = 1
                if HStategrid.Gun_list[gun_id].gun_charge_cost and HStategrid.Gun_list[gun_id].gun_charge_session:
                    info = {
                        "device_id": HStategrid.Device_ID,
                        "gun_num": HHhdlist.gun_num,
                        "gun_id": gun_id + 1,
                        "gun_type": HStategrid.Gun_list[gun_id].get_gun_type(),
                        "charge_status": charge_status,
                        "soc_now": HHhdlist.bms.get(gun_id, {}).get(106, 0),
                        "fault_code": "0000",
                        "car_connection_status": 2,
                        "charge_cost": 0,
                        "dc_charge_vol": HHhdlist.gun.get(gun_id, {}).get(112, 0),
                        "dc_charge_cur": 0,
                        "bms_need_vol": HHhdlist.bms.get(gun_id, {}).get(100, 0),
                        "bms_need_cur": 0,
                        "bms_charge_mode": HHhdlist.bms.get(gun_id, {}).get(102, 0),
                        "ac_a_vol": 3800,
                        "ac_b_vol": 3800,
                        "ac_c_vol": 3800,
                        "ac_a_cur": 0,
                        "ac_b_cur": 0,
                        "ac_c_cur": 0,
                        "charge_full_time": HHhdlist.bms.get(gun_id, {}).get(107, 0),
                        "charge_time": HStategrid.Gun_list[gun_id].get_gun_charge("charge_time"),
                        "charge_kw_amount": 0,
                        "start_meter": 0,
                        "now_meter": 0,
                        "start_charge_type": start_charge_type,
                        "charge_policy": HStategrid.Gun_list[gun_id].get_gun_charge("charge_policy"),
                        "charge_policy_param": HStategrid.Gun_list[gun_id].get_gun_charge("charge_policy_param"),
                        "book_flag": 0,
                        "charge_id": HStategrid.Gun_list[gun_id].get_gun_charge("charge_id"),
                        "book_timeout": 0,
                        "book_start_time": 0,
                        "start_card_balance": 0,
                        "charge_mode": charge_mode,
                        "charge_power_kw": 0,
                        "device_temperature": 800,
                    }
                    for gun in gun_list:
                        info["charge_cost"] += HStategrid.Gun_list[gun].get_gun_charge("total_cost") // 10
                        info["dc_charge_cur"] += HHhdlist.gun.get(gun, {}).get(113, 0)
                        info["charge_kw_amount"] += HStategrid.Gun_list[gun].get_gun_charge("total_energy")
                        info["bms_need_cur"] += HHhdlist.bms.get(gun, {}).get(101, 0)
                        info["start_meter"] += HStategrid.Gun_list[gun].get_gun_charge("start_meter_value")
                        info["now_meter"] += HHhdlist.meter.get(gun, {}).get(0, 0)
                        info["charge_power_kw"] += HHhdlist.gun.get(gun, {}).get(115, 0) // 100
                else:
                    info = {
                        "device_id": HStategrid.Device_ID,
                        "gun_num": HHhdlist.gun_num,
                        "gun_id": gun_id + 1,
                        "gun_type": HStategrid.Gun_list[gun_id].get_gun_type(),
                        "charge_status": charge_status,
                        "soc_now": HHhdlist.bms.get(gun_id, {}).get(106, 0),
                        "fault_code": "0000",
                        "car_connection_status": 2,
                        "charge_cost": 0,
                        "dc_charge_vol": HHhdlist.gun.get(gun_id, {}).get(112, 0),
                        "dc_charge_cur": 0,
                        "bms_need_vol": HHhdlist.bms.get(gun_id, {}).get(100, 0),
                        "bms_need_cur": 0,
                        "bms_charge_mode": HHhdlist.bms.get(gun_id, {}).get(102, 0),
                        "ac_a_vol": 3800,
                        "ac_b_vol": 3800,
                        "ac_c_vol": 3800,
                        "ac_a_cur": 0,
                        "ac_b_cur": 0,
                        "ac_c_cur": 0,
                        "charge_full_time": HHhdlist.bms.get(gun_id, {}).get(107, 0),
                        "charge_time": 0,
                        "charge_kw_amount": 0,
                        "start_meter": 0,
                        "now_meter": 0,
                        "start_charge_type": start_charge_type,
                        "charge_policy": HStategrid.Gun_list[gun_id].get_gun_charge("charge_policy"),
                        "charge_policy_param": HStategrid.Gun_list[gun_id].get_gun_charge("charge_policy_param"),
                        "book_flag": 0,
                        "charge_id": HStategrid.Gun_list[gun_id].get_gun_charge("charge_id"),
                        "book_timeout": 0,
                        "book_start_time": 0,
                        "start_card_balance": 0,
                        "charge_mode": charge_mode,
                        "charge_power_kw": HHhdlist.gun.get(gun_id, {}).get(115, 0) // 100,
                        "device_temperature": 800,
                    }
                    for gun in gun_list:
                        info["dc_charge_cur"] += HHhdlist.gun.get(gun, {}).get(113, 0)
                        info["bms_need_cur"] += HHhdlist.bms.get(gun, {}).get(101, 0)
                        info["start_meter"] += HStategrid.Gun_list[gun].get_gun_charge("start_meter_value")
                        info["now_meter"] += HHhdlist.meter.get(gun, {}).get(0, 0)
                        info["charge_power_kw"] += HHhdlist.gun.get(gun, {}).get(115, 0) // 100
                HStategrid.tpp_cmd_104(info)
            elif charge_status == HStategrid.Gun_Status.Charging_completed_not_unplugged.value:
                gun_list = HStategrid.Gun_list[gun_id].get_gun_charge_gun_id()
                start_source = HStategrid.Gun_list[gun_id].get_gun_charge_reserve("start_source")
                start_charge_type = {
                    0: 0,
                    1: 1,
                    2: 2,
                    3: 2,
                }.get(start_source, 1)
                if len(gun_list) == 1:
                    charge_mode = 0
                else:
                    charge_mode = 1
                info = {
                    "device_id": HStategrid.Device_ID,
                    "gun_num": HHhdlist.gun_num,
                    "gun_id": gun_id + 1,
                    "gun_type": HStategrid.Gun_list[gun_id].get_gun_type(),
                    "charge_status": charge_status,
                    "soc_now": HHhdlist.bms.get(gun_id, {}).get(106, 0),
                    "fault_code": "0000",
                    "car_connection_status": 2,
                    "charge_cost": 0,
                    "dc_charge_vol": HHhdlist.gun.get(gun_id, {}).get(112, 0),
                    "dc_charge_cur": 0,
                    "bms_need_vol": HHhdlist.bms.get(gun_id, {}).get(100, 0),
                    "bms_need_cur": 0,
                    "bms_charge_mode": HHhdlist.bms.get(gun_id, {}).get(102, 0),
                    "ac_a_vol": 3800,
                    "ac_b_vol": 3800,
                    "ac_c_vol": 3800,
                    "ac_a_cur": 0,
                    "ac_b_cur": 0,
                    "ac_c_cur": 0,
                    "charge_full_time": HHhdlist.bms.get(gun_id, {}).get(107, 0),
                    "charge_time": HStategrid.Gun_list[gun_id].get_gun_charge_reserve("charge_time"),
                    "charge_kw_amount": 0,
                    "start_meter": 0,
                    "now_meter": 0,
                    "start_charge_type": start_charge_type,
                    "charge_policy": HStategrid.Gun_list[gun_id].get_gun_charge_reserve("charge_policy"),
                    "charge_policy_param": HStategrid.Gun_list[gun_id].get_gun_charge_reserve("charge_policy_param"),
                    "book_flag": 0,
                    "charge_id": HStategrid.Gun_list[gun_id].get_gun_charge_reserve("charge_id"),
                    "book_timeout": 0,
                    "book_start_time": 0,
                    "start_card_balance": 0,
                    "charge_mode": charge_mode,
                    "charge_power_kw": 0,
                    "device_temperature": 800,
                }
                for gun in gun_list:
                    info["charge_cost"] += HStategrid.Gun_list[gun].get_gun_charge_reserve("total_cost") // 10
                    info["dc_charge_cur"] += HHhdlist.gun.get(gun, {}).get(113, 0)
                    info["charge_kw_amount"] += HStategrid.Gun_list[gun].get_gun_charge_reserve("total_energy")
                    info["bms_need_cur"] += HHhdlist.bms.get(gun, {}).get(101, 0)
                    info["start_meter"] += HStategrid.Gun_list[gun].get_gun_charge_reserve("start_meter_value")
                    info["now_meter"] += HHhdlist.meter.get(gun, {}).get(0, 0)
                    info["charge_power_kw"] += HHhdlist.gun.get(gun, {}).get(115, 0) // 100
                HStategrid.tpp_cmd_104(info)
    except Exception as e:
        HSyslog.log_info(f"hhd_to_tpp_104'msg error: {e}")
        return False


def hhd_to_tpp_106(msg):
    try:

        info = {
            "device_power_model_num": HStategrid.get_DeviceInfo("00111"),
            "device_power": HStategrid.get_DeviceInfo("00121"),
            "device_id": HStategrid.Device_ID,
            "offline_is": 0x01,
            "device_version": HStategrid.get_VerInfoEvt(HHhdlist.device_ctrl_type.DTU.value)[1],
            "device_type": 0x00,
            "device_start_nums": HStategrid.get_DeviceInfo("device_start_nums"),
            "report_mode": 2,
            "sign_interval": 30,
            "TCU_flag": 0,
            "gun_num": HStategrid.get_DeviceInfo("00110"),
            "heart_interval": 30,
            "heart_timeout_nums": 3,
            "charge_record_num": HStategrid.get_DeviceInfo("charge_record_num"),
            "system_time": HStategrid.get_datetime_timestamp(),
            "device_charge_time": HStategrid.get_DeviceInfo("device_charge_time"),
            "device_start_time": HStategrid.get_DeviceInfo("device_start_time"),
            "sign_code": "",
            "mac_addr": HStategrid.get_mac_address("eth1"),
            "ccu_version": HStategrid.get_VerInfoEvt(HHhdlist.device_ctrl_type.DTU.value)[1],
        }
        HStategrid.tpp_cmd_106(info)
        for gun_info in HStategrid.Gun_list:
            gun_id = str("{:02}".format(gun_info.gun_id + 1))
            gun_info.set_gun_qr(f"{HStategrid.gun_qrcode}{HStategrid.Device_ID}{gun_id}")
            HStategrid.save_DeviceInfo(f"qrcode_{gun_info.gun_id + 1}", HStategrid.DB_Data_Type.DATA_STR.value, f"{HStategrid.gun_qrcode}{HStategrid.Device_ID}{gun_info.gun_id + 1}", 0)
    except Exception as e:
        HSyslog.log_info(f"hhd_to_tpp_106'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_114(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_info(f"hhd_to_tpp_114'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_302(msg=None):
    try:
        pass
    except Exception as e:
        HSyslog.log_info(f"hhd_to_tpp_302'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_304(msg):
    try:
        gun_id = msg.get("gun_id")
        info = {
            "gun_id": gun_id + 1,
            "device_id": HStategrid.Device_ID,
            "charge_id": HStategrid.Gun_list[gun_id].get_gun_charge("charge_id"),
            "charge_status": HStategrid.Gun_list[gun_id].get_gun_status(),
            "brm_bms_connect_version": HHhdlist.bms.get(gun_id, {}).get(0, 0),
            "brm_battery_type": HHhdlist.bms.get(gun_id, {}).get(1, 0),
            "brm_battery_power": HHhdlist.bms.get(gun_id, {}).get(2, 0),
            "brm_battery_voltage": HHhdlist.bms.get(gun_id, {}).get(3, 0),
            "brm_battery_supplier": HHhdlist.bms.get(gun_id, {}).get(4, 0),
            # "brm_battery_seq": HHhdlist.bms.get(gun_id, {}).get(5, 0),
            "brm_battery_seq": 0,
            "brm_battery_produce_year": 0,
            "brm_battery_produce_month": 0,
            "brm_battery_produce_day": 0,
            "brm_battery_charge_count": HHhdlist.bms.get(gun_id, {}).get(7, 0),
            "brm_battery_property_identification": HHhdlist.bms.get(gun_id, {}).get(8, 0),
            "brm_vin": HHhdlist.bms.get(gun_id, {}).get(9, 0),
            "brm_BMS_version": HHhdlist.bms.get(gun_id, {}).get(10, 0),
            "bcp_max_voltage": HHhdlist.bms.get(gun_id, {}).get(11, 0),
            "bcp_max_current": HHhdlist.bms.get(gun_id, {}).get(12, 0),
            "bcp_max_power": HHhdlist.bms.get(gun_id, {}).get(13, 0),
            "bcp_total_voltage": HHhdlist.bms.get(gun_id, {}).get(14, 0),
            "bcp_max_temperature": HHhdlist.bms.get(gun_id, {}).get(15, 0),
            "bcp_battery_soc": HHhdlist.bms.get(gun_id, {}).get(16, 0),
            "bcp_battery_soc_current_voltage": HHhdlist.bms.get(gun_id, {}).get(17, 0),
            "bro_BMS_isReady": 0xAA,
            "cro_cevice_isReady": 0xAA,
        }
        HStategrid.tpp_cmd_304(info)
    except Exception as e:
        HSyslog.log_info(f"hhd_to_tpp_304'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_306(msg=None):
    try:
        if msg is None:
            for gun_info in HStategrid.Gun_list:
                if gun_info.get_gun_status() == HStategrid.Gun_Status.Charging.value:
                    gun_id = gun_info.gun_id
                    info = {
                        "gun_id": gun_id + 1,
                        "device_id": HStategrid.Device_ID,
                        "charge_id": HStategrid.Gun_list[gun_id].get_gun_charge("charge_id"),
                        "charge_status": gun_info.get_gun_status(),
                        "bcl_voltage_need": HHhdlist.bms.get(gun_id, {}).get(100, 0),
                        "bcl_current_need": HHhdlist.bms.get(gun_id, {}).get(101, 0),
                        "bcl_charge_mode": HHhdlist.bms.get(gun_id, {}).get(102, 0),
                        "bcs_test_voltage": HHhdlist.bms.get(gun_id, {}).get(103, 0),
                        "bcs_test_current": HHhdlist.bms.get(gun_id, {}).get(104, 0),
                        "bcs_max_single_voltage": HHhdlist.bms.get(gun_id, {}).get(105, 0),
                        "bcs_max_single_no": 0,
                        "bcs_current_soc": HHhdlist.bms.get(gun_id, {}).get(106, 0),
                        "last_charge_time": HHhdlist.bms.get(gun_id, {}).get(107, 0),
                        "bsm_single_no": HHhdlist.bms.get(gun_id, {}).get(108, 0),
                        "bsm_max_temperature": HHhdlist.bms.get(gun_id, {}).get(109, 0),
                        "bsm_max_temperature_check_no": HHhdlist.bms.get(gun_id, {}).get(110, 0),
                        "bsm_min_temperature": HHhdlist.bms.get(gun_id, {}).get(111, 0),
                        "bsm_min_temperature_check_no": HHhdlist.bms.get(gun_id, {}).get(112, 0),
                        "bsm_voltage_too_high_or_too_low": 0x00,
                        "bsm_car_battery_soc_too_high_or_too_low": 0x00,
                        "bsm_car_battery_charge_over_current": 0x00,
                        "bsm_battery_temperature_too_high": 0x00,
                        "bsm_battery_insulation_state": 0x00,
                        "bsm_battery_connect_state": 0x00,
                        "bsm_allow_charge": HHhdlist.bms.get(gun_id, {}).get(113, 0),
                    }
                    HStategrid.tpp_cmd_306(info)
        else:
            gun_id = msg.get("gun_id")
            info = {
                "gun_id": gun_id + 1,
                "device_id": HStategrid.Device_ID,
                "charge_id": HStategrid.Gun_list[gun_id].get_gun_charge("charge_id"),
                "charge_status": 2,
                "bcl_voltage_need": HHhdlist.bms.get(gun_id, {}).get(100, 0),
                "bcl_current_need": HHhdlist.bms.get(gun_id, {}).get(101, 0),
                "bcl_charge_mode": HHhdlist.bms.get(gun_id, {}).get(102, 0),
                "bcs_test_voltage": HHhdlist.bms.get(gun_id, {}).get(103, 0),
                "bcs_test_current": HHhdlist.bms.get(gun_id, {}).get(104, 0),
                "bcs_max_single_voltage": HHhdlist.bms.get(gun_id, {}).get(105, 0),
                "bcs_max_single_no": 0,
                "bcs_current_soc": HHhdlist.bms.get(gun_id, {}).get(106, 0),
                "last_charge_time": HHhdlist.bms.get(gun_id, {}).get(107, 0),
                "bsm_single_no": HHhdlist.bms.get(gun_id, {}).get(108, 0),
                "bsm_max_temperature": HHhdlist.bms.get(gun_id, {}).get(109, 0),
                "bsm_max_temperature_check_no": HHhdlist.bms.get(gun_id, {}).get(110, 0),
                "bsm_min_temperature": HHhdlist.bms.get(gun_id, {}).get(111, 0),
                "bsm_min_temperature_check_no": HHhdlist.bms.get(gun_id, {}).get(112, 0),
                "bsm_voltage_too_high_or_too_low": 0x00,
                "bsm_car_battery_soc_too_high_or_too_low": 0x00,
                "bsm_car_battery_charge_over_current": 0x00,
                "bsm_battery_temperature_too_high": 0x00,
                "bsm_battery_insulation_state": 0x00,
                "bsm_battery_connect_state": 0x00,
                "bsm_allow_charge": HHhdlist.bms.get(gun_id, {}).get(113, 0),
            }
            HStategrid.tpp_cmd_306(info)
    except Exception as e:
        HSyslog.log_info(f"hhd_to_tpp_306'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_308(msg):
    try:
        gun_id = msg.get("gun_id")
        info = {
            "gun_id": gun_id + 1,
            "device_id": HStategrid.Device_ID,
            "charge_id": HStategrid.Gun_list[gun_id].get_gun_charge("charge_id"),
            "charge_status": 7,
            "cst_stop_reason": 0,
            "cst_fault_reason": 0,
            "cst_error_reason": 0,
        }
        HStategrid.tpp_cmd_308(info)
    except Exception as e:
        HSyslog.log_info(f"hhd_to_tpp_308'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_310(msg):
    try:
        gun_id = msg.get("gun_id")
        info = {
            "gun_id": gun_id + 1,
            "device_id": HStategrid.Device_ID,
            "charge_id": HStategrid.Gun_list[gun_id].get_gun_charge("charge_id"),
            "charge_status": 7,
            "bst_stop_reason": 0,
            "bst_fault_reason": 0,
            "bst_error_reason": 0,
        }
        HStategrid.tpp_cmd_310(info)
    except Exception as e:
        HSyslog.log_info(f"hhd_to_tpp_310'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_312(msg):
    try:
        gun_id = msg.get("gun_id")
        info = {
            "gun_id": gun_id + 1,
            "device_id": HStategrid.Device_ID,
            "charge_id": HStategrid.Gun_list[gun_id].get_gun_charge("charge_id"),
            "charge_status": HStategrid.Gun_list[gun_id].get_gun_status(),
            "bst_stop_soc": HHhdlist.bms.get(gun_id, {}).get(106, 0),
            "bsd_battery_low_voltage": HHhdlist.bms.get(gun_id, {}).get(18, 0),
            "bsd_battery_high_voltage": HHhdlist.bms.get(gun_id, {}).get(105, 0),
            "bsd_battery_low_temperature": HHhdlist.bms.get(gun_id, {}).get(111, 0),
            "bsd_battery_high_temperature": HHhdlist.bms.get(gun_id, {}).get(109, 0),
            "bem_2560_00": 0x00,
            "bem_2560_AA": 0x00,
            "bem_sync_max_output_timeout": 0x00,
            "bem_prep_complete_timeout": 0x00,
            "bem_status_timeout": 0x00,
            "bem_stop_charge_timeout": 0x00,
            "bem_stats_timeout": 0x00,
            "bem_other": 0x00,
        }
        HStategrid.tpp_cmd_312(info)
    except Exception as e:
        HSyslog.log_info(f"hhd_to_tpp_312'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_202(msg):
    try:
        gun_id = msg.get("gun_id")
        if len(HStategrid.Gun_list[gun_id].get_gun_charge_gun_id()) == 1:
            charge_start_time = HStategrid.Gun_list[gun_id].get_gun_charge_order("start_time")
            charge_stop_time = HStategrid.Gun_list[gun_id].get_gun_charge_order("stop_time")
            kwh_amount = [0] * 48
            for interval in HStategrid.Gun_list[gun_id].get_gun_charge_order("interval"):
                start_time_h = int(datetime.fromtimestamp(interval.get("start_time")).strftime("%H"))
                start_time_m = int(datetime.fromtimestamp(interval.get("start_time")).strftime("%M"))
                if start_time_m < 30:
                    kwh_amount[start_time_h * 2] = (interval.get("stop_meter_value") - interval.get("start_meter_value")) // 10
                else:
                    kwh_amount[start_time_h * 2 + 1] = (interval.get("stop_meter_value") - interval.get("start_meter_value")) // 10
            charge_stop_reason = HHhdlist.get_stop_reason(HStategrid.Gun_list[gun_id].get_gun_charge_order("stop_reason"))
            if charge_stop_reason == "1008":
                charge_card_stop_is = 0
            elif charge_stop_reason == "1003" or charge_stop_reason == "1004":
                charge_card_stop_is = 2
            else:
                charge_card_stop_is = 1
            start_charge_type = {
                5: 0,
                4: 1,
                7: 3
            }.get(HStategrid.Gun_list[gun_id].get_gun_charge("start_source"), 1)
            info = {
                "device_id": HStategrid.Device_ID,
                "gun_type": HStategrid.Gun_DC_AC.DC_gun.value,
                "gun_id": gun_id + 1,
                "charge_id": HStategrid.Gun_list[gun_id].get_gun_charge_order("cloud_session_id"),
                "charge_start_time": charge_start_time,
                "charge_stop_time": charge_stop_time,
                "charge_time": HStategrid.Gun_list[gun_id].get_gun_charge_order("charge_time"),
                "charge_start_soc": HStategrid.Gun_list[gun_id].get_gun_charge_order("start_soc"),
                "charge_stop_soc": HStategrid.Gun_list[gun_id].get_gun_charge_order("stop_soc"),
                "charge_stop_reason": charge_stop_reason,
                "charge_kwh_amount": HStategrid.Gun_list[gun_id].get_gun_charge_order("total_energy"),
                "charge_start_meter": HStategrid.Gun_list[gun_id].get_gun_charge_order("start_meter_value"),
                "charge_stop_meter": HStategrid.Gun_list[gun_id].get_gun_charge_order("stop_meter_value"),
                "charge_cost": HStategrid.Gun_list[gun_id].get_gun_charge_order("total_cost"),
                "charge_card_stop_is": charge_card_stop_is,
                "charge_start_balance": 0,
                "charge_stop_balance": 0,
                "charge_server_cost": HStategrid.Gun_list[gun_id].get_gun_charge_order("total_service_cost"),
                "pay_offline_is": 0x00,
                "charge_policy": HStategrid.Gun_list[gun_id].get_gun_charge("charge_policy"),
                "charge_policy_param": HStategrid.Gun_list[gun_id].get_gun_charge("charge_policy_param"),
                "car_vin": HStategrid.Gun_list[gun_id].get_gun_charge_order("vin"),
                "car_card": "",
                "kwh_amount": kwh_amount,
                "start_source": start_charge_type,
                "device_session_id": HStategrid.Gun_list[gun_id].get_gun_charge_order("device_session_id"),
                "cloud_session_id": HStategrid.Gun_list[gun_id].get_gun_charge_order("cloud_session_id"),
            }
            HStategrid.tpp_cmd_202(info)
            HStategrid.save_DeviceOrder(info)
            HStategrid.Gun_list[gun_id].set_gun_status(HStategrid.Gun_Status.Charging_completed_not_unplugged.value)
            HStategrid.charge_record_num += 1
            HStategrid.save_DeviceInfo("charge_record_num", HStategrid.DB_Data_Type.DATA_INT.value, "", HStategrid.charge_record_num)

            info = {
                "gun_id": gun_id,
                "cloud_session_id": HStategrid.Gun_list[gun_id].get_gun_charge_order("cloud_session_id"),
                "device_session_id": HStategrid.Gun_list[gun_id].get_gun_charge_order("device_session_id"),
                "result": 0
            }
            HHhdlist.platform_device_data.put([HHhdlist.topic_hqc_main_event_reply_charge_record, info])

            order_confirm_is = {
                "gun_id": gun_id,
                "charge_id": HStategrid.Gun_list[gun_id].get_gun_charge_order("cloud_session_id"),
                "device_session_id": HStategrid.Gun_list[gun_id].get_gun_charge_order("device_session_id"),
                "cloud_session_id": HStategrid.Gun_list[gun_id].get_gun_charge_order("cloud_session_id"),
                "confirm_is": 0,
            }
            HStategrid.save_HistoryOrder(order_confirm_is)

            HStategrid.Gun_list[gun_id].empty_gun_charge()
            HStategrid.Gun_list[gun_id].empty_gun_charge_order()
            HStategrid.Gun_list[gun_id].gun_charge_cost = False
            HStategrid.Gun_list[gun_id].gun_charge_session = False
        else:
            gun_list = HStategrid.Gun_list[gun_id].get_gun_charge_gun_id()
            for gun_id in gun_list:
                if HStategrid.Gun_list[gun_id].get_gun_charge_order() == {}:
                    return False

            kwh_amount = [0] * 48
            charge_stop_reason = HHhdlist.get_stop_reason(HStategrid.Gun_list[gun_id].get_gun_charge_order("stop_reason"))
            if charge_stop_reason == "1008":
                charge_card_stop_is = 0
            elif charge_stop_reason == "1003" or charge_stop_reason == "1004":
                charge_card_stop_is = 2
            else:
                charge_card_stop_is = 1
            start_charge_type = {
                5: 0,
                4: 1,
                7: 3
            }.get(HStategrid.Gun_list[gun_id].get_gun_charge("start_source"), 1)
            charge_start_time = HStategrid.Gun_list[gun_id].get_gun_charge_order("start_time")
            charge_stop_time = HStategrid.Gun_list[gun_id].get_gun_charge_order("stop_time")
            info = {
                "device_id": HStategrid.Device_ID,
                "gun_type": HStategrid.Gun_DC_AC.DC_gun.value,
                "gun_id": gun_id,
                "charge_id": HStategrid.Gun_list[gun_id].get_gun_charge_order("cloud_session_id"),
                "charge_start_time": charge_start_time,
                "charge_stop_time": charge_stop_time,
                "charge_time": HStategrid.Gun_list[gun_id].get_gun_charge_order("charge_time"),
                "charge_start_soc": HStategrid.Gun_list[gun_id].get_gun_charge_order("start_soc"),
                "charge_stop_soc": HStategrid.Gun_list[gun_id].get_gun_charge_order("stop_soc"),
                "charge_stop_reason": charge_stop_reason,
                "charge_kwh_amount": 0,
                "charge_start_meter": 0,
                "charge_stop_meter": 0,
                "charge_cost": 0,
                "charge_card_stop_is": charge_card_stop_is,
                "charge_start_balance": 0,
                "charge_stop_balance": 0,
                "charge_server_cost": 0,
                "pay_offline_is": 0x00,
                "charge_policy": HStategrid.Gun_list[gun_id].get_gun_charge("charge_policy"),
                "charge_policy_param": HStategrid.Gun_list[gun_id].get_gun_charge("charge_policy_param"),
                "car_vin": HStategrid.Gun_list[gun_id].get_gun_charge_order("vin"),
                "car_card": "",
                "kwh_amount": kwh_amount,
                "start_source": start_charge_type,
                "device_session_id": HStategrid.Gun_list[gun_id].get_gun_charge_order("device_session_id"),
                "cloud_session_id": HStategrid.Gun_list[gun_id].get_gun_charge_order("cloud_session_id"),
            }
            for gun_id in gun_list:
                if HStategrid.Gun_list[gun_id].get_gun_status() == HStategrid.Gun_Status.Stopping.value and HStategrid.Gun_list[gun_id].get_gun_charge_order() != {}:
                    for interval in HStategrid.Gun_list[gun_id].get_gun_charge_order("interval"):
                        start_time_h = int(datetime.fromtimestamp(interval.get("start_time")).strftime("%H"))
                        start_time_m = int(datetime.fromtimestamp(interval.get("start_time")).strftime("%M"))
                        if start_time_m < 30:
                            kwh_amount[start_time_h * 2] += (interval.get("stop_meter_value") - interval.get("start_meter_value")) // 10
                        else:
                            kwh_amount[start_time_h * 2 + 1] += (interval.get("stop_meter_value") - interval.get("start_meter_value")) // 10
                    info["charge_kwh_amount"] += HStategrid.Gun_list[gun_id].get_gun_charge_order("total_energy")
                    info["charge_start_meter"] += HStategrid.Gun_list[gun_id].get_gun_charge_order("start_meter_value")
                    info["charge_stop_meter"] += HStategrid.Gun_list[gun_id].get_gun_charge_order("stop_meter_value")
                    info["charge_cost"] += HStategrid.Gun_list[gun_id].get_gun_charge_order("total_cost")
                    info["charge_server_cost"] += HStategrid.Gun_list[gun_id].get_gun_charge_order("total_service_cost")

            info["kwh_amount"] = kwh_amount
            HStategrid.tpp_cmd_202(info)
            HStategrid.save_DeviceOrder(info)
            for gun_id in gun_list:
                HStategrid.Gun_list[gun_id].set_gun_status(HStategrid.Gun_Status.Charging_completed_not_unplugged.value)
            HStategrid.charge_record_num += 1
            HStategrid.save_DeviceInfo("charge_record_num", HStategrid.DB_Data_Type.DATA_INT.value, "", HStategrid.charge_record_num)

            info = {
                "gun_id": gun_id,
                "cloud_session_id": HStategrid.Gun_list[gun_id].get_gun_charge_order("cloud_session_id"),
                "device_session_id": HStategrid.Gun_list[gun_id].get_gun_charge_order("device_session_id"),
                "result": 0
            }
            HHhdlist.platform_device_data.put([HHhdlist.topic_hqc_main_event_reply_charge_record, info])

            order_confirm_is = {
                "gun_id": gun_id,
                "charge_id": HStategrid.Gun_list[gun_id].get_gun_charge_order("cloud_session_id"),
                "device_session_id": HStategrid.Gun_list[gun_id].get_gun_charge_order("device_session_id"),
                "cloud_session_id": HStategrid.Gun_list[gun_id].get_gun_charge_order("cloud_session_id"),
                "confirm_is": 0,
            }
            HStategrid.save_HistoryOrder(order_confirm_is)

            for gun_id in gun_list:
                info = {
                    "gun_id": gun_id,
                    "cloud_session_id": HStategrid.Gun_list[gun_id].get_gun_charge("cloud_session_id"),
                    "device_session_id": HStategrid.Gun_list[gun_id].get_gun_charge("device_session_id"),
                    "result": 0
                }
                HHhdlist.platform_device_data.put([HHhdlist.topic_hqc_main_event_reply_charge_record, info])
                HStategrid.Gun_list[gun_id].empty_gun_charge()
                HStategrid.Gun_list[gun_id].empty_gun_charge_order()
                HStategrid.Gun_list[gun_id].gun_charge_cost = False
                HStategrid.Gun_list[gun_id].gun_charge_session = False
    except Exception as e:
        HSyslog.log_info(f"hhd_to_tpp_202'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_206(msg):
    try:
        order_list = HStategrid.get_HistoryOrder()
        for order_info in order_list:
            charge_id = order_info.get("charge_id")
            order = HStategrid.get_DeviceOrder_pa_id(charge_id)
            HStategrid.tpp_cmd_202(order)
    except Exception as e:
        HSyslog.log_info(f"hhd_to_tpp_206'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_402(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_info(f"hhd_to_tpp_402'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_24(msg):
    try:
        info = {
            "gun_id": msg.get("gun_id"),
            "result": msg.get("result")
        }
        HStategrid.tpp_cmd_24(info)
    except Exception as e:
        HSyslog.log_info(f"hhd_to_tpp_24'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_1304(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_info(f"hhd_to_tpp_1304'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_1306(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_info(f"hhd_to_tpp_1306'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_1308(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_info(f"hhd_to_tpp_1308'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_1310(msg):
    try:
        result = msg.get("result")
        fee_id = msg.get("fee_id")
        if result == 0x00:
            info = {
                "result": 0
            }
        else:
            info = {
                "result": 2
            }
        HStategrid.tpp_cmd_1310(info)
    except Exception as e:
        HSyslog.log_info(f"hhd_to_tpp_1310'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_108(msg):
    try:
        info = {
            "gun_id": msg.get("gun_id") + 1,
            "cmd_addr": msg.get("cmd_addr"),
            "addr_data": msg.get("addr_data", "0000"),
            "charge_id": msg.get("charge_id", ""),
        }
        HStategrid.tpp_cmd_108(info)
        if msg.get("cmd_addr") == HStategrid.Gun_Connect_Status.Start_Charge.value:
            info = {
                "gun_id": msg.get("gun_id"),
            }
            hhd_to_tpp_304(info)
    except Exception as e:
        HSyslog.log_info(f"hhd_to_tpp_108'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_118(msg):
    try:
        for gun_info in HStategrid.Gun_list:
            gun_fault = gun_info.get_gun_fault()
            if gun_fault == {}:
                pass
            else:
                for fault_code, fault_info in gun_fault.items():
                    info = {
                        "gun_id": gun_info.gun_id + 1,
                        "device_id": HStategrid.Device_ID,
                        "fault_code": fault_info.get("fault_id"),
                        "fault_status": fault_info.get("status")
                    }
                    HStategrid.tpp_cmd_118(info)
    except Exception as e:
        HSyslog.log_info(f"hhd_to_tpp_118'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_120(msg):
    try:
        for gun_info in HStategrid.Gun_list:
            if gun_info.get_gun_status() == HStategrid.Gun_Status.Charging.value:
                gun_warn = gun_info.get_gun_warn()
                if gun_warn == {}:
                    pass
                else:
                    for warn_code, warn_info in gun_warn.items():
                        info = {
                            "gun_id": gun_info.gun_id + 1,
                            "device_id": HStategrid.Device_ID,
                            "warn_code": warn_info.get("warn_id"),
                            "charge_id": "",
                            "warn_type": 1,
                            "warn_value": 0
                        }
                        HStategrid.tpp_cmd_120(info)
    except Exception as e:
        HSyslog.log_info(f"hhd_to_tpp_120'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_408(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_info(f"hhd_to_tpp_408'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_410(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_info(f"hhd_to_tpp_410'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_1102(msg):
    try:
        info = {
            "ota_status": msg.get("ota_status"),
            "ota_md5": msg.get("ota_md5")
        }
        HStategrid.tpp_cmd_1102(info)
    except Exception as e:
        HSyslog.log_info(f"hhd_to_tpp_1102'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_802(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_info(f"hhd_to_tpp_802'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_510(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_info(f"hhd_to_tpp_510'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_34(msg):
    try:
        gun_id = msg.get("gun_id")
        info = {
            "device_id": HStategrid.Device_ID,
            "gun_id": gun_id + 1,
            "user_card_id": HStategrid.Gun_list[gun_id].get_gun_charge("card_id"),
            "charge_random": "",
            "physical_cord_id": ""
        }
        HStategrid.tpp_cmd_34(info)
    except Exception as e:
        HSyslog.log_info(f"hhd_to_tpp_34'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_36(msg):
    try:
        gun_id = msg.get("gun_id")
        info = {
            "device_id": HStategrid.Device_ID,
            "gun_id": msg.get("gun_id") + 1,
            "user_card_id": HStategrid.Gun_list[gun_id].get_gun_charge("card_id"),
        }
        HStategrid.tpp_cmd_36(info)
    except Exception as e:
        HSyslog.log_info(f"hhd_to_tpp_36'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_38(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_info(f"hhd_to_tpp_38'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_332(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_info(f"hhd_to_tpp_332'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_40(msg):
    try:
        gun_id = msg.get("gun_id")
        info = {
            "device_id": HStategrid.Device_ID,
            "gun_id": msg.get("gun_id") + 1,
            "car_vin": HStategrid.Gun_list[gun_id].get_gun_charge("car_vin"),
        }
        HStategrid.tpp_cmd_40(info)
    except Exception as e:
        HSyslog.log_info(f"hhd_to_tpp_40'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_42(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_info(f"hhd_to_tpp_42'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_44(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_info(f"hhd_to_tpp_44'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_80(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_info(f"hhd_to_tpp_80'msg error: {msg}. {e}")
        return False


'''################################################# 数据处理函数索引 ##################################################'''

hhd_to_tpp = {
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_2.value: hhd_to_tpp_2,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_4.value: hhd_to_tpp_4,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_502.value: hhd_to_tpp_502,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_506.value: hhd_to_tpp_506,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_508.value: hhd_to_tpp_508,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_512.value: hhd_to_tpp_512,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_514.value: hhd_to_tpp_514,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_516.value: hhd_to_tpp_516,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_6.value: hhd_to_tpp_6,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_8.value: hhd_to_tpp_8,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_12.value: hhd_to_tpp_12,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_14.value: hhd_to_tpp_14,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_16.value: hhd_to_tpp_16,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_504.value: hhd_to_tpp_504,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_18.value: hhd_to_tpp_18,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_20.value: hhd_to_tpp_20,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_102.value: hhd_to_tpp_102,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_104.value: hhd_to_tpp_104,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_106.value: hhd_to_tpp_106,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_114.value: hhd_to_tpp_114,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_302.value: hhd_to_tpp_302,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_304.value: hhd_to_tpp_304,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_306.value: hhd_to_tpp_306,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_308.value: hhd_to_tpp_308,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_310.value: hhd_to_tpp_310,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_312.value: hhd_to_tpp_312,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_202.value: hhd_to_tpp_202,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_206.value: hhd_to_tpp_206,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_402.value: hhd_to_tpp_402,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_24.value: hhd_to_tpp_24,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_1304.value: hhd_to_tpp_1304,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_1306.value: hhd_to_tpp_1306,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_1308.value: hhd_to_tpp_1308,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_1310.value: hhd_to_tpp_1310,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_108.value: hhd_to_tpp_108,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_118.value: hhd_to_tpp_118,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_120.value: hhd_to_tpp_120,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_408.value: hhd_to_tpp_408,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_410.value: hhd_to_tpp_410,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_1102.value: hhd_to_tpp_1102,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_802.value: hhd_to_tpp_802,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_510.value: hhd_to_tpp_510,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_34.value: hhd_to_tpp_34,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_36.value: hhd_to_tpp_36,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_38.value: hhd_to_tpp_38,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_332.value: hhd_to_tpp_332,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_40.value: hhd_to_tpp_40,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_42.value: hhd_to_tpp_42,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_44.value: hhd_to_tpp_44,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_80.value: hhd_to_tpp_80,
}
tpp_to_hhd = {
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_1.value: tpp_to_hhd_1,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_3.value: tpp_to_hhd_3,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_501.value: tpp_to_hhd_501,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_505.value: tpp_to_hhd_505,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_507.value: tpp_to_hhd_507,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_511.value: tpp_to_hhd_511,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_513.value: tpp_to_hhd_513,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_515.value: tpp_to_hhd_515,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_5.value: tpp_to_hhd_5,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_7.value: tpp_to_hhd_7,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_11.value: tpp_to_hhd_11,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_13.value: tpp_to_hhd_13,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_15.value: tpp_to_hhd_15,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_503.value: tpp_to_hhd_503,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_17.value: tpp_to_hhd_17,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_19.value: tpp_to_hhd_19,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_101.value: tpp_to_hhd_101,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_103.value: tpp_to_hhd_103,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_105.value: tpp_to_hhd_105,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_113.value: tpp_to_hhd_113,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_301.value: tpp_to_hhd_301,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_303.value: tpp_to_hhd_303,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_305.value: tpp_to_hhd_305,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_307.value: tpp_to_hhd_307,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_309.value: tpp_to_hhd_309,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_311.value: tpp_to_hhd_311,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_201.value: tpp_to_hhd_201,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_205.value: tpp_to_hhd_205,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_401.value: tpp_to_hhd_401,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_23.value: tpp_to_hhd_23,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_1303.value: tpp_to_hhd_1303,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_1305.value: tpp_to_hhd_1305,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_1307.value: tpp_to_hhd_1307,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_1309.value: tpp_to_hhd_1309,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_107.value: tpp_to_hhd_107,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_117.value: tpp_to_hhd_117,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_119.value: tpp_to_hhd_119,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_407.value: tpp_to_hhd_407,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_409.value: tpp_to_hhd_409,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_1101.value: tpp_to_hhd_1101,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_801.value: tpp_to_hhd_801,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_509.value: tpp_to_hhd_509,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_33.value: tpp_to_hhd_33,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_35.value: tpp_to_hhd_35,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_37.value: tpp_to_hhd_37,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_331.value: tpp_to_hhd_331,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_41.value: tpp_to_hhd_41,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_43.value: tpp_to_hhd_43,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_45.value: tpp_to_hhd_45,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_81.value: tpp_to_hhd_81,
}
