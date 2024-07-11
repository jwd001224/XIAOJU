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
                    for cmd, func in xj_to_hhd.item():
                        if cmd == msg[0]:
                            func(msg[1])
                        else:
                            print("参数错误")
            except Exception as e:
                raise Exception("program exit")


def do_mqtt_resv_data():
    mqttSendThread = threading.Thread(target=__mqtt_resv_data)
    mqttSendThread.start()
    HSyslog.log_info("do_mqtt_resv_data")


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


def hhd_to_xj_2():
    pass


def hhd_to_xj_4():
    pass


def hhd_to_xj_6():
    pass


def hhd_to_xj_8():
    pass


def hhd_to_xj_12():
    pass


def hhd_to_xj_24():
    pass


def hhd_to_xj_34():
    pass


def hhd_to_xj_36():
    pass


def hhd_to_xj_40():
    pass


def hhd_to_xj_102():
    pass


def hhd_to_xj_104():
    pass


def hhd_to_xj_106():
    pass


def hhd_to_xj_108():
    pass


def hhd_to_xj_114():
    pass


def hhd_to_xj_118():
    pass


def hhd_to_xj_120():
    pass


def hhd_to_xj_302():
    pass


def hhd_to_xj_304():
    pass


def hhd_to_xj_306():
    pass


def hhd_to_xj_308():
    pass


def hhd_to_xj_310():
    pass


def hhd_to_xj_312():
    pass


def hhd_to_xj_202():
    pass


def hhd_to_xj_206():
    pass


def hhd_to_xj_410():
    pass


def hhd_to_xj_502():
    pass


def hhd_to_xj_504():
    pass


def hhd_to_xj_510():
    pass


def hhd_to_xj_802():
    pass


def hhd_to_xj_1102():
    pass


def hhd_to_xj_1304():
    pass


def hhd_to_xj_1306():
    pass


def hhd_to_xj_1310():
    pass


'''################################################# 数据处理函数索引 ##################################################'''

hhd_to_xj = {
    2: hhd_to_xj_2,
    4: hhd_to_xj_4,
    6: hhd_to_xj_6,
    8: hhd_to_xj_8,
    12: hhd_to_xj_12,
    24: hhd_to_xj_24,
    34: hhd_to_xj_34,
    36: hhd_to_xj_36,
    40: hhd_to_xj_40,
    102: hhd_to_xj_102,
    104: hhd_to_xj_104,
    106: hhd_to_xj_106,
    108: hhd_to_xj_108,
    114: hhd_to_xj_114,
    118: hhd_to_xj_118,
    120: hhd_to_xj_120,
    302: hhd_to_xj_302,
    304: hhd_to_xj_304,
    306: hhd_to_xj_306,
    308: hhd_to_xj_308,
    310: hhd_to_xj_310,
    312: hhd_to_xj_312,
    202: hhd_to_xj_202,
    206: hhd_to_xj_206,
    410: hhd_to_xj_410,
    502: hhd_to_xj_502,
    504: hhd_to_xj_504,
    510: hhd_to_xj_510,
    802: hhd_to_xj_802,
    1102: hhd_to_xj_1102,
    1304: hhd_to_xj_1304,
    1306: hhd_to_xj_1306,
    1310: hhd_to_xj_1310,
}
xj_to_hhd = {
    1: xj_to_hhd_1,
    3: xj_to_hhd_3,
    5: xj_to_hhd_5,
    7: xj_to_hhd_7,
    11: xj_to_hhd_11,
    23: xj_to_hhd_23,
    33: xj_to_hhd_33,
    35: xj_to_hhd_35,
    41: xj_to_hhd_41,
    101: xj_to_hhd_101,
    103: xj_to_hhd_103,
    105: xj_to_hhd_105,
    107: xj_to_hhd_107,
    113: xj_to_hhd_113,
    117: xj_to_hhd_117,
    119: xj_to_hhd_119,
    301: xj_to_hhd_301,
    303: xj_to_hhd_303,
    305: xj_to_hhd_305,
    307: xj_to_hhd_307,
    309: xj_to_hhd_309,
    311: xj_to_hhd_311,
    201: xj_to_hhd_201,
    205: xj_to_hhd_205,
    409: xj_to_hhd_409,
    501: xj_to_hhd_501,
    503: xj_to_hhd_503,
    509: xj_to_hhd_509,
    801: xj_to_hhd_801,
    1101: xj_to_hhd_1101,
    1303: xj_to_hhd_1303,
    1305: xj_to_hhd_1305,
    1309: xj_to_hhd_1309,
}
