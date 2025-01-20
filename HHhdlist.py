#!/bin/python3
import json
import os
import queue
import re
import subprocess
import time
from datetime import datetime
from enum import Enum
import platform

import HSyslog

ota_version = None
config_file = '/opt/hhd/ex_cloud/DeviceCode.json'
config_directory = '/opt/hhd/ex_cloud/'
device_mqtt_status = False
package_num = 0  # 包序号
Device_ready = False
gun_num = 0

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
    '1000': [5, 35, 36, 57, 191],
    '1001': [1, 4],
    '1002': [],
    '1003': [2, 11, 51, 59],
    '1004': [3, 6, 12, 14, ],
    '1005': [33],
    '1006': [37],
    '1007': [34],
    '1008': [52],
    '1009': [],
    '2000': [],
    '2001': [],
    '2002': [],
    '2003': [],
    '2004': [],
    '2005': [],
    '2006': [],
    '2007': [],
    '2008': [53, 54, 600, 601],
    '2009': [],
    '2020': [],
    '2021': [],
    '2022': [],
    '2024': [],
    '2025': [],
    '2026': [],
    '2027': [],
    '3000': [46, 177],
    '3001': [47],
    '3002': [16, 72],
    '3003': [15, 71],
    '3004': [75, 515, 513, 517, 518],
    '3005': [32],
    '3006': [261],
    '3007': [615],
    '3008': [31],
    '3009': [410],
    '3010': [100, 101, 170, 171],
    '3011': [108, 107],
    '3012': [],
    '3013': [95],
    '3014': [604],  # 绝缘监测故障
    '3015': [94, 606, 607],
    '3016': [80],
    '3017': [81, 82, 113, 114],
    '3018': [76, 77, 78, 79],
    '3019': [262, 263, 264, 265, 266, 267, 268],
    '3020': [],
    '3021': [],
    '3022': [39],
    '3023': [],
    '3028': [597],
    '3029': [25, 26, 27],
    '3030': [602, 610],
    '3031': [441],
    '3032': [],
    '3033': [510, 511, 512, 513, 514],
    '3034': [],
    '3035': [],
    '3036': [],
    '3037': [],
    '3038': [106, ],
    '3039': [],
    '3040': [96, 506],
    '3041': [110],
    '3042': [501],
    '3043': [74],
    '3044': [29],
    '3045': [406, 445, 446],
    '3046': [28, 458],
    '3047': [],
    '3048': [],
    '3049': [],
    '3050': [],
    '3051': [613],
    '4000': [49, 112, 121, 122, 124, 125, 126],
    '4001': [131, 132, 133],
    '4002': [135],
    '4003': [134, 136],
    '4004': [138],
    '4005': [18, 105],
    '4006': [155],
    '4007': [],
    '4008': [],
    '4009': [123],
    '4010': [],
    '4011': [42],
    '4012': [43],
    '4013': [519],
    '5000': [],
    '5001': [187],  # BCP充电参数配置报文超时
    '5002': [194, 195],
    '5003': [202],
    '5004': [197],
    '5005': [224, 225, 226],
    '5006': [243, 244, 245],
    '5007': [209, 210, 211],
    '5008': [],
    '5009': [137, 181, 182, 183],
    '5010': [],
    '5011': [257],
    '5012': [213],
    '5013': [214],  # BSM 报文中单体动力蓄电池电压过低
    '5014': [215],
    '5015': [216],
    '5016': [217],
    '5017': [212, 218, 221, 222],
    '5018': [219],
    '5019': [220],
    '5020': [255],
    '5021': [207],
    '5022': [139, 141],
    '5023': [],
    '5024': [],
    '5025': [204, 203],
    '5026': [175],
    '5027': [],
    '5028': [],
    '5029': [],
    '5030': [230],
    '5031': [154, 232],
    '5032': [233],
    '5033': [234],
    '5034': [235],
    '5035': [236],
    '5036': [239],
    '5037': [238],  # BST检测点2电压检测故障
    '5038': [237],
    '5039': [201, 240],
    '5040': [185, 186],
    '5041': [188, 189],
    '5042': [192],
    '5043': [193, 196],
    '5044': [],
    '6000': [],
    '6001': [403],
    '6002': [404],
    '6003': [],
    '6004': [400],
    '6005': [409],
    '6006': [407, 457],
    '6007': [509],
    '6008': [447, 448, 449, 450, 455, 456],
    '6009': [408, 614],
    '6010': [],
    '6011': [153],
    '6012': [258],
    '6013': [259, 260, 268],
    '6014': [103, 104, 504, 505],
    '6015': [],
    '6016': [],
    '6017': [401],
    '6018': [402],
    '6019': [],
    '100a': [],
    '100b': [],
    '100c': [599],
    '100d': [20, 55, 617],
    '200a': [],
    '200b': [],
    '200c': [21, 608, 609],
    '200d': [24, 596, 616],
    '200e': [],
    '201e': [],
    '201f': [],
    '300a': [30, 440],
    '300b': [411],
    '300c': [612],
    '300d': [],
    '300e': [45, 50, 58],
    '300f': [99, 169],
    '301a': [22, 23, 40, 92, 93],
    '301b': [],
    '301c': [172],
    '301d': [38, 618],
    '301e': [],
    '301f': [],
    '302a': [19, 97, 98, 507, 508],
    '302b': [],
    '302c': [44],
    '302d': [],
    '302e': [],
    '302f': [602, 611],
    '303a': [],
    '303b': [157, 158, 159, 605],
    '303c': [],
    '303d': [91, 166],
    '303e': [],
    '303f': [],
    '304a': [168, 443, 444],
    '304b': [],
    '304c': [],
    '304d': [],
    '304e': [412],
    '304f': [],
    '400a': [111, 502],
    '400b': [],
    '400c': [17, 73],
    '400d': [],
    '400e': [],
    '400f': [],
    '500a': [184],
    '500b': [246, 247, 248, 249, 250, 251, 256],
    '500c': [173, 200],
    '500d': [152],
    '500e': [],
    '500f': [],
    '501a': [151],
    '501b': [252],
    '501c': [208],
    '501d': [],
    '501e': [253],
    '501f': [254],
    '502a': [56],
    '502b': [],
    '502c': [162],  # 启动充电前直流输出接触器外侧电压与通信报文电池电压相差＞±5%
    '502d': [165],
    '502e': [198, 199],
    '502f': [],
    '503a': [174, 241],
    '503b': [231, 242],
    '503c': [163, 164],
    '503d': [160],
    '503e': [161],
    '503f': [176, 190, 223],
    '600a': [],
    '600b': [],
    '600c': [],
    '600d': [102, 503],
    '600e': [405],
    '600f': [413, 451, 452, 453, 454],
    '9000': [],
    '9001': [],
    '9002': [],
    '9003': [],
    '9004': [],
    '9005': [206],
    '9006': [48],
    '9007': [],
    '9008': [],
    '9009': [],
    '900a': [],
    '900b': [],
    '900c': [],
    '900d': [],
    '900e': [520, 521, 522],
    '900f': [],
    '9010': [],
    '9011': [140],
    '9012': [],
    '9013': [205],
    '9014': [],
    '9015': [598],
    '9016': [],
    '9017': [],
    '9018': [],
    '9019': [],
    '901a': [],
    '901b': [],
    '901c': [],
    '901d': [],
    '901e': [],
    '901f': [156, 167],
    '9020': [],
    '9021': [],
    '9022': [],
    '9023': [],
    '9024': [],
    '9025': [],
    '9026': [],
    '9027': [],
    '9028': [],
    '9029': [],
    '902a': [],
    '902b': [],
    '902c': [41],
    '902d': [],
    '902e': [109, 500]
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


class device_system_mode(Enum):
    Windows = 1
    Linux = 2
    Darwin = 3


system_mode = device_system_mode.Linux.value


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
    return '0000'


def get_ip_from_resolv():
    if system_mode == device_system_mode.Linux.value:
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
    else:
        return "8.8.8.8"


def ping_ip(IP):
    if system_mode == device_system_mode.Linux.value:
        ping_process = subprocess.Popen(
            ['ping', '-c', '4', IP],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        ping_output, ping_error = ping_process.communicate()
        return ping_output.decode('utf-8'), ping_process.returncode
    else:
        # Windows 的 ping 命令
        ping_process = subprocess.Popen(
            ['ping', '-n', '4', IP],  # '-n 4' 表示发送 4 个包
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        ping_output, ping_error = ping_process.communicate()
        return ping_output.decode('gbk'), ping_process.returncode


def parse_ping_output(output):
    try:
        if system_mode == device_system_mode.Linux.value:
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
        else:
            loss_match = re.search(r"丢失 = \d+ \((\d+)% 丢失\)", output)
            rtt_match = re.search(r"平均 = (\d+)ms", output)
            # 提取丢包率
            if loss_match:
                packet_loss = int(loss_match.group(1))
            else:
                packet_loss = 100  # 如果没有找到丢包率信息，则认为是100%丢包

            # 提取平均延迟
            if rtt_match:
                average_latency = float(rtt_match.group(1))
            else:
                average_latency = None

            return packet_loss, average_latency
    except Exception as e:
        HSyslog.log_error(f"Error parsing ping output: {e}")
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
            HSyslog.log_error(f"Error calculating sigVal: {e}")
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
                HSyslog.log_error(f"Error calculating sigVal: {e}")
                return 0
        else:
            net_status["sigVal"] = 0
    except Exception as e:
        HSyslog.log_error(f"get_net: {return_code} . {ping_output} .{e}")

    try:
        if system_mode == device_system_mode.Linux.value:
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
        else:
            # Windows 使用 `ipconfig`
            net_cmd = ['ipconfig']
            net_process = subprocess.Popen(net_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            net_output, net_error = net_process.communicate()

            # 解码输出为 GBK 编码（适用于简体中文系统）
            net_output = net_output.decode('gbk', errors='ignore')

            # 检查接口类型
            if "无线局域网适配器" in net_output or "Wireless" in net_output:
                net_status["netType"] = 5  # 无线网络
                net_status["netId"] = 3
            elif "以太网适配器" in net_output or "Ethernet" in net_output:
                net_status["netType"] = 6  # 有线网络
                net_status["netId"] = 2
            elif "PPP" in net_output:
                net_status["netType"] = 2  # PPP 网络
                net_status["netId"] = 1
            else:
                net_status["netType"] = 6
                net_status["netId"] = 2
    except Exception as e:
        HSyslog.log_error(f"get_net: {ifconfig_process} . {ifconfig_output} .{e}")


def get_sysytem_mode():
    global system_mode
    os_name = platform.system()
    if os_name == "Windows":
        system_mode = device_system_mode.Windows.value
        return device_system_mode.Windows.value
    elif os_name == "Linux":
        system_mode = device_system_mode.Linux.value
        return device_system_mode.Linux.value
    elif os_name == "Darwin":
        system_mode = device_system_mode.Darwin.value
        return device_system_mode.Darwin.value
    else:
        system_mode = device_system_mode.Linux.value
        return device_system_mode.Linux.value


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
            HSyslog.log_error(f"无法解析文件 {file_path}。使用空配置。")
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
