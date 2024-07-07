# import inspect
# import json
# import queue
# import random
# import time
#
# from paho.mqtt import client as mqtt_client
#
# import HHhdlist
# from HHhdlist import *
# import HSyslog
#
# thmc = None
# DtoP_queue = queue.Queue()
# package_num = 0  # 包序号
#
#
# class PMqttClient:
#     def __init__(self, broker, port, client_id, username, password, topic) -> None:
#         self.broker = broker
#         self.port = port
#         self.client_id = client_id
#         self.username = username
#         self.password = password
#         self.topic = topic
#         self.connectStatus = False
#         self.clientDev = None
#
#     def connect_mqtt(self) -> mqtt_client:
#         client = mqtt_client.Client(self.client_id)
#         client.username_pw_set(self.username, self.password)
#
#         client.on_connect = self.on_connect  # 连接成功时的回调函数
#         client.on_message = self.on_message  # 连接成功时的订阅函数
#         client.on_disconnect = self.on_disconnect  # 断开连接的回调函数
#         client.connect(self.broker, self.port, keepalive=60)
#         self.clientDev = client
#         return self.clientDev
#
#     def on_connect(self, client, userdata, flags, rc):
#         if rc == 0:
#             self.connectStatus = True
#             HSyslog.log_info("Connected to MQTT Broker!")
#             print("Connected to MQTT Broker!")
#             HHhdlist.device_mqtt_status = True
#         else:
#             self.connectStatus = False
#             print("Failed to connect, return code %d\n", rc)
#             HHhdlist.device_mqtt_status = False
#
#     def on_message(self, client, userdata, msg):
#         self.__subscribe(msg.payload.decode('utf-8', 'ignore'), msg.topic)
#
#     def on_disconnect(self, client, userdata, rc):
#         HSyslog.log_info("check connection is closed! rc = {}".format(rc))
#         print("check connection is closed! rc = {}".format(rc))
#         self.connectStatus = False
#         self.clientDev.disconnect()
#
#     def on_publish(self, client, userdata, mid):
#         pass
#
#     def init_mqtt(self, client):
#         client.on_publish = self.on_publish
#         client.on_disconnect = self.on_disconnect
#
#     def subscribe(self):  # 订阅
#         self.clientDev.subscribe(topic=self.topic, qos=0)
#
#     def publish(self, topic, msg, qos):  # 发布
#         if self.connectStatus:
#             result = self.clientDev.publish(topic, msg, qos)
#             if not result[0]:
#                 print(f"Send: \033[93m{msg}\033[0m to topic: \033[93m{topic}\033[0m")
#                 if topic != '/hqc/sys/network-state':
#                     HSyslog.log_info(f"Send_to_Device: {msg} to topic: {topic}")
#                 return True
#             else:
#                 print(f"Failed to send message to topic {topic}")
#                 return False
#
#         return False
#
#     def __subscribe(self, msg, topic) -> bool:
#         print(f"Received: \033[93m{msg}\033[0m from topic:\033[93m{topic}\033[0m")
#         app_subscribe(msg, topic)
#         return True
#
#
# def analysis_msg_dict(func_dict: dict, msg_dict: dict, topic: str):
#     version = msg_dict.get('version', "")  # string
#     package_num = msg_dict.get('package_num', -1)  # int
#     package_seq = msg_dict.get('package_seq', -1)  # int
#     sub_pkt_num = msg_dict.get('sub_pkt_num', -1)  # int
#     need_response = msg_dict.get('need_response', False)  # bool
#     func_dict['func'](msg_dict.get('body', {}))
#
#
# def app_subscribe(msg: str, topic: str):
#     cmd_code =
#     if topic not in app_func_dict.keys():
#         print("does not exist this topic")
#         return False
#     if not app_func_dict[topic]['func']:
#         return False
#     msg_dict = json.loads(msg)
#     analysis_msg_dict(app_func_dict[topic], msg_dict, topic)
#
#
# def modify_msg_head(msg: dict):
#     global package_num
#     package_num += 1
#     msg['package_num'] = package_num
#     '''修改包间序号，分包数量，消息是否需要确认'''
#
#     return msg
#
#
# def app_publish(topic: str, msg_body: dict):
#     msg_dict = {'version': '1.1.1',
#                 'package_num': -1,  # 包序号
#                 'package_seq': 1,  # 包头序号
#                 'sub_pkt_num': 1,  # 分包数量
#                 'need_response': False,  # 消息是否需要确认
#                 'body': msg_body
#                 }
#     '''修改包头'''
#     msg_dict = modify_msg_head(msg_dict)
#     msg = json.dumps(msg_dict)
#     qos = app_func_dict[topic]["qos"]
#     msg = {"topic": topic, "msg": msg, "qos": qos}
#     if msg_body.get("info_id", -1) != -1:
#         if msg_body.get("info_id", -1) == 8:
#             HHhdlist.device_charfer_p[msg_body.get("gun_id") + 1]["stop_package_num"] = msg_dict.get("package_num")
#         elif msg_body.get("info_id", -1) == 6:
#             HHhdlist.device_charfer_p[msg_body.get("gun_id") + 1]["start_package_num"] = msg_dict.get("package_num")
#     DtoP_queue.put(msg)
#
#
# def keep_mqtt(broker, port):
#     global thmc
#     thmc = PMqttClient(broker, port)
#     isFirst = True
#     hmclient = None
#     while True:
#         if not thmc.connectStatus:
#             if isFirst:
#                 isFirst = False
#                 try:
#                     print('!!!!! MQTT重连 !!!!!')
#                     hmclient = thmc.connect_mqtt()  # 客户端对象
#                 except Exception as e:
#                     print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
#                     isFirst = True
#                 if thmc.connectStatus and thmc.client:
#                     hmclient.loop_start()
#             else:
#                 hmclient.loop_stop()
#                 try:
#                     hmclient.reconnect()
#                 except Exception as e:
#                     print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
#                 print('will send netstatus')
#                 hmclient.loop_start()
#                 thmc.subscribe()
#         else:
#             if hmclient._state == 2 or hmclient._state == 0:
#                 hmclient.disconnect()
#                 thmc.connectStatus = False
#                 print("The connection is Closed! state is {}".format(hmclient._state))
#
#         time.sleep(1)
#
#
# def do_link_mqtt():
#     mqttKeepThread = threading.Thread(target=keep_mqtt, args=["epower-equipment-server-test.xiaojukeji.com", 1884])
#     mqttKeepThread.start()
#     HSyslog.log_info("do_link_mqtt")
#
#
# def __mqtt_send_data():
#     while True:
#         if not DtoP_queue:
#             time.sleep(0.5)
#         else:
#             try:
#                 if DtoP_queue.empty():
#                     time.sleep(0.5)
#                 else:
#                     msg = dict(DtoP_queue.get())
#                     if "topic" not in msg.keys():
#                         continue
#                     thmc.publish(msg.get("topic"), msg.get("msg", ""), msg.get("qos", 0))
#             except Exception as e:
#                 raise Exception("program exit")
#
#
# def do_mqtt_send_data():
#     mqttSendThread = threading.Thread(target=__mqtt_send_data)
#     mqttSendThread.start()
#     HSyslog.log_info("do_mqtt_send_data")
#
#
# def __mqtt_period_event():
#     period_time = time.time()
#     while True:
#         if int(time.time()) - int(period_time) > 5:
#             if HStategrid.net_status == 1 and HStategrid.link_init_status == 1:
#                 app_net_status(HHhdlist.net_type.wired_net.value, 3, HHhdlist.net_id.id_4G.value)
#             if HStategrid.net_status == 0 and HStategrid.link_init_status == 0:
#                 app_net_status(HHhdlist.net_type.no_net.value, 0, HHhdlist.net_id.id_4G.value)
#             period_time = time.time()
#         time.sleep(1)
#
#
# def do_mqtt_period():
#     mqttPeriodThread = threading.Thread(target=__mqtt_period_event)
#     mqttPeriodThread.start()
#     HSyslog.log_info("do_mqtt_period")


import json

import paho.mqtt.client as mqtt

import HStategrid

# MQTT 代理的地址和端口
# broker = "epower-equipment-server-test.xiaojukeji.com"
# port = 1884

broker = "unicron.didichuxing.com"
port = 1883

# 客户端标识符和用户名密码
client_id = "TEST00001"
username = "91110113MA01CF8F83"
password = "JvL8so96zyM6ppaTPfEe2JRt9lsnJ07EhT/oQhcCAyuE7Eyo5RoQ0MXBIXyyD13cNN2LqK3ViHLKCFbE/IkKXpeDfIMpCWt8niVn29Vpaf38gtVf0ne7RWPpHC4PlP+gIWLPRVUV1ei1RSeCWfJ4GtDJ0fuOuq7ij0gq/4BIiKU="

# 创建 MQTT 客户端实例
client = mqtt.Client(client_id=client_id)

# 设置用户名和密码
client.username_pw_set(username, password)


# 连接成功时的回调函数
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
        # 订阅主题或发送其他消息
        client.subscribe(client_id)  # 示例：订阅一个主题
    else:
        print(f"Connection failed with code {rc}")


# 消息发送成功时的回调函数
def on_publish(client, userdata, mid):
    print(f"Message published with mid: {mid}")


# 接收到消息时的回调函数
def on_message(client, userdata, message):
    print(f"Received message '{message.payload.hex()}' on topic '{message.topic}'")
    protocol = HStategrid.Protocol(message.payload.hex())
    protocol.Pprint()


# 设置回调函数
client.on_connect = on_connect
client.on_publish = on_publish
client.on_message = on_message

# 连接到 MQTT 代理
client.connect(broker, port)

# 开始循环处理网络流量
client.loop_forever()


