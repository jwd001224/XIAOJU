import time
import HStategrid
import paho.mqtt.client as mqtt

info_114 = {
    "equipment_id": "TEST00001",
    "reserve": 0,
}
msg = HStategrid.xj_cmd_114(info_114)
send_114 = HStategrid.Protocol_Decode(msg, 114)
msg = send_114.build_msg()

# MQTT 代理的地址和端口
# broker = "epower-equipment-server-test.xiaojukeji.com"
# port = 1884

broker = "unicron.didichuxing.com"
port = 1883

# 客户端标识符和用户名密码
client_id = "TEST00001"
username = "91350100770663716E"
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
        time.sleep(5)
        client.publish(client_id, msg, 1)
    else:
        print(f"Connection failed with code {rc}")


# 消息发送成功时的回调函数
def on_publish(client, userdata, mid):
    print(f"Message published with mid: {mid}")


# 接收到消息时的回调函数
def on_message(client, userdata, message):
    print(f"Received message '{list(message.payload)}' on topic '{message.topic}'")
    print(type(message.payload.hex()))


# 设置回调函数
client.on_connect = on_connect
client.on_publish = on_publish
client.on_message = on_message

# # 连接到 MQTT 代理
# client.connect(broker, port)
#
# # 开始循环处理网络流量
# client.loop_forever()


# import HStategrid messag =
# '7dd09700000a00030100000071000000000065706f7765722d65717569706d656e742d7365727665722e7869616f6a756b656a692e636f6d0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000005c0700001d' message = b'}\xc3\x97\x00\x00\n\x00\x03\x01\x00\x00\x00q\x00\x00\x00\x00\x00epower-equipment-server.xiaojukeji.com\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\\\x07\x00\x00\x1d'
#
# protocol = HStategrid.Protocol
# protocol(message)
# protocol.Pprint()
# protocol.cleck_cmd()
# protocol.cleck_serial_code()
# protocol.cleck_func()
# result = protocol.callback_func(protocol.datas)
# print(result)


# info_106 = {
#     "charge_mode_num": 2,
#     "charge_mode_rate": 1200,
#     "equipment_id": "hhdtest0001",
#     "offline_charge_flag": 1,
#     "stake_version": "A2.4.8",
#     "stake_type": 0x7D00,
#     "stake_start_times": 1,
#     "data_up_mode": 2,
#     "sign_interval": 15,
#     "reserve": 2,
#     "gun_index": 2,
#     "heartInterval": 180,
#     "heart_out_times": 2,
#     "stake_charge_record_num": 2,
#     "stake_systime": "2024-07-09-9:21:45",
#     "stake_last_charge_time": "2024-07-09-9:19:45",
#     "stake_last_start_time": "2024-07-09-9:17:45",
#     "signCode": "hhd",
#     "mac": "70:77:81:A0:42:FF",
#     "ccu_version": "A0.1.0",
# }

# print(info_106.get("charge_mode_rate"))
# print(info_106.get("equipment_id"))
# print(info_106.get("stake_last_charge_time"))
# print(info_106.get("stake_version"))
# print(info_106.get("mac"))
#
# charge_mode_rate = HStategrid.info_to_little_hex(info_106.get("charge_mode_rate"), 2, 1)
# print(charge_mode_rate)
#
# equipment_id = HStategrid.info_to_little_hex(info_106.get("equipment_id"), 32, 0)
# print(equipment_id)
#
# stake_last_charge_time = HStategrid.info_to_little_hex(info_106.get("stake_last_charge_time"), 8, 2)
# print(stake_last_charge_time)
#
# stake_version = HStategrid.info_to_little_hex(info_106.get("stake_version"), 4, 3)
# print(stake_version)
#
# mac = HStategrid.info_to_little_hex(info_106.get("mac"), 32, 0)
# print(mac)
#
# print(HStategrid.hex_to_little_info(charge_mode_rate, 1))
# print(HStategrid.hex_to_little_info(equipment_id, 0))
# print(HStategrid.hex_to_little_info(stake_last_charge_time, 2))
# print(HStategrid.hex_to_little_info(stake_version, 3))
# print(HStategrid.hex_to_little_info(mac, 0))


# msg = HStategrid.xj_cmd_106(info)
# print(msg)


# test = [125, 208,
#         149, 0,
#         3, 0, 11, 0,
#         0, 0, 0, 0,
#         113, 0,
#         0, 0, 0, 0,
#         101, 112, 111, 119, 101, 114, 45, 101, 113, 117, 105, 112, 109, 101, 110, 116, 45, 115, 101, 114, 118, 101, 114,
#         46, 120, 105, 97, 111, 106, 117, 107, 101, 106, 105, 46, 99, 111, 109, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
#         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
#         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
#         0, 0, 92, 7, 0, 0, 29]
#
# protocol = HStategrid.Protocol_Encode(test)
# protocol.Pprint()
# print(protocol.cleck_cmd())
# print(protocol.cleck_serial_code())
# print(protocol.cleck_header_code())
# print(protocol.cleck_version_code())
# protocol.cleck_func()
# protocol.protocol_message()


if 1 in HStategrid.xj_mqtt_cmd_enum:
    print(1)