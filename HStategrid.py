from datetime import datetime
import inspect
import queue
import sqlite3
import time
from enum import Enum

import HSyslog




class XJ_GUN:
    def __init__(self, gun_id):
        self.gun_id = gun_id
        self.flaut = None
        self.bms_info = None
        self.gun_status = None


class xj_mqtt_cmd_enum(Enum):
    xj_cmd_type_1 = 1
    xj_cmd_type_2 = 2
    xj_cmd_type_3 = 3
    xj_cmd_type_4 = 4
    xj_cmd_type_5 = 5
    xj_cmd_type_6 = 6
    xj_cmd_type_7 = 7
    xj_cmd_type_8 = 8
    xj_cmd_type_11 = 11
    xj_cmd_type_12 = 12
    xj_cmd_type_23 = 23
    xj_cmd_type_24 = 24
    xj_cmd_type_33 = 33
    xj_cmd_type_34 = 34
    xj_cmd_type_35 = 35
    xj_cmd_type_36 = 36
    xj_cmd_type_40 = 40
    xj_cmd_type_41 = 41
    xj_cmd_type_101 = 101
    xj_cmd_type_102 = 102
    xj_cmd_type_103 = 103
    xj_cmd_type_104 = 104
    xj_cmd_type_105 = 105
    xj_cmd_type_106 = 106
    xj_cmd_type_107 = 107
    xj_cmd_type_108 = 108
    xj_cmd_type_113 = 113
    xj_cmd_type_114 = 114
    xj_cmd_type_117 = 117
    xj_cmd_type_118 = 118
    xj_cmd_type_119 = 119
    xj_cmd_type_120 = 120
    xj_cmd_type_201 = 201
    xj_cmd_type_202 = 202
    xj_cmd_type_205 = 205
    xj_cmd_type_206 = 206
    xj_cmd_type_301 = 301
    xj_cmd_type_302 = 302
    xj_cmd_type_303 = 303
    xj_cmd_type_304 = 304
    xj_cmd_type_305 = 305
    xj_cmd_type_306 = 306
    xj_cmd_type_307 = 307
    xj_cmd_type_308 = 308
    xj_cmd_type_309 = 309
    xj_cmd_type_310 = 310
    xj_cmd_type_311 = 311
    xj_cmd_type_312 = 312
    xj_cmd_type_409 = 409
    xj_cmd_type_410 = 410
    xj_cmd_type_501 = 501
    xj_cmd_type_502 = 502
    xj_cmd_type_503 = 503
    xj_cmd_type_504 = 504
    xj_cmd_type_509 = 509
    xj_cmd_type_510 = 510
    xj_cmd_type_801 = 801
    xj_cmd_type_802 = 802
    xj_cmd_type_1101 = 1101
    xj_cmd_type_1102 = 1102
    xj_cmd_type_1303 = 1303
    xj_cmd_type_1304 = 1304
    xj_cmd_type_1305 = 1305
    xj_cmd_type_1306 = 1306
    xj_cmd_type_1309 = 1309
    xj_cmd_type_1310 = 1310


def xj_cmd_1(p_data: list):  # 平台发送，设备接收
    try:
        info = {
            "cmd_type": p_data[4],
            "cmd_num": p_data[9],
            "cmd_len": p_data[10:12],
            "start_addr": p_data[5:9],
            "data": p_data[12:],
            "serial_code": p_data[0:4]
        }

        xj_resv_data.put([1, info])
        return info
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {p_data}")
        HSyslog.log_info(f"Service_mainres .{p_data} .{e} .{inspect.currentframe().f_lineno}")
        return {}


def xj_cmd_2(d_data: dict):  # 设备发送，平台接收
    equipment_id = d_data.get("equipment_id")
    cmd_type = d_data.get("cmd_type")
    cmd_num = d_data.get("cmd_num")
    result = d_data.get("result")
    start_addr = d_data.get("start_addr")
    data = d_data.get("data")
    serial_code = d_data.get("serial_code")

    try:
        xj_cmd_2_msg = []
        xj_cmd_2_msg += info_to_little_hex(serial_code, 4, 1)
        xj_cmd_2_msg += info_to_little_hex(equipment_id, 32, 0)
        xj_cmd_2_msg += info_to_little_hex(cmd_type, 1, 1)
        xj_cmd_2_msg += info_to_little_hex(start_addr, 4, 1)
        xj_cmd_2_msg += info_to_little_hex(cmd_num, 1, 1)
        xj_cmd_2_msg += info_to_little_hex(result, 1, 1)
        for data_addr, data_len in cleck_code_1.items():
            if start_addr == data_addr:
                xj_cmd_2_msg += info_to_little_hex(data, data_len[0], data_len[1])

        return xj_cmd_2_msg
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {d_data}")
        HSyslog.log_info(f"Service_mainres .{d_data} .{e} .{inspect.currentframe().f_lineno}")
        return []


def xj_cmd_3(p_data: list):  # 平台发送，设备接收
    int.from_bytes(p_data[5:9], byteorder='little')
    info = {
        "cmd_type": p_data[4],
        "start_addr": p_data[5:9],
        "cmd_num": p_data[10],
        "cmd_len": p_data[9:11],
        "data": p_data[11:p_data[10] + 1],
        "serial_code": p_data[0:4]
    }
    xj_resv_data.put(p_data)
    return info


def xj_cmd_4(d_data: dict):  # 设备发送，平台接收
    equipment_id = d_data.get("equipment_id")
    cmd_type = d_data.get("cmd_type")
    result = d_data.get("result")
    start_addr = d_data.get("start_addr")
    data = d_data.get("data")
    serial_code = d_data.get("serial_code")
    dataLen = d_data.get("dataLen")  # 用于记录要发送查询的数据长度  ，但实际协议中并没有该字段

    try:
        xj_cmd_4_msg = []
        xj_cmd_4_msg += info_to_little_hex(serial_code, 4, 1)
        xj_cmd_4_msg += info_to_little_hex(equipment_id, 32, 0)
        xj_cmd_4_msg += info_to_little_hex(cmd_type, 1, 1)
        xj_cmd_4_msg += info_to_little_hex(start_addr, 4, 1)
        xj_cmd_4_msg += info_to_little_hex(result, 1, 1)
        for data_addr, data_len in cleck_code_1.items():
            if start_addr == data_addr:
                xj_cmd_4_msg += info_to_little_hex(data, data_len[0], data_len[1])

        return xj_cmd_4_msg
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {d_data}")
        HSyslog.log_info(f"Service_mainres .{d_data} .{e} .{inspect.currentframe().f_lineno}")
        return []


def xj_cmd_5(p_data: list):  # 平台发送，设备接收
    try:
        info = {
            "gun_index": p_data[4],
            "addr": p_data[5:9],
            "cmd_num": p_data[9],
            "cmd_len": p_data[10:12],
            "cmd_param": p_data[12:],
            "serial_code": p_data[0:4]
        }
        xj_resv_data.put(p_data)
        return info
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {p_data}")
        HSyslog.log_info(f"Service_mainres .{p_data} .{e} .{inspect.currentframe().f_lineno}")
        return {}


def xj_cmd_6(d_data: dict):  # 设备发送，平台接收
    equipment_id = d_data.get("equipment_id")
    gun_index = d_data.get("gun_index")
    addr = d_data.get("addr")
    cmd_num = d_data.get("cmd_num")
    result = d_data.get("result")
    serial_code = d_data.get("serial_code")

    try:
        xj_cmd_6_msg = []
        xj_cmd_6_msg += info_to_little_hex(serial_code, 4, 1)
        xj_cmd_6_msg += info_to_little_hex(equipment_id, 32, 0)
        xj_cmd_6_msg += info_to_little_hex(gun_index, 1, 1)
        xj_cmd_6_msg += info_to_little_hex(addr, 4, 1)
        xj_cmd_6_msg += info_to_little_hex(cmd_num, 1, 1)
        xj_cmd_6_msg += info_to_little_hex(result, 4, 0)

        return xj_cmd_6_msg
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {d_data}")
        HSyslog.log_info(f"Service_mainres .{d_data} .{e} .{inspect.currentframe().f_lineno}")
        return []


def xj_cmd_7(p_data: list):  # 平台发送，设备接收
    try:
        info = {
            "user_tel": p_data[2:4],
            "gun_index": p_data[4],
            "charge_type": p_data[5:9],
            "charge_policy": p_data[9:13],
            "charge_policy_param": p_data[13:17],
            "book_time": p_data[17:25],
            "book_delay_time": p_data[25],
            "charge_user_id": p_data[26:58],
            "allow_offline_charge": p_data[58],
            "allow_offline_charge_kw_amout": p_data[59:63],
            "charge_delay_fee": p_data[63],
            "charge_delay_wait_time": p_data[64:],
            "serial_code": p_data[0:2],
        }
        xj_resv_data.put(p_data)
        return info
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {p_data}")
        HSyslog.log_info(f"Service_mainres .{p_data} .{e} .{inspect.currentframe().f_lineno}")
        return {}


def xj_cmd_8(d_data: dict):  # 设备发送，平台接收
    equipment_id = d_data.get("equipment_id")
    gun_index = d_data.get("gun_index")
    result = d_data.get("result")
    charge_user_id = d_data.get("charge_user_id")
    serial_code = d_data.get("serial_code")

    try:
        xj_cmd_8_msg = []
        xj_cmd_8_msg += info_to_little_hex(serial_code, 4, 1)
        xj_cmd_8_msg += info_to_little_hex(equipment_id, 32, 0)
        xj_cmd_8_msg += info_to_little_hex(gun_index, 1, 1)
        xj_cmd_8_msg += info_to_little_hex(result, 4, 0)
        xj_cmd_8_msg += info_to_little_hex(charge_user_id, 32, 0)

        return xj_cmd_8_msg
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {d_data}")
        HSyslog.log_info(f"Service_mainres .{d_data} .{e} .{inspect.currentframe().f_lineno}")
        return []


def xj_cmd_11(p_data: list):  # 平台发送，设备接收
    try:
        info = {
            "equipment_id": p_data[0:32],
            "gun_index": p_data[32],
            "charge_seq": p_data[33:65],
            "serial_code": p_data[10],
        }
        xj_resv_data.put(p_data)
        return info
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {p_data}")
        HSyslog.log_info(f"Service_mainres .{p_data} .{e} .{inspect.currentframe().f_lineno}")
        return {}


def xj_cmd_12(d_data: dict):  # 设备发送，平台接收
    equipment_id = d_data.get("equipment_id")
    gun_index = d_data.get("gun_index")
    charge_seq = d_data.get("charge_seq")
    result = d_data.get("result")

    try:
        xj_cmd_12_msg = []
        xj_cmd_12_msg += info_to_little_hex(equipment_id, 32, 0)
        xj_cmd_12_msg += info_to_little_hex(gun_index, 1, 1)
        xj_cmd_12_msg += info_to_little_hex(charge_seq, 32, 0)
        xj_cmd_12_msg += info_to_little_hex(result, 4, 0)

        return xj_cmd_12_msg
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {d_data}")
        HSyslog.log_info(f"Service_mainres .{d_data} .{e} .{inspect.currentframe().f_lineno}")
        return []


def xj_cmd_23(p_data: list):  # 平台发送，设备接收
    try:
        info = {
            "equipment_id": p_data[4:36],
            "gun_index": p_data[36],
            "lock_type": p_data[37],
            "serial_code": p_data[0:4],
        }
        xj_resv_data.put(p_data)
        return info
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {p_data}")
        HSyslog.log_info(f"Service_mainres .{p_data} .{e} .{inspect.currentframe().f_lineno}")
        return {}


def xj_cmd_24(d_data: dict):  # 设备发送，平台接收
    equipment_id = d_data.get("equipment_id")
    gun_index = d_data.get("gun_index")
    result = d_data.get("result")
    serial_code = d_data.get("serial_code")

    try:
        xj_cmd_24_msg = []
        xj_cmd_24_msg += info_to_little_hex(serial_code, 4, 1)
        xj_cmd_24_msg += info_to_little_hex(equipment_id, 32, 0)
        xj_cmd_24_msg += info_to_little_hex(gun_index, 1, 1)
        xj_cmd_24_msg += info_to_little_hex(result, 1, 1)

        return xj_cmd_24_msg
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {d_data}")
        HSyslog.log_info(f"Service_mainres .{d_data} .{e} .{inspect.currentframe().f_lineno}")
        return []


def xj_cmd_33(p_data: list):  # 平台发送，设备接收
    try:
        info = {
            "equipment_id": p_data[0:32],
            "gun_index": p_data[32:34],
            "auth_result": p_data[34:36],
            "card_money": p_data[36:],
        }
        xj_resv_data.put(p_data)
        return info
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {p_data}")
        HSyslog.log_info(f"Service_mainres .{p_data} .{e} .{inspect.currentframe().f_lineno}")
        return {}


def xj_cmd_35(p_data: list):  # 平台发送，设备接收
    try:
        info = {
            "gun_index": p_data[32:34],
            "equipment_id": p_data[0:32],
            "card_id": p_data[34:50],
            "result": p_data[50:52],
        }
        xj_resv_data.put(p_data)
        return info
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {p_data}")
        HSyslog.log_info(f"Service_mainres .{p_data} .{e} .{inspect.currentframe().f_lineno}")
        return {}


def xj_cmd_41(p_data: list):  # 平台发送，设备接收
    try:
        info = {
            "equipment_id": p_data[0:32],
            "gun_index": p_data[32],
            "charge_user_id": p_data[33:65],
            "vin": p_data[82],
            "balance": p_data[82:86],
            "Request_result": p_data[86],
            "failure_reasons": p_data[87],
            "remainkon": p_data[88:92],
            "dump_energy": p_data[92:96],
            "residue_degree": p_data[96:100],
            "phone": p_data[100:],
            "serial_code": p_data[10],
        }
        xj_resv_data.put(p_data)
        return info
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {p_data}")
        HSyslog.log_info(f"Service_mainres .{p_data} .{e} .{inspect.currentframe().f_lineno}")
        return {}


def xj_cmd_34(d_data: dict):  # 设备发送，平台接收
    equipment_id = d_data.get("equipment_id")
    gun_index = d_data.get("gun_index")
    card_id = d_data.get("card_id")
    random_id = d_data.get("random_id")
    phy_card_id = d_data.get("phy_card_id")

    try:
        xj_cmd_34_msg = []
        xj_cmd_34_msg += info_to_little_hex(equipment_id, 32, 0)
        xj_cmd_34_msg += info_to_little_hex(gun_index, 2, 1)
        xj_cmd_34_msg += info_to_little_hex(card_id, 16, 0)
        xj_cmd_34_msg += info_to_little_hex(random_id, 48, 0)
        xj_cmd_34_msg += info_to_little_hex(phy_card_id, 4, 0)

        return xj_cmd_34_msg
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {d_data}")
        HSyslog.log_info(f"Service_mainres .{d_data} .{e} .{inspect.currentframe().f_lineno}")
        return []


def xj_cmd_36(d_data: dict):  # 设备发送，平台接收
    equipment_id = d_data.get("equipment_id")
    gun_index = d_data.get("gun_index")
    card_id = d_data.get("card_id")

    try:
        xj_cmd_36_msg = []
        xj_cmd_36_msg += info_to_little_hex(equipment_id, 32, 0)
        xj_cmd_36_msg += info_to_little_hex(gun_index, 2, 1)
        xj_cmd_36_msg += info_to_little_hex(card_id, 16, 0)

        return xj_cmd_36_msg
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {d_data}")
        HSyslog.log_info(f"Service_mainres .{d_data} .{e} .{inspect.currentframe().f_lineno}")
        return []


def xj_cmd_40(d_data: dict):  # 设备发送，平台接收
    equipment_id = d_data.get("equipment_id")
    gun_index = d_data.get("gun_index")
    vin = d_data.get("vin")
    serial_code = d_data.get("serial_code")

    try:
        xj_cmd_40_msg = []
        xj_cmd_40_msg += info_to_little_hex(serial_code, 2, 1)
        xj_cmd_40_msg += info_to_little_hex(equipment_id, 32, 0)
        xj_cmd_40_msg += info_to_little_hex(gun_index, 1, 1)
        xj_cmd_40_msg += info_to_little_hex(vin, 17, 0)

        return xj_cmd_40_msg
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {d_data}")
        HSyslog.log_info(f"Service_mainres .{d_data} .{e} .{inspect.currentframe().f_lineno}")
        return []


def xj_cmd_101(p_data: list):  # 平台发送，设备接收
    try:
        info = {
            "serial_code": p_data[0:4],
            "heart_index": p_data[4:6],
        }
        xj_resv_data.put(p_data)
        return info
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {p_data}")
        HSyslog.log_info(f"Service_mainres .{p_data} .{e} .{inspect.currentframe().f_lineno}")
        return {}


def xj_cmd_102(d_data: dict):  # 设备发送，平台接收
    equipment_id = d_data.get("equipment_id")
    heart_index = d_data.get("heart_index")

    try:
        xj_cmd_102_msg = []
        xj_cmd_102_msg += info_to_little_hex(serial_code, 4, 1)
        xj_cmd_102_msg += info_to_little_hex(equipment_id, 32, 0)
        xj_cmd_102_msg += info_to_little_hex(heart_index, 2, 1)

        return xj_cmd_102_msg
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {d_data}")
        HSyslog.log_info(f"Service_mainres .{d_data} .{e} .{inspect.currentframe().f_lineno}")
        return []


def xj_cmd_103(p_data: list):  # 平台发送，设备接收
    try:
        info = {
            "serial_code": p_data[0:4],
            "gun_index": p_data[4],
            "charge_user_id": p_data[5:37],
            "charge_card_account": p_data[37:41],
            "accountEnoughFlag": p_data[41],
        }
        xj_resv_data.put(p_data)
        return info
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {p_data}")
        HSyslog.log_info(f"Service_mainres .{p_data} .{e} .{inspect.currentframe().f_lineno}")
        return {}


def xj_cmd_104(d_data: dict):  # 设备发送，平台接收
    equipment_id = d_data.get("equipment_id")
    gun_cnt = d_data.get("gun_cnt")
    gun_index = d_data.get("gun_index")
    gun_type = d_data.get("gun_type")
    work_stat = d_data.get("work_stat")
    soc_percent = d_data.get("soc_percent")
    alarm_stat = d_data.get("alarm_stat")
    car_connection_stat = d_data.get("car_connection_stat")
    cumulative_charge_fee = d_data.get("cumulative_charge_fee")
    dc_charge_voltage = d_data.get("dc_charge_voltage")
    dc_charge_current = d_data.get("dc_charge_current")
    bms_need_voltage = d_data.get("bms_need_voltage")
    bms_need_current = d_data.get("bms_need_current")
    bms_charge_mode = d_data.get("bms_charge_mode")
    ac_a_vol = d_data.get("ac_a_vol")
    ac_b_vol = d_data.get("ac_b_vol")
    ac_c_vol = d_data.get("ac_c_vol")
    ac_a_cur = d_data.get("ac_a_cur")
    ac_b_cur = d_data.get("ac_b_cur")
    ac_c_cur = d_data.get("ac_c_cur")
    charge_full_time_left = d_data.get("charge_full_time_left")
    charged_sec = d_data.get("charged_sec")
    cum_charge_kwh_amount = d_data.get("cum_charge_kwh_amount")
    before_charge_meter_kwh_num = d_data.get("before_charge_meter_kwh_num")
    now_meter_kwh_num = d_data.get("now_meter_kwh_num")
    start_charge_type = d_data.get("start_charge_type")
    charge_policy = d_data.get("charge_policy")
    charge_policy_param = d_data.get("charge_policy_param")
    book_flag = d_data.get("book_flag")
    charge_user_id = d_data.get("charge_user_id")
    book_timeout_min = d_data.get("book_timeout_min")
    book_start_charge_time = d_data.get("book_start_charge_time")
    before_charge_card_account = d_data.get("before_charge_card_account")
    charge_power_kw = d_data.get("charge_power_kw")
    serial_code = d_data.get("serial_code")

    try:
        xj_cmd_104_msg = []
        xj_cmd_104_msg += info_to_little_hex(serial_code, 4, 1)
        xj_cmd_104_msg += info_to_little_hex(equipment_id, 32, 0)
        xj_cmd_104_msg += info_to_little_hex(gun_cnt, 1, 1)
        xj_cmd_104_msg += info_to_little_hex(gun_index, 1, 1)
        xj_cmd_104_msg += info_to_little_hex(gun_type, 1, 1)
        xj_cmd_104_msg += info_to_little_hex(work_stat, 1, 1)
        xj_cmd_104_msg += info_to_little_hex(soc_percent, 1, 1)
        xj_cmd_104_msg += info_to_little_hex(alarm_stat, 4, 0)
        xj_cmd_104_msg += info_to_little_hex(car_connection_stat, 1, 1)
        xj_cmd_104_msg += info_to_little_hex(cumulative_charge_fee, 1, 1)
        xj_cmd_104_msg += info_to_little_hex(serial_code, 8, 1)
        xj_cmd_104_msg += info_to_little_hex(dc_charge_voltage, 2, 1)
        xj_cmd_104_msg += info_to_little_hex(dc_charge_current, 2, 1)
        xj_cmd_104_msg += info_to_little_hex(bms_need_voltage, 2, 1)
        xj_cmd_104_msg += info_to_little_hex(bms_need_current, 2, 1)
        xj_cmd_104_msg += info_to_little_hex(bms_charge_mode, 1, 1)
        xj_cmd_104_msg += info_to_little_hex(ac_a_vol, 2, 1)
        xj_cmd_104_msg += info_to_little_hex(ac_b_vol, 2, 1)
        xj_cmd_104_msg += info_to_little_hex(ac_c_vol, 2, 1)
        xj_cmd_104_msg += info_to_little_hex(ac_a_cur, 2, 1)
        xj_cmd_104_msg += info_to_little_hex(ac_b_cur, 2, 1)
        xj_cmd_104_msg += info_to_little_hex(ac_c_cur, 2, 1)
        xj_cmd_104_msg += info_to_little_hex(charge_full_time_left, 2, 1)
        xj_cmd_104_msg += info_to_little_hex(charged_sec, 4, 1)
        xj_cmd_104_msg += info_to_little_hex(cum_charge_kwh_amount, 4, 1)
        xj_cmd_104_msg += info_to_little_hex(before_charge_meter_kwh_num, 8, 1)
        xj_cmd_104_msg += info_to_little_hex(now_meter_kwh_num, 8, 1)
        xj_cmd_104_msg += info_to_little_hex(start_charge_type, 1, 1)
        xj_cmd_104_msg += info_to_little_hex(charge_policy, 4, 1)
        xj_cmd_104_msg += info_to_little_hex(charge_policy_param, 4, 1)
        xj_cmd_104_msg += info_to_little_hex(book_flag, 1, 1)
        xj_cmd_104_msg += info_to_little_hex(charge_user_id, 32, 1)
        xj_cmd_104_msg += info_to_little_hex(book_timeout_min, 1, 1)
        xj_cmd_104_msg += info_to_little_hex(book_start_charge_time, 8, 1)
        xj_cmd_104_msg += info_to_little_hex(before_charge_card_account, 4, 1)
        xj_cmd_104_msg += info_to_little_hex(serial_code, 4, 1)
        xj_cmd_104_msg += info_to_little_hex(charge_power_kw, 4, 1)
        xj_cmd_104_msg += info_to_little_hex(serial_code, 12, 1)

        return xj_cmd_104_msg
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {d_data}")
        HSyslog.log_info(f"Service_mainres .{d_data} .{e} .{inspect.currentframe().f_lineno}")
        return []


def xj_cmd_105(p_data: list):  # 平台发送，设备接收
    try:
        info = {
            "reserve1": p_data[0:2],
            "reserve2": p_data[2:4],
            "time": p_data[4:12],
        }
        xj_resv_data.put(p_data)
        return info
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {p_data}")
        HSyslog.log_info(f"Service_mainres .{p_data} .{e} .{inspect.currentframe().f_lineno}")
        return {}


def xj_cmd_106(d_data: dict):  # 设备发送，平台接收
    charge_mode_num = d_data.get("charge_mode_num")
    charge_mode_rate = d_data.get("charge_mode_rate")
    equipment_id = d_data.get("equipment_id")
    offline_charge_flag = d_data.get("offline_charge_flag")
    stake_version = d_data.get("stake_version")
    stake_type = d_data.get("stake_type")
    stake_start_times = d_data.get("stake_start_times")
    data_up_mode = d_data.get("data_up_mode")
    sign_interval = d_data.get("sign_interval")
    reserve = d_data.get("reserve")
    gun_index = d_data.get("gun_index")
    heartInterval = d_data.get("heartInterval")
    heart_out_times = d_data.get("heart_out_times")
    stake_charge_record_num = d_data.get("stake_charge_record_num")
    stake_systime = d_data.get("stake_systime")
    stake_last_charge_time = d_data.get("stake_last_charge_time")
    stake_last_start_time = d_data.get("stake_last_start_time")
    signCode = d_data.get("signCode")
    mac = d_data.get("mac")
    ccu_version = d_data.get("ccu_version")

    try:
        xj_cmd_106_msg = []
        xj_cmd_106_msg += info_to_little_hex(charge_mode_num, 2, 1)
        xj_cmd_106_msg += info_to_little_hex(charge_mode_rate, 2, 1)
        xj_cmd_106_msg += info_to_little_hex(equipment_id, 32, 0)
        xj_cmd_106_msg += info_to_little_hex(offline_charge_flag, 1, 1)
        xj_cmd_106_msg += info_to_little_hex(stake_version, 4, 3)
        xj_cmd_106_msg += info_to_little_hex(stake_type, 2, 1)
        xj_cmd_106_msg += info_to_little_hex(stake_start_times, 4, 1)
        xj_cmd_106_msg += info_to_little_hex(data_up_mode, 1, 1)
        xj_cmd_106_msg += info_to_little_hex(sign_interval, 2, 1)
        xj_cmd_106_msg += info_to_little_hex(reserve, 1, 1)
        xj_cmd_106_msg += info_to_little_hex(gun_index, 1, 1)
        xj_cmd_106_msg += info_to_little_hex(heartInterval, 1, 1)
        xj_cmd_106_msg += info_to_little_hex(heart_out_times, 1, 1)
        xj_cmd_106_msg += info_to_little_hex(stake_charge_record_num, 4, 1)
        xj_cmd_106_msg += info_to_little_hex(stake_systime, 8, 2)
        xj_cmd_106_msg += info_to_little_hex(stake_last_charge_time, 8, 2)
        xj_cmd_106_msg += info_to_little_hex(stake_last_start_time, 8, 2)
        xj_cmd_106_msg += info_to_little_hex(signCode, 8, 0)
        xj_cmd_106_msg += info_to_little_hex(mac, 32, 0)
        xj_cmd_106_msg += info_to_little_hex(ccu_version, 4, 3)

        return xj_cmd_106_msg
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {d_data}")
        HSyslog.log_info(f"Service_mainres .{d_data} .{e} .{inspect.currentframe().f_lineno}")
        return {}


def xj_cmd_107(p_data: list):  # 平台发送，设备接收
    try:
        info = {
            "equipment_id": p_data[0:32],
            "gun_index": p_data[32],
            "event_name": p_data[33:37],
        }
        xj_resv_data.put(p_data)
        return info
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {p_data}")
        HSyslog.log_info(f"Service_mainres .{p_data} .{e} .{inspect.currentframe().f_lineno}")
        return {}


def xj_cmd_108(d_data: dict):  # 设备发送，平台接收
    gun_index = d_data.get("gun_index")
    event_addr = d_data.get("event_addr")
    event_param = d_data.get("event_param")
    charge_user_id = d_data.get("charge_user_id")
    serial_code = d_data.get("serial_code")

    try:
        xj_cmd_108_msg = []
        xj_cmd_108_msg += info_to_little_hex(serial_code, 4, 1)
        xj_cmd_108_msg += info_to_little_hex(gun_index, 1, 1)
        xj_cmd_108_msg += info_to_little_hex(event_addr, 4, 1)
        xj_cmd_108_msg += info_to_little_hex(event_param, 4, 1)
        xj_cmd_108_msg += info_to_little_hex(charge_user_id, 32, 0)

        return xj_cmd_108_msg
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {d_data}")
        HSyslog.log_info(f"Service_mainres .{d_data} .{e} .{inspect.currentframe().f_lineno}")
        return []


def xj_cmd_113(p_data: list):  # 平台发送，设备接收
    try:
        info = {
            "url": (p_data[4:-4][:p_data[4:-4].find(b'\x00')] if p_data[4:-4].find(b'\x00') != -1 else p_data[4:-4]).
            decode('utf-8', errors='ignore'),
            "port": int.from_bytes(p_data[-4:], byteorder='little'),
        }
        xj_resv_data.put(p_data)
        return info
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {p_data}")
        HSyslog.log_info(f"Service_mainres .{p_data} .{e} .{inspect.currentframe().f_lineno}")
        return {}


def xj_cmd_114(d_data: dict):  # 设备发送，平台接收
    equipment_id = d_data.get("equipment_id")
    reserve = d_data.get("reserve")

    try:
        xj_cmd_114_msg = []
        xj_cmd_114_msg += info_to_little_hex(reserve, 4, 1)
        xj_cmd_114_msg += info_to_little_hex(equipment_id, 32, 0)

        return xj_cmd_114_msg
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {d_data}")
        HSyslog.log_info(f"Service_mainres .{d_data} .{e} .{inspect.currentframe().f_lineno}")
        return {}


def xj_cmd_117(p_data: list):  # 平台发送，设备接收
    try:
        info = {
            "equipment_id": p_data[0:32],
            "gun_index": p_data[32],
            "errCode": p_data[33:37],
        }
        xj_resv_data.put(p_data)
        return info
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {p_data}")
        HSyslog.log_info(f"Service_mainres .{p_data} .{e} .{inspect.currentframe().f_lineno}")
        return {}


def xj_cmd_118(d_data: dict):  # 设备发送，平台接收
    equipment_id = d_data.get("equipment_id")
    gun_index = d_data.get("gun_index")
    err_code = d_data.get("err_code")
    err_status = d_data.get("err_status")

    try:
        xj_cmd_118_msg = []
        xj_cmd_118_msg += info_to_little_hex(equipment_id, 32, 1)
        xj_cmd_118_msg += info_to_little_hex(gun_index, 1, 1)
        xj_cmd_118_msg += info_to_little_hex(err_code, 4, 0)
        xj_cmd_118_msg += info_to_little_hex(err_status, 1, 1)

        return xj_cmd_118_msg
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {d_data}")
        HSyslog.log_info(f"Service_mainres .{d_data} .{e} .{inspect.currentframe().f_lineno}")
        return []


def xj_cmd_119(p_data: list):  # 平台发送，设备接收
    try:
        info = {
            "equipment_id": p_data[0:32],
            "gun_index": p_data[32],
            "warning_code": p_data[33:37],
        }
        xj_resv_data.put(p_data)
        return info
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {p_data}")
        HSyslog.log_info(f"Service_mainres .{p_data} .{e} .{inspect.currentframe().f_lineno}")
        return {}


def xj_cmd_120(d_data: dict):  # 设备发送，平台接收
    equipment_id = d_data.get("equipment_id")
    gun_index = d_data.get("gun_index")
    warning_code = d_data.get("warning_code")
    charge_user_id = d_data.get("charge_user_id")
    type = d_data.get("type")
    threshold = d_data.get("threshold")
    retain = d_data.get("retain")
    err_status = d_data.get("err_status")

    try:
        xj_cmd_120_msg = []
        xj_cmd_120_msg += info_to_little_hex(equipment_id, 32, 0)
        xj_cmd_120_msg += info_to_little_hex(gun_index, 1, 1)
        xj_cmd_120_msg += info_to_little_hex(warning_code, 4, 0)
        xj_cmd_120_msg += info_to_little_hex(charge_user_id, 32, 0)
        xj_cmd_120_msg += info_to_little_hex(type, 1, 1)
        xj_cmd_120_msg += info_to_little_hex(threshold, 4, 1)
        xj_cmd_120_msg += info_to_little_hex(retain, 4, 1)

        return xj_cmd_120_msg
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {d_data}")
        HSyslog.log_info(f"Service_mainres .{d_data} .{e} .{inspect.currentframe().f_lineno}")
        return []


def xj_cmd_301(p_data: list):  # 平台发送，设备接收
    try:
        info = {
            "equipment_id": p_data[4:36],
            "gun_index": p_data[2:4],
        }
        xj_resv_data.put(p_data)
        return info
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {p_data}")
        HSyslog.log_info(f"Service_mainres .{p_data} .{e} .{inspect.currentframe().f_lineno}")
        return {}


def xj_cmd_302(d_data: dict):  # 设备发送，平台接收
    gun_index = d_data.get("gun_index")
    equipment_id = d_data.get("equipment_id")
    work_stat = d_data.get("work_stat")
    car_connect_stat = d_data.get("car_connect_stat")
    brm_bms_connect_version = d_data.get("brm_bms_connect_version")
    brm_battery_type = d_data.get("brm_battery_type")
    brm_battery_power = d_data.get("brm_battery_power")
    brm_battery_voltage = d_data.get("brm_battery_voltage")
    brm_battery_supplier = d_data.get("brm_battery_supplier")
    brm_battery_seq = d_data.get("brm_battery_seq")
    brm_battery_produce_year = d_data.get("brm_battery_produce_year")
    brm_battery_produce_month = d_data.get("brm_battery_produce_month")
    brm_battery_produce_day = d_data.get("brm_battery_produce_day")
    brm_battery_charge_count = d_data.get("brm_battery_charge_count")
    brm_battery_property_identification = d_data.get("brm_battery_property_identification")
    serial_code = d_data.get("serial_code")
    brm_vin = d_data.get("brm_vin")
    brm_BMS_version = d_data.get("brm_BMS_version")
    bcp_max_voltage = d_data.get("bcp_max_voltage")
    bcp_max_current = d_data.get("bcp_max_current")
    bcp_max_power = d_data.get("bcp_max_power")
    bcp_total_voltage = d_data.get("bcp_total_voltage")
    bcp_max_temperature = d_data.get("bcp_max_temperature")
    bcp_battery_soc = d_data.get("bcp_battery_soc")
    bcp_battery_soc_current_voltage = d_data.get("bcp_battery_soc_current_voltage")
    bro_BMS_isReady = d_data.get("bro_BMS_isReady")

    bcl_voltage_need = d_data.get("bcl_voltage_need")
    bcl_current_need = d_data.get("bcl_current_need")
    bcl_charge_mode = d_data.get("bcl_charge_mode")
    bcs_test_voltage = d_data.get("bcs_test_voltage")
    bcs_test_current = d_data.get("bcs_test_current")
    bcs_max_single_voltage = d_data.get("bcs_max_single_voltage")
    bcs_max_single_no = d_data.get("bcs_max_single_no")
    bcs_current_soc = d_data.get("bcs_current_soc")
    last_charge_time = d_data.get("last_charge_time")
    bsm_single_no = d_data.get("bsm_single_no")
    bsm_max_temperature = d_data.get("bsm_max_temperature")
    bsm_max_temperature_check_no = d_data.get("bsm_max_temperature_check_no")
    bsm_min_temperature = d_data.get("bsm_min_temperature")
    bsm_min_temperature_check_no = d_data.get("bsm_min_temperature_check_no")
    bsm_voltage_too_high_or_too_low = d_data.get("bsm_voltage_too_high_or_too_low")
    bsm_car_battery_soc_too_high_or_too_low = d_data.get("bsm_car_battery_soc_too_high_or_too_low")
    bsm_car_battery_charge_over_current = d_data.get("bsm_car_battery_charge_over_current")
    bsm_battery_temperature_too_high = d_data.get("bsm_battery_temperature_too_high")
    bsm_battery_insulation_state = d_data.get("bsm_battery_insulation_state")
    bsm_battery_connect_state = d_data.get("bsm_battery_connect_state")
    bsm_allow_charge = d_data.get("bsm_allow_charge")

    bst_BMS_soc_target = d_data.get("bst_BMS_soc_target")
    bst_BMS_voltage_target = d_data.get("bst_BMS_voltage_target")
    bst_single_voltage_target = d_data.get("bst_single_voltage_target")
    bst_finish = d_data.get("bst_finish")
    bst_isolation_error = d_data.get("bst_isolation_error")
    bst_connect_over_temperature = d_data.get("bst_connect_over_temperature")
    bst_BMS_over_temperature = d_data.get("bst_BMS_over_temperature")
    bst_connect_error = d_data.get("bst_connect_error")
    bst_battery_over_temperature = d_data.get("bst_battery_over_temperature")
    bst_high_voltage_relay_error = d_data.get("bst_high_voltage_relay_error")
    bst_point2_test_error = d_data.get("bst_point2_test_error")
    bst_other_error = d_data.get("bst_other_error")
    bst_current_too_high = d_data.get("bst_current_too_high")
    bst_voltage_too_high = d_data.get("bst_voltage_too_high")
    bst_stop_soc = d_data.get("bst_stop_soc")
    bsd_battery_low_voltage = d_data.get("bsd_battery_low_voltage")
    bsd_battery_high_voltage = d_data.get("bsd_battery_high_voltage")
    bsd_battery_low_temperature = d_data.get("bsd_battery_low_temperature")
    bsd_battery_high_temperature = d_data.get("bsd_battery_high_temperature")
    error_68 = d_data.get("error_68")
    error_69 = d_data.get("error_69")
    error_70 = d_data.get("error_70")
    error_71 = d_data.get("error_71")
    error_72 = d_data.get("error_72")
    error_73 = d_data.get("error_73")
    error_74 = d_data.get("error_74")
    error_75 = d_data.get("error_75")

    try:
        xj_cmd_302_msg = []
        xj_cmd_302_msg += info_to_little_hex(serial_code, 2, 1)
        xj_cmd_302_msg += info_to_little_hex(gun_index, 2, 1)
        xj_cmd_302_msg += info_to_little_hex(equipment_id, 32, 0)
        xj_cmd_302_msg += info_to_little_hex(work_stat, 1, 1)
        xj_cmd_302_msg += info_to_little_hex(car_connect_stat, 1, 0)
        xj_cmd_302_msg += info_to_little_hex(brm_bms_connect_version, 3, 3)
        xj_cmd_302_msg += info_to_little_hex(brm_battery_type, 1, 1)
        xj_cmd_302_msg += info_to_little_hex(brm_battery_power, 4, 1)
        xj_cmd_302_msg += info_to_little_hex(brm_battery_voltage, 4, 1)
        xj_cmd_302_msg += info_to_little_hex(brm_battery_supplier, 4, 1)
        xj_cmd_302_msg += info_to_little_hex(brm_battery_seq, 4, 0)
        xj_cmd_302_msg += info_to_little_hex(brm_battery_produce_year, 2, 1)
        xj_cmd_302_msg += info_to_little_hex(brm_battery_produce_month, 1, 1)
        xj_cmd_302_msg += info_to_little_hex(brm_battery_produce_day, 1, 0)
        xj_cmd_302_msg += info_to_little_hex(brm_battery_charge_count, 4, 1)
        xj_cmd_302_msg += info_to_little_hex(brm_battery_property_identification, 1, 1)
        xj_cmd_302_msg += info_to_little_hex(serial_code, 1, 1)
        xj_cmd_302_msg += info_to_little_hex(brm_vin, 17, 0)
        xj_cmd_302_msg += info_to_little_hex(brm_BMS_version, 8, 0)
        xj_cmd_302_msg += info_to_little_hex(bcp_max_voltage, 4, 1)
        xj_cmd_302_msg += info_to_little_hex(bcp_max_current, 4, 1)
        xj_cmd_302_msg += info_to_little_hex(bcp_max_power, 4, 1)
        xj_cmd_302_msg += info_to_little_hex(bcp_total_voltage, 4, 1)
        xj_cmd_302_msg += info_to_little_hex(bcp_max_temperature, 1, 1)
        xj_cmd_302_msg += info_to_little_hex(bcp_battery_soc, 2, 1)
        xj_cmd_302_msg += info_to_little_hex(bcp_battery_soc_current_voltage, 4, 1)
        xj_cmd_302_msg += info_to_little_hex(bro_BMS_isReady, 1, 1)
        xj_cmd_302_msg += info_to_little_hex(bcl_voltage_need, 4, 1)
        xj_cmd_302_msg += info_to_little_hex(bcl_current_need, 4, 1)
        xj_cmd_302_msg += info_to_little_hex(bcl_charge_mode, 1, 1)
        xj_cmd_302_msg += info_to_little_hex(bcs_test_voltage, 4, 1)
        xj_cmd_302_msg += info_to_little_hex(bcs_test_current, 4, 1)
        xj_cmd_302_msg += info_to_little_hex(bcs_max_single_voltage, 4, 1)
        xj_cmd_302_msg += info_to_little_hex(bcs_max_single_no, 1, 1)
        xj_cmd_302_msg += info_to_little_hex(bcs_current_soc, 2, 1)
        xj_cmd_302_msg += info_to_little_hex(last_charge_time, 4, 1)
        xj_cmd_302_msg += info_to_little_hex(bsm_single_no, 1, 1)
        xj_cmd_302_msg += info_to_little_hex(bsm_max_temperature, 1, 1)
        xj_cmd_302_msg += info_to_little_hex(bsm_max_temperature_check_no, 1, 1)
        xj_cmd_302_msg += info_to_little_hex(bsm_min_temperature, 1, 1)
        xj_cmd_302_msg += info_to_little_hex(bsm_min_temperature_check_no, 1, 1)
        xj_cmd_302_msg += info_to_little_hex(bsm_voltage_too_high_or_too_low, 1, 1)
        xj_cmd_302_msg += info_to_little_hex(bsm_car_battery_soc_too_high_or_too_low, 1, 1)
        xj_cmd_302_msg += info_to_little_hex(bsm_car_battery_charge_over_current, 1, 1)
        xj_cmd_302_msg += info_to_little_hex(bsm_battery_temperature_too_high, 1, 1)
        xj_cmd_302_msg += info_to_little_hex(bsm_battery_insulation_state, 1, 1)
        xj_cmd_302_msg += info_to_little_hex(bsm_battery_connect_state, 1, 1)
        xj_cmd_302_msg += info_to_little_hex(bsm_allow_charge, 1, 1)
        xj_cmd_302_msg += info_to_little_hex(bst_BMS_soc_target, 1, 1)
        xj_cmd_302_msg += info_to_little_hex(bst_BMS_voltage_target, 1, 1)
        xj_cmd_302_msg += info_to_little_hex(bst_single_voltage_target, 1, 1)
        xj_cmd_302_msg += info_to_little_hex(bst_finish, 1, 1)
        xj_cmd_302_msg += info_to_little_hex(bst_isolation_error, 1, 1)
        xj_cmd_302_msg += info_to_little_hex(bst_connect_over_temperature, 1, 1)
        xj_cmd_302_msg += info_to_little_hex(bst_BMS_over_temperature, 1, 1)
        xj_cmd_302_msg += info_to_little_hex(bst_connect_error, 1, 1)
        xj_cmd_302_msg += info_to_little_hex(bst_battery_over_temperature, 1, 1)
        xj_cmd_302_msg += info_to_little_hex(bst_high_voltage_relay_error, 1, 1)
        xj_cmd_302_msg += info_to_little_hex(bst_point2_test_error, 1, 1)
        xj_cmd_302_msg += info_to_little_hex(bst_other_error, 1, 1)
        xj_cmd_302_msg += info_to_little_hex(bst_current_too_high, 1, 1)
        xj_cmd_302_msg += info_to_little_hex(bst_voltage_too_high, 1, 1)
        xj_cmd_302_msg += info_to_little_hex(bst_stop_soc, 2, 1)
        xj_cmd_302_msg += info_to_little_hex(bsd_battery_low_voltage, 4, 1)
        xj_cmd_302_msg += info_to_little_hex(bsd_battery_high_voltage, 4, 1)
        xj_cmd_302_msg += info_to_little_hex(bsd_battery_low_temperature, 1, 1)
        xj_cmd_302_msg += info_to_little_hex(bsd_battery_high_temperature, 1, 1)
        xj_cmd_302_msg += info_to_little_hex(error_68, 1, 1)
        xj_cmd_302_msg += info_to_little_hex(error_69, 1, 1)
        xj_cmd_302_msg += info_to_little_hex(error_70, 1, 1)
        xj_cmd_302_msg += info_to_little_hex(error_71, 1, 1)
        xj_cmd_302_msg += info_to_little_hex(error_72, 1, 1)
        xj_cmd_302_msg += info_to_little_hex(error_73, 1, 1)
        xj_cmd_302_msg += info_to_little_hex(error_74, 1, 1)
        xj_cmd_302_msg += info_to_little_hex(error_75, 1, 1)

        return xj_cmd_302_msg
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {d_data}")
        HSyslog.log_info(f"Service_mainres .{d_data} .{e} .{inspect.currentframe().f_lineno}")
        return []


def xj_cmd_303(p_data: list):  # 平台发送，设备接收
    try:
        info = {
            "serial_code": p_data[0:2],
            "gun_index": p_data[2:4],
            "equipment_id": p_data[4:36],
            "charge_user_id": p_data[36:68],
        }
        xj_resv_data.put(p_data)
        return info
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {p_data}")
        HSyslog.log_info(f"Service_mainres .{p_data} .{e} .{inspect.currentframe().f_lineno}")
        return {}


def xj_cmd_304(d_data: dict):  # 设备发送，平台接收
    serial_code = d_data.get("serial_code")
    gun_index = d_data.get("gun_index")
    equipment_id = d_data.get("equipment_id")
    charge_user_id = d_data.get("charge_user_id")
    work_stat = d_data.get("work_stat")
    brm_bms_connect_version = d_data.get("brm_bms_connect_version")
    brm_battery_type = d_data.get("brm_battery_type")
    brm_battery_power = d_data.get("brm_battery_power")
    brm_battery_voltage = d_data.get("brm_battery_voltage")
    brm_battery_supplier = d_data.get("brm_battery_supplier")
    brm_battery_seq = d_data.get("brm_battery_seq")
    brm_battery_produce_year = d_data.get("brm_battery_produce_year")
    brm_battery_produce_month = d_data.get("brm_battery_produce_month")
    brm_battery_produce_day = d_data.get("brm_battery_produce_day")
    brm_battery_charge_count = d_data.get("brm_battery_charge_count")
    brm_battery_property_identification = d_data.get("brm_battery_property_identification")
    brm_vin = d_data.get("brm_vin")
    brm_BMS_version = d_data.get("brm_BMS_version")
    bcp_max_voltage = d_data.get("bcp_max_voltage")
    bcp_max_current = d_data.get("bcp_max_current")
    bcp_max_power = d_data.get("bcp_max_power")
    bcp_total_voltage = d_data.get("bcp_total_voltage")
    bcp_max_temperature = d_data.get("bcp_max_temperature")
    bcp_battery_soc = d_data.get("bcp_battery_soc")
    bcp_battery_soc_current_voltage = d_data.get("bcp_battery_soc_current_voltage")
    bro_BMS_isReady = d_data.get("bro_BMS_isReady")
    CRO_isReady = d_data.get("CRO_isReady")

    try:
        xj_cmd_304_msg = []
        xj_cmd_304_msg += info_to_little_hex(gun_index, 2, 1)
        xj_cmd_304_msg += info_to_little_hex(equipment_id, 32, 0)
        xj_cmd_304_msg += info_to_little_hex(charge_user_id, 32, 0)
        xj_cmd_304_msg += info_to_little_hex(work_stat, 1, 1)
        xj_cmd_304_msg += info_to_little_hex(brm_bms_connect_version, 3, 3)
        xj_cmd_304_msg += info_to_little_hex(brm_battery_type, 1, 1)
        xj_cmd_304_msg += info_to_little_hex(brm_battery_power, 4, 1)
        xj_cmd_304_msg += info_to_little_hex(brm_battery_voltage, 4, 1)
        xj_cmd_304_msg += info_to_little_hex(brm_battery_supplier, 4, 1)
        xj_cmd_304_msg += info_to_little_hex(brm_battery_seq, 4, 0)
        xj_cmd_304_msg += info_to_little_hex(brm_battery_produce_year, 2, 1)
        xj_cmd_304_msg += info_to_little_hex(brm_battery_produce_month, 2, 1)
        xj_cmd_304_msg += info_to_little_hex(brm_battery_produce_day, 2, 1)
        xj_cmd_304_msg += info_to_little_hex(brm_battery_charge_count, 4, 1)
        xj_cmd_304_msg += info_to_little_hex(brm_battery_property_identification, 1, 1)
        xj_cmd_304_msg += info_to_little_hex(serial_code, 1, 1)
        xj_cmd_304_msg += info_to_little_hex(brm_vin, 17, 0)
        xj_cmd_304_msg += info_to_little_hex(brm_BMS_version, 8, 1)
        xj_cmd_304_msg += info_to_little_hex(bcp_max_voltage, 4, 1)
        xj_cmd_304_msg += info_to_little_hex(bcp_max_current, 4, 1)
        xj_cmd_304_msg += info_to_little_hex(bcp_max_power, 4, 1)
        xj_cmd_304_msg += info_to_little_hex(bcp_total_voltage, 4, 1)
        xj_cmd_304_msg += info_to_little_hex(bcp_max_temperature, 1, 1)
        xj_cmd_304_msg += info_to_little_hex(bcp_battery_soc, 2, 1)
        xj_cmd_304_msg += info_to_little_hex(bcp_battery_soc_current_voltage, 4, 1)
        xj_cmd_304_msg += info_to_little_hex(bro_BMS_isReady, 1, 1)
        xj_cmd_304_msg += info_to_little_hex(CRO_isReady, 1, 1)

        return xj_cmd_304_msg
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {d_data}")
        HSyslog.log_info(f"Service_mainres .{d_data} .{e} .{inspect.currentframe().f_lineno}")
        return []


def xj_cmd_305(p_data: list):  # 平台发送，设备接收
    try:
        info = {
            "serial_code": p_data[0:2],
            "gun_index": p_data[2:4],
            "equipment_id": p_data[4:36],
            "charge_user_id": p_data[36:68],
        }
        xj_resv_data.put(p_data)
        return info
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {p_data}")
        HSyslog.log_info(f"Service_mainres .{p_data} .{e} .{inspect.currentframe().f_lineno}")
        return {}


def xj_cmd_306(d_data: dict):  # 设备发送，平台接收
    serial_code = d_data.get("equipment_id")
    gun_index = d_data.get("gun_index")
    equipment_id = d_data.get("err_code")
    charge_user_id = d_data.get("err_status")
    work_stat = d_data.get("type")
    bcl_voltage_need = d_data.get("threshold")
    bcl_current_need = d_data.get("retain")
    bcl_charge_mode = d_data.get("err_status")
    bcs_test_voltage = d_data.get("equipment_id")
    bcs_test_current = d_data.get("gun_index")
    bcs_max_single_voltage = d_data.get("err_code")
    bcs_max_single_no = d_data.get("err_status")
    bcs_current_soc = d_data.get("type")
    last_charge_time = d_data.get("threshold")
    bsm_single_no = d_data.get("retain")
    bsm_max_temperature = d_data.get("err_status")
    bsm_max_temperature_check_no = d_data.get("equipment_id")
    bsm_min_temperature = d_data.get("gun_index")
    bsm_min_temperature_check_no = d_data.get("err_code")
    bsm_voltage_too_high_or_too_low = d_data.get("err_status")
    bsm_car_battery_soc_too_high_or_too_low = d_data.get("type")
    bsm_car_battery_charge_over_current = d_data.get("threshold")
    bsm_battery_temperature_too_high = d_data.get("err_status")
    bsm_battery_insulation_state = d_data.get("type")
    bsm_battery_connect_state = d_data.get("threshold")
    bsm_allow_charge = d_data.get("retain")

    try:
        xj_cmd_306_msg = []
        xj_cmd_306_msg += info_to_little_hex(gun_index, 2, 1)
        xj_cmd_306_msg += info_to_little_hex(equipment_id, 32, 0)
        xj_cmd_306_msg += info_to_little_hex(charge_user_id, 32, 0)
        xj_cmd_306_msg += info_to_little_hex(work_stat, 1, 1)
        xj_cmd_306_msg += info_to_little_hex(brm_bms_connect_version, 3, 3)
        xj_cmd_306_msg += info_to_little_hex(brm_battery_type, 1, 1)
        xj_cmd_306_msg += info_to_little_hex(brm_battery_power, 4, 1)
        xj_cmd_306_msg += info_to_little_hex(brm_battery_voltage, 4, 1)
        xj_cmd_306_msg += info_to_little_hex(brm_battery_supplier, 4, 1)
        xj_cmd_306_msg += info_to_little_hex(brm_battery_seq, 4, 0)
        xj_cmd_306_msg += info_to_little_hex(brm_battery_produce_year, 2, 1)
        xj_cmd_306_msg += info_to_little_hex(brm_battery_produce_month, 2, 1)
        xj_cmd_306_msg += info_to_little_hex(brm_battery_produce_day, 2, 1)
        xj_cmd_306_msg += info_to_little_hex(brm_battery_charge_count, 4, 1)
        xj_cmd_306_msg += info_to_little_hex(brm_battery_property_identification, 1, 1)
        xj_cmd_306_msg += info_to_little_hex(serial_code, 1, 1)
        xj_cmd_306_msg += info_to_little_hex(brm_vin, 17, 0)
        xj_cmd_306_msg += info_to_little_hex(brm_BMS_version, 8, 1)
        xj_cmd_306_msg += info_to_little_hex(bcp_max_voltage, 4, 1)
        xj_cmd_306_msg += info_to_little_hex(bcp_max_current, 4, 1)
        xj_cmd_306_msg += info_to_little_hex(bcp_max_power, 4, 1)
        xj_cmd_306_msg += info_to_little_hex(bcp_total_voltage, 4, 1)
        xj_cmd_306_msg += info_to_little_hex(bcp_max_temperature, 1, 1)
        xj_cmd_306_msg += info_to_little_hex(bcp_battery_soc, 2, 1)
        xj_cmd_306_msg += info_to_little_hex(bcp_battery_soc_current_voltage, 4, 1)
        xj_cmd_306_msg += info_to_little_hex(bro_BMS_isReady, 1, 1)
        xj_cmd_306_msg += info_to_little_hex(CRO_isReady, 1, 1)

        return xj_cmd_306_msg
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {d_data}")
        HSyslog.log_info(f"Service_mainres .{d_data} .{e} .{inspect.currentframe().f_lineno}")
        return []


def xj_cmd_307(p_data: list):  # 平台发送，设备接收
    try:
        info = {
            "serial_code": p_data[0:2],
            "gun_index": p_data[2:4],
            "equipment_id": p_data[4:36],
            "charge_user_id": p_data[36:68],
        }
        xj_resv_data.put(p_data)
        return info
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {p_data}")
        HSyslog.log_info(f"Service_mainres .{p_data} .{e} .{inspect.currentframe().f_lineno}")
        return {}


def xj_cmd_308(d_data: dict):  # 设备发送，平台接收
    serial_code = d_data.get("equipment_id")
    gun_index = d_data.get("gun_index")
    equipment_id = d_data.get("err_code")
    charge_user_id = d_data.get("err_status")
    work_stat = d_data.get("type")
    CST_stop_reason = d_data.get("threshold")
    CST_fault_reason = d_data.get("retain")
    CST_error_reason = d_data.get("err_status")


def xj_cmd_309(p_data: list):  # 平台发送，设备接收
    try:
        info = {
            "serial_code": p_data[0:2],
            "gun_index": p_data[2:4],
            "equipment_id": p_data[4:36],
            "charge_user_id": p_data[36:68],
        }
        xj_resv_data.put(p_data)
        return info
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {p_data}")
        HSyslog.log_info(f"Service_mainres .{p_data} .{e} .{inspect.currentframe().f_lineno}")
        return {}


def xj_cmd_310(d_data: dict):  # 设备发送，平台接收
    serial_code = d_data.get("equipment_id")
    gun_index = d_data.get("gun_index")
    equipment_id = d_data.get("err_code")
    charge_user_id = d_data.get("err_status")
    work_stat = d_data.get("type")
    BST_stop_reason = d_data.get("threshold")
    BST_fault_reason = d_data.get("retain")
    BST_error_reason = d_data.get("err_status")


def xj_cmd_311(p_data: list):  # 平台发送，设备接收
    try:
        info = {
            "serial_code": p_data[0:2],
            "gun_index": p_data[2:4],
            "equipment_id": p_data[4:36],
            "charge_user_id": p_data[36:68],
        }
        xj_resv_data.put(p_data)
        return info
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {p_data}")
        HSyslog.log_info(f"Service_mainres .{p_data} .{e} .{inspect.currentframe().f_lineno}")
        return {}


def xj_cmd_312(d_data: dict):  # 设备发送，平台接收
    serial_code = d_data.get("equipment_id")
    gun_index = d_data.get("gun_index")
    equipment_id = d_data.get("err_code")
    charge_user_id = d_data.get("err_status")
    work_stat = d_data.get("type")
    bsd_stop_soc = d_data.get("threshold")
    bsd_battery_low_voltage = d_data.get("retain")
    bsd_battery_high_voltage = d_data.get("err_status")
    bsd_battery_low_temperature = d_data.get("equipment_id")
    bsd_battery_high_temperature = d_data.get("gun_index")
    error_68 = d_data.get("err_code")
    error_69 = d_data.get("err_status")
    error_70 = d_data.get("type")
    error_71 = d_data.get("threshold")
    error_72 = d_data.get("retain")
    error_73 = d_data.get("err_status")
    error_74 = d_data.get("retain")
    error_75 = d_data.get("err_status")


def xj_cmd_201(p_data: list):  # 平台发送，设备接收
    try:
        info = {
            "gun_index": p_data[0:4],
            "user_id": p_data[4],
            "serial_code": p_data[5:37],
        }
        xj_resv_data.put(p_data)
        return info
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {p_data}")
        HSyslog.log_info(f"Service_mainres .{p_data} .{e} .{inspect.currentframe().f_lineno}")
        return {}


def xj_cmd_202(d_data: dict):  # 设备发送，平台接收
    equipment_id = d_data.get("equipment_id")
    gun_type = d_data.get("gun_index")
    gun_index = d_data.get("err_code")
    charge_user_id = d_data.get("err_status")
    charge_start_time = d_data.get("type")
    charge_end_time = d_data.get("threshold")
    charge_time = d_data.get("retain")
    start_soc = d_data.get("err_status")
    end_soc = d_data.get("equipment_id")
    err_no = d_data.get("gun_index")
    charge_kwh_amount = d_data.get("err_code")
    start_charge_kwh_meter = d_data.get("err_status")
    end_charge_kwh_meter = d_data.get("type")
    total_charge_fee = d_data.get("threshold")
    is_not_stoped_by_card = d_data.get("retain")
    start_card_money = d_data.get("err_status")
    end_card_money = d_data.get("retain")
    total_service_fee = d_data.get("err_status")
    is_paid_by_offline = d_data.get("equipment_id")
    charge_policy = d_data.get("gun_index")
    charge_policy_param = d_data.get("err_code")
    car_vin = d_data.get("err_status")
    car_plate_no = d_data.get("type")
    kwh_amount_1 = d_data.get("threshold")
    kwh_amount_2 = d_data.get("retain")
    kwh_amount_3 = d_data.get("err_status")
    kwh_amount_4 = d_data.get("equipment_id")
    kwh_amount_5 = d_data.get("gun_index")
    kwh_amount_6 = d_data.get("err_code")
    kwh_amount_7 = d_data.get("err_status")
    kwh_amount_8 = d_data.get("type")
    kwh_amount_9 = d_data.get("threshold")
    kwh_amount_10 = d_data.get("retain")
    kwh_amount_11 = d_data.get("err_status")
    kwh_amount_12 = d_data.get("retain")
    kwh_amount_13 = d_data.get("err_status")
    kwh_amount_14 = d_data.get("equipment_id")
    kwh_amount_15 = d_data.get("gun_index")
    kwh_amount_16 = d_data.get("err_code")
    kwh_amount_17 = d_data.get("err_status")
    kwh_amount_18 = d_data.get("type")
    kwh_amount_19 = d_data.get("threshold")
    kwh_amount_20 = d_data.get("retain")
    kwh_amount_21 = d_data.get("err_status")
    kwh_amount_22 = d_data.get("equipment_id")
    kwh_amount_23 = d_data.get("gun_index")
    kwh_amount_24 = d_data.get("err_code")
    kwh_amount_25 = d_data.get("err_status")
    kwh_amount_26 = d_data.get("type")
    kwh_amount_27 = d_data.get("threshold")
    kwh_amount_28 = d_data.get("retain")
    kwh_amount_29 = d_data.get("err_status")
    kwh_amount_30 = d_data.get("retain")
    kwh_amount_31 = d_data.get("err_status")
    kwh_amount_32 = d_data.get("err_code")
    kwh_amount_33 = d_data.get("err_status")
    kwh_amount_34 = d_data.get("type")
    kwh_amount_35 = d_data.get("threshold")
    kwh_amount_36 = d_data.get("retain")
    kwh_amount_37 = d_data.get("err_status")
    kwh_amount_38 = d_data.get("equipment_id")
    kwh_amount_39 = d_data.get("gun_index")
    kwh_amount_40 = d_data.get("err_code")
    kwh_amount_41 = d_data.get("err_status")
    kwh_amount_42 = d_data.get("type")
    kwh_amount_43 = d_data.get("threshold")
    kwh_amount_44 = d_data.get("retain")
    kwh_amount_45 = d_data.get("err_status")
    kwh_amount_46 = d_data.get("retain")
    kwh_amount_47 = d_data.get("err_status")
    kwh_amount_48 = d_data.get("err_status")
    start_charge_type = d_data.get("retain")
    serial_code = d_data.get("err_status")


def xj_cmd_205(p_data: list):  # 平台发送，设备接收
    try:
        info = {
            "gun_index": p_data[4],
            "user_id": p_data[5:37],
            "serial_code": p_data[0:4],
        }
        xj_resv_data.put(p_data)
        return info
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {p_data}")
        HSyslog.log_info(f"Service_mainres .{p_data} .{e} .{inspect.currentframe().f_lineno}")
        return {}


def xj_cmd_206(d_data: dict):  # 设备发送，平台接收
    equipment_id = d_data.get("equipment_id")
    gun_type = d_data.get("gun_index")
    gun_index = d_data.get("err_code")
    charge_user_id = d_data.get("err_status")
    charge_start_time = d_data.get("type")
    charge_end_time = d_data.get("threshold")
    charge_time = d_data.get("retain")
    start_soc = d_data.get("err_status")
    end_soc = d_data.get("equipment_id")
    err_no = d_data.get("gun_index")
    charge_kwh_amount = d_data.get("err_code")
    start_charge_kwh_meter = d_data.get("err_status")
    end_charge_kwh_meter = d_data.get("type")
    total_charge_fee = d_data.get("threshold")
    is_not_stoped_by_card = d_data.get("retain")
    start_card_money = d_data.get("err_status")
    end_card_money = d_data.get("retain")
    total_service_fee = d_data.get("err_status")
    is_paid_by_offline = d_data.get("equipment_id")
    charge_policy = d_data.get("gun_index")
    charge_policy_param = d_data.get("err_code")
    car_vin = d_data.get("err_status")
    car_plate_no = d_data.get("type")
    kwh_amount_1 = d_data.get("threshold")
    kwh_amount_2 = d_data.get("retain")
    kwh_amount_3 = d_data.get("err_status")
    kwh_amount_4 = d_data.get("equipment_id")
    kwh_amount_5 = d_data.get("gun_index")
    kwh_amount_6 = d_data.get("err_code")
    kwh_amount_7 = d_data.get("err_status")
    kwh_amount_8 = d_data.get("type")
    kwh_amount_9 = d_data.get("threshold")
    kwh_amount_10 = d_data.get("retain")
    kwh_amount_11 = d_data.get("err_status")
    kwh_amount_12 = d_data.get("retain")
    kwh_amount_13 = d_data.get("err_status")
    kwh_amount_14 = d_data.get("equipment_id")
    kwh_amount_15 = d_data.get("gun_index")
    kwh_amount_16 = d_data.get("err_code")
    kwh_amount_17 = d_data.get("err_status")
    kwh_amount_18 = d_data.get("type")
    kwh_amount_19 = d_data.get("threshold")
    kwh_amount_20 = d_data.get("retain")
    kwh_amount_21 = d_data.get("err_status")
    kwh_amount_22 = d_data.get("equipment_id")
    kwh_amount_23 = d_data.get("gun_index")
    kwh_amount_24 = d_data.get("err_code")
    kwh_amount_25 = d_data.get("err_status")
    kwh_amount_26 = d_data.get("type")
    kwh_amount_27 = d_data.get("threshold")
    kwh_amount_28 = d_data.get("retain")
    kwh_amount_29 = d_data.get("err_status")
    kwh_amount_30 = d_data.get("retain")
    kwh_amount_31 = d_data.get("err_status")
    kwh_amount_32 = d_data.get("err_code")
    kwh_amount_33 = d_data.get("err_status")
    kwh_amount_34 = d_data.get("type")
    kwh_amount_35 = d_data.get("threshold")
    kwh_amount_36 = d_data.get("retain")
    kwh_amount_37 = d_data.get("err_status")
    kwh_amount_38 = d_data.get("equipment_id")
    kwh_amount_39 = d_data.get("gun_index")
    kwh_amount_40 = d_data.get("err_code")
    kwh_amount_41 = d_data.get("err_status")
    kwh_amount_42 = d_data.get("type")
    kwh_amount_43 = d_data.get("threshold")
    kwh_amount_44 = d_data.get("retain")
    kwh_amount_45 = d_data.get("err_status")
    kwh_amount_46 = d_data.get("retain")
    kwh_amount_47 = d_data.get("err_status")
    kwh_amount_48 = d_data.get("err_status")
    start_charge_type = d_data.get("retain")
    serial_code = d_data.get("err_status")


def xj_cmd_409(p_data: list):  # 平台发送，设备接收
    try:
        info = {
            "equipment_id": p_data[4:36],
            "log_name": p_data[36:],
            "serial_code": p_data[0:4],
        }
        xj_resv_data.put(p_data)
        return info
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {p_data}")
        HSyslog.log_info(f"Service_mainres .{p_data} .{e} .{inspect.currentframe().f_lineno}")
        return {}


def xj_cmd_410(d_data: dict):  # 设备发送，平台接收
    equipment_id = d_data.get("equipment_id")
    log_name = d_data.get("gun_index")
    serial_code = d_data.get("err_code")


def xj_cmd_501(p_data: list):  # 平台发送，设备接收
    try:
        info = {
            "serial_code": p_data[0:4],
            "cmd_len": p_data[4:6],
            "data": p_data[6:],
        }
        xj_resv_data.put(p_data)
        return info
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {p_data}")
        HSyslog.log_info(f"Service_mainres .{p_data} .{e} .{inspect.currentframe().f_lineno}")
        return {}


def xj_cmd_502(d_data: dict):  # 设备发送，平台接收
    serial_code = d_data.get("equipment_id")
    success_number = d_data.get("gun_index")
    equipment_id = d_data.get("err_code")
    set_result = d_data.get("err_code")


def xj_cmd_503(p_data: list):  # 平台发送，设备接收
    try:
        info = {
            "serial_code": p_data[0],
            "equipment_id": p_data[0:32],
            "data_len": p_data[0],
            "data": p_data[0],
        }
        xj_resv_data.put(p_data)
        return info
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {p_data}")
        HSyslog.log_info(f"Service_mainres .{p_data} .{e} .{inspect.currentframe().f_lineno}")
        return {}


def xj_cmd_504(d_data: dict):  # 设备发送，平台接收
    serial_code = d_data.get("equipment_id")
    equipment_id = d_data.get("gun_index")
    set_result = d_data.get("err_code")


def xj_cmd_509(p_data: list):  # 平台发送，设备接收
    try:
        info = {
            "equipment_id": p_data[4:36],
            "gun_index": p_data[2:4],
            "log_name": p_data[36:],
            "serial_code": p_data[0:2],
        }
        xj_resv_data.put(p_data)
        return info
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {p_data}")
        HSyslog.log_info(f"Service_mainres .{p_data} .{e} .{inspect.currentframe().f_lineno}")
        return {}


def xj_cmd_510(d_data: dict):  # 设备发送，平台接收
    equipment_id = d_data.get("equipment_id")
    log_name = d_data.get("gun_index")
    serial_code = d_data.get("err_code")


def xj_cmd_801(p_data: list):  # 平台发送，设备接收
    try:
        info = {
            "key_len": p_data[0:4],
            "key_datas": p_data[4:4 + p_data[0:4]],
            "equipment_id": p_data[4 + p_data[0:4]:4 + p_data[0:4] + 32],
            "encrypted_type": p_data[4 + p_data[0:4] + 32: 4 + p_data[0:4] + 32 + 2],
            "encrypted_version": p_data[4 + p_data[0:4] + 32 + 2:],
            "serial_code": p_data[0],
        }
        xj_resv_data.put(p_data)
        return info
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {p_data}")
        HSyslog.log_info(f"Service_mainres .{p_data} .{e} .{inspect.currentframe().f_lineno}")
        return {}


def xj_cmd_802(d_data: dict):  # 设备发送，平台接收
    key_len = d_data.get("equipment_id")
    key_datas = d_data.get("gun_index")
    equipment_id = d_data.get("err_code")
    encrypted_type = d_data.get("equipment_id")
    encrypted_version = d_data.get("gun_index")
    serial_code = d_data.get("err_code")


def xj_cmd_1101(p_data: list):  # 平台发送，设备接收
    try:
        info = {
            "soft_type": p_data[0],
            "soft_param": p_data[1],
            "download_url": p_data[2:130],
            "md5": p_data[130:],
            "serial_code": p_data[4],
        }
        xj_resv_data.put(p_data)
        return info
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {p_data}")
        HSyslog.log_info(f"Service_mainres .{p_data} .{e} .{inspect.currentframe().f_lineno}")
        return {}


def xj_cmd_1102(d_data: dict):  # 设备发送，平台接收
    update_result = d_data.get("equipment_id")
    md5 = d_data.get("gun_index")
    serial_code = d_data.get("err_code")
    encrypted_type = d_data.get("equipment_id")
    encrypted_version = d_data.get("gun_index")
    serial_code = d_data.get("err_code")


def xj_cmd_1303(p_data: list):  # 平台发送，设备接收
    try:
        info = {
            "cmd_type": p_data[0],
            "fee_data": p_data[4],
            "serial_code": p_data[0],
        }
        xj_resv_data.put(p_data)
        return info
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {p_data}")
        HSyslog.log_info(f"Service_mainres .{p_data} .{e} .{inspect.currentframe().f_lineno}")
        return {}


def xj_cmd_1304(d_data: dict):  # 设备发送，平台接收
    fee_data = d_data.get("equipment_id")
    serial_code = d_data.get("gun_index")


def xj_cmd_1305(p_data: list):  # 平台发送，设备接收
    try:
        info = {
            "cmd_type": p_data[0],
            "gun_index": p_data[1],
            "fee_data": p_data[2:6],
            "serial_code": p_data[6],
        }
        xj_resv_data.put(p_data)
        return info
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {p_data}")
        HSyslog.log_info(f"Service_mainres .{p_data} .{e} .{inspect.currentframe().f_lineno}")
        return {}


def xj_cmd_1306(d_data: dict):  # 设备发送，平台接收
    cmd_type = d_data.get("equipment_id")
    gun_index = d_data.get("gun_index")
    fee_data = d_data.get("equipment_id")
    serial_code = d_data.get("gun_index")


def xj_cmd_1309(p_data: list):  # 平台发送，设备接收
    try:
        info = {
            "serial_code": p_data[0],
            "data_len": p_data[4],
            "class_num": p_data[0],
            "data": p_data[0],
        }
        xj_resv_data.put(p_data)
        return info
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {p_data}")
        HSyslog.log_info(f"Service_mainres .{p_data} .{e} .{inspect.currentframe().f_lineno}")
        return {}


def xj_cmd_1310(d_data: dict):  # 设备发送，平台接收
    serial_code = d_data.get("equipment_id")
    set_result = d_data.get("gun_index")


xj_mqtt_cmd_type = {
    xj_mqtt_cmd_enum.xj_cmd_type_1.value: {"func": xj_cmd_1, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_2.value: {"func": xj_cmd_2, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_3.value: {"func": xj_cmd_3, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_4.value: {"func": xj_cmd_4, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_5.value: {"func": xj_cmd_5, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_6.value: {"func": xj_cmd_6, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_7.value: {"func": xj_cmd_7, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_8.value: {"func": xj_cmd_8, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_11.value: {"func": xj_cmd_11, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_12.value: {"func": xj_cmd_12, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_23.value: {"func": xj_cmd_23, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_24.value: {"func": xj_cmd_24, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_33.value: {"func": xj_cmd_33, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_34.value: {"func": xj_cmd_34, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_35.value: {"func": xj_cmd_35, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_36.value: {"func": xj_cmd_36, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_40.value: {"func": xj_cmd_40, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_41.value: {"func": xj_cmd_41, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_101.value: {"func": xj_cmd_101, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_102.value: {"func": xj_cmd_102, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_103.value: {"func": xj_cmd_103, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_104.value: {"func": xj_cmd_104, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_105.value: {"func": xj_cmd_105, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_106.value: {"func": xj_cmd_106, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_107.value: {"func": xj_cmd_107, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_108.value: {"func": xj_cmd_108, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_113.value: {"func": xj_cmd_113, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_114.value: {"func": xj_cmd_114, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_117.value: {"func": xj_cmd_117, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_118.value: {"func": xj_cmd_118, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_119.value: {"func": xj_cmd_119, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_120.value: {"func": xj_cmd_120, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_201.value: {"func": xj_cmd_201, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_202.value: {"func": xj_cmd_202, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_205.value: {"func": xj_cmd_205, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_206.value: {"func": xj_cmd_206, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_301.value: {"func": xj_cmd_301, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_302.value: {"func": xj_cmd_302, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_303.value: {"func": xj_cmd_303, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_304.value: {"func": xj_cmd_304, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_305.value: {"func": xj_cmd_305, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_306.value: {"func": xj_cmd_306, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_307.value: {"func": xj_cmd_307, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_308.value: {"func": xj_cmd_308, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_309.value: {"func": xj_cmd_309, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_310.value: {"func": xj_cmd_310, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_311.value: {"func": xj_cmd_311, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_312.value: {"func": xj_cmd_312, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_409.value: {"func": xj_cmd_409, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_410.value: {"func": xj_cmd_410, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_501.value: {"func": xj_cmd_501, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_502.value: {"func": xj_cmd_502, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_503.value: {"func": xj_cmd_503, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_504.value: {"func": xj_cmd_504, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_509.value: {"func": xj_cmd_509, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_510.value: {"func": xj_cmd_510, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_801.value: {"func": xj_cmd_801, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_802.value: {"func": xj_cmd_802, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_1101.value: {"func": xj_cmd_1101, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_1102.value: {"func": xj_cmd_1102, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_1303.value: {"func": xj_cmd_1303, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_1304.value: {"func": xj_cmd_1304, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_1305.value: {"func": xj_cmd_1305, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_1306.value: {"func": xj_cmd_1306, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_1309.value: {"func": xj_cmd_1309, "qos": 1},
    xj_mqtt_cmd_enum.xj_cmd_type_1310.value: {"func": xj_cmd_1310, "qos": 1},
}

# def st_108_cmd
#
# 	 gun_cnt
# 	xj_event_type type
# 	 event_param

"""
/* #################################################### 数据信息 #######################################################*/
"""
User_Name = None
Enterprise_Code = None
SDK_Version = None

serial_code = 0x00000000

data_path = "/opt/hhd/Platform.db"
syslog_path = '/var/log'  # 替换为实际路径

red_char = "\033[91m"
green_char = "\033[92m"
init_char = "\033[0m"

xj_send_data = queue.Queue()
xj_resv_data = queue.Queue()

ack_data = {
    "serial_code": None,
    "cmd_code": None,
    "send_data": None,
    "send_num": None
}

cleck_code_1 = {
    1: [4, 1],
    2: [4, 1],
    3: [4, 1],
    4: [4, 1],
    5: [4, 1],
    6: [4, 1],
    7: [4, 1],
    8: [4, 1],
    9: [4, 1],
    10: [4, 1],
    11: [4, 0],
    12: [4, 1],
    13: [4, 0],
    14: [4, 1],
    15: [4, 1],
    16: [4, 1],
    17: [4, 1],
    18: [4, 1],
    19: [4, 1],
    20: [4, 1],
    21: [4, 1],
    22: [4, 1],
    23: [4, 1],
    24: [4, 1],
    25: [4, 1],
    26: [4, 1],
    27: [4, 1],
    28: [4, 1],
    29: [4, 1],
    30: [4, 1],
    31: [4, 1],
    32: [4, 1],
    33: [4, 1],
    34: [4, 0],
    35: [4, 0],
    36: [4, 1],
    37: [4, 1],
    38: [4, 1],
    39: [4, 1],
    40: [4, 1],
    41: [4, 1],
    42: [4, 1],
    43: [4, 1],
    44: [4, 1],
    45: [4, 1],
    46: [4, 1],
    47: [4, 1],
    48: [4, 1],
    49: [4, 1],
    50: [4, 1],
    51: [4, 1],
}

cleck_code_3 = {
    1: [32, 0],
    2: [8, 2],
    3: [8, 0],
    4: [8, 0],
    5: [6, 0],
    6: [16, 1],
    7: [1, 0],
    8: [128, 0],
    9: [128, 0],
    10: [16, 0],
    11: [16, 0],
    12: [256, 0],
    13: [128, 0],
    14: [4, 0],
    15: [156, 0],
    16: [128, 0],
    17: [128, 0],
    18: [128, 0],
    19: [128, 0],
}

cleck_code_501 = {
    1: [128, 0],
    2: [128, 0],
    3: [128, 0],
    4: [128, 0],
    5: [128, 0],
    6: [128, 0],
    7: [128, 0],
    8: [128, 0],
    9: [128, 0],
    10: [128, 0],
    11: [128, 0],
    12: [128, 0],
    13: [128, 0],
    14: [128, 0],
    15: [128, 0],
    16: [128, 0],
    17: [128, 0],
    18: [128, 0],
    19: [128, 0],
    20: [128, 0],
    21: [128, 0],
    22: [128, 0],
    23: [128, 0],
    24: [128, 0],
    25: [128, 0],
    26: [128, 0],
    27: [128, 0],
    28: [128, 0],
    29: [128, 0],
    30: [128, 0],
    31: [128, 0],
    32: [128, 0],
    33: [128, 0],
    34: [128, 0],
    35: [128, 0],
}

cleck_code_5 = {
    1: [128, 0],
    2: [128, 0],
    3: [128, 0],
    4: [128, 0],
    5: [128, 0],
    6: [128, 0],
    7: [128, 0],
    8: [128, 0],
    9: [128, 0],
    10: [128, 0],
    11: [128, 0],
    12: [128, 0],
    13: [128, 0],
    14: [128, 0],
    15: [128, 0],
    16: [128, 0],
    17: [128, 0],
    18: [128, 0],
    19: [128, 0],
    20: [128, 0],
}

cleck_code_120 = {
    0x7001: [4, 0],
    0x7002: [4, 0.1],
    0x7003: [4, 0],
    0x7004: [4, 0],
    0x7005: [4, 0.1],
    0x7006: [4, 0],
    0x7007: [4, 0.1],
    0x7008: [4, 0.01],
    0x7009: [4, 0],
    0x700A: [4, 0],
    0x700B: [4, 0],
    0x700C: [4, 0],
    0x700D: [4, 0.1],
    0x700E: [4, 0],
    0x700F: [4, 0],
    0x7010: [4, 0.1],
    0x7011: [4, 0.1],
    0x7012: [4, 0.1],
    0x7013: [4, 0.1],
    0x7014: [4, 0.1],
    0x7015: [4, 0],
    0x7016: [4, 0],
    0x7017: [4, 0],
    0x7018: [4, 0],
    0x7019: [4, 0],
    0x701A: [4, 0],
    0x701B: [4, 0],
    0x701C: [4, 0],
    0x701D: [4, 0],
    0x701E: [4, 0],
    0x701F: [4, 0],
    0x7020: [4, 0],
    0x7021: [4, 0],
    0x7022: [4, 0],
    0x7023: [4, 0],
    0x7024: [4, 0],
    0x7025: [4, 0],
    0x7026: [4, 0.1],
}

"""
/* #################################################### 数据信息 #######################################################*/
"""

"""
/* ##################################################### 组码 #########################################################*/
"""


class Protocol_Decode:
    def __init__(self, msg: list, cmd: int):
        self.header_code = None
        self.length_code = None
        self.version_code = None
        self.serial_code = None
        self.cmd_code = cmd
        self.check_code = None
        self.datas = msg
        self.qos = None

    def Pprint(self):
        print(self.header_code)
        print(self.length_code)
        print(self.version_code)
        print(self.serial_code)
        print(self.cmd_code)
        print(self.check_code)
        print(self.datas)

    def get_header_code(self):
        if Enterprise_Code is not None:
            self.header_code = Enterprise_Code
            return True
        else:
            return False

    def get_version_code(self):
        if SDK_Version is not None:
            self.version_code = SDK_Version
            return True
        else:
            return False

    def get_serial_code(self):
        self.serial_code = serial_code
        return True

    def get_length_code(self):
        self.length_code = 2 + 2 + 4 + 4 + 2 + 1 + len(self.datas)

    def get_check_code(self):
        self.check_code = (sum(self.datas) + self.cmd_code) % 127

    def build_msg(self):
        if self.header_code is None:
            self.get_header_code()
        if self.length_code is None:
            self.get_length_code()
        if self.version_code is None:
            self.get_version_code()
        if self.serial_code is None:
            self.get_serial_code()
        if self.check_code is None:
            self.get_check_code()

        msg = []
        msg += info_to_little_hex(self.header_code, 2, 1)
        msg += info_to_little_hex(self.length_code, 2, 1)
        msg += info_to_little_hex(self.version_code, 4, 1)
        msg += info_to_little_hex(self.serial_code, 4, 1)
        msg += info_to_little_hex(self.cmd_code, 4, 1)
        msg += self.datas
        msg += info_to_little_hex(self.check_code, 1, 1)
        return msg


# 字符串转换为小端序的16进制码
def string_to_little_endian_ascii(s, fixed_length):
    ascii_list = [ord(char) for char in s]  # 将字符串转为ASCII码列表
    if len(ascii_list) < fixed_length:
        ascii_list.extend([0] * (fixed_length - len(ascii_list)))  # 不足长度补零
    return ascii_list


# 数字转换为小端序的16进制码
def number_to_little_endian_hex(num, byte_length):
    hex_str = format(num, 'x')  # 将数字转换为16进制字符串
    hex_str = hex_str.zfill(byte_length * 2)
    hex_list = [int(hex_str[i:i + 2], 16) for i in range(0, len(hex_str), 2)]  # 每两个字符转为一个整数
    if len(hex_list) < byte_length:
        hex_list.extend([0] * (byte_length - len(hex_list)))
    hex_list.reverse()
    return hex_list


def time_to_little_endian_bcd(input_time):
    try:
        datetime_obj = datetime.strptime(input_time, "%Y-%m-%d-%H:%M:%S")
        return [
            datetime_obj.year // 1000 % 10 << 4 | datetime_obj.year // 100 % 10,
            datetime_obj.year % 100 // 10 << 4 | datetime_obj.year % 100 % 10,
            datetime_obj.month // 10 << 4 | datetime_obj.month % 10,
            datetime_obj.day // 10 << 4 | datetime_obj.day % 10,
            datetime_obj.hour // 10 << 4 | datetime_obj.hour % 10,
            datetime_obj.minute // 10 << 4 | datetime_obj.minute % 10,
            datetime_obj.second // 10 << 4 | datetime_obj.second % 10,
            0xff
        ]
    except ValueError:
        try:
            timestamp = int(input_time)
            datetime_obj = datetime.fromtimestamp(timestamp)
            return [
                datetime_obj.year // 1000 % 10 << 4 | datetime_obj.year // 100 % 10,
                datetime_obj.year % 100 // 10 << 4 | datetime_obj.year % 100 % 10,
                datetime_obj.month // 10 << 4 | datetime_obj.month % 10,
                datetime_obj.day // 10 << 4 | datetime_obj.day % 10,
                datetime_obj.hour // 10 << 4 | datetime_obj.hour % 10,
                datetime_obj.minute // 10 << 4 | datetime_obj.minute % 10,
                datetime_obj.second // 10 << 4 | datetime_obj.second % 10,
                0xff
            ]
        except ValueError:
            print("输入格式不正确，无法转换。请提供标准时间格式或时间戳。")
            return None


def version_to_little_endian_hex(ver, ver_len):
    version_string = ver[1:]
    # 将版本号按照点号分割
    parts = version_string.split('.')

    if len(parts) != 3:
        raise ValueError("Version string must have exactly three parts (major.minor.patch)")

    major = int(parts[0])
    minor = int(parts[1])
    patch = int(parts[2])

    # Build the version array with integers
    version_array = [
        (major >> 8) & 0xFF,  # High byte of major version
        major & 0xFF,  # Low byte of major version
        minor,  # Minor version
        patch  # Patch version
    ]

    return version_array


def info_to_little_hex(info, info_len, info_type):
    result = None
    try:
        if info_type == 0:
            result = string_to_little_endian_ascii(info, info_len)
        if info_type == 1:
            result = number_to_little_endian_hex(info, info_len)
        if info_type == 2:
            result = time_to_little_endian_bcd(info)
        if info_type == 3:
            result = version_to_little_endian_hex(info, info_len)

        if result is None:
            return [0x00] * info_len
        else:
            if len(result) != info_len:
                return [0x00] * info_len
            else:
                return result
    except Exception as e:
        print(f"\033[91m{e} .{inspect.currentframe().f_lineno}\033[0m")
        print(f"input_data: {info}")
        HSyslog.log_info(f"Service_mainres .{info} .{e} .{inspect.currentframe().f_lineno}")
        return None


"""
/* ##################################################### 组码 #########################################################*/
"""

"""
/* ##################################################### 解码 #########################################################*/
"""


class Protocol_Encode:
    def __init__(self, msg: bytes):
        self.header_code = msg[0:2]
        self.length_code = msg[2:4]
        self.version_code = msg[4:8]
        self.serial_code = msg[8:12]
        self.cmd_code = msg[12:14]
        self.check_code = msg[-1:]
        self.datas = msg[14:-1]
        self.callback_func = None
        self.qos = None

    def Pprint(self):
        print(self.header_code.hex())
        print(self.length_code.hex())
        print(self.version_code.hex())
        print(self.serial_code.hex())
        print(self.cmd_code.hex())
        print(self.check_code.hex())
        print(self.datas)

    def cleck_header_code(self):
        if self.header_code == Enterprise_Code:
            return True
        else:
            return False

    def cleck_version_code(self):
        if self.version_code == SDK_Version:
            return True
        else:
            return False

    def cleck_cmd(self):
        decimal_number = int.from_bytes(self.cmd_code, byteorder='little')
        return decimal_number

    def cleck_serial_code(self):
        decimal_number = int.from_bytes(self.serial_code, byteorder='little')
        return decimal_number

    def cleck_func(self):
        for cmd, func in xj_mqtt_cmd_type.items():
            if cmd == self.cleck_cmd():
                self.callback_func = func["func"]
                self.qos = func["qos"]

    def protocol_message(self):
        if self.callback_func is None:
            return False
        result = self.callback_func(self.datas)
        if result == {}:
            return False
        else:
            return True


# 16进制码转换为小端序的字符串
def ascii_list_to_str(ascii_list):
    # 使用列表推导式将ASCII码列表中的每个整数转换为对应的字符，并拼接为字符串
    # 遇到ASCII码值为0的元素则停止拼接
    return ''.join(chr(char) for char in ascii_list if char != 0)


# 16进制码转换为小端序的字符串
def hex_list_to_int(hex_list):
    # 使用列表推导式将ASCII码列表中的每个整数转换为对应的字符，并拼接为字符串
    # 遇到ASCII码值为0的元素则停止拼接
    return int.from_bytes(hex_list, byteorder='little')


def bcd_list_to_str(bcd_list):
    # 将每个BCD码转换为对应的十进制数
    year_h = ((bcd_list[0] >> 4) & 0x0F) * 10 + (bcd_list[0] & 0x0F)
    year_l = ((bcd_list[1] >> 4) & 0x0F) * 10 + (bcd_list[1] & 0x0F)
    month = ((bcd_list[2] >> 4) & 0x0F) * 10 + (bcd_list[2] & 0x0F)
    day = ((bcd_list[3] >> 4) & 0x0F) * 10 + (bcd_list[3] & 0x0F)
    hour = ((bcd_list[4] >> 4) & 0x0F) * 10 + (bcd_list[4] & 0x0F)
    minute = ((bcd_list[5] >> 4) & 0x0F) * 10 + (bcd_list[5] & 0x0F)
    second = ((bcd_list[6] >> 4) & 0x0F) * 10 + (bcd_list[6] & 0x0F)

    # 返回时间元组或字符串
    return f"{year_h}{year_l}-{month:02}-{day:02}-{hour:02}:{minute:02}:{second:02}"


def version_list_to_str(version):
    if len(version) != 4:
        raise ValueError("Version array must have exactly 4 elements")

        # Convert each element from hexadecimal string to integer
    major = int(version[0] + version[1])
    minor = int(version[2])
    patch = int(version[3])

    version_string = f"A"
    # Construct the version string
    version_string += f"{major}.{minor}.{patch}"

    return version_string


def hex_to_little_info(hex_list, hex_type):
    if hex_type == 0:
        return ascii_list_to_str(hex_list)
    if hex_type == 1:
        return hex_list_to_int(hex_list)
    if hex_type == 2:
        return bcd_list_to_str(hex_list)
    if hex_type == 3:
        return version_list_to_str(hex_list)


"""
/* ##################################################### 解码 #########################################################*/
"""

"""
/* ##################################################### 数据库 ########################################################*/
"""


def datadb_init():
    conn = sqlite3.connect(data_path)
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS VerInfoEvt (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id INTEGER,
            device_type INTEGER,
            hard_version TEXT,
            soft_version TEXT,
            ota_version TEXT
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS DeviceInfo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_id TEXT,
            data_type INTEGER,
            data_str TEXT,
            data_int INTEGER
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS FeeModel (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            SegFlag INTEGER,
            TimeNum INTEGER,
            TimeSeg TEXT,
            chargeFee INTEGER,
            serviceFee INTEGER
        )
    ''')
    cur.execute('''
            CREATE TABLE IF NOT EXISTS dcOutMeterIty (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gunNo INTEGER,
                acqTime TEXT,
                mailAddr TEXT,
                meterNo TEXT,
                assetId TEXT,
                sumMeter INTEGER,
                elec INTEGER,
                lastTrade TEXT
            )
        ''')
    cur.execute('''
            CREATE TABLE IF NOT EXISTS BmsCST (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gun_index INTEGER,
                equipment_id TEXT,
                charge_user_id TEXT,
                work_stat INTEGER,
                CST_stop_reason INTEGER,
                CST_fault_reason INTEGER,
                CST_error_reason INTEGER,
            )
        ''')
    cur.execute('''
            CREATE TABLE IF NOT EXISTS BmsBST (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gun_index INTEGER,
                equipment_id TEXT,
                charge_user_id TEXT,
                work_stat INTEGER,
                BST_stop_reason INTEGER,
                BST_fault_reason INTEGER,
                BST_error_reason INTEGER,
            )
        ''')
    cur.execute('''
            CREATE TABLE IF NOT EXISTS BmsBST (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gun_index INTEGER,
                equipment_id TEXT,
                charge_user_id TEXT,
                work_stat INTEGER,
                bsd_stop_soc INTEGER,
                bsd_battery_low_voltage INTEGER,
                bsd_battery_high_voltage INTEGER,
                bsd_battery_low_temperature INTEGER,
                bsd_battery_high_temperature INTEGER,
                error_68 INTEGER,
                error_69 INTEGER,
                error_70 INTEGER,
                error_71 INTEGER,
                error_72 INTEGER,
                error_73 INTEGER,
                error_74 INTEGER,
                error_75 INTEGER,

            )
        ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS DeviceOrder (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            equipment_id TEXT,
            gun_type INTEGER,
            gun_index INTEGER,
            charge_user_id TEXT,
            charge_start_time INTEGER,
            charge_end_time INTEGER,
            charge_time INTEGER,
            start_soc INTEGER,
            end_soc INTEGER,
            err_no TEXT,
            charge_kwh_amount INTEGER,
            start_charge_kwh_meter INTEGER,
            end_charge_kwh_meter INTEGER,
            total_charge_fee INTEGER,
            is_not_stoped_by_card INTEGER,
            start_card_money INTEGER,
            end_card_money INTEGER,
            total_service_fee INTEGER,
            is_paid_by_offline INTEGER,
            charge_policy INTEGER,
            charge_policy_param INTEGER,
            car_vin TEXT,
            car_plate_no TEXT,
            kwh_amount_1 INTEGER,
            kwh_amount_2 INTEGER,
            kwh_amount_3 INTEGER,
            kwh_amount_4 INTEGER,
            kwh_amount_5 INTEGER,
            kwh_amount_6 INTEGER,
            kwh_amount_7 INTEGER,
            car_plate_no INTEGER,
            kwh_amount_1 INTEGER,
            kwh_amount_2 INTEGER,
            kwh_amount_3 INTEGER,
            kwh_amount_4 INTEGER,
            kwh_amount_5 INTEGER,
            kwh_amount_6 INTEGER,
            kwh_amount_7 INTEGER,
            kwh_amount_8 INTEGER,
            kwh_amount_9 INTEGER,
            kwh_amount_10 INTEGER,
            kwh_amount_11 INTEGER,
            kwh_amount_12 INTEGER,
            kwh_amount_13 INTEGER,
            kwh_amount_14 INTEGER,
            kwh_amount_15 INTEGER,
            kwh_amount_16 INTEGER,
            kwh_amount_17 INTEGER,
            kwh_amount_18 INTEGER,
            kwh_amount_19 INTEGER,
            kwh_amount_20 INTEGER,
            kwh_amount_21 INTEGER,
            kwh_amount_22 INTEGER,
            kwh_amount_23 INTEGER,
            kwh_amount_24 INTEGER,
            kwh_amount_25 INTEGER,
            kwh_amount_26 INTEGER,
            kwh_amount_27 INTEGER,
            kwh_amount_28 INTEGER,
            kwh_amount_29 INTEGER,
            kwh_amount_30 INTEGER,
            kwh_amount_31 INTEGER,
            kwh_amount_32 INTEGER,
            kwh_amount_33 INTEGER,
            kwh_amount_34 INTEGER,
            kwh_amount_35 INTEGER,
            kwh_amount_36 INTEGER,
            kwh_amount_37 INTEGER,
            kwh_amount_38 INTEGER,
            kwh_amount_39 INTEGER,
            kwh_amount_40 INTEGER,
            kwh_amount_41 INTEGER,
            kwh_amount_42 INTEGER,
            kwh_amount_43 INTEGER,
            kwh_amount_44 INTEGER,
            kwh_amount_45 INTEGER,
            kwh_amount_46 INTEGER,
            kwh_amount_47 INTEGER,
            kwh_amount_48 INTEGER,
            start_charge_type INTEGER
        )
    ''')

    conn.commit()
    conn.close()


def save_DeviceInfo(data_id, data_type, data_str, data_int):
    conn = sqlite3.connect(data_path)
    cur = conn.cursor()
    if get_DeviceInfo(data_id) is None:
        cur.execute('''INSERT INTO DeviceInfo (data_id, data_type, data_str, data_int) VALUES (?, ?, ?, ?)''',
                    (data_id, data_type, data_str, data_int))
    else:
        cur.execute('''UPDATE DeviceInfo SET data_type = ?, data_str = ?, data_int = ? WHERE data_id = ?''',
                    (data_type, data_str, data_int, data_id))
    conn.commit()
    conn.close()


def get_DeviceInfo(data_id):
    conn = sqlite3.connect(data_path)
    cur = conn.cursor()
    cur.execute('SELECT * FROM DeviceInfo WHERE data_id = ?', (data_id,))
    result = cur.fetchone()
    conn.commit()
    conn.close()
    if not result:
        return None
    else:
        if result[2] == 1:
            return result[3]
        if result[2] == 2:
            return result[4]


def save_VerInfoEvt(device_id, device_type, hard_version, soft_version, dtu_ota_version):
    conn = sqlite3.connect(data_path)
    cur = conn.cursor()
    if get_VerInfoEvt(device_type)[0] is None:
        cur.execute(
            '''INSERT INTO VerInfoEvt (device_id, device_type, hard_version, soft_version, ota_version) VALUES (?, ?, ?, ?, ?)''',
            (device_id, device_type, hard_version, soft_version, dtu_ota_version))
    else:
        cur.execute(
            '''UPDATE VerInfoEvt SET device_id = ?, hard_version = ?, soft_version = ?, ota_version = ? WHERE device_type = ?''',
            (device_id, hard_version, soft_version, dtu_ota_version, device_type))
    conn.commit()
    conn.close()


def get_VerInfoEvt(device_type):
    conn = sqlite3.connect(data_path)
    cur = conn.cursor()
    cur.execute('SELECT * FROM VerInfoEvt WHERE device_type = ?', (device_type,))
    result = cur.fetchone()
    conn.commit()
    conn.close()
    if not result:
        return None, None
    else:
        return result[4] + result[5], result[3]


def save_FeeModel(dict_info):
    conn = sqlite3.connect(data_path)
    cur = conn.cursor()
    TimeNum = dict_info.get("TimeNum")
    SegFlag = dict_info.get("SegFlag")
    TimeSeg = dict_info.get("TimeSeg")
    chargeFee = dict_info.get("chargeFee")
    serviceFee = dict_info.get("serviceFee")
    cur.execute('DELETE FROM FeeModel')
    for i in range(0, TimeNum):
        cur.execute(
            '''INSERT INTO FeeModel (SegFlag, TimeNum, TimeSeg, chargeFee, serviceFee) VALUES (?, ?, ?, ?, ?)''',
            (SegFlag[i], TimeNum, TimeSeg[i], chargeFee[SegFlag[i] - 10], serviceFee[SegFlag[i] - 10]))
    conn.commit()
    conn.close()


def get_FeeModel():
    conn = sqlite3.connect(data_path)
    cur = conn.cursor()
    cur.execute('SELECT * FROM FeeModel')
    result = cur.fetchone()
    conn.commit()
    conn.close()
    return result


def save_DeviceOrder(dict_order: dict):
    conn = sqlite3.connect(data_path)
    cur = conn.cursor()
    if get_DeviceOrder(dict_order.get("device_session_id")) is None:
        cur.execute(
            '''INSERT INTO DeviceOrder (gunNo, preTradeNo, tradeNo, vinCode, timeDivType, chargeStartTime, 
            chargeEndTime, startSoc, endSoc, reason, eleModelId, serModelId, sumStart, sumEnd, totalElect, sharpElect, 
            peakElect, flatElect, valleyElect, totalPowerCost, totalServCost, sharpPowerCost, peakPowerCost, flatPowerCost, 
            valleyPowerCost, sharpServCost, peakServCost, flatServCost, valleyServCost, device_session_id) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (dict_order.get("gunNo"), dict_order.get("preTradeNo"), dict_order.get("tradeNo"),
             dict_order.get("vinCode"), dict_order.get("timeDivType"), dict_order.get("chargeStartTime"),
             dict_order.get("chargeEndTime"), dict_order.get("startSoc"), dict_order.get("endSoc"),
             dict_order.get("reason"), dict_order.get("eleModelId"), dict_order.get("serModelId"),
             dict_order.get("sumStart"), dict_order.get("sumEnd"), dict_order.get("totalElect"),
             dict_order.get("sharpElect"), dict_order.get("peakElect"), dict_order.get("flatElect"),
             dict_order.get("valleyElect"), dict_order.get("totalPowerCost"), dict_order.get("totalServCost"),
             dict_order.get("sharpPowerCost"), dict_order.get("peakPowerCost"), dict_order.get("flatPowerCost"),
             dict_order.get("valleyPowerCost"), dict_order.get("sharpServCost"), dict_order.get("peakServCost"),
             dict_order.get("flatServCost"), dict_order.get("valleyServCost"), dict_order.get("device_session_id")))
    else:
        cur.execute(
            '''UPDATE DeviceOrder SET gunNo = ?, preTradeNo = ?, tradeNo = ?, vinCode = ?, timeDivType = ?, 
            chargeStartTime = ?, chargeEndTime = ?, startSoc = ?, endSoc = ?, reason = ?, eleModelId = ?, 
            serModelId = ?, sumStart = ?, sumEnd = ?, totalElect = ?, sharpElect = ?, peakElect = ?, flatElect = ?, 
            valleyElect = ?, totalPowerCost = ?, totalServCost = ?, sharpPowerCost = ?, peakPowerCost = ?, 
            flatPowerCost = ?, valleyPowerCost = ?, sharpServCost = ?, peakServCost = ?, flatServCost = ?, 
            valleyServCost = ? WHERE device_session_id = ? ''',
            (dict_order.get("gunNo"), dict_order.get("preTradeNo"), dict_order.get("tradeNo"),
             dict_order.get("vinCode"), dict_order.get("timeDivType"), dict_order.get("chargeStartTime"),
             dict_order.get("chargeEndTime"), dict_order.get("startSoc"), dict_order.get("endSoc"),
             dict_order.get("reason"), dict_order.get("eleModelId"), dict_order.get("serModelId"),
             dict_order.get("sumStart"), dict_order.get("sumEnd"), dict_order.get("totalElect"),
             dict_order.get("sharpElect"), dict_order.get("peakElect"), dict_order.get("flatElect"),
             dict_order.get("valleyElect"), dict_order.get("totalPowerCost"), dict_order.get("totalServCost"),
             dict_order.get("sharpPowerCost"), dict_order.get("peakPowerCost"), dict_order.get("flatPowerCost"),
             dict_order.get("valleyPowerCost"), dict_order.get("sharpServCost"), dict_order.get("peakServCost"),
             dict_order.get("flatServCost"), dict_order.get("valleyServCost"), dict_order.get("device_session_id")
             ))
    conn.commit()
    conn.close()


def get_DeviceOrder(device_session_id):
    conn = sqlite3.connect(data_path)
    cur = conn.cursor()
    cur.execute('SELECT * FROM DeviceOrder WHERE device_session_id = ?', (device_session_id,))
    result = cur.fetchone()
    conn.commit()
    conn.close()
    return result


def get_DeviceOrder_tradeNo(tradeNo):
    conn = sqlite3.connect(data_path)
    cur = conn.cursor()
    cur.execute('SELECT * FROM DeviceOrder WHERE tradeNo = ?', (tradeNo,))
    result = cur.fetchone()
    conn.commit()
    conn.close()
    if result is None:
        return ""
    else:
        return result[30]


def get_DeviceOrder_preTradeNo(preTradeNo):
    conn = sqlite3.connect(data_path)
    cur = conn.cursor()
    cur.execute('SELECT * FROM DeviceOrder WHERE preTradeNo = ?', (preTradeNo,))
    result = cur.fetchone()
    conn.commit()
    conn.close()
    if result is None:
        return ""
    else:
        return result[30]


def get_last_DeviceOrder():
    conn = sqlite3.connect(data_path)
    cur = conn.cursor()
    cur.execute('SELECT * FROM DeviceOrder ORDER BY id DESC LIMIT 1')
    result = cur.fetchone()
    conn.commit()
    conn.close()
    return result[2]


def get_log_DeviceOrder(startDate, stopDate):
    DeviceOrder = []
    conn = sqlite3.connect(data_path)
    cur = conn.cursor()
    cur.execute('SELECT * FROM DeviceOrder')
    result = cur.fetchall()
    for info in result:
        if int(info[6]) >= int(startDate) or int(info[7]) <= int(stopDate):
            DeviceOrder.append(info)
    conn.commit()
    conn.close()
    return DeviceOrder


def save_dcOutMeterIty(dict_info: dict):
    conn = sqlite3.connect(data_path)
    cur = conn.cursor()
    gunNo = dict_info.get("gunNo")
    acqTime = dict_info.get("acqTime")
    mailAddr = dict_info.get("mailAddr")
    meterNo = dict_info.get("meterNo")
    assetId = dict_info.get("assetId")
    sumMeter = dict_info.get("sumMeter")
    lastTrade = dict_info.get("lastTrade")
    elec = dict_info.get("elec")
    cur.execute(
        '''INSERT INTO dcOutMeterIty (gunNo, acqTime, mailAddr, meterNo, assetId, sumMeter, elec, lastTrade) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
        (gunNo, acqTime, mailAddr, meterNo, assetId, sumMeter, elec, lastTrade))
    conn.commit()
    conn.close()


def get_log_dcOutMeterIty(startDate, stopDate):
    dcOutMeterIty = []
    conn = sqlite3.connect(data_path)
    cur = conn.cursor()
    cur.execute('SELECT * FROM dcOutMeterIty')
    result = cur.fetchall()
    for info in result:
        if int(startDate) <= int(datetime.strptime(info[2], '%Y%m%d%H%M%S').timestamp()) <= int(stopDate):
            dcOutMeterIty.append(info)
    conn.commit()
    conn.close()
    return dcOutMeterIty


def save_dcBmsRunIty(dict_info: dict):
    conn = sqlite3.connect(data_path)
    cur = conn.cursor()
    get_time = int(time.time())
    gunNo = dict_info.get("gunNo")
    preTradeNo = dict_info.get("preTradeNo")
    tradeNo = dict_info.get("tradeNo")
    socVal = dict_info.get("socVal")
    BMSVer = dict_info.get("BMSVer")
    BMSMaxVol = dict_info.get("BMSMaxVol")
    batType = dict_info.get("batType")
    batRatedCap = dict_info.get("batRatedCap")
    batRatedTotalVol = dict_info.get("batRatedTotalVol")
    singlBatMaxAllowVol = dict_info.get("singlBatMaxAllowVol")
    maxAllowCur = dict_info.get("maxAllowCur")
    battotalEnergy = dict_info.get("battotalEnergy")
    maxVol = dict_info.get("maxVol")
    maxTemp = dict_info.get("maxTemp")
    batCurVol = dict_info.get("batCurVol")
    cur.execute(
        '''INSERT INTO dcBmsRunIty (gunNo, preTradeNo, tradeNo, socVal, BMSVer, BMSMaxVol, batType, batRatedCap, batRatedTotalVol, 
         singlBatMaxAllowVol, maxAllowCur, battotalEnergy, maxVol, maxTemp, batCurVol, get_time) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (gunNo, preTradeNo, tradeNo, socVal, BMSVer, BMSMaxVol, batType, batRatedCap, batRatedTotalVol,
         singlBatMaxAllowVol, maxAllowCur, battotalEnergy, maxVol, maxTemp, batCurVol, get_time))
    conn.commit()
    conn.close()


def get_log_dcBmsRunIty(startDate, stopDate):
    dcBmsRunIty = []
    conn = sqlite3.connect(data_path)
    cur = conn.cursor()
    cur.execute('SELECT * FROM dcBmsRunIty')
    result = cur.fetchall()
    for info in result:
        if int(startDate) <= int(info[16]) <= int(stopDate):
            dcBmsRunIty.append(info)
    conn.commit()
    conn.close()
    return dcBmsRunIty


"""
/* #################################################### 数据库 #########################################################*/
"""
