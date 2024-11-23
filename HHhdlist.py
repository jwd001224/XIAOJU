#!/bin/python3
import json
import os
import queue
import re
import subprocess
import time
from datetime import datetime
from enum import Enum

import HSyslog

ota_version = None
config_file = '/opt/hhd/ex_cloud/DeviceCode.json'
config_directory = '/opt/hhd/ex_cloud/'
device_mqtt_status = False
package_num = 0  # 包序号
Device_ready = False
gun_num = 0
qrcode_nums = 0
hd_send_data = queue.Queue()

device_platform_data = queue.Queue()
platform_device_data = queue.Queue()

read_param_is = False
write_param_is = False

net_status = {
    "netType": 6,
    "sigVal": 4,
    "netId": 2,
}

stop_fault_code = {
    "1000": [0, 5],
    "1001": [1],
    "1002": [13, 14],
    "1003": [7, 51, 59, 599],
    "1004": [2, 3, 4],
    "1005": [33],
    "1006": [37],
    "1007": [34],
    "1008": [52],
    "1009": [],
    "100A": [],
    "100B": [35, 36],
    "100C": [6, 8, 57],
    "100D": [],

    "2000": [615, 616],
    "2001": [],
    "2002": [],
    "2003": [],
    "2004": [],
    "2005": [],
    "2006": [],
    "2007": [],
    "2008": [53, 54, 600, 608, 609],
    "2009": [],
    "200A": [],
    "200B": [],
    "200C": [21],
    "200D": [24, 596],
    "201E": [],
    "201F": [],
    "2020": [],
    "2021": [],
    "2022": [],

    "3000": [177],
    "3001": [47],
    "3002": [16, 72],
    "3003": [15, 71],
    "3004": [75, 515, 516, 517, 518, 519, 520, 521, 522],
    "3005": [400],
    "3006": [261],
    "3007": [],
    "3008": [31, 406, 440, 441, 442, 443, 444, 445, 446, 447, 448, 449, 450, 451, 452, 453, 454, 455, 456, 457, 458],
    "3009": [410],
    "300A": [30, 407, 408, 409],
    "300B": [32, 411],
    "300C": [39],
    "300D": [91],
    "300E": [45, 50, 58],
    "300F": [106],
    "3010": [99, 100, 101, 169, 170, 171],
    "3011": [107, 108],
    "3012": [102, 103, 104],
    "3013": [95],
    "3014": [152, 153, 154, 157, 158, 159, 166, 167, 604, 605],
    "3015": [9, 412, 413, 606, 607],
    "3016": [80, 258, ],
    "3017": [81, 82, 113, 114, 259, 260, 268],
    "3018": [76, 77, 78, 79],
    "3019": [109, 110, 500, 501],
    "301A": [22, 23, 29, 40, 92, 93],
    "301B": [172, 175, 617],
    "301C": [],
    "301D": [17, 28, 38, 41, 73, 74],
    "301E": [],
    "301F": [],
    "3020": [],
    "3021": [25, 26, 27, 46, 595],
    "3022": [48, ],
    "3028": [],
    "3029": [49],
    "302A": [19, 96, 97, 98, 506, 507, 508],
    "302B": [],
    "302C": [],
    "302D": [503, 504, 505],
    "302E": [165],
    "302F": [60, 597, 598, 603],
    "3030": [601, 602, 610, 611],
    "3031": [44, 168, 612],
    "3032": [],
    "3033": [262, 263, 264, 265, 266, 267, 510, 511, 512, 513, 514],
    "3034": [613],
    "3035": [],
    "3036": [],
    "3037": [],
    "3038": [],
    "3039": [20, 55],
    "303A": [],

    "4000": [42, 43, 112, 121, 122, 124, 125, 126, 401, 402],
    "4001": [131, 132, 133, 403],
    "4002": [135, 136, 137, 404],
    "4003": [134, 405],
    "4004": [138, 614],
    "4005": [18, 105],
    "4006": [],
    "4007": [],
    "4008": [],
    "4009": [123, 509],
    "400A": [111, 502],
    "400B": [],
    "400C": [],
    "400D": [],
    "400E": [],
    "400F": [],
    "4010": [],

    "5000": [],
    "5001": [176, 187, 188, 189, 190, 191],
    "5002": [],
    "5003": [202, 203, 204, 205, 206, 207, 208],
    "5004": [174, 197, 198, 199, ],
    "5005": [224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242],
    "5006": [243, 244, 245],
    "5007": [56, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221],
    "5008": [192, 193, 194, 195, 196],
    "5009": [140, 160, 161, 163, 164, 181, 182, 183],
    "500A": [184, 185, 186],
    "500B": [246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256],
    "500C": [173, 200, 201],
    "500D": [155, 156],
    "500E": [],
    "500F": [],
    "5010": [],
    "5011": [257, 618],
    "5012": [],
    "5013": [],
    "5014": [],
    "5015": [141],
    "5016": [],
    "5017": [222],
    "5018": [],
    "5019": [],
    "501A": [151],
    "501B": [],
    "501C": [162, 223],
    "501D": [],
    "501E": [],
    "501F": [],
    "5020": [],
    "5021": [],
    "5022": [139],
    "5023": [],
    "5024": [],
}

chargeSys = {}  # 系统
cabinet = {}  # 主机柜
gun = {}  # 枪
pdu = {}  # 模块控制器
module = {}  # 模块
bms = {}  # bms
meter = {}  # 电表
parkLock = {}  # 地锁

topic_hqc_sys_network_state = '/hqc/sys/network-state'  # 网络状态消息
topic_hqc_sys_time_sync = '/hqc/sys/time-sync'  # 时间同步消息
topic_hqc_main_telemetry_notify_fault = '/hqc/main/telemetry-notify/fault'  # 设备故障消息
topic_hqc_cloud_event_notify_fault = '/hqc/cloud/event-notify/fault'  # 设备故障查询消息
topic_hqc_main_telemetry_notify_info = '/hqc/main/telemetry-notify/info'  # 遥测遥信消息
topic_hqc_cloud_event_notify_info = '/hqc/cloud/event-notify/info'  # 遥测遥信查询消息
topic_hqc_main_event_notify_request_charge = '/hqc/main/event-notify/request-charge'  # 充电请求消息
topic_hqc_main_event_reply_request_charge = '/hqc/main/event-reply/request-charge'  # 充电请求应答消息
topic_hqc_main_event_notify_control_charge = '/hqc/main/event-notify/control-charge'  # 充电控制消息
topic_hqc_main_event_reply_control_charge = '/hqc/main/event-reply/control-charge'  # 充电控制应答消息
topic_hqc_ui_event_notify_auth_gun = '/hqc/ui/event-notify/auth-gun'  # 鉴权绑定消息
topic_hqc_main_event_notify_check_vin = '/hqc/main/event-notify/check-vin'  # 车辆VIN鉴权消息
topic_hqc_main_event_reply_check_vin = '/hqc/main/event-reply/check-vin'  # 车辆VIN鉴权应答消息
topic_hqc_main_event_notify_charge_record = '/hqc/main/event-notify/charge-record'  # 充电记录消息
topic_hqc_main_event_reply_charge_record = '/hqc/main/event-reply/charge-record'  # 充电记录应答消息
topic_hqc_main_event_notify_charge_cost = '/hqc/main/event-notify/charge-cost'  # 充电费用消息
topic_hqc_main_event_notify_charge_elec = '/hqc/main/event-notify/charge-elec'  # 充电电量冻结消息
topic_hqc_main_event_notify_charge_account = '/hqc/main/event-notify/charge-account'  # 充电结算消息
topic_hqc_cloud_event_notify_recharge = '/hqc/cloud/event-notify/recharge'  # 账户充值消息
topic_hqc_cloud_event_reply_recharge = '/hqc/cloud/event-reply/recharge'  # 账户充值应答消息
topic_hqc_cloud_event_notify_balance_query = '/hqc/cloud/event-notify/balance-query'  # 账户余额查询消息
topic_hqc_cloud_event_reply_balance_query = '/hqc/cloud/event-reply/balance-query'  # 账户余额查询结果消息
topic_hqc_cloud_event_notify_request_rate = '/hqc/cloud/event-notify/request-rate'  # 充电系统费率请求消息
topic_hqc_cloud_event_reply_request_rate = '/hqc/cloud/event-reply/request-rate'  # 充电系统费率请求应答消息
topic_hqc_cloud_event_notify_query_rate = '/hqc/cloud/event-notify/query-rate'  # 充电系统费率查询消息
topic_hqc_cloud_event_reply_query_rate = '/hqc/cloud/event-reply/query-rate'  # 充电系统费率查询结果消息
topic_hqc_cloud_event_notify_request_gunrate = '/hqc/cloud/event-notify/request-gunrate'  # 充电枪费率请求消息
topic_hqc_cloud_event_reply_request_gunrate = '/hqc/cloud/event-reply/request-gunrate'  # 充电枪费率请求应答消息
topic_hqc_cloud_event_notify_query_gunrate = '/hqc/cloud/event-notify/query-gunrate'  # 充电枪费率查询消息
topic_hqc_cloud_event_reply_query_gunrate = '/hqc/cloud/event-reply/query-gunrate'  # 充电枪费率查询结果消息
topic_hqc_cloud_event_notify_request_startup = '/hqc/cloud/event-notify/request-startup'  # 充电启动策略请求消息
topic_hqc_cloud_event_reply_request_startup = '/hqc/cloud/event-reply/request-startup'  # 充电启动策略请求应答消息
topic_hqc_cloud_event_notify_query_startup = '/hqc/cloud/event-notify/query-startup'  # 充电启动策略查询消息
topic_hqc_cloud_event_reply_query_startup = '/hqc/cloud/event-reply/query-startup'  # 充电启动策略查询结果消息
topic_hqc_cloud_event_notify_request_dispatch = '/hqc/cloud/event-notify/request-dispatch'  # 功率分配策略请求消息
topic_hqc_cloud_event_reply_request_dispatch = '/hqc/cloud/event-reply/request-dispatch'  # 功率分配策略请求应答消息
topic_hqc_cloud_event_notify_query_dispatch = '/hqc/cloud/event-notify/query-dispatch'  # 功率分配策略查询消息
topic_hqc_cloud_event_reply_query_dispatch = '/hqc/cloud/event-reply/query-dispatch'  # 功率分配策略查询结果消息
topic_hqc_cloud_event_notify_request_offlinelist = '/hqc/cloud/event-notify/request-offlinelist'  # 离线名单版本请求消息
topic_hqc_cloud_event_reply_request_offlinelist = '/hqc/cloud/event-reply/request-offlinelist'  # 离线名单版本应答消息
topic_hqc_main_event_notify_charge_session = '/hqc/main/event-notify/charge-session'  # 充电会话消息
topic_hqc_main_event_reply_charge_session = '/hqc/main/event-reply/charge-session'  # 充电会话应答消息
topic_hqc_main_event_notify_update_param = '/hqc/main/event-notify/update-param'  # 设置参数消息
topic_hqc_main_event_reply_update_param = '/hqc/main/event-reply/update-param'  # 设置参数应答消息
topic_hqc_main_event_notify_update_qrcode = '/hqc/main/event-notify/update-qrcode'  # 二维码更新消息
topic_hqc_main_event_notify_reserve_count_down = '/hqc/main/event-notify/reserve-count-down'  # 预约延时启动倒计时消息
topic_hqc_cloud_event_notify_m1_secret = '/hqc/cloud/event-notify/m1-secret'  # M1卡密钥更新消息
topic_hqc_cloud_event_reply_m1_secret = '/hqc/cloud/event-reply/m1-secret'  # M1卡密钥更新结果消息
topic_hqc_main_event_reply_update_qrcode = '/hqc/main/event-reply/update-qrcode'  # 二维码更新应答消息
topic_hqc_cloud_event_notify_pos_pre_transaction = '/hqc/cloud/event-notify/pos-pre-transaction'  # POS机预交易信息消息
topic_hqc_cloud_event_notify_pos_charge_cost = '/hqc/cloud/event-notify/pos-charge-cost'  # POS机扣费消息
topic_hqc_cloud_event_reply_pos_charge_cost = '/hqc/cloud/event-reply/pos-charge-cost'  # POS机扣费结果消息
topic_hqc_cloud_event_notify_update_charge_order_id = '/hqc/cloud/event-notify/update-charge-order-id'  # 充电订单ID更新消息
_hqc_cloud_event_reply_update_charge_order_id = '/hqc/cloud/event-reply/update-charge-order-id'  # 充电订单ID更新结果消息
topic_hqc_main_event_notify_update_rate = '/hqc/main/event-notify/update-rate'  # 充电系统费率同步消息
topic_hqc_main_event_reply_update_rate = '/hqc/main/event-reply/update-rate'  # 充电系统费率同步应答消息
topic_hqc_main_event_notify_update_gunrate = '/hqc/main/event-notify/update-gunrate'  # 充电枪费率同步消息
topic_hqc_main_event_reply_update_gunrate = '/hqc/main/event-reply/update-gunrate'  # 充电枪费率同步应答消息
topic_hqc_main_event_notify_update_startup = '/hqc/main/event-notify/update-startup'  # 充电启动策略同步消息
topic_hqc_main_event_reply_update_startup = '/hqc/main/event-reply/update-startup'  # 充电启动策略同步应答消息
topic_hqc_main_event_notify_update_dispatch = '/hqc/main/event-notify/update-dispatch'  # 功率分配策略同步消息
topic_hqc_main_event_reply_update_dispatch = '/hqc/main/event-reply/update-dispatch'  # 功率分配策略同步应答消息
topic_hqc_main_event_notify_update_offlinelist = '/hqc/main/event-notify/update-offlinelist'  # 离线名单版本同步消息
topic_hqc_main_event_reply_update_offflinelist = '/hqc/main/event-reply/update-offflinelist'  # 离线名单版本同步应答消息
topic_hqc_main_event_notify_offlinelist_log = '/hqc/main/event-notify/offlinelist-log'  # 离线名单项操作日志消息
topic_hqc_main_event_reply_offlinelist_log = '/hqc/main/event-reply/offlinelist-log'  # 离线名单项操作日志应答消息
topic_hqc_main_event_notify_clear = '/hqc/main/event-notify/clear'  # 清除故障、事件消息
topic_hqc_main_event_reply_clear = '/hqc/main/event-reply/clear'  # 清除故障、事件应答消息
topic_hqc_sys_upgrade_notify_notify = '/hqc/sys/upgrade-notify/notify'  # 升级控制消息
topic_hqc_sys_upgrade_reply_notify = '/hqc/sys/upgrade-reply/notify'  # 升级控制应答消息
topic_hqc_sys_upgrade_notify_process = '/hqc/sys/upgrade-notify/process'  # 升级进度消息
topic_hqc_sys_upgrade_notify_result = '/hqc/sys/upgrade-notify/result'  # 升级结果消息
topic_hqc_sys_upload_notify_notify = '/hqc/sys/upload-notify/notify'  # 日志文件上传请求消息
topic_hqc_sys_upload_reply_notify = '/hqc/sys/upload-reply/notify'  # 日志文件上传请求应答消息
topic_hqc_sys_upgrade_notify_version = '/hqc/sys/upgrade-notify/version'  # 读取版本号消息
topic_hqc_sys_upgrade_reply_version = '/hqc/sys/upgrade-reply/version'  # 读取版本号应答消息
topic_hqc_sys_upgrade_notify_control_command = '/hqc/sys/upgrade-notify/control_command'  # 远程控制命令消息
topic_hqc_sys_upgrade_reply_control_command = '/hqc/sys/upgrade-reply/control_command'  # 远程控制命令应答消息
topic_hqc_main_event_notify_read_param = '/hqc/main/event-notify/read-param'  # 参数读取消息
topic_hqc_main_event_reply_read_param = '/hqc/main/event-reply/read-param'  # 参数读取应答消息
topic_hqc_main_event_notify_read_fault = '/hqc/main/event-notify/read-fault'  # 当前/历史故障读取消息
topic_hqc_main_event_reply_read_fault = '/hqc/main/event-reply/read-fault'  # 当前/历史读取应答消息
topic_hqc_main_event_notify_read_event = '/hqc/main/event-notify/read-event'  # 事件读取消息
topic_hqc_main_event_reply_read_event = '/hqc/main/event-reply/read-event'  # 事件读取应答消息


class net_type(Enum):  # 网络状态
    no_net = 0
    other_net = 1
    net_4G = 2
    net_5G = 3
    NB_IOT = 4
    WIFI = 5
    wired_net = 6


class net_id(Enum):  # 网络运营商
    unknow = 0
    id_4G = 1
    id_cable = 2
    id_WIFI = 3


class control_charge(Enum):  # 充电控制
    start_charge = 1
    stop_charge = 2
    rev_charge = 3
    rev_not_charge = 4


class device_param_type(Enum):  # 设备分类
    chargeSys = 0x00
    cabinet = 0x01
    gun = 0x02
    pdu = 0x03
    module = 0x04
    bms = 0x05
    meter = 0x06
    parkLock = 0x07


class device_ctrl_type(Enum):  # 设备硬件分类
    TIU = 0x00
    GCU = 0x01
    PDU = 0x02
    CCU = 0x03
    DTU = 0x04
    ACU = 0x05
    UI = 0x1A
    SDK = 0x1B


#  充电枪遥测


def do_start_source(i):
    if i == 10:
        return 0x01
    elif i == 11:
        return 0x07
    elif i == 12:
        return 0x3F
    elif i == 13:
        return 0x01
    elif i == 14:
        return 0x3F
    elif i == 15:
        return 0x04


def unix_time(unix_t):
    dt_time = datetime.fromtimestamp(unix_t)
    return dt_time.strftime("%y%m%d")


def unix_time_14(unix_t):
    dt_time = datetime.fromtimestamp(unix_t)
    return dt_time.strftime("%Y%m%d%H%M%S")


def get_unix_time():
    return int(time.time())


def get_auxiliary_power_options(auxiliary_power_options):
    if auxiliary_power_options == 0:
        return 0x5A
    if auxiliary_power_options == 1:
        return 0xA5


def get_reservation_status(reservation_status):
    if reservation_status == 0x0A:
        return 1
    else:
        return 0


def get_control_reason(control_reason):
    if control_reason == 0:
        return 0x00
    if control_reason == 1:
        return 0x08
    if control_reason == 2:
        return 0x05
    if control_reason == 3:
        return 0x01
    if control_reason == 4:
        return 0x02


def get_reply_check_vin_result(result):
    if result == 0x01:
        return 0x00
    if result == 0x00:
        return 0x01


def get_reply_check_vin_reason(reason):
    if reason == 0x00:
        return 0x00
    if reason == 0x01:
        return 0x01
    if reason == 0x02:
        return 0x02
    if reason == 0x03:
        return 0x03
    if reason == 0x04:
        return 0x03


def get_stop_reason(stop_code):
    for stop_reason, reason_list in stop_fault_code.items():
        if stop_code in reason_list:
            return stop_reason


def get_ip_from_resolv():
    if os.path.getsize("/etc/resolv.conf") == 0:
        with open("/etc/resolv.conf", 'a') as file:
            file.write("nameserver 8.8.8.8\n")
        return "8.8.8.8"
    else:
        with open("/etc/resolv.conf", 'r') as file:
            lines = file.readlines()
            # 提取最后一行中的 IP 地址
            for line in lines:
                if line.startswith("nameserver"):
                    return "8.8.8.8"


def ping_ip(IP):
    ping_process = subprocess.Popen(
        ['ping', '-c', '4', IP],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    ping_output, ping_error = ping_process.communicate()
    return ping_output.decode('utf-8'), ping_process.returncode


def parse_ping_output(output):
    try:
        loss_match = re.search(r'(\d+)% packet loss', output)
        rtt_match = re.search(r'rtt min/avg/max/mdev = [\d.]+/([\d.]+)/[\d.]+/[\d.]+ ms', output)

        if loss_match:
            packet_loss = int(loss_match.group(1))
        else:
            packet_loss = 100  # 如果没有找到丢包率信息，则认为是100%丢包

        if rtt_match:
            average_latency = float(rtt_match.group(1))
        else:
            average_latency = None

        return packet_loss, average_latency
    except Exception as e:
        print(f"Error parsing ping output: {e}")
        return None, None


def calculate_sigval(packet_loss, latency):
    if latency is None:
        return 0

    if packet_loss < 100:
        if 0 <= latency < 50:
            sigVal = 4
        elif 50 <= latency < 120:
            sigVal = 3
        elif 120 <= latency < 200:
            sigVal = 2
        elif 200 <= latency < 300:
            sigVal = 1
        else:
            sigVal = 0
        return sigVal
    else:
        return 0


def get_ping():
    IP = get_ip_from_resolv()
    ping_output, return_code = ping_ip(IP)
    if return_code == 0:
        try:
            packet_loss, average_latency = parse_ping_output(ping_output)
            if packet_loss is not None and average_latency is not None:
                if packet_loss <= 100:
                    return 1
                else:
                    return 0
        except Exception as e:
            HSyslog.log_info(f"Error calculating sigVal: {e}")
            return 0
    else:
        return 0


def get_net():
    IP = get_ip_from_resolv()
    ping_output, return_code = ping_ip(IP)
    try:
        if return_code == 0:
            try:
                packet_loss, average_latency = parse_ping_output(ping_output)
                # 检查丢包率
                if packet_loss is not None and average_latency is not None:
                    if packet_loss <= 90:
                        net_status["sigVal"] = calculate_sigval(packet_loss, average_latency)
                    else:
                        net_status["sigVal"] = calculate_sigval(packet_loss, average_latency)
            except Exception as e:
                print(f"Error calculating sigVal: {e}")
                return 0
        else:
            net_status["sigVal"] = 0
    except Exception as e:
        HSyslog.log_info(f"get_net: {return_code} . {ping_output} .{e}")

    try:
        # 获取网络接口信息
        ifconfig_process = subprocess.Popen(['ifconfig'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ifconfig_output, _ = ifconfig_process.communicate()
        # 检查网络接口类型
        if 'wlan' in str(ifconfig_output):
            net_status["netType"] = 5
            net_status["netId"] = 3
        elif 'eth' in str(ifconfig_output):
            net_status["netType"] = 6
            net_status["netId"] = 2
        elif 'ppp0' in str(ifconfig_output):
            net_status["netType"] = 2
            net_status["netId"] = 1
        else:
            net_status["netType"] = 6
            net_status["netId"] = 2
    except Exception as e:
        HSyslog.log_info(f"get_net: {return_code} . {ping_output} .{e}")


def read_json_config(config_type, file_path=config_file):
    try:
        with open(file_path, 'r') as config_file:
            config_data = json.load(config_file)
            if config_data:
                return config_data.get(config_type)
    except FileNotFoundError:
        print(f"文件 {file_path} 未找到。")
    except json.JSONDecodeError:
        print(f"无法解析文件 {file_path}。")
    return None


def save_json_config(config_data, file_path=config_file, directory_path=config_directory):
    # 如果文件存在，先读取现有的配置
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as config_file:
                existing_config = json.load(config_file)
        except json.JSONDecodeError:
            HSyslog.log_info(f"无法解析文件 {file_path}。使用空配置。")
            existing_config = {}
    else:
        # 如果文件不存在，初始化为空配置
        os.makedirs(directory_path)
        existing_config = {}

    # 更新现有配置
    existing_config.update(config_data)

    # 保存更新后的配置
    try:
        with open(file_path, 'w') as config_file:
            json.dump(existing_config, config_file, indent=4)
        print(f"配置成功更新并保存到 {file_path}")
    except Exception as e:
        print(f"保存配置文件失败: {e}")

