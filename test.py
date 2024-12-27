# import os
#
# import qrcode
#
#
# qr_data = f"https://epower.xiaojukeji.com/epower/static/resources/xcxconf/XIAOJU.101437000.001224000200060507"
#
# # 创建二维码
# qr = qrcode.QRCode(
#     version=8,
#     error_correction=qrcode.constants.ERROR_CORRECT_L,
#     box_size=15,
#     border=2,
# )
# qr.add_data(qr_data)
# qr.make(fit=True)
#
# # 生成二维码图片
# img = qr.make_image(fill='black', back_color='white')
#
# # 保存二维码图片
# img_path = os.path.join("C:\Works\XIAOJU", f'枪07.png')
# img.save(img_path)
import json

# test = "31303134333730303030303139333638466f776c316673765077354670316f746c44716d53737a554d456f357669653374774d78684c3846526f4c4c784f56351765222518"
# print(len(test))
#
# print(test[0:32])
# print(test[32:64])
# print(test[-4:0])

import paho.mqtt.client as mqtt
import HHhdlist
import HStategrid


class MQTTClient:
    def __init__(self, broker_address, port=1883, keepalive=60, client_id=""):
        self.broker_address = broker_address
        self.port = port
        self.keepalive = keepalive
        self.client = mqtt.Client(client_id=client_id)
        self.client.username_pw_set("91110113MA01CF8F83", "JvL8so96zyM6ppaTPfEe2JRt9lsnJ07EhT/oQhcCAyuE7Eyo5RoQ0MXBIXyyD13cNN2LqK3ViHLKCFbE/IkKXpeDfIMpCWt8niVn29Vpaf38gtVf0ne7RWPpHC4PlP+gIWLPRVUV1ei1RSeCWfJ4GtDJ0fuOuq7ij0gq/4BIiKU=")

        # 设置回调函数
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

    def connect(self):
        """连接到MQTT服务器"""
        try:
            self.client.connect(self.broker_address, self.port, self.keepalive)
            self.client.loop_start()  # 启动网络循环以处理连接
            print(f"Connected to MQTT broker at {self.broker_address}:{self.port}")
        except Exception as e:
            print(f"Failed to connect to broker: {e}")

    def disconnect(self):
        """断开与MQTT服务器的连接"""
        self.client.loop_stop()
        self.client.disconnect()
        print("Disconnected from MQTT broker")

    def on_connect(self, client, userdata, flags, rc):
        """连接成功时的回调函数"""
        if rc == 0:
            print("Successfully connected to MQTT broker")
        else:
            print(f"Connection failed with code {rc}")

    def on_disconnect(self, client, userdata, rc):
        """断开连接时的回调函数"""
        print("Disconnected from MQTT broker with code", rc)
        # 断线自动重连
        if rc != 0:
            print("Attempting to reconnect...")
            self.reconnect()

    def reconnect(self):
        """重新连接到MQTT服务器"""
        try:
            self.client.reconnect()
            print("Reconnected to MQTT broker")
        except Exception as e:
            print(f"Reconnection failed: {e}")

    def subscribe(self, topic):
        """订阅主题"""
        self.client.subscribe(topic)
        print(f"Subscribed to topic: {topic}")

    def on_message(self, client, userdata, msg):
        """接收消息时的回调函数"""
        print(f"Received message: {msg.payload.decode()} on topic {msg.topic}")

    def send_message(self, topic, message):
        """向主题发送消息"""
        result = self.client.publish(topic, message)
        # 检查是否发送成功
        status = result[0]
        if status == 0:
            print(f"Message '{message}' sent to topic '{topic}'")
        else:
            print(f"Failed to send message to topic {topic}")


d_client = MQTTClient("192.168.40.13", 1883)
p_client = MQTTClient("116.85.2.49", 1884)

fault_code = "5010"
device_code = 702

charge_record = {
    "version": "1.0.0",
    "package_num": 3093,
    "sub_pkt_num": 1,
    "package_seq": 1,
    "body": {
        "gun_id": 0,
        "cloud_session_id": "101437000173233234026200702",
        "device_session_id": "0000100600241123140621",
        "start_time": 1732332389,
        "stop_time": 1732332863,
        "charge_time": 474,
        "start_meter_value": 1438688,
        "stop_meter_value": 1439791,
        "start_soc": 40,
        "stop_soc": 40,
        "extend_stop_reason": "",
        "bat_max_vol": 0,
        "bat_max_vol_num": 0,
        "bat_min_vol": 0,
        "bat_min_vol_num": 0,
        "bat_max_temperature": 0,
        "bat_max_temperature_num": 0,
        "bat_min_temperature": 0,
        "bat_min_temperature_num": 0,
        "start_source": 5,
        "stop_type": 0,
        "stop_condition": 0,
        "stop_reason": device_code,
        "normal_end": 1,
        "electric_rate_id": "0",
        "cusp_energy": 0,
        "cusp_electric_cost": 0,
        "cusp_service_cost": 0,
        "peak_energy": 0,
        "peak_electric_cost": 0,
        "peak_service_cost": 0,
        "normal_energy": 0,
        "normal_electric_cost": 0,
        "normal_service_cost": 0,
        "valley_energy": 0,
        "valley_electric_cost": 0,
        "valley_service_cost": 0,
        "deep_valley_energy": 0,
        "deep_valley_electric_cost": 0,
        "deep_valley_service_cost": 0,
        "total_energy": 1103,
        "total_electric_cost": 2316 - 1103,
        "total_service_cost": 1103,
        "total_cost": 2316,
        "card_id": "76283769",
        "user_id": "",
        "vin": "TEST0000000000004",
        "record_type": 0,
        "main_session_id": "",
        "connect_time": 1732334401,
        "multi_mode": 0,
        "interval_count": 0,
        "interval": [],
        "extend_count": 0,
        "extend": []
    },
    "need_response": True
}

d_client.connect()
p_client.connect()
d_client.send_message(HHhdlist.topic_hqc_main_telemetry_notify_fault,
                      '{"version":"1.0.0","package_num":8543,"sub_pkt_num":1,"package_seq":1,"body":{"faultVal":[{"device_num":0,"fault_id":702,"start_time":1732600482,"desc":"1#主机急停故障"}],"warnVal":[],"faultSum":1,"warnSum":0},"need_response":false}')
d_client.send_message(HHhdlist.topic_hqc_main_telemetry_notify_info, '{"version":"1.0.0","package_num":8897,"sub_pkt_num":1,"package_seq":1,"body":{"dcCharger":{"gun":{"0":{"0":11,"1":9,"2":0,"3":1,"4":0,"5":0,"6":1,"7":0,"8":0,"9":0,"10":0,"11":0,"12":0,"16":0,"17":0}}}},"need_response":false}')
d_client.send_message(HHhdlist.topic_hqc_main_telemetry_notify_info, '{"version":"1.0.0","package_num":8897,"sub_pkt_num":1,"package_seq":1,"body":{"dcCharger":{"gun":{"1":{"0":11,"1":9,"2":0,"3":1,"4":0,"5":0,"6":1,"7":0,"8":0,"9":0,"10":0,"11":0,"12":0,"16":0,"17":0}}}},"need_response":false}')

d_client.send_message(HHhdlist.topic_hqc_main_event_notify_charge_record, json.dumps(charge_record))

# 程序结束时断开连接
d_client.disconnect()


info = {
    "gun_id": 1,
    "device_id": HStategrid.Device_ID,
    "result": fault_code,
    "charge_id": "101437000173233234026200702"
}
msg = HStategrid.tpp_cmd_8(info)
d_client.send_message(HStategrid.Device_ID, msg)
tpp_202 = {
    "device_id": "0012240002000605",
    "gun_type": 1,
    "gun_id": 1,
    "charge_id": "101437000173233234026200702",
    "charge_start_time": 1732332389,
    "charge_stop_time": 1732332863,
    "charge_time": 474,
    "charge_start_soc": 40,
    "charge_stop_soc": 40,
    "charge_stop_reason": fault_code,
    "charge_kwh_amount": 1103,
    "charge_start_meter": 1438688,
    "charge_stop_meter": 1439791,
    "charge_cost": 2316,
    "charge_card_stop_is": 1,
    "charge_start_balance": 0,
    "charge_stop_balance": 0,
    "charge_server_cost": 1103,
    "pay_offline_is": 0,
    "charge_policy": 0,
    "charge_policy_param": 0,
    "car_vin": "TEST0000000000004",
    "car_card": "",
    "kwh_amount": [
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 48, 62, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    "start_source": 1,
    "device_session_id": "0000100600241123140621",
    "cloud_session_id": "101437000173233234026200702"
}
msg = HStategrid.tpp_cmd_202(tpp_202)
d_client.send_message(HStategrid.Device_ID, msg)

# 程序结束时断开连接
p_client.disconnect()
