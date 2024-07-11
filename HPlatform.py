import inspect
import json
import queue
import random
import time

from paho.mqtt import client as mqtt_client

import HHhdlist
import HStategrid
from HHhdlist import *
import HSyslog

thmc = None
mqttThreadStatus = None


def xj_init():
    HStategrid.User_Name = HStategrid.get_DeviceInfo("User_Name")
    HStategrid.Enterprise_Code = HStategrid.get_DeviceInfo("Enterprise_Code")


class PMqttClient:
    def __init__(self, broker, port, client_id, username, password, topic) -> None:
        self.broker = broker
        self.port = port
        self.client_id = client_id
        self.username = username
        self.password = password
        self.topic = topic
        self.connectStatus = False
        self.clientDev = None

    def connect_mqtt(self) -> mqtt_client:
        client = mqtt_client.Client(self.client_id)
        client.username_pw_set(self.username, self.password)

        client.on_connect = self.on_connect  # 连接成功时的回调函数
        client.on_message = self.on_message  # 连接成功时的订阅函数
        client.on_disconnect = self.on_disconnect  # 断开连接的回调函数
        client.connect(self.broker, self.port, keepalive=60)
        self.clientDev = client
        return self.clientDev

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connectStatus = True
            HSyslog.log_info("Connected to MQTT Broker!")
            HHhdlist.device_mqtt_status = True
        else:
            self.connectStatus = False
            HSyslog.log_info(f"Failed to connect, return code: {rc}")
            HHhdlist.device_mqtt_status = False

    def on_message(self, client, userdata, message):
        self.__subscribe(message.payload, message.topic)

    def on_disconnect(self, client, userdata, rc):
        HSyslog.log_info("check connection is closed! rc = {}".format(rc))
        self.connectStatus = False
        self.clientDev.disconnect()

    def on_publish(self, client, userdata, mid):
        pass

    def init_mqtt(self, client):
        client.on_publish = self.on_publish
        client.on_disconnect = self.on_disconnect

    def subscribe(self):  # 订阅
        self.clientDev.subscribe(topic=self.topic, qos=0)

    def publish(self, topic, msg, qos):  # 发布
        if self.connectStatus:
            result = self.clientDev.publish(topic, msg, qos)
            if not result[0]:
                if topic != '/hqc/sys/network-state':
                    HSyslog.log_info(f"Send_to_Device: {msg} to topic: {topic}")
                return True
            else:
                return False
        return False

    def __subscribe(self, msg, topic) -> bool:
        HSyslog.log_info(f"Received: {msg} from topic:{topic}")
        app_subscribe(msg, topic)
        return True


def app_subscribe(msg: bytes, topic: str):
    protocol_encode = HStategrid.Protocol_Encode(msg)
    if protocol_encode.protocol_message():
        protocol = None


def modify_msg_head(msg: dict):
    global package_num
    package_num += 1
    msg['package_num'] = package_num
    '''修改包间序号，分包数量，消息是否需要确认'''

    return msg


def app_publish(topic: str, msg_body: dict):
    msg_dict = {'version': '1.1.1',
                'package_num': -1,  # 包序号
                'package_seq': 1,  # 包头序号
                'sub_pkt_num': 1,  # 分包数量
                'need_response': False,  # 消息是否需要确认
                'body': msg_body
                }
    '''修改包头'''
    msg_dict = modify_msg_head(msg_dict)
    msg = json.dumps(msg_dict)
    qos = app_func_dict[topic]["qos"]
    msg = {"topic": topic, "msg": msg, "qos": qos}
    if msg_body.get("info_id", -1) != -1:
        if msg_body.get("info_id", -1) == 8:
            HHhdlist.device_charfer_p[msg_body.get("gun_id") + 1]["stop_package_num"] = msg_dict.get("package_num")
        elif msg_body.get("info_id", -1) == 6:
            HHhdlist.device_charfer_p[msg_body.get("gun_id") + 1]["start_package_num"] = msg_dict.get("package_num")
    DtoP_queue.put(msg)


def keep_mqtt(broker, port):
    global thmc
    thmc = PMqttClient(broker, port)
    isFirst = True
    hmclient = None
    while True:
        if not thmc.connectStatus:
            if isFirst:
                isFirst = False
                try:
                    print('!!!!! MQTT重连 !!!!!')
                    hmclient = thmc.connect_mqtt()  # 客户端对象
                except Exception as e:
                    print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
                    isFirst = True
                if thmc.connectStatus and thmc.client:
                    hmclient.loop_start()
            else:
                hmclient.loop_stop()
                try:
                    hmclient.reconnect()
                except Exception as e:
                    print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
                print('will send netstatus')
                hmclient.loop_start()
                thmc.subscribe()
        else:
            if hmclient._state == 2 or hmclient._state == 0:
                hmclient.disconnect()
                thmc.connectStatus = False
                print("The connection is Closed! state is {}".format(hmclient._state))

        time.sleep(1)


def do_link_mqtt():
    mqttKeepThread = threading.Thread(target=keep_mqtt, args=["epower-equipment-server-test.xiaojukeji.com", 1884])
    mqttKeepThread.start()
    HSyslog.log_info("do_link_mqtt")


def __mqtt_send_data():
    while True:
        if not HStategrid.xj_send_data:
            time.sleep(0.5)
        else:
            try:
                if HStategrid.xj_send_data.empty():
                    time.sleep(0.5)
                else:
                    msg = dict(HStategrid.xj_send_data.get())
                    if "topic" not in msg.keys():
                        continue
                    thmc.publish(msg.get("topic"), msg.get("msg", ""), msg.get("qos", 0))
            except Exception as e:
                raise Exception("program exit")


def do_mqtt_send_data():
    mqttSendThread = threading.Thread(target=__mqtt_send_data)
    mqttSendThread.start()
    HSyslog.log_info("do_mqtt_send_data")


def __mqtt_period_event(interval):
    period_time = time.time()
    while True:
        if int(time.time()) - int(period_time) > interval:
            period_time = time.time()
        time.sleep(1)


def do_mqtt_period():
    interval = HStategrid.get_DeviceInfo("heat_interval")
    mqttPeriodThread = threading.Thread(target=__mqtt_period_event, args=(interval,))
    mqttPeriodThread.start()
    HSyslog.log_info("do_mqtt_period")


def __mqtt_resv_data():
    while mqttThreadStatus:
        if not HStategrid.xj_resv_data:
            time.sleep(0.5)
        else:
            try:
                if HStategrid.xj_resv_data.empty():
                    time.sleep(0.5)
                else:
                    msg = HStategrid.xj_resv_data.get()
                    if msg[0] not in HStategrid.xj_mqtt_cmd_enum:
                        continue
            except Exception as e:
                raise Exception("program exit")


'''################################################### 接收数据处理 ####################################################'''


def xj_to_hhd_1():
    pass


def xj_to_hhd_3():
    pass


def xj_to_hhd_5():
    pass


def xj_to_hhd_7():
    pass


def xj_to_hhd_11():
    pass


def xj_to_hhd_23():
    pass


def xj_to_hhd_33():
    pass


def xj_to_hhd_35():
    pass


def xj_to_hhd_41():
    pass


def xj_to_hhd_101():
    pass


def xj_to_hhd_103():
    pass


def xj_to_hhd_105():
    pass


def xj_to_hhd_107():
    pass


def xj_to_hhd_113():
    pass


def xj_to_hhd_117():
    pass


def xj_to_hhd_119():
    pass


def xj_to_hhd_301():
    pass


def xj_to_hhd_303():
    pass


def xj_to_hhd_305():
    pass


def xj_to_hhd_307():
    pass


def xj_to_hhd_309():
    pass


def xj_to_hhd_311():
    pass


def xj_to_hhd_201():
    pass


def xj_to_hhd_205():
    pass


def xj_to_hhd_409():
    pass


def xj_to_hhd_501():
    pass


def xj_to_hhd_503():
    pass


def xj_to_hhd_509():
    pass


def xj_to_hhd_801():
    pass


def xj_to_hhd_1101():
    pass


def xj_to_hhd_1303():
    pass


def xj_to_hhd_1305():
    pass


def xj_to_hhd_1309():
    pass


'''################################################### 发送数据处理 ####################################################'''


def xj_to_hhd_2():
    pass


def xj_to_hhd_4():
    pass


def xj_to_hhd_6():
    pass


def xj_to_hhd_8():
    pass


def xj_to_hhd_12():
    pass


def xj_to_hhd_24():
    pass


def xj_to_hhd_34():
    pass


def xj_to_hhd_36():
    pass


def xj_to_hhd_40():
    pass


def xj_to_hhd_102():
    pass


def xj_to_hhd_104():
    pass


def xj_to_hhd_106():
    pass


def xj_to_hhd_108():
    pass


def xj_to_hhd_114():
    pass


def xj_to_hhd_118():
    pass


def xj_to_hhd_120():
    pass


def xj_to_hhd_302():
    pass


def xj_to_hhd_304():
    pass


def xj_to_hhd_306():
    pass


def xj_to_hhd_308():
    pass


def xj_to_hhd_310():
    pass


def xj_to_hhd_312():
    pass


def xj_to_hhd_202():
    pass


def xj_to_hhd_206():
    pass


def xj_to_hhd_410():
    pass


def xj_to_hhd_502():
    pass


def xj_to_hhd_504():
    pass


def xj_to_hhd_510():
    pass


def xj_to_hhd_802():
    pass


def xj_to_hhd_1102():
    pass


def xj_to_hhd_1304():
    pass


def xj_to_hhd_1306():
    pass


def xj_to_hhd_1310():
    pass
