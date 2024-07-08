# import time
#
# import paho.mqtt.client as mqtt
#
#
#
# # MQTT 代理的地址和端口
# # broker = "epower-equipment-server-test.xiaojukeji.com"
# # port = 1884
#
# broker = "unicron.didichuxing.com"
# port = 1883
#
# # 客户端标识符和用户名密码
# client_id = "TEST00001"
# username = "91350100770663716E"
# password = "JvL8so96zyM6ppaTPfEe2JRt9lsnJ07EhT/oQhcCAyuE7Eyo5RoQ0MXBIXyyD13cNN2LqK3ViHLKCFbE/IkKXpeDfIMpCWt8niVn29Vpaf38gtVf0ne7RWPpHC4PlP+gIWLPRVUV1ei1RSeCWfJ4GtDJ0fuOuq7ij0gq/4BIiKU="
#
# # 创建 MQTT 客户端实例
# client = mqtt.Client(client_id=client_id)
#
# # 设置用户名和密码
# client.username_pw_set(username, password)
#
#
# def get_check_sum(data, cmd):
#     return hex((sum(data) + cmd) % 127)
#
#
# data = [0x00, 0x00, 0x00, 0x00, 0x54, 0x45, 0x53, 0x54, 0x30, 0x30, 0x30, 0x30, 0x31]
# cmd = 0x72
#
# print(get_check_sum(data, cmd))
#
#
# def asd():
#     # hex_string = """7D D0 8D 00 03 00 0A 00 01 00 00 00 6A 00 00 00 00 00 54 45 53 54 30 30 30 30 31 00 00 00 00 00
#     # 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 01 00 00 00 00 02 00 00 00 00 1E 00 00 01 1E 03 01
#     # 00 00 00 20 20 07 09 14 41 39 FF 00 00 00 00 00 00 00 FF 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 30 30
#     # 30 30 30 30 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 65"""
#
#     hex_string = """
#         7D D0
#         1C 00
#         00 0A 00 03
#         01 00 00 00
#         72 00
#         00 00 00 00
#         54 45 53 54 30 30 30 30 31
#         28
#     """
#
#     # 去除空格，并分割成十六进制字符列表
#     hex_list = hex_string.split()
#
#     # 将十六进制字符转换为字节，并存入字节流列表
#     byte_stream = []
#     for hex_byte in hex_list:
#         byte = int(hex_byte, 16)  # 将十六进制字符转换为整数
#         byte_stream.append(byte)  # 将字节添加到字节流列表中
#
#     # 输出字节流列表
#     return bytes(byte_stream)
#
#
# # 连接成功时的回调函数
# def on_connect(client, userdata, flags, rc):
#     if rc == 0:
#         print("Connected to MQTT broker")
#         # 订阅主题或发送其他消息
#         client.subscribe(client_id)  # 示例：订阅一个主题
#         time.sleep(5)
#         client.publish(client_id, asd(), 1)
#     else:
#         print(f"Connection failed with code {rc}")
#
#
# # 消息发送成功时的回调函数
# def on_publish(client, userdata, mid):
#     print(f"Message published with mid: {mid}")
#
#
# # 接收到消息时的回调函数
# def on_message(client, userdata, message):
#     print(f"Received message '{message.payload}' on topic '{message.topic}'")
#     print(type(message.payload.hex()))
#
#
# # 设置回调函数
# client.on_connect = on_connect
# client.on_publish = on_publish
# client.on_message = on_message
#
# # # 连接到 MQTT 代理
# # client.connect(broker, port)
# #
# # # 开始循环处理网络流量
# # client.loop_forever()
#
#
# import HStategrid
# messag = '7dd09700000a00030100000071000000000065706f7765722d65717569706d656e742d7365727665722e7869616f6a756b656a692e636f6d0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000005c0700001d'
# message = b'}\xc3\x97\x00\x00\n\x00\x03\x01\x00\x00\x00q\x00\x00\x00\x00\x00epower-equipment-server.xiaojukeji.com\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\\\x07\x00\x00\x1d'
#
# protocol = HStategrid.Protocol
# protocol(message)
# protocol.Pprint()
# protocol.cleck_cmd()
# protocol.cleck_serial_code()
# protocol.cleck_func()
# result = protocol.callback_func(protocol.datas)
# print(result)

import HStategrid
# 示例用法
number = 1234567890
byte_length = 4  # 例如，使用4个字节来表示该数字
hex_bytes = HStategrid.number_to_little_endian_hex_bytes(number, byte_length)
print(hex_bytes)

# 示例用法
string_data = "Hello, World!"
hex_bytes = HStategrid.string_to_little_endian_hex_bytes(string_data)
print(hex_bytes)