import queue
import threading
from datetime import datetime
from enum import Enum

ota_version = None

device_mqtt_status = False
qr_queue = queue.Queue()
fee_queue = queue.Queue()

device_charfer_p = {}  # 平台充电参数
'''
device_charfer_p{
    1:{}
    2:{}
}
'''

flaut_warning_type = {
    "device": {
        0x2000: [],
        0x2001: [],
        0x2002: [],
        0x2003: [],
        0x2004: [],
        0x2005: [],
        0x2006: [],
        0x2007: [],
        0x2008: [53, 54, 600, 608, 609],
        0x2009: [],
        0x200A: [],
        0x200B: [],
        0x200C: [],
        0x200D: [24],
        0x201E: [],
        0x201F: [],
        0x2020: [],
        0x2021: [],
        0x2022: [],
        0x3000: [],
        0x3001: [47],
        0x3002: [16, 72],
        0x3003: [15, 71],
        0x3004: [21, 75],
        0x3005: [400],
        0x3007: [],
        0x3008: [31, 406],
        0x3009: [],
        0x300A: [30, 44, 407, 408, 409, 612],
        0x300B: [32],
        0x3010: [100, 101],
        0x3011: [108],
        0x3012: [440, 441, 442, 443, 444, 445, 446, 447, 448, 449, 450, 451, 452, 453, 454, 455, 456],
        0x3013: [],
        0x3016: [80, 258],
        0x3019: [110, 501],
        0x301A: [22, 40, 92, 93],
        0x301D: [38],
        0x3022: [12, 39],
        0x3028: [23],
        0x3029: [46],
        0x302A: [19, 96, 97, 98],
        0x302C: [],
        0x302D: [102, 103, 104, 503, 504, 505],
        0x3031: [168],
        0x3032: [903, 904, 905, 906, 907, 908],
        0x3033: [],
        0x3034: [],
        0x3035: [],
        0x3036: [],
        0x3037: [],
        0x3038: [],
        0x303A: [],
        0x4000: [42, 43, 112, 121, 122, 124, 125, 126, 401, 402, 457],
        0x4001: [132, 133, 403],
        0x4002: [135, 136, 405],
        0x4003: [134, 404],
        0x4004: [138],
        0x4005: [18, 105, 506, 507, 508],
        0x4006: [],
        0x4007: [],
        0x4008: [],
        0x4009: [123],
        0x400A: [111, 502],
        0x400B: [],
        0x400C: [17, 73],
        0x400D: [],
        0x400E: [],
        0x400F: [],
        0x4010: [],

    },
    "gun": {
        0x1000: [5, 13, 191, 205, 227],
        0x1001: [1],
        0x1002: [],
        0x1003: [2, 11, 51],
        0x1004: [3, 4],
        0x1005: [33],
        0x1006: [37],
        0x1007: [14, 34],
        0x1008: [52],
        0x1009: [95],
        0x100A: [],
        0x100B: [35, 229],
        0x100C: [36, 57, 230],
        0x100D: [20, 228],
        0x3006: [261],
        0x300C: [167],
        0x300D: [91],
        0x300E: [45, 58, 900, 901, 902],
        0x300F: [99],
        0x3014: [152, 153, 154, 157, 158, 159, 166, 604, 605, 606, 607],
        0x3015: [94],
        0x3017: [81, 82, 259, 260],
        0x3018: [76, 77, 78, 79],
        0x301B: [],
        0x301C: [],
        0x301E: [],
        0x301F: [],
        0x3020: [],
        0x3021: [25, 26, 27],
        0x302B: [],
        0x302E: [165],
        0x302F: [601, 603],
        0x3030: [602, 610, 611],
        0x3039: [55],
        0x5000: [],
        0x5001: [187],
        0x5002: [192, 193],
        0x5003: [202],
        0x5004: [197],
        0x5005: [224],
        0x5006: [243],
        0x5007: [209, 56],
        0x5008: [],
        0x5009: [],
        0x500A: [184],
        0x500B: [246, 249, 250, 251, 252, 253, 254, 255, 256],
        0x500C: [156],
        0x500D: [232],
        0x500E: [233, 234],
        0x500F: [],
        0x5010: [131],
        0x5011: [141, 181, 182, 183, 185, 186, 188, 189, 194, 195, 196, 198, 199, 200, 201, 203, 204, 210, 211, 212,
                 221,
                 222, 223, 225, 226, 231, 237, 239, 242, 244, 245, 247, 248, 257],
        0x5012: [213],
        0x5013: [214],
        0x5014: [215],
        0x5015: [216],
        0x5016: [217],
        0x5017: [218, 236],
        0x5018: [219],
        0x5019: [220, 235],
        0x501A: [151],
        0x501B: [],
        0x501C: [155, 160, 161, 162, 163, 164, 190, 206, 207, 208, 238, 241],
        0x501D: [],
        0x501E: [],
        0x501F: [],
        0x5020: [],
        0x5021: [137, 240],
        0x5022: [139, 140],
        0x5023: [],
        0x5024: [],

    },
}

chargeSys = {}  # 系统
cabinet = {}  # 主机柜
gun = {}  # 枪
pdu = {}  # 模块控制器
module = {}  # 模块
bms = {}  # bms
meter = {}  # 电表
parkLock = {}  # 地锁

authstart = threading.Event()
gun_status = {}
charger_status = {
    "leisure": 0,
    "starting": 1,
    "charging": 2,
    "stopping": 3,
    "finish": 4,
    "fault": 5,
}

bms_sum = {}

topic_app_net_status = '/hqc/sys/network-state'
topic_app_device_fault_query = '/hqc/cloud/event-notify/fault'
topic_app_telemetry_remote_query = '/hqc/cloud/event-notify/info'
topic_app_charge_request_response = '/hqc/main/event-reply/request-charge'
topic_app_charge_control = '/hqc/main/event-notify/control-charge'
topic_app_app_authentication_response = '/hqc/main/event-reply/check-vin'
topic_app_charge_record_response = '/hqc/main/event-reply/charge-record'
topic_app_charge_settlement = '/hqc/main/event-notify/charge-account'
topic_app_account_recharge = '/hqc/cloud/event-notify/recharge'
topic_app_charge_rate_request_response = '/hqc/cloud/event-reply/request-rate'
topic_app_charge_start_strategy_request_response = '/hqc/cloud/event-reply/request-startup'
topic_app_power_allocation_strategy_request_response = '/hqc/cloud/event-reply/request-dispatch'
topic_app_offline_list_version_response = '/hqc/cloud/event-reply/request-offlinelist'
topic_app_charge_session_response = '/hqc/main/event-reply/charge-session'
topic_app_set_parameters = '/hqc/main/event-notify/update-param'
topic_app_QR_code_update = '/hqc/main/event-notify/update-qrcode'
topic_app_charge_rate_sync_message = '/hqc/main/event-notify/update-rate'
topic_app_charge_start_strategy_sync = '/hqc/main/event-notify/update-startup'
topic_app_power_allocation_strategy_sync = '/hqc/main/event-notify/update-dispatch'
topic_app_offline_list_version_sync = '/hqc/main/event-notify/update-offlinelist'
topic_app_offline_list_item_operation_log = '/hqc/main/event-notify/offlinelist-log'
topic_app_clear_faults_events = '/hqc/main/event-notify/clear'
topic_app_upgrade_control = '/hqc/sys/upgrade-notify/notify'
topic_app_read_version_number = '/hqc/sys/upgrade-notify/version'
topic_app_fetch_parameter = '/hqc/main/event-notify/read-param'
topic_app_fetch_current_Historical_fault = '/hqc/main/event-notify/read-fault'
topic_app_fetch_event = '/hqc/main/event-notify/read-event'
topic_app_time_sync = '/hqc/sys/time-sync'


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


#  充电枪遥测
Gun_Pistol = {
    0: None,
    1: None,
    2: None,
    3: None,
    4: None,
    5: None,
    6: None,
    7: None,
    8: None,
    9: None,
    10: None,
    11: None,
    12: None,
    110: None,
    111: None,
    112: None,
    113: None,
    114: None,
    115: None,
    116: None,
    117: None,
    118: None,
    119: None,
    120: None,
    121: None,
    122: None,
    123: None,
    124: None,
    125: None,
    126: None,
    127: None,
    128: None,
    129: None,
    130: None,
}

#  充电系统遥测
Device_Pistol = {
    20: None,
    21: None,
    22: None,
    23: None,
    24: None,
    25: None,
    26: None,
    27: None,
    28: None,
    29: None,
    31: None,
    32: None,
}

#  功率柜遥测
Power_Pistol = {
    0: None,
    1: None,
    2: None,
    3: None,
    4: None,
    110: None,
    111: None,
    112: None,
    113: None,
    114: None,
    115: None,
    116: None,
    117: None,
    118: None,
    119: None,
}

#  功率单元遥测
Power_Unit_Pistol = {
    1: None,
    2: None,
    3: None,
    4: None,
    5: None,
    6: None,
}

#  功率控制遥信
Power_Crrl_Plug = {
    1: None,
    2: None,
    3: None,
    4: None,
    5: None,
    6: None,
}

#  BMS遥测
BMS_disposable_Pistol = {
    0: None,
    1: None,
    2: None,
    3: None,
    4: None,
    5: None,
    6: None,
    7: None,
    8: None,
    9: None,
    10: None,
    11: None,
    12: None,
    13: None,
    14: None,
    15: None,
    16: None,
    17: None,
    18: None,
    100: None,
    101: None,
    102: None,
    103: None,
    104: None,
    105: None,
    106: None,
    107: None,
    108: None,
    109: None,
    110: None,
    111: None,
    112: None,
    113: None,
}

#  电表遥测
Meter_Pistol = {
    0: None,
    1: None,
    2: None,
    3: None,
    4: None,
    5: None,
    6: None,
}

#  地锁遥信
Ground_Plug = {
    0: None,
    1: None,
}


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

