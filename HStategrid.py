import copy
import hashlib
import struct
from datetime import datetime
import inspect
import queue
import sqlite3
import time
from enum import Enum

import HSyslog
import HHhdlist


class tpp_mqtt_cmd_enum(Enum):
    tpp_cmd_type_1 = 1
    tpp_cmd_type_2 = 2
    tpp_cmd_type_3 = 3
    tpp_cmd_type_4 = 4

    tpp_cmd_type_501 = 501
    tpp_cmd_type_502 = 502
    tpp_cmd_type_505 = 505
    tpp_cmd_type_506 = 506
    tpp_cmd_type_507 = 507
    tpp_cmd_type_508 = 508
    tpp_cmd_type_511 = 511
    tpp_cmd_type_512 = 512
    tpp_cmd_type_513 = 513
    tpp_cmd_type_514 = 514
    tpp_cmd_type_515 = 515
    tpp_cmd_type_516 = 516

    tpp_cmd_type_5 = 5
    tpp_cmd_type_6 = 6
    tpp_cmd_type_7 = 7
    tpp_cmd_type_8 = 8
    tpp_cmd_type_11 = 11
    tpp_cmd_type_12 = 12
    tpp_cmd_type_13 = 13
    tpp_cmd_type_14 = 14
    tpp_cmd_type_15 = 15
    tpp_cmd_type_16 = 16
    tpp_cmd_type_503 = 503
    tpp_cmd_type_504 = 504
    tpp_cmd_type_17 = 17
    tpp_cmd_type_18 = 18
    tpp_cmd_type_19 = 19
    tpp_cmd_type_20 = 20

    tpp_cmd_type_101 = 101
    tpp_cmd_type_102 = 102
    tpp_cmd_type_103 = 103
    tpp_cmd_type_104 = 104
    tpp_cmd_type_105 = 105
    tpp_cmd_type_106 = 106
    tpp_cmd_type_113 = 113
    tpp_cmd_type_114 = 114

    tpp_cmd_type_301 = 301
    tpp_cmd_type_302 = 302
    tpp_cmd_type_303 = 303
    tpp_cmd_type_304 = 304
    tpp_cmd_type_305 = 305
    tpp_cmd_type_306 = 306
    tpp_cmd_type_307 = 307
    tpp_cmd_type_308 = 308
    tpp_cmd_type_309 = 309
    tpp_cmd_type_310 = 310
    tpp_cmd_type_311 = 311
    tpp_cmd_type_312 = 312

    tpp_cmd_type_201 = 201
    tpp_cmd_type_202 = 202
    tpp_cmd_type_205 = 205
    tpp_cmd_type_206 = 206

    tpp_cmd_type_401 = 401
    tpp_cmd_type_402 = 402

    tpp_cmd_type_23 = 23
    tpp_cmd_type_24 = 24

    tpp_cmd_type_1303 = 1303
    tpp_cmd_type_1304 = 1304
    tpp_cmd_type_1305 = 1305
    tpp_cmd_type_1306 = 1306
    tpp_cmd_type_1307 = 1307
    tpp_cmd_type_1308 = 1308
    tpp_cmd_type_1309 = 1309
    tpp_cmd_type_1310 = 1310

    tpp_cmd_type_107 = 107
    tpp_cmd_type_108 = 108
    tpp_cmd_type_117 = 117
    tpp_cmd_type_118 = 118
    tpp_cmd_type_119 = 119
    tpp_cmd_type_120 = 120

    tpp_cmd_type_407 = 407
    tpp_cmd_type_408 = 408
    tpp_cmd_type_409 = 409
    tpp_cmd_type_410 = 410

    tpp_cmd_type_1101 = 1101
    tpp_cmd_type_1102 = 1102

    tpp_cmd_type_801 = 801
    tpp_cmd_type_802 = 802

    tpp_cmd_type_509 = 509
    tpp_cmd_type_510 = 510

    tpp_cmd_type_33 = 33
    tpp_cmd_type_34 = 34
    tpp_cmd_type_35 = 35
    tpp_cmd_type_36 = 36
    tpp_cmd_type_37 = 37
    tpp_cmd_type_38 = 38
    tpp_cmd_type_331 = 331
    tpp_cmd_type_332 = 332

    tpp_cmd_type_40 = 40
    tpp_cmd_type_41 = 41
    tpp_cmd_type_42 = 42
    tpp_cmd_type_43 = 43
    tpp_cmd_type_44 = 44
    tpp_cmd_type_45 = 45

    tpp_cmd_type_80 = 80
    tpp_cmd_type_81 = 81


def tpp_cmd_1(data: list):  # 平台发送，设备接收
    try:
        data_type = Encode_type.BIN.value
        data_len = 4
        cmd_type = hex_to_info(data[4], Encode_type.BIN.value)
        data_addr = hex_to_info(data[5:9], Encode_type.BIN.value)
        if cmd_type == 1:
            if data_addr in cleck_code_1.keys():
                data_type = cleck_code_1.get(data_addr).get("encode")[1]
                data_len = cleck_code_1.get(data_addr).get("encode")[0]
            else:
                HSyslog.log_info(f"cleck_code_1 error: {data_addr}")
                return {}
            info = {
                "reserved": hex_to_info(data[0:4], Encode_type.BIN.value),  # 保留字节
                "cmd_type": cmd_type,  # 类型：设置
                "data_addr": data_addr,  # 设置参数启始地址
                "cmd_num": hex_to_info(data[9], Encode_type.BIN.value),  # 设置参数的个数
                "cmd_len": hex_to_info(data[10:12], Encode_type.BIN.value),  # 设置参数的字节数
                "data": hex_to_info(data[12:data_len + 12], data_type),  # 设置参数的数据
            }
            tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_1.value, info])
        else:
            info = {
                "reserved": hex_to_info(data[0:4], Encode_type.BIN.value),  # 保留
                "cmd_type": cmd_type,  # 类型：查询
                "data_addr": data_addr,  # 查询参数的启始地址
                "cmd_num": hex_to_info(data[9], Encode_type.BIN.value),  # 查询参数的个数
                "cmd_len": hex_to_info(data[10:12], Encode_type.BIN.value),  # 查询参数的字节数
            }
            tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_1.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_1: {data}")
            HSyslog.log_info(f"tpp_cmd_1: {info}")
        return info
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_1 error: .{data} .{e}")
        return {}


def tpp_cmd_2(data: dict):  # 设备发送，平台接收
    device_id = data.get("device_id", Device_ID)  #
    cmd_type = data.get("cmd_type")
    cmd_num = data.get("cmd_num")
    result = data.get("result")
    data_addr = data.get("data_addr")
    datainfo = data.get("datainfo")
    reserved = data.get("reserved", 0)

    try:
        data_type = Encode_type.BIN.value
        data_len = 4
        if data_addr in cleck_code_1.keys():
            data_type = cleck_code_1.get(data_addr).get("encode")[1]
            data_len = cleck_code_1.get(data_addr).get("encode")[0]
        else:
            HSyslog.log_info(f"cleck_code_1 error: {data_addr}")
            return {}

        tpp_cmd_2_msg = []
        tpp_cmd_2_msg += info_to_hex(reserved, 4, Encode_type.BIN.value)
        tpp_cmd_2_msg += info_to_hex(device_id, 32, Encode_type.ASCII.value)
        tpp_cmd_2_msg += info_to_hex(cmd_type, 1, Encode_type.BIN.value)
        tpp_cmd_2_msg += info_to_hex(data_addr, 4, Encode_type.BIN.value)
        tpp_cmd_2_msg += info_to_hex(cmd_num, 1, Encode_type.BIN.value)
        tpp_cmd_2_msg += info_to_hex(result, 1, Encode_type.BIN.value)
        tpp_cmd_2_msg += info_to_hex(datainfo, data_type, data_len)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_2: {data}")
            HSyslog.log_info(f"tpp_cmd_2: {tpp_cmd_2_msg}")

        return pack(tpp_cmd_2_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_2.value)
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_2 error: .{data} .{e}")
        return []


def tpp_cmd_3(data: list):  # 平台发送，设备接收
    try:
        data_type = Encode_type.ASCII.value
        data_len = hex_to_info(data[9:11], Encode_type.BIN.value)
        data_addr = hex_to_info(data[5:9], Encode_type.BIN.value)
        cmd_type = hex_to_info(data[4], Encode_type.BIN.value)
        if cmd_type == 1:
            if data_addr in cleck_code_3.keys():
                data_type = cleck_code_3.get(data_addr).get("encode")[1]
                data_len = cleck_code_3.get(data_addr).get("encode")[0]
            else:
                HSyslog.log_info(f"cleck_code_3 error: {data_addr}")
                return {}
            info = {
                "reserved": hex_to_info(data[0:4], Encode_type.BIN.value),
                "cmd_type": cmd_type,  #
                "data_addr": data_addr,  #
                "data_len": data_len,  #
                "data": hex_to_info(data[11:data_len + 11], data_type),  #
            }
            tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_3.value, info])
        else:
            info = {
                "reserved": hex_to_info(data[0:4], Encode_type.BIN.value),
                "cmd_type": cmd_type,  #
                "data_addr": data_addr,  #
                "data_len": data_len,  #
            }
            tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_3.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_3: {data}")
            HSyslog.log_info(f"tpp_cmd_3: {info}")
        return info
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_3 error: .{data} .{e}")
        return {}


def tpp_cmd_4(data: dict):  # 设备发送，平台接收
    device_id = data.get("device_id", Device_ID)
    cmd_type = data.get("cmd_type")
    result = data.get("result")
    data_addr = data.get("data_addr")
    datainfo = data.get("datainfo")
    reserved = data.get("reserved", 0)

    try:
        if data_addr in cleck_code_3.keys():
            data_type = cleck_code_3.get(data_addr).get("encode")[1]
            data_len = cleck_code_3.get(data_addr).get("encode")[0]
        else:
            HSyslog.log_info(f"cleck_code_3 error: {data_addr}")
            return {}
        tpp_cmd_4_msg = []
        tpp_cmd_4_msg += info_to_hex(reserved, 4, Encode_type.BIN.value)
        tpp_cmd_4_msg += info_to_hex(device_id, 32, Encode_type.ASCII.value)
        tpp_cmd_4_msg += info_to_hex(cmd_type, 1, Encode_type.BIN.value)
        tpp_cmd_4_msg += info_to_hex(data_addr, 4, Encode_type.BIN.value)
        tpp_cmd_4_msg += info_to_hex(result, 1, Encode_type.BIN.value)
        tpp_cmd_4_msg += info_to_hex(datainfo, data_len, data_type)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_4: {data}")
            HSyslog.log_info(f"tpp_cmd_4: {tpp_cmd_4_msg}")

        return pack(tpp_cmd_4_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_4.value)
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_4 error: .{data} .{e}")
        return []


def tpp_cmd_501(data: list):  # 平台发送，设备接收
    try:
        data_info = {}
        data_list = data[4:]
        while data_list:
            data_addr = hex_to_info(data_list[0:2], Encode_type.BIN.value)
            if data_addr in cleck_code_501.keys():
                data_type = cleck_code_501.get(data_addr).get("encode")[1]
                data_len = cleck_code_501.get(data_addr).get("encode")[0]
                if data_addr == 6:
                    data_info.update({data_addr: f"{hex_to_info(data_list[2:4], Encode_type.BIN.value)}:{hex_to_info(data_list[4:data_len + 4], data_type)}"})
                else:
                    data_info.update({data_addr: hex_to_info(data_list[2:data_len + 2], data_type)})

                data_list = data_list[data_len + 2:]
            else:
                HSyslog.log_info(f"cleck_code_501 error: {data_addr}")
                break

        info = {
            "reserved": hex_to_info(data[0:4], Encode_type.BIN.value),
            "data_dict": data_info,  #
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_501.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_501: {data}")
            HSyslog.log_info(f"tpp_cmd_501: {info}")
        return info
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_501 error: .{data} .{e}")
        return {}


def tpp_cmd_502(data: dict):  # 设备发送，平台接收
    device_id = data.get("device_id", Device_ID)
    suss_num = data.get("suss_num")
    result = data.get("result")

    try:
        tpp_cmd_502_msg = []
        tpp_cmd_502_msg += info_to_hex(suss_num, 4, Encode_type.BIN.value)
        tpp_cmd_502_msg += info_to_hex(device_id, 32, Encode_type.ASCII.value)
        tpp_cmd_502_msg += info_to_hex(result, 1, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_502: {data}")
            HSyslog.log_info(f"tpp_cmd_502: {tpp_cmd_502_msg}")

        return pack(tpp_cmd_502_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_502.value)
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_502 error: .{data} .{e}")
        return []


def tpp_cmd_505(data: list):  # 平台发送，设备接收
    try:
        info = {
            "reserved": hex_to_info(data[0:4], Encode_type.BIN.value),  #
            "gun_id": hex_to_info(data[4], Encode_type.BIN.value),  #
            "charge_id": hex_to_info(data[5:37], Encode_type.ASCII.value),  #
            "cur_reg_coefficient_single_overvol_protection_4": hex_to_info(data[37:39], Encode_type.BIN.value),  #
            "point_reg_coefficient_single_overvoltage_protection": hex_to_info(data[39:41], Encode_type.BIN.value),  #
            "max_temperature_alarm": hex_to_info(data[41:43], Encode_type.BIN.value),  #
            "max_temperature_protection": hex_to_info(data[43:45], Encode_type.BIN.value),  #
            "cur_reg_coefficient_single_overvol_protection_5": hex_to_info(data[45:47], Encode_type.BIN.value),  #
            "battery_temperature_warn": hex_to_info(data[47:49], Encode_type.ASCII.value),  #
            "battery_temperature_protection": hex_to_info(data[49:51], Encode_type.BIN.value),  #
            "cur_reg_coefficient_temperature_protection": hex_to_info(data[51:53], Encode_type.BIN.value),  #
            "temperature_difference_warning": hex_to_info(data[53:55], Encode_type.BIN.value),  #
            "temperature_difference_protection": hex_to_info(data[55:57], Encode_type.BIN.value),  #
            "cur_reg_coefficient_temperature_difference_warning": hex_to_info(data[57:59], Encode_type.BIN.value),  #
            "overcharge_warning": hex_to_info(data[59:61], Encode_type.BIN.value),  #
            "overcharge_protection": hex_to_info(data[61:63], Encode_type.BIN.value),  #
            "battery_health_SOH": hex_to_info(data[63:65], Encode_type.BIN.value),  #
            "cur_reg_coefficient_overcharge_warning ": hex_to_info(data[65:67], Encode_type.BIN.value),  #
            "SOC_abnormal_protection_coefficient": hex_to_info(data[67:69], Encode_type.BIN.value),  #
            "battery_vol_inconsistent_BCP_battery_vol": hex_to_info(data[69:71], Encode_type.BIN.value),  #
            "battery_vol_range_protection": hex_to_info(data[71:73], Encode_type.BIN.value),  #
            "idle_gun_head_charged": hex_to_info(data[73:75], Encode_type.BIN.value),  #
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_505.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_505: {data}")
            HSyslog.log_info(f"tpp_cmd_505: {info}")

        return info
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_505 error: .{data} .{e}")
        return {}


def tpp_cmd_506(data: dict):  # 设备发送，平台接收
    gun_id = data.get("gun_id")
    result = data.get("result")
    charge_id = data.get("charge_id")
    reserved = data.get("reserved", 0)

    try:
        tpp_cmd_506_msg = []
        tpp_cmd_506_msg += info_to_hex(reserved, 4, Encode_type.BIN.value)
        tpp_cmd_506_msg += info_to_hex(gun_id, 1, Encode_type.BIN.value)
        tpp_cmd_506_msg += info_to_hex(charge_id, 32, Encode_type.ASCII.value)
        tpp_cmd_506_msg += info_to_hex(result, 1, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_506: {data}")
            HSyslog.log_info(f"tpp_cmd_506: {tpp_cmd_506_msg}")

        return pack(tpp_cmd_506_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_506.value)
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_506 error: .{data} .{e}")
        return []


def tpp_cmd_507(data: list):  # 平台发送，设备接收
    try:
        data_info = {}
        data_list = data[38:]
        while data_list:
            data_addr = hex_to_info(data_list[0], Encode_type.BIN.value)
            data_len = hex_to_info(data_list[1], Encode_type.BIN.value)
            if data_addr in cleck_code_507.keys():
                data_type = cleck_code_507.get(data_addr).get("encode")[1]
                data_len = cleck_code_507.get(data_addr).get("encode")[0]
                data_info.update({data_addr: hex_to_info(data_list[2:data_len + 2], data_type)})

                data_list = data_list[data_len + 2:]
            else:
                HSyslog.log_info(f"cleck_code_507 error: {data_addr}")
                break

        info = {
            "device_id": hex_to_info(data[0:32], Encode_type.ASCII.value),
            "reserved1": hex_to_info(data[32:36], Encode_type.BIN.value),
            "cmd_num": hex_to_info(data[36], Encode_type.BIN.value),
            "reserved2": hex_to_info(data[37], Encode_type.BIN.value),
            "data_dict": data_info,  #
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_507.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_507: {data}")
            HSyslog.log_info(f"tpp_cmd_507: {info}")
        return info
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_507 error: .{data} .{e}")
        return {}


def tpp_cmd_508(data: dict):  # 设备发送，平台接收
    reserved = data.get("reserved", 0)
    device_id = data.get("device_id", Device_ID)
    suss_num = data.get("suss_num")
    fail_num = data.get("fail_num")
    result = data.get("result")
    fail_data_info = data.get("fail_data_info")

    try:
        tpp_cmd_508_msg = []
        tpp_cmd_508_msg += info_to_hex(device_id, 32, Encode_type.ASCII.value)
        tpp_cmd_508_msg += info_to_hex(reserved, 4, Encode_type.BIN.value)
        tpp_cmd_508_msg += info_to_hex(result, 2, Encode_type.BIN.value)
        tpp_cmd_508_msg += info_to_hex(suss_num, 1, Encode_type.BIN.value)
        tpp_cmd_508_msg += info_to_hex(fail_num, 1, Encode_type.BIN.value)
        if len(fail_data_info) != 0:
            for data_cmd, data_reson in fail_data_info.items():
                tpp_cmd_508_msg += info_to_hex(data_cmd, 1, Encode_type.BIN.value)
                tpp_cmd_508_msg += info_to_hex(data_reson, 1, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_508: {data}")
            HSyslog.log_info(f"tpp_cmd_508: {tpp_cmd_508_msg}")

        return pack(tpp_cmd_508_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_508.value)
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_508 error: .{data} .{e}")
        return []


def tpp_cmd_511(data: list):  # 平台发送，设备接收
    try:
        info = {
            "device_id": hex_to_info(data[0:32], Encode_type.ASCII.value),
            "reserved1": hex_to_info(data[32:36], Encode_type.BIN.value),
            "ctrl_cmd": hex_to_info(data[36], Encode_type.BIN.value),
            "reserved2": hex_to_info(data[37:40], Encode_type.BIN.value),
            "cmd_addr": hex_to_info(data[40:42], Encode_type.BIN.value),
            "cmd_ctrl": hex_to_info(data[42:44], Encode_type.BIN.value)
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_511.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_511: {data}")
            HSyslog.log_info(f"tpp_cmd_511: {info}")
        return info
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_511 error: .{data} .{e}")
        return {}


def tpp_cmd_512(data: dict):  # 设备发送，平台接收
    reserved = data.get("reserved", 0)
    device_id = data.get("device_id", Device_ID)
    result = data.get("result")
    fail_reason = data.get("fail_reason")

    try:
        tpp_cmd_512_msg = []
        tpp_cmd_512_msg += info_to_hex(device_id, 32, Encode_type.ASCII.value)
        tpp_cmd_512_msg += info_to_hex(reserved, 4, Encode_type.BIN.value)
        tpp_cmd_512_msg += info_to_hex(result, 1, Encode_type.BIN.value)
        tpp_cmd_512_msg += info_to_hex(fail_reason, 1, Encode_type.BIN.value)
        tpp_cmd_512_msg += info_to_hex(reserved, 2, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_512: {data}")
            HSyslog.log_info(f"tpp_cmd_512: {tpp_cmd_512_msg}")

        return pack(tpp_cmd_512_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_512.value)
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_512 error: .{data} .{e}")
        return []


def tpp_cmd_513(data: list):  # 平台发送，设备接收
    try:
        info = {
            "device_id": hex_to_info(data[0:32], Encode_type.ASCII.value),
            "reserved1": hex_to_info(data[32:36], Encode_type.BIN.value),
            "cmd_num": hex_to_info(data[36], Encode_type.BIN.value),
            "reserved2": hex_to_info(data[37], Encode_type.BIN.value),
            "data_list": data[38:],  #
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_513.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_513: {data}")
            HSyslog.log_info(f"tpp_cmd_513: {info}")
        return info
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_513 error: .{data} .{e}")
        return {}


def tpp_cmd_514(data: dict):  # 设备发送，平台接收
    reserved = data.get("reserved", 0)
    device_id = data.get("device_id", Device_ID)
    data_num = data.get("data_num")
    data_info = data.get("data_info")

    try:
        tpp_cmd_514_msg = []
        tpp_cmd_514_msg += info_to_hex(device_id, 32, Encode_type.ASCII.value)
        tpp_cmd_514_msg += info_to_hex(reserved, 4, Encode_type.BIN.value)
        tpp_cmd_514_msg += info_to_hex(data_num, 1, Encode_type.BIN.value)
        tpp_cmd_514_msg += info_to_hex(reserved, 1, Encode_type.BIN.value)
        for data_cmd, data_dict in data_info.items():
            tpp_cmd_514_msg += info_to_hex(data_cmd, 1, Encode_type.BIN.value)
            tpp_cmd_514_msg += info_to_hex(data_dict.get("data_result"), 1, Encode_type.BIN.value)
            tpp_cmd_514_msg += info_to_hex(data_dict.get("data_len"), 1, Encode_type.BIN.value)
            tpp_cmd_514_msg += info_to_hex(data_dict.get("data"), data_dict.get("data_len"), data_dict.get("data_type"))

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_514: {data}")
            HSyslog.log_info(f"tpp_cmd_514: {tpp_cmd_514_msg}")

        return pack(tpp_cmd_514_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_514.value)
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_514 error: .{data} .{e}")
        return []


def tpp_cmd_515(data: list):  # 平台发送，设备接收
    pass


def tpp_cmd_516(data: dict):  # 设备发送，平台接收
    pass


def tpp_cmd_5(data: list):  # 平台发送，设备接收
    try:
        data_type = Encode_type.BIN.value
        data_len = hex_to_info(data[10:12], Encode_type.BIN.value)
        data_addr = hex_to_info(data[5:9], Encode_type.BIN.value)
        if data_addr in cleck_code_5.keys():
            data_type = cleck_code_5.get(data_addr).get("encode")[1]
            data_len = cleck_code_5.get(data_addr).get("encode")[0]
        else:
            HSyslog.log_info(f"cleck_code_5 error: {data_addr}")
            return {}
        info = {
            "reserved": hex_to_info(data[0:4], Encode_type.BIN.value),
            "gun_id": hex_to_info(data[4], Encode_type.BIN.value),  #
            "data_addr": data_addr,  #
            "cmd_num": hex_to_info(data[9], Encode_type.BIN.value),  #
            "data_len": data_len,  #
            "data": hex_to_info(data[12:data_len + 12], data_type),  #
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_5.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_5: {data}")
            HSyslog.log_info(f"tpp_cmd_5: {info}")

        return info
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_5 error: .{data} .{e}")
        return {}


def tpp_cmd_6(data: dict):  # 设备发送，平台接收
    device_id = data.get("device_id", Device_ID)
    gun_id = data.get("gun_id")
    data_addr = data.get("data_addr")
    cmd_num = data.get("cmd_num")
    result = data.get("result")
    reserved = data.get("reserved", 0)

    try:
        tpp_cmd_6_msg = []
        tpp_cmd_6_msg += info_to_hex(reserved, 4, Encode_type.BIN.value)
        tpp_cmd_6_msg += info_to_hex(device_id, 32, Encode_type.ASCII.value)
        tpp_cmd_6_msg += info_to_hex(gun_id, 1, Encode_type.BIN.value)
        tpp_cmd_6_msg += info_to_hex(data_addr, 4, Encode_type.BIN.value)
        tpp_cmd_6_msg += info_to_hex(cmd_num, 1, Encode_type.BIN.value)
        tpp_cmd_6_msg += info_to_hex(result, 4, Encode_type.ASCII.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_6: {data}")
            HSyslog.log_info(f"tpp_cmd_6: {tpp_cmd_6_msg}")

        return pack(tpp_cmd_6_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_6.value)
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_6 error: .{data} .{e}")
        return []


def tpp_cmd_7(data: list):  # 平台发送，设备接收
    try:
        info = {
            "reserved1": hex_to_info(data[0:2], Encode_type.BIN.value),  #
            "user_phone": hex_to_info(data[2:4], Encode_type.BIN.value),  #
            "gun_id": hex_to_info(data[4], Encode_type.BIN.value),  #
            "charge_type": hex_to_info(data[5:9], Encode_type.BIN.value),  #
            "reserved2": hex_to_info(data[9:13], Encode_type.BIN.value),  #
            "charge_policy": hex_to_info(data[13:17], Encode_type.BIN.value),  #
            "charge_policy_param": hex_to_info(data[17:21], Encode_type.BIN.value),  #
            "book_time": hex_to_info(data[21:29], Encode_type.TIME.value),  #
            "book_timeout": hex_to_info(data[29], Encode_type.BIN.value),  #
            "charge_id": hex_to_info(data[30:62], Encode_type.ASCII.value),  #
            "allow_offline_charge": hex_to_info(data[62], Encode_type.BIN.value),  #
            "allow_offline_charge_kw_amout": hex_to_info(data[63:67], Encode_type.BIN.value),  #
            "charge_delay_cost_is": hex_to_info(data[67], Encode_type.BIN.value),  #
            "charge_delay_cost_time": hex_to_info(data[68:72], Encode_type.BIN.value),  #

        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_7.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_7: {data}")
            HSyslog.log_info(f"tpp_cmd_7: {info}")

        return info
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_7 error: .{data} .{e}")
        return {}


def tpp_cmd_8(data: dict):  # 设备发送，平台接收
    device_id = data.get("device_id", Device_ID)
    gun_id = data.get("gun_id")
    result = data.get("result")
    charge_id = data.get("charge_id")
    reserved = data.get("reserved", 0)

    try:
        tpp_cmd_8_msg = []
        tpp_cmd_8_msg += info_to_hex(reserved, 4, Encode_type.BIN.value)
        tpp_cmd_8_msg += info_to_hex(device_id, 32, Encode_type.ASCII.value)
        tpp_cmd_8_msg += info_to_hex(gun_id, 1, Encode_type.BIN.value)
        tpp_cmd_8_msg += info_to_hex(result, 4, Encode_type.ASCII.value)
        tpp_cmd_8_msg += info_to_hex(charge_id, 32, Encode_type.ASCII.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_8: {data}")
            HSyslog.log_info(f"tpp_cmd_8: {tpp_cmd_8_msg}")

        return pack(tpp_cmd_8_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_8.value)
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_8 error: .{data} .{e}")
        return []


def tpp_cmd_11(data: list):  # 平台发送，设备接收
    try:
        info = {
            "device_id": hex_to_info(data[0:32], Encode_type.ASCII.value),  #
            "gun_id": hex_to_info(data[32], Encode_type.BIN.value),  #
            "charge_id": hex_to_info(data[33:65], Encode_type.ASCII.value)
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_11.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_11: {data}")
            HSyslog.log_info(f"tpp_cmd_11: {info}")

        return info
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_11 error: .{data} .{e}")
        return {}


def tpp_cmd_12(data: dict):  # 设备发送，平台接收
    device_id = data.get("device_id", Device_ID)
    gun_id = data.get("gun_id")
    charge_id = data.get("charge_id")
    result = data.get("result")

    try:
        tpp_cmd_12_msg = []
        tpp_cmd_12_msg += info_to_hex(device_id, 32, Encode_type.ASCII.value)
        tpp_cmd_12_msg += info_to_hex(gun_id, 1, Encode_type.BIN.value)
        tpp_cmd_12_msg += info_to_hex(charge_id, 32, Encode_type.ASCII.value)
        tpp_cmd_12_msg += info_to_hex(result, 4, Encode_type.ASCII.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_12: {data}")
            HSyslog.log_info(f"tpp_cmd_12: {tpp_cmd_12_msg}")

        return pack(tpp_cmd_12_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_12.value)
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_12 error: .{data} .{e}")
        return []


def tpp_cmd_13(data: list):  # 平台发送，设备接收
    try:
        info = {
            "device_id": hex_to_info(data[0:32], Encode_type.ASCII.value),  #
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_13.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_13: {data}")
            HSyslog.log_info(f"tpp_cmd_13: {info}")

        return info
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_13 error: .{data} .{e}")
        return {}


def tpp_cmd_14(data: dict):  # 设备发送，平台接收
    device_id = data.get("device_id", Device_ID)
    power_model_num = data.get("power_model_num")
    device_power = data.get("device_power")
    power_model_list = data.get("power_model_list")

    try:
        tpp_cmd_14_msg = []
        tpp_cmd_14_msg += info_to_hex(device_id, 32, Encode_type.ASCII.value)
        tpp_cmd_14_msg += info_to_hex(power_model_num, 4, Encode_type.BIN.value)
        tpp_cmd_14_msg += info_to_hex(device_power, 4, Encode_type.BIN.value)
        for i in range(0, power_model_num):
            tpp_cmd_14_msg += info_to_hex(power_model_list[i].get("power_model_status"), 1, Encode_type.BIN.value)
            tpp_cmd_14_msg += info_to_hex(power_model_list[i].get("power_model_kw"), 4, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_14: {data}")
            HSyslog.log_info(f"tpp_cmd_14: {tpp_cmd_14_msg}")

        return pack(tpp_cmd_14_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_14.value)
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_14 error: .{data} .{e}")
        return []


def tpp_cmd_15(data: list):  # 平台发送，设备接收
    try:
        power_out_num_list = []
        power_model_num = hex_to_info(data[34:38], Encode_type.BIN.value)
        for i in (0, power_model_num):
            power_out_num_list += hex_to_info(data[38 + i], Encode_type.BIN.value)
        info = {
            "device_id": hex_to_info(data[0:32], Encode_type.ASCII.value),  #
            "gun_id": hex_to_info(data[32], Encode_type.BIN.value),  #
            "charge_policy_date": hex_to_info(data[33], Encode_type.BIN.value),  #
            "power_model_num": power_model_num,  #
            "power_out_nums": power_out_num_list
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_15.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_15: {data}")
            HSyslog.log_info(f"tpp_cmd_15: {info}")

        return info
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_15 error: .{data} .{e}")
        return {}


def tpp_cmd_16(data: dict):  # 设备发送，平台接收
    device_id = data.get("device_id", Device_ID)
    gun_id = data.get("gun_id")
    gun_power = data.get("gun_power")
    result = data.get("result")

    try:
        tpp_cmd_16_msg = []
        tpp_cmd_16_msg += info_to_hex(device_id, 32, Encode_type.ASCII.value)
        tpp_cmd_16_msg += info_to_hex(gun_id, 1, Encode_type.BIN.value)
        tpp_cmd_16_msg += info_to_hex(gun_power, 4, Encode_type.BIN.value)
        tpp_cmd_16_msg += info_to_hex(result, 4, Encode_type.ASCII.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_16: {data}")
            HSyslog.log_info(f"tpp_cmd_16: {tpp_cmd_16_msg}")

        return pack(tpp_cmd_16_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_16.value)
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_16 error: .{data} .{e}")
        return []


def tpp_cmd_503(data: list):  # 平台发送，设备接收
    try:
        max_power_list = []
        max_power = data[32:]
        for i in (0, len(max_power), 5):
            max_power_list.append({
                hex_to_info(max_power[i], Encode_type.BIN.value): hex_to_info(max_power[i + 1: i + 1 + 4], Encode_type.BIN.value)
            })
        info = {
            "device_id": hex_to_info(data[0:32], Encode_type.ASCII.value),  #
            "max_power": max_power_list,
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_503.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_503: {data}")
            HSyslog.log_info(f"tpp_cmd_503: {info}")

        return info
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_503 error: .{data} .{e}")
        return {}


def tpp_cmd_504(data: dict):  # 设备发送，平台接收
    device_id = data.get("device_id", Device_ID)
    result = data.get("result")

    try:
        tpp_cmd_504_msg = []
        tpp_cmd_504_msg += info_to_hex(device_id, 32, Encode_type.ASCII.value)
        tpp_cmd_504_msg += info_to_hex(result, 1, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_504: {data}")
            HSyslog.log_info(f"tpp_cmd_504: {tpp_cmd_504_msg}")

        return pack(tpp_cmd_504_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_504.value)
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_504 error: .{data} .{e}")
        return []


def tpp_cmd_17(data: list):  # 平台发送，设备接收
    try:
        info = {
            "device_id": hex_to_info(data[0:32], Encode_type.ASCII.value),  #
            "gun_id": hex_to_info(data[32], Encode_type.BIN.value),  #
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_17.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_17: {data}")
            HSyslog.log_info(f"tpp_cmd_17: {info}")

        return info
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_17 error: .{data} .{e}")
        return {}


def tpp_cmd_18(data: dict):  # 设备发送，平台接收
    device_id = data.get("device_id", Device_ID)
    gun_id = data.get("gun_id")
    charge_policy_date = data.get("charge_policy_date")
    power_model_num = data.get("power_model_num")
    power_model_out_list = data.get("power_model_out_list")

    try:
        tpp_cmd_18_msg = []
        tpp_cmd_18_msg += info_to_hex(device_id, 32, Encode_type.ASCII.value)
        tpp_cmd_18_msg += info_to_hex(gun_id, 1, Encode_type.BIN.value)
        tpp_cmd_18_msg += info_to_hex(charge_policy_date, 1, Encode_type.BIN.value)
        tpp_cmd_18_msg += info_to_hex(power_model_num, 4, Encode_type.ASCII.value)
        for i in power_model_out_list:
            tpp_cmd_18_msg += info_to_hex(i, 1, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_18: {data}")
            HSyslog.log_info(f"tpp_cmd_18: {tpp_cmd_18_msg}")

        return pack(tpp_cmd_18_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_18.value)
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_18 error: .{data} .{e}")
        return []


def tpp_cmd_19(data: list):  # 平台发送，设备接收
    try:
        info = {
            "device_id": hex_to_info(data[0:32], Encode_type.ASCII.value),  #
            "gun_id": hex_to_info(data[32], Encode_type.BIN.value),  #
            "max_gun_power": hex_to_info(data[33:37], Encode_type.BIN.value),  #
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_19.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_19: {data}")
            HSyslog.log_info(f"tpp_cmd_19: {info}")

        return info
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_19 error: .{data} .{e}")
        return {}


def tpp_cmd_20(data: dict):  # 设备发送，平台接收
    device_id = data.get("device_id", Device_ID)
    gun_id = data.get("gun_id")
    result = data.get("result")

    try:
        tpp_cmd_20_msg = []
        tpp_cmd_20_msg += info_to_hex(device_id, 32, Encode_type.ASCII.value)
        tpp_cmd_20_msg += info_to_hex(gun_id, 1, Encode_type.BIN.value)
        tpp_cmd_20_msg += info_to_hex(result, 1, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_20: {data}")
            HSyslog.log_info(f"tpp_cmd_20: {tpp_cmd_20_msg}")

        return pack(tpp_cmd_20_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_20.value)
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_20 error: .{data} .{e}")
        return []


def tpp_cmd_101(data: list):  # 平台发送，设备接收
    try:
        info = {
            "reserved": hex_to_info(data[0:4], Encode_type.BIN.value),  #
            "heart_index": hex_to_info(data[4:6], Encode_type.BIN.value),  #
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_101.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_101: {data}")
            HSyslog.log_info(f"tpp_cmd_101: {info}")

        return info
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_101 error: .{data} .{e}")
        return {}


def tpp_cmd_102(data: dict):  # 设备发送，平台接收
    reserved = data.get("reserved", 0)
    device_id = data.get("device_id", Device_ID)
    heart_index = data.get("heart_index")

    try:
        tpp_cmd_102_msg = []
        tpp_cmd_102_msg += info_to_hex(reserved, 4, Encode_type.BIN.value)
        tpp_cmd_102_msg += info_to_hex(device_id, 32, Encode_type.ASCII.value)
        tpp_cmd_102_msg += info_to_hex(heart_index, 2, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_102: {data}")
            HSyslog.log_info(f"tpp_cmd_102: {tpp_cmd_102_msg}")

        return pack(tpp_cmd_102_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_102.value)
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_102 error: .{data} .{e}")
        return []


def tpp_cmd_103(data: list):  # 平台发送，设备接收
    try:
        info = {
            "reserved": hex_to_info(data[0:2], Encode_type.BIN.value),  #
            "speed_charge": hex_to_info(data[2:4], Encode_type.BIN.value),  #
            "gun_id": hex_to_info(data[4], Encode_type.BIN.value),  #
            "user_card_id": hex_to_info(data[5:37], Encode_type.ASCII.value),  #
            "user_card_balance": hex_to_info(data[37:41], Encode_type.BIN.value),  #
            "card_balance_is": hex_to_info(data[41], Encode_type.BIN.value),  #
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_103.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_103: {data}")
            HSyslog.log_info(f"tpp_cmd_103: {info}")

        return info
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_103 error: .{data} .{e}")
        return {}


def tpp_cmd_104(data: dict):  # 设备发送，平台接收
    device_id = data.get("device_id", Device_ID)
    gun_num = data.get("gun_num")
    gun_id = data.get("gun_id")
    gun_type = data.get("gun_type")
    charge_status = data.get("charge_status")
    soc_now = data.get("soc_now")
    fault_code = data.get("fault_code")
    car_connection_status = data.get("car_connection_status")
    charge_cost = data.get("charge_cost")
    dc_charge_vol = data.get("dc_charge_vol")
    dc_charge_cur = data.get("dc_charge_cur")
    bms_need_vol = data.get("bms_need_vol")
    bms_need_cur = data.get("bms_need_cur")
    bms_charge_mode = data.get("bms_charge_mode")
    ac_a_vol = data.get("ac_a_vol")
    ac_b_vol = data.get("ac_b_vol")
    ac_c_vol = data.get("ac_c_vol")
    ac_a_cur = data.get("ac_a_cur")
    ac_b_cur = data.get("ac_b_cur")
    ac_c_cur = data.get("ac_c_cur")
    charge_full_time = data.get("charge_full_time")
    charge_time = data.get("charge_time")
    charge_kw_amount = data.get("charge_kw_amount")
    start_meter = data.get("start_meter")
    now_meter = data.get("now_meter")
    start_charge_type = data.get("start_charge_type")
    charge_policy = data.get("charge_policy")
    charge_policy_param = data.get("charge_policy_param")
    book_flag = data.get("book_flag")
    charge_id = data.get("charge_id")
    book_timeout = data.get("book_timeout")
    book_start_time = data.get("book_start_time")
    start_card_balance = data.get("start_card_balance")
    charge_mode = data.get("charge_mode")
    charge_power_kw = data.get("charge_power_kw")
    device_temperature = data.get("device_temperature")
    reserved = data.get("reserved", 0)

    try:
        tpp_cmd_104_msg = []
        tpp_cmd_104_msg += info_to_hex(reserved, 4, Encode_type.BIN.value)
        tpp_cmd_104_msg += info_to_hex(device_id, 32, Encode_type.ASCII.value)
        tpp_cmd_104_msg += info_to_hex(gun_num, 1, Encode_type.BIN.value)
        tpp_cmd_104_msg += info_to_hex(gun_id, 1, Encode_type.BIN.value)
        tpp_cmd_104_msg += info_to_hex(gun_type, 1, Encode_type.BIN.value)
        tpp_cmd_104_msg += info_to_hex(charge_status, 1, Encode_type.BIN.value)
        tpp_cmd_104_msg += info_to_hex(soc_now, 1, Encode_type.BIN.value)
        tpp_cmd_104_msg += info_to_hex(fault_code, 4, Encode_type.ASCII.value)
        tpp_cmd_104_msg += info_to_hex(car_connection_status, 1, Encode_type.BIN.value)
        tpp_cmd_104_msg += info_to_hex(charge_cost, 4, Encode_type.BIN.value)
        tpp_cmd_104_msg += info_to_hex(reserved, 8, Encode_type.BIN.value)
        tpp_cmd_104_msg += info_to_hex(dc_charge_vol, 2, Encode_type.BIN.value)
        tpp_cmd_104_msg += info_to_hex(dc_charge_cur, 2, Encode_type.BIN.value)
        tpp_cmd_104_msg += info_to_hex(bms_need_vol, 2, Encode_type.BIN.value)
        tpp_cmd_104_msg += info_to_hex(bms_need_cur, 2, Encode_type.BIN.value)
        tpp_cmd_104_msg += info_to_hex(bms_charge_mode, 1, Encode_type.BIN.value)
        tpp_cmd_104_msg += info_to_hex(ac_a_vol, 2, Encode_type.BIN.value)
        tpp_cmd_104_msg += info_to_hex(ac_b_vol, 2, Encode_type.BIN.value)
        tpp_cmd_104_msg += info_to_hex(ac_c_vol, 2, Encode_type.BIN.value)
        tpp_cmd_104_msg += info_to_hex(ac_a_cur, 2, Encode_type.BIN.value)
        tpp_cmd_104_msg += info_to_hex(ac_b_cur, 2, Encode_type.BIN.value)
        tpp_cmd_104_msg += info_to_hex(ac_c_cur, 2, Encode_type.BIN.value)
        tpp_cmd_104_msg += info_to_hex(charge_full_time, 2, Encode_type.BIN.value)
        tpp_cmd_104_msg += info_to_hex(charge_time, 4, Encode_type.BIN.value)
        tpp_cmd_104_msg += info_to_hex(charge_kw_amount, 4, Encode_type.BIN.value)
        tpp_cmd_104_msg += info_to_hex(start_meter, 8, Encode_type.BIN.value)
        tpp_cmd_104_msg += info_to_hex(now_meter, 8, Encode_type.BIN.value)
        tpp_cmd_104_msg += info_to_hex(start_charge_type, 1, Encode_type.BIN.value)
        tpp_cmd_104_msg += info_to_hex(charge_policy, 1, Encode_type.BIN.value)
        tpp_cmd_104_msg += info_to_hex(charge_policy_param, 4, Encode_type.BIN.value)
        tpp_cmd_104_msg += info_to_hex(book_flag, 1, Encode_type.BIN.value)
        tpp_cmd_104_msg += info_to_hex(charge_id, 32, Encode_type.ASCII.value)
        tpp_cmd_104_msg += info_to_hex(book_timeout, 1, Encode_type.BIN.value)
        tpp_cmd_104_msg += info_to_hex(book_start_time, 8, Encode_type.TIME.value)
        tpp_cmd_104_msg += info_to_hex(start_card_balance, 4, Encode_type.BIN.value)
        tpp_cmd_104_msg += info_to_hex(charge_mode, 4, Encode_type.BIN.value)
        tpp_cmd_104_msg += info_to_hex(charge_power_kw, 4, Encode_type.BIN.value)
        tpp_cmd_104_msg += info_to_hex(device_temperature, 4, Encode_type.BIN.value)
        tpp_cmd_104_msg += info_to_hex(reserved, 8, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_104: {data}")
            HSyslog.log_info(f"tpp_cmd_104: {tpp_cmd_104_msg}")

        return pack(tpp_cmd_104_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_104.value)
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_104 error: .{data} .{e}")
        return []


def tpp_cmd_105(data: list):  # 平台发送，设备接收
    try:
        info = {
            "reserved": hex_to_info(data[0:4], Encode_type.BIN.value),  #
            "system_time": hex_to_info(data[4:12], Encode_type.TIME.value),  #
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_105.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_105: {data}")
            HSyslog.log_info(f"tpp_cmd_105: {info}")

        return info
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_105 error: .{data} .{e}")
        return {}


def tpp_cmd_106(data: dict):  # 设备发送，平台接收
    device_power_model_num = data.get("device_power_model_num")  # 1
    device_power = data.get("device_power")  # 2
    device_id = data.get("device_id", Device_ID)
    offline_is = data.get("offline_is")
    device_version = data.get("device_version")
    device_type = data.get("device_type")
    device_start_nums = data.get("device_start_nums")
    report_mode = data.get("report_mode")
    sign_interval = data.get("sign_interval")
    TCU_flag = data.get("TCU_flag")
    gun_num = data.get("gun_num")
    heart_interval = data.get("heart_interval")
    heart_timeout_nums = data.get("heart_timeout_nums")
    charge_record_num = data.get("charge_record_num")
    system_time = data.get("system_time")
    device_charge_time = data.get("device_charge_time")
    device_start_time = data.get("device_start_time")
    sign_code = data.get("sign_code")
    mac_addr = data.get("mac_addr")
    ccu_version = data.get("ccu_version")

    try:
        tpp_cmd_106_msg = []
        tpp_cmd_106_msg += info_to_hex(device_power_model_num, 2, Encode_type.BIN.value)
        tpp_cmd_106_msg += info_to_hex(device_power, 2, Encode_type.BIN.value)
        tpp_cmd_106_msg += info_to_hex(device_id, 32, Encode_type.ASCII.value)
        tpp_cmd_106_msg += info_to_hex(offline_is, 1, Encode_type.BIN.value)
        tpp_cmd_106_msg += info_to_hex(device_version, 4, Encode_type.VERSION.value)
        tpp_cmd_106_msg += info_to_hex(device_type, 2, Encode_type.BIN.value)
        tpp_cmd_106_msg += info_to_hex(device_start_nums, 4, Encode_type.BIN.value)
        tpp_cmd_106_msg += info_to_hex(report_mode, 1, Encode_type.BIN.value)
        tpp_cmd_106_msg += info_to_hex(sign_interval, 2, Encode_type.BIN.value)
        tpp_cmd_106_msg += info_to_hex(TCU_flag, 1, Encode_type.BIN.value)
        tpp_cmd_106_msg += info_to_hex(gun_num, 1, Encode_type.BIN.value)
        tpp_cmd_106_msg += info_to_hex(heart_interval, 1, Encode_type.BIN.value)
        tpp_cmd_106_msg += info_to_hex(heart_timeout_nums, 1, Encode_type.BIN.value)
        tpp_cmd_106_msg += info_to_hex(charge_record_num, 4, Encode_type.BIN.value)
        tpp_cmd_106_msg += info_to_hex(system_time, 8, Encode_type.TIME.value)
        tpp_cmd_106_msg += info_to_hex(device_charge_time, 8, Encode_type.TIME.value)
        tpp_cmd_106_msg += info_to_hex(device_start_time, 8, Encode_type.TIME.value)
        tpp_cmd_106_msg += info_to_hex(sign_code, 8, Encode_type.ASCII.value)
        tpp_cmd_106_msg += info_to_hex(mac_addr, 32, Encode_type.MAC.value)
        tpp_cmd_106_msg += info_to_hex(ccu_version, 4, Encode_type.VERSION.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_106: {data}")
            HSyslog.log_info(f"tpp_cmd_106: {tpp_cmd_106_msg}")

        return pack(tpp_cmd_106_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_106.value)
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_106 error: .{data} .{e}")
        return {}


def tpp_cmd_113(data: list):  # 平台发送，设备接收
    try:
        info = {
            "reserved": hex_to_info(data[0:4], Encode_type.BIN.value),
            "server_ip": hex_to_info(data[4:132], Encode_type.ASCII.value),
            "server_port": hex_to_info(data[132:136], Encode_type.BIN.value),
        }

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_113: {data}")
            HSyslog.log_info(f"tpp_cmd_113: {info}")

        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_113.value, info])
        return info
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_113 error: .{data} .{e}")
        return {}


def tpp_cmd_114(data: dict):  # 设备发送，平台接收
    reserved = data.get("reserved", 0)
    device_id = data.get("device_id", Device_ID)

    try:
        tpp_cmd_114_msg = []
        tpp_cmd_114_msg += info_to_hex(reserved, 4, Encode_type.BIN.value)
        tpp_cmd_114_msg += info_to_hex(device_id, 32, Encode_type.ASCII.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_114: {data}")
            HSyslog.log_info(f"tpp_cmd_114: {tpp_cmd_114_msg}")

        return pack(tpp_cmd_114_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_114.value)
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_114 error: .{data} .{e}")
        return []


def tpp_cmd_301(data: list):  # 平台发送，设备接收
    try:
        info = {
            "reserved": hex_to_info(data[0:2], Encode_type.BIN.value),  #
            "gun_id": hex_to_info(data[2:4], Encode_type.BIN.value),  #
            "device_id": hex_to_info(data[4:36], Encode_type.ASCII.value),  #
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_301.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_301: {data}")
            HSyslog.log_info(f"tpp_cmd_301: {info}")

        return info
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_301 error: .{data} .{e}")
        return {}


def tpp_cmd_302(data: dict):  # 设备发送，平台接收
    reserved = data.get("reserved", 0)
    gun_id = data.get("gun_id")
    device_id = data.get("device_id", Device_ID)
    charge_status = data.get("charge_status")
    car_connection_status = data.get("car_connection_status")
    brm_bms_connect_version = data.get("brm_bms_connect_version")
    brm_battery_type = data.get("brm_battery_type")
    brm_battery_power = data.get("brm_battery_power")
    brm_battery_voltage = data.get("brm_battery_voltage")
    brm_battery_supplier = data.get("brm_battery_supplier")
    brm_battery_seq = data.get("brm_battery_seq")
    brm_battery_produce_year = data.get("brm_battery_produce_year")
    brm_battery_produce_month = data.get("brm_battery_produce_month")
    brm_battery_produce_day = data.get("brm_battery_produce_day")
    brm_battery_charge_count = data.get("brm_battery_charge_count")
    brm_battery_property_identification = data.get("brm_battery_property_identification")
    brm_vin = data.get("brm_vin")
    brm_BMS_version = data.get("brm_BMS_version")
    bcp_max_voltage = data.get("bcp_max_voltage")
    bcp_max_current = data.get("bcp_max_current")
    bcp_max_power = data.get("bcp_max_power")
    bcp_total_voltage = data.get("bcp_total_voltage")
    bcp_max_temperature = data.get("bcp_max_temperature")
    bcp_battery_soc = data.get("bcp_battery_soc")
    bcp_battery_soc_current_voltage = data.get("bcp_battery_soc_current_voltage")
    bro_BMS_isReady = data.get("bro_BMS_isReady")
    bcl_voltage_need = data.get("bcl_voltage_need")
    bcl_current_need = data.get("bcl_current_need")
    bcl_charge_mode = data.get("bcl_charge_mode")
    bcs_test_voltage = data.get("bcs_test_voltage")
    bcs_test_current = data.get("bcs_test_current")
    bcs_max_single_voltage = data.get("bcs_max_single_voltage")
    bcs_max_single_no = data.get("bcs_max_single_no")
    bcs_current_soc = data.get("bcs_current_soc")
    last_charge_time = data.get("last_charge_time")
    bsm_single_no = data.get("bsm_single_no")
    bsm_max_temperature = data.get("bsm_max_temperature")
    bsm_max_temperature_check_no = data.get("bsm_max_temperature_check_no")
    bsm_min_temperature = data.get("bsm_min_temperature")
    bsm_min_temperature_check_no = data.get("bsm_min_temperature_check_no")
    bsm_voltage_too_high_or_too_low = data.get("bsm_voltage_too_high_or_too_low")
    bsm_car_battery_soc_too_high_or_too_low = data.get("bsm_car_battery_soc_too_high_or_too_low")
    bsm_car_battery_charge_over_current = data.get("bsm_car_battery_charge_over_current")
    bsm_battery_temperature_too_high = data.get("bsm_battery_temperature_too_high")
    bsm_battery_insulation_state = data.get("bsm_battery_insulation_state")
    bsm_battery_connect_state = data.get("bsm_battery_connect_state")
    bsm_allow_charge = data.get("bsm_allow_charge")
    bst_BMS_soc_target = data.get("bst_BMS_soc_target")
    bst_BMS_voltage_target = data.get("bst_BMS_voltage_target")
    bst_single_voltage_target = data.get("bst_single_voltage_target")
    bst_finish = data.get("bst_finish")
    bst_isolation_error = data.get("bst_isolation_error")
    bst_connect_over_temperature = data.get("bst_connect_over_temperature")
    bst_BMS_over_temperature = data.get("bst_BMS_over_temperature")
    bst_connect_error = data.get("bst_connect_error")
    bst_battery_over_temperature = data.get("bst_battery_over_temperature")
    bst_high_voltage_relay_error = data.get("bst_high_voltage_relay_error")
    bst_point2_test_error = data.get("bst_point2_test_error")
    bst_other_error = data.get("bst_other_error")
    bst_current_too_high = data.get("bst_current_too_high")
    bst_voltage_too_high = data.get("bst_voltage_too_high")
    bst_stop_soc = data.get("bst_stop_soc")
    bsd_battery_low_voltage = data.get("bsd_battery_low_voltage")
    bsd_battery_high_voltage = data.get("bsd_battery_high_voltage")
    bsd_battery_low_temperature = data.get("bsd_battery_low_temperature")
    bsd_battery_high_temperature = data.get("bsd_battery_high_temperature")
    bem_2560_00 = data.get("bem_2560_00")
    bem_2560_AA = data.get("bem_2560_AA")
    bem_sync_max_output_timeout = data.get("bem_sync_max_output_timeout")
    bem_prep_complete_timeout = data.get("bem_prep_complete_timeout")
    bem_status_timeout = data.get("bem_status_timeout")
    bem_stop_charge_timeout = data.get("bem_stop_charge_timeout")
    bem_stats_timeout = data.get("bem_stats_timeout")
    bem_other = data.get("bem_other")

    try:
        tpp_cmd_302_msg = []
        tpp_cmd_302_msg += info_to_hex(reserved, 2, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(gun_id, 2, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(device_id, 32, Encode_type.ASCII.value)
        tpp_cmd_302_msg += info_to_hex(charge_status, 1, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(car_connection_status, 1, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(brm_bms_connect_version, 3, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(brm_battery_type, 1, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(brm_battery_power, 4, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(brm_battery_voltage, 4, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(brm_battery_supplier, 4, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(brm_battery_seq, 4, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(brm_battery_produce_year, 2, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(brm_battery_produce_month, 1, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(brm_battery_produce_day, 1, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(brm_battery_charge_count, 4, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(brm_battery_property_identification, 1, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(reserved, 1, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(brm_vin, 17, Encode_type.ASCII.value)
        tpp_cmd_302_msg += info_to_hex(brm_BMS_version, 8, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bcp_max_voltage, 4, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bcp_max_current, 4, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bcp_max_power, 4, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bcp_total_voltage, 4, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bcp_max_temperature, 1, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bcp_battery_soc, 2, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bcp_battery_soc_current_voltage, 4, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bro_BMS_isReady, 1, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bcl_voltage_need, 4, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bcl_current_need, 4, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bcl_charge_mode, 1, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bcs_test_voltage, 4, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bcs_test_current, 4, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bcs_max_single_voltage, 4, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bcs_max_single_no, 1, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bcs_current_soc, 2, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(last_charge_time, 4, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bsm_single_no, 1, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bsm_max_temperature, 1, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bsm_max_temperature_check_no, 1, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bsm_min_temperature, 1, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bsm_min_temperature_check_no, 1, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bsm_voltage_too_high_or_too_low, 1, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bsm_car_battery_soc_too_high_or_too_low, 1, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bsm_car_battery_charge_over_current, 1, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bsm_battery_temperature_too_high, 1, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bsm_battery_insulation_state, 1, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bsm_battery_connect_state, 1, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bsm_allow_charge, 1, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bst_BMS_soc_target, 1, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bst_BMS_voltage_target, 1, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bst_single_voltage_target, 1, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bst_finish, 1, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bst_isolation_error, 1, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bst_connect_over_temperature, 1, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bst_BMS_over_temperature, 1, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bst_connect_error, 1, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bst_battery_over_temperature, 1, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bst_high_voltage_relay_error, 1, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bst_point2_test_error, 1, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bst_other_error, 1, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bst_current_too_high, 1, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bst_voltage_too_high, 1, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bst_stop_soc, 2, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bsd_battery_low_voltage, 4, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bsd_battery_high_voltage, 4, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bsd_battery_low_temperature, 1, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bsd_battery_high_temperature, 1, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bem_2560_00, 1, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bem_2560_AA, 1, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bem_sync_max_output_timeout, 1, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bem_prep_complete_timeout, 1, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bem_status_timeout, 1, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bem_stop_charge_timeout, 1, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bem_stats_timeout, 1, Encode_type.BIN.value)
        tpp_cmd_302_msg += info_to_hex(bem_other, 1, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_302: {data}")
            HSyslog.log_info(f"tpp_cmd_302: {tpp_cmd_302_msg}")

        return pack(tpp_cmd_302_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_302.value)
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_302 error: .{data} .{e}")
        return []


def tpp_cmd_303(data: list):  # 平台发送，设备接收
    try:
        info = {
            "reserved": hex_to_info(data[0:2], Encode_type.BIN.value),  #
            "gun_id": hex_to_info(data[2:4], Encode_type.BIN.value),  #
            "device_id": hex_to_info(data[4:36], Encode_type.ASCII.value),  #
            "charge_id": hex_to_info(data[36:68], Encode_type.ASCII.value),  #
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_303.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_303: {data}")
            HSyslog.log_info(f"tpp_cmd_303: {info}")

        return info
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_303 error: .{data} .{e}")
        return {}


def tpp_cmd_304(data: dict):  # 设备发送，平台接收
    reserved = data.get("reserved", 0)
    gun_id = data.get("gun_id")
    device_id = data.get("device_id", Device_ID)
    charge_id = data.get("charge_id")
    charge_status = data.get("charge_status")
    brm_bms_connect_version = data.get("brm_bms_connect_version")
    brm_battery_type = data.get("brm_battery_type")
    brm_battery_power = data.get("brm_battery_power")
    brm_battery_voltage = data.get("brm_battery_voltage")
    brm_battery_supplier = data.get("brm_battery_supplier")
    brm_battery_seq = data.get("brm_battery_seq")
    brm_battery_produce_year = data.get("brm_battery_produce_year")
    brm_battery_produce_month = data.get("brm_battery_produce_month")
    brm_battery_produce_day = data.get("brm_battery_produce_day")
    brm_battery_charge_count = data.get("brm_battery_charge_count")
    brm_battery_property_identification = data.get("brm_battery_property_identification")
    brm_vin = data.get("brm_vin")
    brm_BMS_version = data.get("brm_BMS_version")
    bcp_max_voltage = data.get("bcp_max_voltage")
    bcp_max_current = data.get("bcp_max_current")
    bcp_max_power = data.get("bcp_max_power")
    bcp_total_voltage = data.get("bcp_total_voltage")
    bcp_max_temperature = data.get("bcp_max_temperature")
    bcp_battery_soc = data.get("bcp_battery_soc")
    bcp_battery_soc_current_voltage = data.get("bcp_battery_soc_current_voltage")
    bro_BMS_isReady = data.get("bro_BMS_isReady")
    cro_cevice_isReady = data.get("cro_cevice_isReady")

    try:
        tpp_cmd_304_msg = []
        tpp_cmd_304_msg += info_to_hex(gun_id, 2, Encode_type.BIN.value)
        tpp_cmd_304_msg += info_to_hex(device_id, 32, Encode_type.ASCII.value)
        tpp_cmd_304_msg += info_to_hex(charge_id, 32, Encode_type.ASCII.value)
        tpp_cmd_304_msg += info_to_hex(charge_status, 1, Encode_type.BIN.value)
        tpp_cmd_304_msg += info_to_hex(brm_bms_connect_version, 3, Encode_type.BIN.value)
        tpp_cmd_304_msg += info_to_hex(brm_battery_type, 1, Encode_type.BIN.value)
        tpp_cmd_304_msg += info_to_hex(brm_battery_power, 4, Encode_type.BIN.value)
        tpp_cmd_304_msg += info_to_hex(brm_battery_voltage, 4, Encode_type.BIN.value)
        tpp_cmd_304_msg += info_to_hex(brm_battery_supplier, 4, Encode_type.ASCII.value)
        tpp_cmd_304_msg += info_to_hex(brm_battery_seq, 4, Encode_type.BIN.value)
        tpp_cmd_304_msg += info_to_hex(brm_battery_produce_year, 2, Encode_type.BIN.value)
        tpp_cmd_304_msg += info_to_hex(brm_battery_produce_month, 1, Encode_type.BIN.value)
        tpp_cmd_304_msg += info_to_hex(brm_battery_produce_day, 1, Encode_type.BIN.value)
        tpp_cmd_304_msg += info_to_hex(brm_battery_charge_count, 4, Encode_type.BIN.value)
        tpp_cmd_304_msg += info_to_hex(brm_battery_property_identification, 1, Encode_type.BIN.value)
        tpp_cmd_304_msg += info_to_hex(reserved, 1, Encode_type.BIN.value)
        tpp_cmd_304_msg += info_to_hex(brm_vin, 17, Encode_type.ASCII.value)
        tpp_cmd_304_msg += info_to_hex(brm_BMS_version, 8, Encode_type.BIN.value)
        tpp_cmd_304_msg += info_to_hex(bcp_max_voltage, 4, Encode_type.BIN.value)
        tpp_cmd_304_msg += info_to_hex(bcp_max_current, 4, Encode_type.BIN.value)
        tpp_cmd_304_msg += info_to_hex(bcp_max_power, 4, Encode_type.BIN.value)
        tpp_cmd_304_msg += info_to_hex(bcp_total_voltage, 4, Encode_type.BIN.value)
        tpp_cmd_304_msg += info_to_hex(bcp_max_temperature, 1, Encode_type.BIN.value)
        tpp_cmd_304_msg += info_to_hex(bcp_battery_soc, 2, Encode_type.BIN.value)
        tpp_cmd_304_msg += info_to_hex(bcp_battery_soc_current_voltage, 4, Encode_type.BIN.value)
        tpp_cmd_304_msg += info_to_hex(bro_BMS_isReady, 1, Encode_type.BIN.value)
        tpp_cmd_304_msg += info_to_hex(cro_cevice_isReady, 1, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_304: {data}")
            HSyslog.log_info(f"tpp_cmd_304: {tpp_cmd_304_msg}")

        return pack(tpp_cmd_304_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_304.value)
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_304 error: .{data} .{e}")
        return []


def tpp_cmd_305(data: list):  # 平台发送，设备接收
    try:
        info = {
            "reserved": hex_to_info(data[0:2], Encode_type.BIN.value),  #
            "gun_id": hex_to_info(data[2:4], Encode_type.BIN.value),  #
            "device_id": hex_to_info(data[4:36], Encode_type.ASCII.value),  #
            "charge_id": hex_to_info(data[36:68], Encode_type.ASCII.value),  #
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_307.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_305: {data}")
            HSyslog.log_info(f"tpp_cmd_305: {info}")

        return info
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_305 error: .{data} .{e}")
        return {}


def tpp_cmd_306(data: dict):  # 设备发送，平台接收
    reserved = data.get("reserved", 0)
    gun_id = data.get("gun_id")
    device_id = data.get("device_id", Device_ID)
    charge_id = data.get("charge_id")
    charge_status = data.get("charge_status")
    bcl_voltage_need = data.get("bcl_voltage_need")
    bcl_current_need = data.get("bcl_current_need")
    bcl_charge_mode = data.get("bcl_charge_mode")
    bcs_test_voltage = data.get("bcs_test_voltage")
    bcs_test_current = data.get("bcs_test_current")
    bcs_max_single_voltage = data.get("bcs_max_single_voltage")
    bcs_max_single_no = data.get("bcs_max_single_no")
    bcs_current_soc = data.get("bcs_current_soc")
    last_charge_time = data.get("last_charge_time")
    bsm_single_no = data.get("bsm_single_no")
    bsm_max_temperature = data.get("bsm_max_temperature")
    bsm_max_temperature_check_no = data.get("bsm_max_temperature_check_no")
    bsm_min_temperature = data.get("bsm_min_temperature")
    bsm_min_temperature_check_no = data.get("bsm_min_temperature_check_no")
    bsm_voltage_too_high_or_too_low = data.get("bsm_voltage_too_high_or_too_low")
    bsm_car_battery_soc_too_high_or_too_low = data.get("bsm_car_battery_soc_too_high_or_too_low")
    bsm_car_battery_charge_over_current = data.get("bsm_car_battery_charge_over_current")
    bsm_battery_temperature_too_high = data.get("bsm_battery_temperature_too_high")
    bsm_battery_insulation_state = data.get("bsm_battery_insulation_state")
    bsm_battery_connect_state = data.get("bsm_battery_connect_state")
    bsm_allow_charge = data.get("bsm_allow_charge")

    try:
        tpp_cmd_306_msg = []
        tpp_cmd_306_msg += info_to_hex(gun_id, 2, Encode_type.BIN.value)
        tpp_cmd_306_msg += info_to_hex(device_id, 32, Encode_type.ASCII.value)
        tpp_cmd_306_msg += info_to_hex(charge_id, 32, Encode_type.ASCII.value)
        tpp_cmd_306_msg += info_to_hex(charge_status, 1, Encode_type.BIN.value)
        tpp_cmd_306_msg += info_to_hex(bcl_voltage_need, 4, Encode_type.BIN.value)
        tpp_cmd_306_msg += info_to_hex(bcl_current_need, 4, Encode_type.BIN.value)
        tpp_cmd_306_msg += info_to_hex(bcl_charge_mode, 1, Encode_type.BIN.value)
        tpp_cmd_306_msg += info_to_hex(bcs_test_voltage, 4, Encode_type.BIN.value)
        tpp_cmd_306_msg += info_to_hex(bcs_test_current, 4, Encode_type.BIN.value)
        tpp_cmd_306_msg += info_to_hex(bcs_max_single_voltage, 4, Encode_type.BIN.value)
        tpp_cmd_306_msg += info_to_hex(bcs_max_single_no, 1, Encode_type.BIN.value)
        tpp_cmd_306_msg += info_to_hex(bcs_current_soc, 2, Encode_type.BIN.value)
        tpp_cmd_306_msg += info_to_hex(last_charge_time, 4, Encode_type.BIN.value)
        tpp_cmd_306_msg += info_to_hex(bsm_single_no, 1, Encode_type.BIN.value)
        tpp_cmd_306_msg += info_to_hex(bsm_max_temperature, 1, Encode_type.BIN.value)
        tpp_cmd_306_msg += info_to_hex(bsm_max_temperature_check_no, 1, Encode_type.BIN.value)
        tpp_cmd_306_msg += info_to_hex(bsm_min_temperature, 1, Encode_type.BIN.value)
        tpp_cmd_306_msg += info_to_hex(bsm_min_temperature_check_no, 1, Encode_type.BIN.value)
        tpp_cmd_306_msg += info_to_hex(bsm_voltage_too_high_or_too_low, 1, Encode_type.BIN.value)
        tpp_cmd_306_msg += info_to_hex(bsm_car_battery_soc_too_high_or_too_low, 1, Encode_type.BIN.value)
        tpp_cmd_306_msg += info_to_hex(bsm_car_battery_charge_over_current, 1, Encode_type.BIN.value)
        tpp_cmd_306_msg += info_to_hex(bsm_battery_temperature_too_high, 1, Encode_type.BIN.value)
        tpp_cmd_306_msg += info_to_hex(bsm_battery_insulation_state, 1, Encode_type.BIN.value)
        tpp_cmd_306_msg += info_to_hex(bsm_battery_connect_state, 1, Encode_type.BIN.value)
        tpp_cmd_306_msg += info_to_hex(bsm_allow_charge, 1, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_306: {data}")
            HSyslog.log_info(f"tpp_cmd_306: {tpp_cmd_306_msg}")

        return pack(tpp_cmd_306_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_306.value)
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_306 error: .{data} .{e}")
        return []


def tpp_cmd_307(data: list):  # 平台发送，设备接收
    try:
        info = {
            "reserved": hex_to_info(data[0:2], Encode_type.BIN.value),  #
            "gun_id": hex_to_info(data[2:4], Encode_type.BIN.value),  #
            "device_id": hex_to_info(data[4:36], Encode_type.ASCII.value),  #
            "charge_id": hex_to_info(data[36:68], Encode_type.ASCII.value),  #
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_307.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_307: {data}")
            HSyslog.log_info(f"tpp_cmd_307: {info}")

        return info
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_307 error: .{data} .{e}")
        return {}


def tpp_cmd_308(data: dict):  # 设备发送，平台接收
    reserved = data.get("reserved", 0)
    gun_id = data.get("gun_id")
    device_id = data.get("device_id", Device_ID)
    charge_id = data.get("charge_id")
    charge_status = data.get("charge_status")
    cst_stop_reason = data.get("cst_stop_reason")
    cst_fault_reason = data.get("cst_fault_reason")
    cst_error_reason = data.get("cst_error_reason")

    try:
        tpp_cmd_308_msg = []
        tpp_cmd_308_msg += info_to_hex(gun_id, 2, Encode_type.BIN.value)
        tpp_cmd_308_msg += info_to_hex(device_id, 32, Encode_type.ASCII.value)
        tpp_cmd_308_msg += info_to_hex(charge_id, 32, Encode_type.ASCII.value)
        tpp_cmd_308_msg += info_to_hex(charge_status, 1, Encode_type.BIN.value)
        tpp_cmd_308_msg += info_to_hex(cst_stop_reason, 1, Encode_type.BIN.value)
        tpp_cmd_308_msg += info_to_hex(cst_fault_reason, 2, Encode_type.BIN.value)
        tpp_cmd_308_msg += info_to_hex(cst_error_reason, 1, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_308: {data}")
            HSyslog.log_info(f"tpp_cmd_308: {tpp_cmd_308_msg}")

        return pack(tpp_cmd_308_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_308.value)
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_308 error: .{data} .{e}")
        return []


def tpp_cmd_309(data: list):  # 平台发送，设备接收
    try:
        info = {
            "reserved": hex_to_info(data[0:2], Encode_type.BIN.value),  #
            "gun_id": hex_to_info(data[2:4], Encode_type.BIN.value),  #
            "device_id": hex_to_info(data[4:36], Encode_type.ASCII.value),  #
            "charge_id": hex_to_info(data[36:68], Encode_type.ASCII.value),  #
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_309.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_309: {data}")
            HSyslog.log_info(f"tpp_cmd_309: {info}")

        return info
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_309 error: .{data} .{e}")
        return {}


def tpp_cmd_310(data: dict):  # 设备发送，平台接收
    reserved = data.get("reserved", 0)
    gun_id = data.get("gun_id")
    device_id = data.get("device_id", Device_ID)
    charge_id = data.get("charge_id")
    charge_status = data.get("charge_status")
    bst_stop_reason = data.get("bst_stop_reason")
    bst_fault_reason = data.get("bst_fault_reason")
    bst_error_reason = data.get("bst_error_reason")

    try:
        tpp_cmd_310_msg = []
        tpp_cmd_310_msg += info_to_hex(gun_id, 2, Encode_type.BIN.value)
        tpp_cmd_310_msg += info_to_hex(device_id, 32, Encode_type.ASCII.value)
        tpp_cmd_310_msg += info_to_hex(charge_id, 32, Encode_type.ASCII.value)
        tpp_cmd_310_msg += info_to_hex(charge_status, 1, Encode_type.BIN.value)
        tpp_cmd_310_msg += info_to_hex(bst_stop_reason, 1, Encode_type.BIN.value)
        tpp_cmd_310_msg += info_to_hex(bst_fault_reason, 2, Encode_type.BIN.value)
        tpp_cmd_310_msg += info_to_hex(bst_error_reason, 1, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_310: {data}")
            HSyslog.log_info(f"tpp_cmd_310: {tpp_cmd_310_msg}")

        return pack(tpp_cmd_310_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_310.value)
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_310 error: .{data} .{e}")
        return []


def tpp_cmd_311(data: list):  # 平台发送，设备接收
    try:
        info = {
            "reserved": hex_to_info(data[0:2], Encode_type.BIN.value),  #
            "gun_id": hex_to_info(data[2:4], Encode_type.BIN.value),  #
            "device_id": hex_to_info(data[4:36], Encode_type.ASCII.value),  #
            "charge_id": hex_to_info(data[36:68], Encode_type.ASCII.value),  #
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_311.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_311: {data}")
            HSyslog.log_info(f"tpp_cmd_311: {info}")

        return info
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_311 error: .{data} .{e}")
        return {}


def tpp_cmd_312(data: dict):  # 设备发送，平台接收
    reserved = data.get("reserved", 0)
    gun_id = data.get("gun_id")
    device_id = data.get("device_id", Device_ID)
    charge_id = data.get("charge_id")
    charge_status = data.get("charge_status")
    bst_stop_soc = data.get("bst_stop_soc")
    bsd_battery_low_voltage = data.get("bsd_battery_low_voltage")
    bsd_battery_high_voltage = data.get("bsd_battery_high_voltage")
    bsd_battery_low_temperature = data.get("bsd_battery_low_temperature")
    bsd_battery_high_temperature = data.get("bsd_battery_high_temperature")
    bem_2560_00 = data.get("bem_2560_00")
    bem_2560_AA = data.get("bem_2560_AA")
    bem_sync_max_output_timeout = data.get("bem_sync_max_output_timeout")
    bem_prep_complete_timeout = data.get("bem_prep_complete_timeout")
    bem_status_timeout = data.get("bem_status_timeout")
    bem_stop_charge_timeout = data.get("bem_stop_charge_timeout")
    bem_stats_timeout = data.get("bem_stats_timeout")
    bem_other = data.get("bem_other")

    try:
        tpp_cmd_312_msg = []
        tpp_cmd_312_msg += info_to_hex(gun_id, 2, Encode_type.BIN.value)
        tpp_cmd_312_msg += info_to_hex(device_id, 32, Encode_type.ASCII.value)
        tpp_cmd_312_msg += info_to_hex(charge_id, 32, Encode_type.ASCII.value)
        tpp_cmd_312_msg += info_to_hex(charge_status, 1, Encode_type.BIN.value)
        tpp_cmd_312_msg += info_to_hex(bst_stop_soc, 1, Encode_type.BIN.value)
        tpp_cmd_312_msg += info_to_hex(bsd_battery_low_voltage, 2, Encode_type.BIN.value)
        tpp_cmd_312_msg += info_to_hex(bsd_battery_high_voltage, 2, Encode_type.BIN.value)
        tpp_cmd_312_msg += info_to_hex(bsd_battery_low_temperature, 1, Encode_type.BIN.value)
        tpp_cmd_312_msg += info_to_hex(bsd_battery_high_temperature, 1, Encode_type.BIN.value)
        tpp_cmd_312_msg += info_to_hex(bem_2560_00, 1, Encode_type.BIN.value)
        tpp_cmd_312_msg += info_to_hex(bem_2560_AA, 1, Encode_type.BIN.value)
        tpp_cmd_312_msg += info_to_hex(bem_sync_max_output_timeout, 1, Encode_type.BIN.value)
        tpp_cmd_312_msg += info_to_hex(bem_prep_complete_timeout, 1, Encode_type.BIN.value)
        tpp_cmd_312_msg += info_to_hex(bem_status_timeout, 1, Encode_type.BIN.value)
        tpp_cmd_312_msg += info_to_hex(bem_stop_charge_timeout, 1, Encode_type.BIN.value)
        tpp_cmd_312_msg += info_to_hex(bem_stats_timeout, 1, Encode_type.BIN.value)
        tpp_cmd_312_msg += info_to_hex(bem_other, 1, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_312: {data}")
            HSyslog.log_info(f"tpp_cmd_312: {tpp_cmd_312_msg}")

        return pack(tpp_cmd_312_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_312.value)
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_312 error: .{data} .{e}")
        return []


def tpp_cmd_201(data: list):  # 平台发送，设备接收
    try:
        info = {
            "reserved": hex_to_info(data[0:4], Encode_type.BIN.value),  #
            "gun_id": hex_to_info(data[4], Encode_type.BIN.value),  #
            "user_card_id": hex_to_info(data[5:37], Encode_type.ASCII.value),  #
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_201.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_201: {data}")
            HSyslog.log_info(f"tpp_cmd_201: {info}")

        return info
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_201 error: .{data} .{e}")
        return {}


def tpp_cmd_202(data: dict):  # 设备发送，平台接收
    reserved = data.get("reserved", 0)
    device_id = data.get("device_id", Device_ID)
    gun_type = data.get("gun_type")
    gun_id = data.get("gun_id")
    charge_id = data.get("charge_id")
    charge_start_time = data.get("charge_start_time")
    charge_stop_time = data.get("charge_stop_time")
    charge_time = data.get("charge_time")
    charge_start_soc = data.get("charge_start_soc")
    charge_stop_soc = data.get("charge_stop_soc")
    charge_stop_reason = data.get("charge_stop_reason")
    charge_kwh_amount = data.get("charge_kwh_amount")
    charge_start_meter = data.get("charge_start_meter")
    charge_stop_meter = data.get("charge_stop_meter")
    charge_cost = data.get("charge_cost")
    charge_card_stop_is = data.get("charge_card_stop_is")
    charge_start_balance = data.get("charge_start_balance")
    charge_stop_balance = data.get("charge_stop_balance")
    charge_server_cost = data.get("charge_server_cost")
    pay_offline_is = data.get("pay_offline_is")
    charge_policy = data.get("charge_policy")
    charge_policy_param = data.get("charge_policy_param")
    car_vin = data.get("car_vin")
    car_card = data.get("car_card")
    kwh_amount = data.get("kwh_amount")  # 半小时一段
    start_source = data.get("start_source")

    try:
        tpp_cmd_202_msg = []
        tpp_cmd_202_msg += info_to_hex(reserved, 4, Encode_type.BIN.value)
        tpp_cmd_202_msg += info_to_hex(device_id, 32, Encode_type.ASCII.value)
        tpp_cmd_202_msg += info_to_hex(gun_type, 1, Encode_type.BIN.value)
        tpp_cmd_202_msg += info_to_hex(gun_id, 1, Encode_type.BIN.value)
        tpp_cmd_202_msg += info_to_hex(charge_id, 32, Encode_type.ASCII.value)
        tpp_cmd_202_msg += info_to_hex(charge_start_time, 8, Encode_type.TIME.value)
        tpp_cmd_202_msg += info_to_hex(charge_stop_time, 8, Encode_type.TIME.value)
        tpp_cmd_202_msg += info_to_hex(charge_time, 4, Encode_type.BIN.value)
        tpp_cmd_202_msg += info_to_hex(charge_start_soc, 1, Encode_type.BIN.value)
        tpp_cmd_202_msg += info_to_hex(charge_stop_soc, 1, Encode_type.BIN.value)
        tpp_cmd_202_msg += info_to_hex(charge_stop_reason, 4, Encode_type.ASCII.value)
        tpp_cmd_202_msg += info_to_hex(charge_kwh_amount, 4, Encode_type.BIN.value)
        tpp_cmd_202_msg += info_to_hex(charge_start_meter, 8, Encode_type.BIN.value)
        tpp_cmd_202_msg += info_to_hex(charge_stop_meter, 8, Encode_type.BIN.value)
        tpp_cmd_202_msg += info_to_hex(charge_cost, 4, Encode_type.BIN.value)
        tpp_cmd_202_msg += info_to_hex(charge_card_stop_is, 4, Encode_type.BIN.value)
        tpp_cmd_202_msg += info_to_hex(charge_start_balance, 4, Encode_type.BIN.value)
        tpp_cmd_202_msg += info_to_hex(charge_stop_balance, 4, Encode_type.BIN.value)
        tpp_cmd_202_msg += info_to_hex(charge_server_cost, 4, Encode_type.BIN.value)
        tpp_cmd_202_msg += info_to_hex(pay_offline_is, 1, Encode_type.BIN.value)
        tpp_cmd_202_msg += info_to_hex(charge_policy, 1, Encode_type.BIN.value)
        tpp_cmd_202_msg += info_to_hex(charge_policy_param, 4, Encode_type.BIN.value)
        tpp_cmd_202_msg += info_to_hex(car_vin, 17, Encode_type.ASCII.value)
        tpp_cmd_202_msg += info_to_hex(car_card, 8, Encode_type.ASCII.value)
        for i in range(0, 48):
            tpp_cmd_202_msg += info_to_hex(kwh_amount[i], 4, Encode_type.BIN.value)
        tpp_cmd_202_msg += info_to_hex(start_source, 1, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_202: {data}")
            HSyslog.log_info(f"tpp_cmd_202: {tpp_cmd_202_msg}")

        return pack(tpp_cmd_202_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_202.value)
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_202 error: .{data} .{e}")
        return []


def tpp_cmd_205(data: list):  # 平台发送，设备接收
    try:
        info = {
            "reserved": hex_to_info(data[0:4], Encode_type.BIN.value),  #
            "gun_id": hex_to_info(data[4], Encode_type.BIN.value),  #
            "user_card_id": hex_to_info(data[5:37], Encode_type.ASCII.value),  #
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_205.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_205: {data}")
            HSyslog.log_info(f"tpp_cmd_205: {info}")

        return info
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_205 error: .{data} .{e}")
        return {}


def tpp_cmd_206(data: dict):  # 设备发送，平台接收
    reserved = data.get("reserved", 0)
    device_id = data.get("device_id", Device_ID)
    gun_type = data.get("gun_type")
    gun_id = data.get("gun_id")
    charge_id = data.get("charge_id")
    charge_start_time = data.get("charge_start_time")
    charge_stop_time = data.get("charge_stop_time")
    charge_time = data.get("charge_time")
    charge_start_soc = data.get("charge_start_soc")
    charge_stop_soc = data.get("charge_stop_soc")
    charge_stop_reason = data.get("charge_stop_reason")
    charge_kwh_amount = data.get("charge_kwh_amount")
    charge_start_meter = data.get("charge_start_meter")
    charge_stop_meter = data.get("charge_stop_meter")
    charge_cost = data.get("charge_cost")
    charge_card_stop_is = data.get("charge_card_stop_is")
    charge_start_balance = data.get("charge_start_balance")
    charge_stop_balance = data.get("charge_stop_balance")
    charge_server_cost = data.get("charge_server_cost")
    pay_offline_is = data.get("pay_offline_is")
    charge_policy = data.get("charge_policy")
    charge_policy_param = data.get("charge_policy_param")
    car_vin = data.get("car_vin")
    car_card = data.get("car_card")
    kwh_amount = data.get("kwh_amount")  # 半小时一段
    start_source = data.get("start_source")

    try:
        tpp_cmd_206_msg = []
        tpp_cmd_206_msg += info_to_hex(reserved, 4, Encode_type.BIN.value)
        tpp_cmd_206_msg += info_to_hex(device_id, 32, Encode_type.ASCII.value)
        tpp_cmd_206_msg += info_to_hex(gun_type, 1, Encode_type.BIN.value)
        tpp_cmd_206_msg += info_to_hex(gun_id, 1, Encode_type.BIN.value)
        tpp_cmd_206_msg += info_to_hex(charge_id, 32, Encode_type.ASCII.value)
        tpp_cmd_206_msg += info_to_hex(charge_start_time, 8, Encode_type.TIME.value)
        tpp_cmd_206_msg += info_to_hex(charge_stop_time, 8, Encode_type.TIME.value)
        tpp_cmd_206_msg += info_to_hex(charge_time, 4, Encode_type.BIN.value)
        tpp_cmd_206_msg += info_to_hex(charge_start_soc, 1, Encode_type.BIN.value)
        tpp_cmd_206_msg += info_to_hex(charge_stop_soc, 1, Encode_type.BIN.value)
        tpp_cmd_206_msg += info_to_hex(charge_stop_reason, 4, Encode_type.ASCII.value)
        tpp_cmd_206_msg += info_to_hex(charge_kwh_amount, 4, Encode_type.BIN.value)
        tpp_cmd_206_msg += info_to_hex(charge_start_meter, 8, Encode_type.BIN.value)
        tpp_cmd_206_msg += info_to_hex(charge_stop_meter, 8, Encode_type.BIN.value)
        tpp_cmd_206_msg += info_to_hex(charge_cost, 4, Encode_type.BIN.value)
        tpp_cmd_206_msg += info_to_hex(charge_card_stop_is, 4, Encode_type.BIN.value)
        tpp_cmd_206_msg += info_to_hex(charge_start_balance, 4, Encode_type.BIN.value)
        tpp_cmd_206_msg += info_to_hex(charge_stop_balance, 4, Encode_type.BIN.value)
        tpp_cmd_206_msg += info_to_hex(charge_server_cost, 4, Encode_type.BIN.value)
        tpp_cmd_206_msg += info_to_hex(pay_offline_is, 1, Encode_type.BIN.value)
        tpp_cmd_206_msg += info_to_hex(charge_policy, 1, Encode_type.BIN.value)
        tpp_cmd_206_msg += info_to_hex(charge_policy_param, 4, Encode_type.BIN.value)
        tpp_cmd_206_msg += info_to_hex(car_vin, 17, Encode_type.ASCII.value)
        tpp_cmd_206_msg += info_to_hex(car_card, 8, Encode_type.ASCII.value)
        for i in range(0, 48):
            tpp_cmd_206_msg += info_to_hex(kwh_amount[i], 4, Encode_type.BIN.value)
        tpp_cmd_206_msg += info_to_hex(start_source, 1, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_206: {data}")
            HSyslog.log_info(f"tpp_cmd_206: {tpp_cmd_206_msg}")

        return pack(tpp_cmd_206_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_202.value)
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_206 error: .{data} .{e}")
        return []


def tpp_cmd_401(data: list):  # 平台发送，设备接收
    try:
        info = {
            "reserved": hex_to_info(data[0:4], Encode_type.BIN.value),  #
            "charge_record_nums": hex_to_info(data[4:8], Encode_type.BIN.value),  #
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_401.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_401: {data}")
            HSyslog.log_info(f"tpp_cmd_401: {info}")

        return info
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_401 error: .{data} .{e}")
        return {}


def tpp_cmd_402(data: dict):  # 设备发送，平台接收
    reserved = data.get("reserved", 0)
    device_id = data.get("device_id", Device_ID)
    gun_type = data.get("gun_type")
    charge_record_nums = data.get("device_id", Device_ID)
    charge_record_num = data.get("gun_type")
    gun_id = data.get("gun_id")
    charge_id = data.get("charge_id")
    charge_start_time = data.get("charge_start_time")
    charge_stop_time = data.get("charge_stop_time")
    charge_time = data.get("charge_time")
    charge_start_soc = data.get("charge_start_soc")
    charge_stop_soc = data.get("charge_stop_soc")
    charge_stop_reason = data.get("charge_stop_reason")
    charge_kwh_amount = data.get("charge_kwh_amount")
    charge_start_meter = data.get("charge_start_meter")
    charge_stop_meter = data.get("charge_stop_meter")
    charge_cost = data.get("charge_cost")
    charge_card_stop_is = data.get("charge_card_stop_is")
    charge_start_balance = data.get("charge_start_balance")
    charge_stop_balance = data.get("charge_stop_balance")
    charge_server_cost = data.get("charge_server_cost")
    pay_offline_is = data.get("pay_offline_is")
    charge_policy = data.get("charge_policy")
    charge_policy_param = data.get("charge_policy_param")
    car_vin = data.get("car_vin")
    car_card = data.get("car_card")
    kwh_amount_1 = data.get("kwh_amount_1")  # 半小时一段
    kwh_amount_2 = data.get("kwh_amount_2")
    kwh_amount_3 = data.get("kwh_amount_3")
    kwh_amount_4 = data.get("kwh_amount_4")
    kwh_amount_5 = data.get("kwh_amount_5")
    kwh_amount_6 = data.get("kwh_amount_6")
    kwh_amount_7 = data.get("kwh_amount_7")
    kwh_amount_8 = data.get("kwh_amount_8")
    kwh_amount_9 = data.get("kwh_amount_9")
    kwh_amount_10 = data.get("kwh_amount_10")
    kwh_amount_11 = data.get("kwh_amount_11")
    kwh_amount_12 = data.get("kwh_amount_12")
    kwh_amount_13 = data.get("kwh_amount_13")
    kwh_amount_14 = data.get("kwh_amount_14")
    kwh_amount_15 = data.get("kwh_amount_15")
    kwh_amount_16 = data.get("kwh_amount_16")
    kwh_amount_17 = data.get("kwh_amount_17")
    kwh_amount_18 = data.get("kwh_amount_18")
    kwh_amount_19 = data.get("kwh_amount_19")
    kwh_amount_20 = data.get("kwh_amount_20")
    kwh_amount_21 = data.get("kwh_amount_21")
    kwh_amount_22 = data.get("kwh_amount_22")
    kwh_amount_23 = data.get("kwh_amount_23")
    kwh_amount_24 = data.get("kwh_amount_24")
    kwh_amount_25 = data.get("kwh_amount_25")
    kwh_amount_26 = data.get("kwh_amount_26")
    kwh_amount_27 = data.get("kwh_amount_27")
    kwh_amount_28 = data.get("kwh_amount_28")
    kwh_amount_29 = data.get("kwh_amount_29")
    kwh_amount_30 = data.get("kwh_amount_30")
    kwh_amount_31 = data.get("kwh_amount_31")
    kwh_amount_32 = data.get("kwh_amount_32")
    kwh_amount_33 = data.get("kwh_amount_33")
    kwh_amount_34 = data.get("kwh_amount_34")
    kwh_amount_35 = data.get("kwh_amount_35")
    kwh_amount_36 = data.get("kwh_amount_36")
    kwh_amount_37 = data.get("kwh_amount_37")
    kwh_amount_38 = data.get("kwh_amount_38")
    kwh_amount_39 = data.get("kwh_amount_39")
    kwh_amount_40 = data.get("kwh_amount_40")
    kwh_amount_41 = data.get("kwh_amount_41")
    kwh_amount_42 = data.get("kwh_amount_42")
    kwh_amount_43 = data.get("kwh_amount_43")
    kwh_amount_44 = data.get("kwh_amount_44")
    kwh_amount_45 = data.get("kwh_amount_45")
    kwh_amount_46 = data.get("kwh_amount_46")
    kwh_amount_47 = data.get("kwh_amount_47")
    kwh_amount_48 = data.get("kwh_amount_48")
    start_source = data.get("start_source")

    try:
        tpp_cmd_402_msg = []
        tpp_cmd_402_msg += info_to_hex(reserved, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(device_id, 32, Encode_type.ASCII.value)
        tpp_cmd_402_msg += info_to_hex(charge_record_nums, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(charge_record_num, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(gun_type, 1, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(gun_id, 1, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(charge_id, 32, Encode_type.ASCII.value)
        tpp_cmd_402_msg += info_to_hex(charge_start_time, 8, Encode_type.TIME.value)
        tpp_cmd_402_msg += info_to_hex(charge_stop_time, 8, Encode_type.TIME.value)
        tpp_cmd_402_msg += info_to_hex(charge_time, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(charge_start_soc, 1, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(charge_stop_soc, 1, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(charge_stop_reason, 4, Encode_type.ASCII.value)
        tpp_cmd_402_msg += info_to_hex(charge_kwh_amount, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(charge_start_meter, 8, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(charge_stop_meter, 8, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(charge_cost, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(charge_card_stop_is, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(charge_start_balance, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(charge_stop_balance, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(charge_server_cost, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(pay_offline_is, 1, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(charge_policy, 1, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(charge_policy_param, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(car_vin, 17, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(car_card, 8, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(kwh_amount_1, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(kwh_amount_2, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(kwh_amount_3, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(kwh_amount_4, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(kwh_amount_5, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(kwh_amount_6, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(kwh_amount_7, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(kwh_amount_8, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(kwh_amount_9, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(kwh_amount_10, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(kwh_amount_11, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(kwh_amount_12, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(kwh_amount_13, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(kwh_amount_14, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(kwh_amount_15, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(kwh_amount_16, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(kwh_amount_17, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(kwh_amount_18, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(kwh_amount_19, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(kwh_amount_20, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(kwh_amount_21, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(kwh_amount_22, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(kwh_amount_23, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(kwh_amount_24, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(kwh_amount_25, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(kwh_amount_26, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(kwh_amount_27, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(kwh_amount_28, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(kwh_amount_29, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(kwh_amount_30, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(kwh_amount_31, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(kwh_amount_32, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(kwh_amount_33, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(kwh_amount_34, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(kwh_amount_35, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(kwh_amount_36, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(kwh_amount_37, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(kwh_amount_38, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(kwh_amount_39, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(kwh_amount_40, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(kwh_amount_41, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(kwh_amount_42, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(kwh_amount_43, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(kwh_amount_44, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(kwh_amount_45, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(kwh_amount_46, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(kwh_amount_47, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(kwh_amount_48, 4, Encode_type.BIN.value)
        tpp_cmd_402_msg += info_to_hex(start_source, 1, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_402: {data}")
            HSyslog.log_info(f"tpp_cmd_402: {tpp_cmd_402_msg}")

        return pack(tpp_cmd_402_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_402.value)
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_402 error: .{data} .{e}")
        return []


def tpp_cmd_23(data: list):  # 平台发送，设备接收
    try:
        info = {
            "reserved": hex_to_info(data[0:4], Encode_type.BIN.value),
            "device_id": hex_to_info(data[4:32], Encode_type.ASCII.value),
            "gun_id": hex_to_info(data[32], Encode_type.BIN.value),
            "lock_ctrl": hex_to_info(data[33], Encode_type.BIN.value),
        }

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_23: {data}")
            HSyslog.log_info(f"tpp_cmd_23: {info}")

        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_23.value, info])
        return info
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_23 error: .{data} .{e}")
        return {}


def tpp_cmd_24(data: dict):  # 设备发送，平台接收
    reserved = data.get("reserved", 0)
    gun_id = data.get("gun_id")
    device_id = data.get("device_id", Device_ID)
    result = data.get("result")

    try:
        tpp_cmd_24_msg = []
        tpp_cmd_24_msg += info_to_hex(reserved, 4, Encode_type.BIN.value)
        tpp_cmd_24_msg += info_to_hex(device_id, 32, Encode_type.ASCII.value)
        tpp_cmd_24_msg += info_to_hex(gun_id, 1, Encode_type.BIN.value)
        tpp_cmd_24_msg += info_to_hex(result, 1, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_24: {data}")
            HSyslog.log_info(f"tpp_cmd_24: {tpp_cmd_24_msg}")

        return pack(tpp_cmd_24_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_24.value)
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_24 error: .{data} .{e}")
        return []


def tpp_cmd_1303(data: list):  # 平台发送，设备接收
    try:
        fee_model_list = []
        fee_model = data[1:]
        for i in range(0, len(fee_model), 4):
            fee_model_list.append(hex_to_info(fee_model[i: i + 4], Encode_type.BIN.value))
        info = {
            "fee_model_type": hex_to_info(data[0], Encode_type.BIN.value),
            "fee_model": fee_model_list,
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_1303.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_1303: {data}")
            HSyslog.log_info(f"tpp_cmd_1303: {info}")

        return info
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_1303 error: .{data} .{e}")
        return {}


def tpp_cmd_1304(data: dict):  # 设备发送，平台接收
    fee_model = data.get("fee_model")
    try:
        tpp_cmd_1304_msg = []
        for fee_num in range(0, len(fee_model)):
            tpp_cmd_1304_msg += info_to_hex(fee_model.get(fee_num), 4, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_1304: {data}")
            HSyslog.log_info(f"tpp_cmd_1304: {tpp_cmd_1304_msg}")

        return pack(tpp_cmd_1304_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_1304.value)
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_1304 error: .{data} .{e}")
        return []


def tpp_cmd_1305(data: list):  # 平台发送，设备接收
    try:
        fee_model_list = []
        fee_model = data[2:]
        for i in range(0, len(fee_model), 4):
            fee_model_list.append(hex_to_info(fee_model[i: i + 4], Encode_type.BIN.value))
        info = {
            "fee_model_type": hex_to_info(data[0], Encode_type.BIN.value),
            "gun_id": hex_to_info(data[1], Encode_type.BIN.value),
            "fee_model": fee_model_list,
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_1305.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_1305: {data}")
            HSyslog.log_info(f"tpp_cmd_1305: {info}")

        return info
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_1305 error: .{data} .{e}")
        return {}


def tpp_cmd_1306(data: dict):  # 设备发送，平台接收
    fee_model_type = data.get("fee_model_type")
    fee_model = data.get("fee_model")
    gun_id = data.get("gun_id")
    try:
        tpp_cmd_1306_msg = []
        tpp_cmd_1306_msg += info_to_hex(fee_model_type, 1, Encode_type.BIN.value)
        tpp_cmd_1306_msg += info_to_hex(gun_id, 1, Encode_type.BIN.value)
        for fee_num in range(0, len(fee_model)):
            tpp_cmd_1306_msg += info_to_hex(fee_model.get(fee_num), 4, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_1306: {data}")
            HSyslog.log_info(f"tpp_cmd_1306: {tpp_cmd_1306_msg}")

        return pack(tpp_cmd_1306_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_1306.value)
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_1306 error: .{data} .{e}")
        return []


def tpp_cmd_1307(data: list):  # 平台发送，设备接收
    try:
        fee_model_list = []
        fee_model = data[33:]
        for i in range(0, len(fee_model), 4):
            fee_model_list.append(hex_to_info(fee_model[i: i + 4], Encode_type.BIN.value))
        info = {
            "fee_model_type": hex_to_info(data[0], Encode_type.BIN.value),
            "device_id": hex_to_info(data[1:33], Encode_type.ASCII.value),
            "fee_model": fee_model_list,
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_1307.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_1307: {data}")
            HSyslog.log_info(f"tpp_cmd_1307: {info}")

        return info
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_1307 error: .{data} .{e}")
        return {}


def tpp_cmd_1308(data: dict):  # 设备发送，平台接收
    fee_model = data.get("fee_model")
    fee_model_type = data.get("fee_model_type")
    device_id = data.get("device_id", Device_ID)
    try:
        tpp_cmd_1308_msg = []
        tpp_cmd_1308_msg += info_to_hex(fee_model_type, 1, Encode_type.BIN.value)
        tpp_cmd_1308_msg += info_to_hex(device_id, 32, Encode_type.ASCII.value)
        for fee_num in range(0, len(fee_model)):
            tpp_cmd_1308_msg += info_to_hex(fee_model.get(fee_num), 4, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_1308: {data}")
            HSyslog.log_info(f"tpp_cmd_1308: {tpp_cmd_1308_msg}")

        return pack(tpp_cmd_1308_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_1308.value)
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_1308 error: .{data} .{e}")
        return []


def tpp_cmd_1309(data: list):  # 平台发送，设备接收
    try:
        fee_model_info = []
        fee_model = data[2:]
        for i in range(0, len(fee_model), 16):
            fee_model_dict = {
                "fee_model_nums": hex_to_info(fee_model[i:i + 2], Encode_type.BIN.value),
                "fee_model_con_num": hex_to_info(fee_model[i + 2:i + 4], Encode_type.BIN.value),
                "fee_electricity": hex_to_info(fee_model[i + 4: i + 8], Encode_type.BIN.value),
                "fee_server": hex_to_info(fee_model[i + 8:i + 12], Encode_type.BIN.value),
                "fee_delay": hex_to_info(fee_model[i + 12:i + 16], Encode_type.BIN.value),
            }
            fee_model_info.append(fee_model_dict)
        info = {
            "fee_model_num": hex_to_info(data[0:2], Encode_type.BIN.value),
            "fee_model_info": fee_model_info,
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_1309.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_1309: {data}")
            HSyslog.log_info(f"tpp_cmd_1309: {info}")

        return info
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_1309 error: .{data} .{e}")
        return {}


def tpp_cmd_1310(data: dict):  # 设备发送，平台接收
    result = data.get("result")

    try:
        tpp_cmd_1310_msg = []
        tpp_cmd_1310_msg += info_to_hex(result, 1, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_1310: {data}")
            HSyslog.log_info(f"tpp_cmd_1310: {tpp_cmd_1310_msg}")

        return pack(tpp_cmd_1310_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_1310.value)
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_1310 error: .{data} .{e}")
        return []


def tpp_cmd_107(data: list):  # 平台发送，设备接收
    try:
        info = {
            "reserved": hex_to_info(data[0:4], Encode_type.BIN.value),
            "device_id": hex_to_info(data[4:36], Encode_type.ASCII.value),
            "gun_id": hex_to_info(data[36], Encode_type.BIN.value),
            "cmd_addr": hex_to_info(data[37:41], Encode_type.BIN.value),
        }

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_107: {data}")
            HSyslog.log_info(f"tpp_cmd_107: {info}")

        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_107.value, info])
        return info
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_107 error: .{data} .{e}")
        return {}


def tpp_cmd_108(data: dict):  # 设备发送，平台接收
    reserved = data.get("reserved", 0)
    gun_id = data.get("gun_id")
    cmd_addr = data.get("cmd_addr")
    addr_data = data.get("addr_data")
    charge_id = data.get("charge_id")

    try:
        tpp_cmd_108_msg = []
        tpp_cmd_108_msg += info_to_hex(reserved, 4, Encode_type.BIN.value)
        tpp_cmd_108_msg += info_to_hex(gun_id, 1, Encode_type.BIN.value)
        tpp_cmd_108_msg += info_to_hex(cmd_addr, 4, Encode_type.BIN.value)
        tpp_cmd_108_msg += info_to_hex(addr_data, 4, Encode_type.ASCII.value)
        tpp_cmd_108_msg += info_to_hex(charge_id, 32, Encode_type.ASCII.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_108: {data}")
            HSyslog.log_info(f"tpp_cmd_108: {tpp_cmd_108_msg}")

        return pack(tpp_cmd_108_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_108.value)
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_108 error: .{data} .{e}")
        return []


def tpp_cmd_117(data: list):  # 平台发送，设备接收
    try:
        info = {
            "device_id": hex_to_info(data[0:32], Encode_type.ASCII.value),
            "gun_id": hex_to_info(data[32], Encode_type.BIN.value),
            "fault_code": hex_to_info(data[33:37], Encode_type.BIN.value),
        }

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_117: {data}")
            HSyslog.log_info(f"tpp_cmd_117: {info}")

        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_117.value, info])
        return info
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_117 error: .{data} .{e}")
        return {}


def tpp_cmd_118(data: dict):  # 设备发送，平台接收
    gun_id = data.get("gun_id")
    device_id = data.get("device_id", Device_ID)
    fault_code = data.get("fault_code")
    fault_status = data.get("fault_status")

    try:
        tpp_cmd_118_msg = []
        tpp_cmd_118_msg += info_to_hex(device_id, 32, Encode_type.ASCII.value)
        tpp_cmd_118_msg += info_to_hex(gun_id, 1, Encode_type.BIN.value)
        tpp_cmd_118_msg += info_to_hex(fault_code, 4, Encode_type.BIN.value)
        tpp_cmd_118_msg += info_to_hex(fault_status, 1, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_118: {data}")
            HSyslog.log_info(f"tpp_cmd_118: {tpp_cmd_118_msg}")

        return pack(tpp_cmd_118_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_118.value)
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_118 error: .{data} .{e}")
        return []


def tpp_cmd_119(data: list):  # 平台发送，设备接收
    try:
        info = {
            "device_id": hex_to_info(data[0:32], Encode_type.ASCII.value),
            "gun_id": hex_to_info(data[32], Encode_type.BIN.value),
            "warn_code": hex_to_info(data[33:37], Encode_type.BIN.value),
        }

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_119: {data}")
            HSyslog.log_info(f"tpp_cmd_119: {info}")

        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_119.value, info])
        return info
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_119 error: .{data} .{e}")
        return {}


def tpp_cmd_120(data: dict):  # 设备发送，平台接收
    reserved = data.get("reserved", 0)
    device_id = data.get("device_id", Device_ID)
    gun_id = data.get("gun_id")
    warn_code = data.get("warn_code")
    charge_id = data.get("charge_id")
    warn_type = data.get("warn_type")
    warn_value = data.get("warn_value")

    try:
        tpp_cmd_120_msg = []
        tpp_cmd_120_msg += info_to_hex(device_id, 32, Encode_type.ASCII.value)
        tpp_cmd_120_msg += info_to_hex(gun_id, 1, Encode_type.BIN.value)
        tpp_cmd_120_msg += info_to_hex(warn_code, 4, Encode_type.ASCII.value)
        tpp_cmd_120_msg += info_to_hex(charge_id, 32, Encode_type.ASCII.value)
        tpp_cmd_120_msg += info_to_hex(warn_type, 1, Encode_type.BIN.value)
        tpp_cmd_120_msg += info_to_hex(warn_value, 4, Encode_type.BIN.value)
        tpp_cmd_120_msg += info_to_hex(reserved, 4, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_120: {data}")
            HSyslog.log_info(f"tpp_cmd_120: {tpp_cmd_120_msg}")

        return pack(tpp_cmd_120_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_120.value)
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_120 error: .{data} .{e}")
        return []


def tpp_cmd_407(data: list):  # 平台发送，设备接收
    try:
        info = {
            "reserved": hex_to_info(data[0:4], Encode_type.BIN.value),
            "device_id": hex_to_info(data[4:36], Encode_type.ASCII.value),
            "result": hex_to_info(data[36], Encode_type.BIN.value),
        }

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_407: {data}")
            HSyslog.log_info(f"tpp_cmd_407: {info}")

        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_407.value, info])
        return info
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_407 error: .{data} .{e}")
        return {}


def tpp_cmd_408(data: dict):  # 设备发送，平台接收
    reserved = data.get("reserved", 0)
    device_id = data.get("device_id", Device_ID)
    log_file_nums = data.get("log_file_nums")

    try:
        tpp_cmd_408_msg = []
        tpp_cmd_408_msg += info_to_hex(reserved, 4, Encode_type.BIN.value)
        tpp_cmd_408_msg += info_to_hex(device_id, 32, Encode_type.ASCII.value)
        tpp_cmd_408_msg += info_to_hex(log_file_nums, 128, Encode_type.ASCII.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_408: {data}")
            HSyslog.log_info(f"tpp_cmd_408: {tpp_cmd_408_msg}")

        return pack(tpp_cmd_408_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_408.value)
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_408 error: .{data} .{e}")
        return []


def tpp_cmd_409(data: list):  # 平台发送，设备接收
    try:
        info = {
            "reserved": hex_to_info(data[0:4], Encode_type.BIN.value),
            "device_id": hex_to_info(data[4:36], Encode_type.ASCII.value),
            "log_file_nums": hex_to_info(data[36:164], Encode_type.BIN.value),
        }

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_409: {data}")
            HSyslog.log_info(f"tpp_cmd_409: {info}")

        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_409.value, info])
        return info
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_409 error: .{data} .{e}")
        return {}


def tpp_cmd_410(data: dict):  # 设备发送，平台接收
    reserved = data.get("reserved", 0)
    device_id = data.get("device_id", Device_ID)
    log_file_nums = data.get("log_file_nums")

    try:
        tpp_cmd_410_msg = []
        tpp_cmd_410_msg += info_to_hex(reserved, 4, Encode_type.BIN.value)
        tpp_cmd_410_msg += info_to_hex(device_id, 32, Encode_type.ASCII.value)
        tpp_cmd_410_msg += info_to_hex(log_file_nums, 128, Encode_type.ASCII.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_410: {data}")
            HSyslog.log_info(f"tpp_cmd_410: {tpp_cmd_410_msg}")

        return pack(tpp_cmd_410_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_410.value)
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_410 error: .{data} .{e}")
        return []


def tpp_cmd_1101(data: list):  # 平台发送，设备接收
    try:
        info = {
            "ota_type": hex_to_info(data[0], Encode_type.BIN.value),  #
            "ota_param": hex_to_info(data[1], Encode_type.BIN.value),  #
            "ota_url": hex_to_info(data[2:130], Encode_type.ASCII.value),  #
            "ota_md5": hex_to_info(data[130:162], Encode_type.ASCII.value),  #
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_1101.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_1101: {data}")
            HSyslog.log_info(f"tpp_cmd_1101: {info}")

        return info
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_1101 error: .{data} .{e}")
        return {}


def tpp_cmd_1102(data: dict):  # 设备发送，平台接收
    ota_status = data.get("ota_status")
    ota_md5 = data.get("ota_md5")

    try:
        tpp_cmd_1102_msg = []
        tpp_cmd_1102_msg += info_to_hex(ota_status, 1, Encode_type.BIN.value)
        tpp_cmd_1102_msg += info_to_hex(ota_md5, 32, Encode_type.ASCII.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_1102: {data}")
            HSyslog.log_info(f"tpp_cmd_1102: {tpp_cmd_1102_msg}")

        return pack(tpp_cmd_1102_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_1102.value)
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_1102 error: .{data} .{e}")
        return []


def tpp_cmd_801(data: list):  # 平台发送，设备接收
    try:
        encrypt_data_len = hex_to_info(data[0:4], Encode_type.BIN.value)
        info = {
            "encrypt_data_len": encrypt_data_len,
            "encrypt_data": hex_to_info(data[4:encrypt_data_len + 4], Encode_type.ASCII.value),
            "device_id": hex_to_info(data[encrypt_data_len + 4:encrypt_data_len + 4 + 32], Encode_type.ASCII.value),
            "encrypt_type": hex_to_info(data[encrypt_data_len + 4 + 32:encrypt_data_len + 4 + 32 + 2], Encode_type.BIN.value),
            "encrypt_version": hex_to_info(data[encrypt_data_len + 4 + 32 + 2:encrypt_data_len + 4 + 32 + 2 + 4], Encode_type.ENCRYPT_VERSION.value),
            "encrypt_version_nums": hex_to_info(data[encrypt_data_len + 4 + 32 + 2 + 4], Encode_type.BIN.value),
        }

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_801: {data}")
            HSyslog.log_info(f"tpp_cmd_801: {info}")

        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_801.value, info])
        return info
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_801 error: .{data} .{e}")
        return {}


def tpp_cmd_802(data: dict):  # 设备发送，平台接收
    encrypt_data_len = data.get("encrypt_data_len")
    encrypt_data = data.get("encrypt_data")
    device_id = data.get("device_id", Device_ID)
    encrypt_type = data.get("encrypt_type")
    encrypt_version = data.get("encrypt_version")
    encrypt_version_nums = data.get("encrypt_version_nums")

    try:
        tpp_cmd_802_msg = []
        tpp_cmd_802_msg += info_to_hex(encrypt_data_len, 4, Encode_type.BIN.value)
        tpp_cmd_802_msg += info_to_hex(encrypt_data, encrypt_data_len, Encode_type.ASCII.value)
        tpp_cmd_802_msg += info_to_hex(device_id, 32, Encode_type.ASCII.value)
        tpp_cmd_802_msg += info_to_hex(encrypt_type, 2, Encode_type.BIN.value)
        tpp_cmd_802_msg += info_to_hex(encrypt_version, 4, Encode_type.ENCRYPT_VERSION.value)
        tpp_cmd_802_msg += info_to_hex(encrypt_version_nums, 1, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_802: {data}")
            HSyslog.log_info(f"tpp_cmd_802: {tpp_cmd_802_msg}")

        return pack(tpp_cmd_802_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_802.value)
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_802 error: .{data} .{e}")
        return []


def tpp_cmd_509(data: list):  # 平台发送，设备接收
    try:
        info = {
            "reserved": hex_to_info(data[0:2], Encode_type.BIN.value),
            "gun_id": hex_to_info(data[2:4], Encode_type.BIN.value),
            "device_id": hex_to_info(data[4:36], Encode_type.ASCII.value),
            "log_file_nums": hex_to_info(data[36:164], Encode_type.ASCII.value),
        }

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_509: {data}")
            HSyslog.log_info(f"tpp_cmd_509: {info}")

        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_509.value, info])
        return info
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_509 error: .{data} .{e}")
        return {}


def tpp_cmd_510(data: dict):  # 设备发送，平台接收
    reserved = data.get("reserved", 0)
    device_id = data.get("device_id", Device_ID)
    log_file_nums = data.get("log_file_nums")

    try:
        tpp_cmd_510_msg = []
        tpp_cmd_510_msg += info_to_hex(reserved, 4, Encode_type.BIN.value)
        tpp_cmd_510_msg += info_to_hex(device_id, 32, Encode_type.ASCII.value)
        tpp_cmd_510_msg += info_to_hex(log_file_nums, 128, Encode_type.ASCII.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_510: {data}")
            HSyslog.log_info(f"tpp_cmd_510: {tpp_cmd_510_msg}")

        return pack(tpp_cmd_510_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_510.value)
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_510 error: .{data} .{e}")
        return []


def tpp_cmd_33(data: list):  # 平台发送，设备接收
    try:
        info = {
            "device_id": hex_to_info(data[0:32], Encode_type.ASCII.value),
            "gun_id": hex_to_info(data[32:34], Encode_type.BIN.value),
            "result": hex_to_info(data[34:36], Encode_type.BIN.value),
            "balance": hex_to_info(data[36:40], Encode_type.BIN.value),
        }

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_33: {data}")
            HSyslog.log_info(f"tpp_cmd_33: {info}")

        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_33.value, info])
        return info
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_33 error: .{data} .{e}")
        return {}


def tpp_cmd_34(data: dict):  # 设备发送，平台接收
    reserved = data.get("reserved", 0)
    device_id = data.get("device_id", Device_ID)
    gun_id = data.get("gun_id")
    user_card_id = data.get("user_card_id")
    charge_random = data.get("charge_random")
    physical_cord_id = data.get("physical_cord_id")

    try:
        tpp_cmd_34_msg = []
        tpp_cmd_34_msg += info_to_hex(device_id, 32, Encode_type.ASCII.value)
        tpp_cmd_34_msg += info_to_hex(gun_id, 2, Encode_type.BIN.value)
        tpp_cmd_34_msg += info_to_hex(user_card_id, 16, Encode_type.ASCII.value)
        tpp_cmd_34_msg += info_to_hex(charge_random, 48, Encode_type.ASCII.value)
        tpp_cmd_34_msg += info_to_hex(physical_cord_id, 4, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_34: {data}")
            HSyslog.log_info(f"tpp_cmd_34: {tpp_cmd_34_msg}")

        return pack(tpp_cmd_34_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_34.value)
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_34 error: .{data} .{e}")
        return []


def tpp_cmd_35(data: list):  # 平台发送，设备接收
    try:
        info = {
            "device_id": hex_to_info(data[0:32], Encode_type.ASCII.value),
            "gun_id": hex_to_info(data[32:34], Encode_type.BIN.value),
            "user_card_id": hex_to_info(data[34:50], Encode_type.ASCII.value),
            "result": hex_to_info(data[50:52], Encode_type.BIN.value),
        }

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_35: {data}")
            HSyslog.log_info(f"tpp_cmd_35: {info}")

        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_35.value, info])
        return info
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_35 error: .{data} .{e}")
        return {}


def tpp_cmd_36(data: dict):  # 设备发送，平台接收
    device_id = data.get("device_id", Device_ID)
    gun_id = data.get("gun_id")
    user_card_id = data.get("user_card_id")

    try:
        tpp_cmd_36_msg = []
        tpp_cmd_36_msg += info_to_hex(device_id, 32, Encode_type.ASCII.value)
        tpp_cmd_36_msg += info_to_hex(gun_id, 2, Encode_type.BIN.value)
        tpp_cmd_36_msg += info_to_hex(user_card_id, 16, Encode_type.ASCII.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_36: {data}")
            HSyslog.log_info(f"tpp_cmd_36: {tpp_cmd_36_msg}")

        return pack(tpp_cmd_36_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_36.value)
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_36 error: .{data} .{e}")
        return []


def tpp_cmd_37(data: list):  # 平台发送，设备接收
    try:
        white_list_num = hex_to_info(data[32:34], Encode_type.BIN.value)
        white_list = data[34:]
        white_list_info = {}
        for i in (0, white_list_num, 17):
            white_list_info.update({
                i: {
                    "user_card_id": hex_to_info(white_list[0 + i:16 + i], Encode_type.ASCII.value),
                    "user_card_status": hex_to_info(white_list[16 + i:1 + 16 + i], Encode_type.BIN.value)
                }
            })
        info = {
            "device_id": hex_to_info(data[0:32], Encode_type.ASCII.value),  #
            "white_list_num": white_list_num,  #
            "white_list": white_list_info,  #
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_37.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_37: {data}")
            HSyslog.log_info(f"tpp_cmd_37: {info}")

        return info
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_37 error: .{data} .{e}")
        return {}


def tpp_cmd_38(data: dict):  # 设备发送，平台接收
    reserved = data.get("reserved", 0)
    device_id = data.get("device_id", Device_ID)
    white_list_num = data.get("white_list_num")
    white_list_info = data.get("white_list_info")

    try:
        tpp_cmd_38_msg = []
        tpp_cmd_38_msg += info_to_hex(device_id, 32, Encode_type.ASCII.value)
        tpp_cmd_38_msg += info_to_hex(white_list_num, 2, Encode_type.BIN.value)
        for white_list_nums, white_list_data in white_list_info.items():
            tpp_cmd_38_msg += info_to_hex(white_list_data.get("user_card_id"), 16, Encode_type.ASCII.value)
            tpp_cmd_38_msg += info_to_hex(white_list_data.get("user_card_status"), 1, Encode_type.BIN.value)
            tpp_cmd_38_msg += info_to_hex(white_list_data.get("user_card_result"), 1, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_38: {data}")
            HSyslog.log_info(f"tpp_cmd_38: {tpp_cmd_38_msg}")

        return pack(tpp_cmd_38_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_38.value)
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_38 error: .{data} .{e}")
        return []


def tpp_cmd_331(data: list):  # 平台发送，设备接收
    try:
        info = {
            "device_id": hex_to_info(data[0:32], Encode_type.ASCII.value),  #
            "reserved": hex_to_info(data[32:34], Encode_type.BIN.value),  #
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_331.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_331: {data}")
            HSyslog.log_info(f"tpp_cmd_331: {info}")

        return info
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_331 error: .{data} .{e}")
        return {}


def tpp_cmd_332(data: dict):  # 设备发送，平台接收
    reserved = data.get("reserved", 0)
    device_id = data.get("device_id", Device_ID)
    result = data.get("result")

    try:
        tpp_cmd_332_msg = []
        tpp_cmd_332_msg += info_to_hex(reserved, 2, Encode_type.BIN.value)
        tpp_cmd_332_msg += info_to_hex(device_id, 32, Encode_type.ASCII.value)
        tpp_cmd_332_msg += info_to_hex(result, 1, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_332: {data}")
            HSyslog.log_info(f"tpp_cmd_332: {tpp_cmd_332_msg}")

        return pack(tpp_cmd_332_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_332.value)
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_332 error: .{data} .{e}")
        return []


def tpp_cmd_40(data: dict):  # 设备发送，平台接收
    reserved = data.get("reserved", 0)
    device_id = data.get("device_id", Device_ID)
    gun_id = data.get("gun_id")
    car_vin = data.get("car_vin")

    try:
        tpp_cmd_40_msg = []
        tpp_cmd_40_msg += info_to_hex(reserved, 2, Encode_type.BIN.value)
        tpp_cmd_40_msg += info_to_hex(device_id, 32, Encode_type.ASCII.value)
        tpp_cmd_40_msg += info_to_hex(gun_id, 1, Encode_type.BIN.value)
        tpp_cmd_40_msg += info_to_hex(car_vin, 17, Encode_type.ASCII.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_40: {data}")
            HSyslog.log_info(f"tpp_cmd_40: {tpp_cmd_40_msg}")

        return pack(tpp_cmd_40_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_40.value)
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_40 error: .{data} .{e}")
        return []


def tpp_cmd_41(data: list):  # 平台发送，设备接收
    try:
        info = {
            "device_id": hex_to_info(data[0:32], Encode_type.ASCII.value),  #
            "gun_id": hex_to_info(data[32], Encode_type.BIN.value),  #
            "charge_id": hex_to_info(data[33:65], Encode_type.ASCII.value),  #
            "car_vin": hex_to_info(data[65:82], Encode_type.ASCII.value),  #
            "user_balance": hex_to_info(data[82:86], Encode_type.BIN.value),  #
            "result": hex_to_info(data[86], Encode_type.BIN.value),  #
            "reason": hex_to_info(data[87], Encode_type.BIN.value),  #
            "remain_mile": hex_to_info(data[88:92], Encode_type.BIN.value),  #
            "chargeable_power": hex_to_info(data[92:96], Encode_type.BIN.value),  #
            "remain_num": hex_to_info(data[96:100], Encode_type.BIN.value),  #
            "user_phone": hex_to_info(data[100:102], Encode_type.BIN.value),  #
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_41.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_41: {data}")
            HSyslog.log_info(f"tpp_cmd_41: {info}")

        return info
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_41 error: .{data} .{e}")
        return {}


def tpp_cmd_42(data: dict):  # 设备发送，平台接收
    reserved = data.get("reserved", 0)
    device_id = data.get("device_id", Device_ID)
    white_list_num = data.get("white_list_num")
    white_list_info = data.get("white_list_info")

    try:
        tpp_cmd_42_msg = []
        tpp_cmd_42_msg += info_to_hex(device_id, 32, Encode_type.ASCII.value)
        tpp_cmd_42_msg += info_to_hex(white_list_num, 2, Encode_type.BIN.value)
        for white_list_nums, white_list_data in white_list_info.items():
            tpp_cmd_42_msg += info_to_hex(white_list_data.get("car_vin"), 17, Encode_type.ASCII.value)
            tpp_cmd_42_msg += info_to_hex(white_list_data.get("car_vin_status"), 1, Encode_type.BIN.value)
            tpp_cmd_42_msg += info_to_hex(white_list_data.get("car_vin_result"), 1, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_42: {data}")
            HSyslog.log_info(f"tpp_cmd_42: {tpp_cmd_42_msg}")

        return pack(tpp_cmd_42_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_42.value)
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_42 error: .{data} .{e}")
        return []


def tpp_cmd_43(data: list):  # 平台发送，设备接收
    try:
        white_list_num = hex_to_info(data[32:34], Encode_type.BIN.value)
        white_list = data[34:]
        white_list_info = {}
        for i in (0, white_list_num, 18):
            white_list_info.update({
                i: {
                    "car_vin": hex_to_info(white_list[0 + i:17 + i], Encode_type.ASCII.value),
                    "car_vin_status": hex_to_info(white_list[17 + i:1 + 17 + i], Encode_type.BIN.value)
                }
            })
        info = {
            "device_id": hex_to_info(data[0:32], Encode_type.ASCII.value),  #
            "white_list_num": white_list_num,  #
            "white_list": white_list_info,  #
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_43.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_43: {data}")
            HSyslog.log_info(f"tpp_cmd_43: {info}")

        return info
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_43 error: .{data} .{e}")
        return {}


def tpp_cmd_44(data: dict):  # 设备发送，平台接收
    reserved = data.get("reserved", 0)
    device_id = data.get("device_id", Device_ID)
    result = data.get("result")

    try:
        tpp_cmd_44_msg = []
        tpp_cmd_44_msg += info_to_hex(reserved, 2, Encode_type.BIN.value)
        tpp_cmd_44_msg += info_to_hex(device_id, 32, Encode_type.ASCII.value)
        tpp_cmd_44_msg += info_to_hex(result, 1, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_44: {data}")
            HSyslog.log_info(f"tpp_cmd_44: {tpp_cmd_44_msg}")

        return pack(tpp_cmd_44_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_44.value)
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_44 error: .{data} .{e}")
        return []


def tpp_cmd_45(data: list):  # 平台发送，设备接收
    try:
        info = {
            "device_id": hex_to_info(data[0:32], Encode_type.ASCII.value),  #
            "reserved": hex_to_info(data[32:34], Encode_type.BIN.value),  #
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_45.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_45: {data}")
            HSyslog.log_info(f"tpp_cmd_45: {info}")

        return info
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_45 error: .{data} .{e}")
        return {}


def tpp_cmd_80(data: dict):  # 设备发送，平台接收
    reserved = data.get("reserved", 0)
    device_id = data.get("device_id", Device_ID)
    gun_id = data.get("gun_id")
    charge_id = data.get("charge_id")
    encrypt_data = data.get("encrypt_data")
    meter_nums = data.get("meter_nums")

    try:
        tpp_cmd_80_msg = []
        tpp_cmd_80_msg += info_to_hex(device_id, 32, Encode_type.ASCII.value)
        tpp_cmd_80_msg += info_to_hex(gun_id, 1, Encode_type.BIN.value)
        tpp_cmd_80_msg += info_to_hex(charge_id, 32, Encode_type.ASCII.value)
        tpp_cmd_80_msg += info_to_hex(encrypt_data, 34, Encode_type.ASCII.value)
        tpp_cmd_80_msg += info_to_hex(meter_nums, 6, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_80: {data}")
            HSyslog.log_info(f"tpp_cmd_80: {tpp_cmd_80_msg}")

        return pack(tpp_cmd_80_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_80.value)
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_80 error: .{data} .{e}")
        return []


def tpp_cmd_81(data: list):  # 平台发送，设备接收
    try:
        info = {
            "gun_id": hex_to_info(data[0], Encode_type.BIN.value),  #
            "device_id": hex_to_info(data[1:33], Encode_type.ASCII.value),  #
            "charge_id": hex_to_info(data[33:65], Encode_type.ASCII.value),  #
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_81.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_81: {data}")
            HSyslog.log_info(f"tpp_cmd_81: {info}")

        return info
    except Exception as e:
        HSyslog.log_info(f"tpp_cmd_81 error: .{data} .{e}")
        return {}


tpp_mqtt_cmd_type = {
    tpp_mqtt_cmd_enum.tpp_cmd_type_1.value: {"func": tpp_cmd_1, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_2.value: {"func": tpp_cmd_2, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_3.value: {"func": tpp_cmd_3, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_4.value: {"func": tpp_cmd_4, "qos": 1},

    tpp_mqtt_cmd_enum.tpp_cmd_type_501.value: {"func": tpp_cmd_501, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_502.value: {"func": tpp_cmd_502, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_505.value: {"func": tpp_cmd_505, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_506.value: {"func": tpp_cmd_506, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_507.value: {"func": tpp_cmd_507, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_508.value: {"func": tpp_cmd_508, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_511.value: {"func": tpp_cmd_511, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_512.value: {"func": tpp_cmd_512, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_513.value: {"func": tpp_cmd_513, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_514.value: {"func": tpp_cmd_514, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_515.value: {"func": tpp_cmd_515, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_516.value: {"func": tpp_cmd_516, "qos": 1},

    tpp_mqtt_cmd_enum.tpp_cmd_type_5.value: {"func": tpp_cmd_5, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_6.value: {"func": tpp_cmd_6, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_7.value: {"func": tpp_cmd_7, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_8.value: {"func": tpp_cmd_8, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_11.value: {"func": tpp_cmd_11, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_12.value: {"func": tpp_cmd_12, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_13.value: {"func": tpp_cmd_13, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_14.value: {"func": tpp_cmd_14, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_15.value: {"func": tpp_cmd_15, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_16.value: {"func": tpp_cmd_16, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_503.value: {"func": tpp_cmd_503, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_504.value: {"func": tpp_cmd_504, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_17.value: {"func": tpp_cmd_17, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_18.value: {"func": tpp_cmd_18, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_19.value: {"func": tpp_cmd_19, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_20.value: {"func": tpp_cmd_20, "qos": 1},

    tpp_mqtt_cmd_enum.tpp_cmd_type_101.value: {"func": tpp_cmd_101, "qos": 0},
    tpp_mqtt_cmd_enum.tpp_cmd_type_102.value: {"func": tpp_cmd_102, "qos": 0},
    tpp_mqtt_cmd_enum.tpp_cmd_type_103.value: {"func": tpp_cmd_103, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_104.value: {"func": tpp_cmd_104, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_105.value: {"func": tpp_cmd_105, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_106.value: {"func": tpp_cmd_106, "qos": 0},
    tpp_mqtt_cmd_enum.tpp_cmd_type_113.value: {"func": tpp_cmd_113, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_114.value: {"func": tpp_cmd_114, "qos": 1},

    tpp_mqtt_cmd_enum.tpp_cmd_type_301.value: {"func": tpp_cmd_301, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_302.value: {"func": tpp_cmd_302, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_303.value: {"func": tpp_cmd_303, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_304.value: {"func": tpp_cmd_304, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_305.value: {"func": tpp_cmd_305, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_306.value: {"func": tpp_cmd_306, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_307.value: {"func": tpp_cmd_307, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_308.value: {"func": tpp_cmd_308, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_309.value: {"func": tpp_cmd_309, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_310.value: {"func": tpp_cmd_310, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_311.value: {"func": tpp_cmd_311, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_312.value: {"func": tpp_cmd_312, "qos": 1},

    tpp_mqtt_cmd_enum.tpp_cmd_type_201.value: {"func": tpp_cmd_201, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_202.value: {"func": tpp_cmd_202, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_205.value: {"func": tpp_cmd_205, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_206.value: {"func": tpp_cmd_206, "qos": 1},

    tpp_mqtt_cmd_enum.tpp_cmd_type_401.value: {"func": tpp_cmd_401, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_402.value: {"func": tpp_cmd_402, "qos": 1},

    tpp_mqtt_cmd_enum.tpp_cmd_type_23.value: {"func": tpp_cmd_23, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_24.value: {"func": tpp_cmd_24, "qos": 1},

    tpp_mqtt_cmd_enum.tpp_cmd_type_1303.value: {"func": tpp_cmd_1303, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_1304.value: {"func": tpp_cmd_1304, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_1305.value: {"func": tpp_cmd_1305, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_1306.value: {"func": tpp_cmd_1306, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_1307.value: {"func": tpp_cmd_1307, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_1308.value: {"func": tpp_cmd_1308, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_1309.value: {"func": tpp_cmd_1309, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_1310.value: {"func": tpp_cmd_1310, "qos": 1},

    tpp_mqtt_cmd_enum.tpp_cmd_type_107.value: {"func": tpp_cmd_107, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_108.value: {"func": tpp_cmd_108, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_117.value: {"func": tpp_cmd_117, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_118.value: {"func": tpp_cmd_118, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_119.value: {"func": tpp_cmd_119, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_120.value: {"func": tpp_cmd_120, "qos": 1},

    tpp_mqtt_cmd_enum.tpp_cmd_type_407.value: {"func": tpp_cmd_407, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_408.value: {"func": tpp_cmd_408, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_409.value: {"func": tpp_cmd_409, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_410.value: {"func": tpp_cmd_410, "qos": 1},

    tpp_mqtt_cmd_enum.tpp_cmd_type_1101.value: {"func": tpp_cmd_1101, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_1102.value: {"func": tpp_cmd_1102, "qos": 1},

    tpp_mqtt_cmd_enum.tpp_cmd_type_801.value: {"func": tpp_cmd_801, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_802.value: {"func": tpp_cmd_802, "qos": 1},

    tpp_mqtt_cmd_enum.tpp_cmd_type_509.value: {"func": tpp_cmd_509, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_510.value: {"func": tpp_cmd_510, "qos": 1},

    tpp_mqtt_cmd_enum.tpp_cmd_type_33.value: {"func": tpp_cmd_33, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_34.value: {"func": tpp_cmd_34, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_35.value: {"func": tpp_cmd_35, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_36.value: {"func": tpp_cmd_36, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_37.value: {"func": tpp_cmd_37, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_38.value: {"func": tpp_cmd_38, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_331.value: {"func": tpp_cmd_331, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_332.value: {"func": tpp_cmd_332, "qos": 1},

    tpp_mqtt_cmd_enum.tpp_cmd_type_40.value: {"func": tpp_cmd_40, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_41.value: {"func": tpp_cmd_41, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_42.value: {"func": tpp_cmd_42, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_43.value: {"func": tpp_cmd_43, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_44.value: {"func": tpp_cmd_44, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_45.value: {"func": tpp_cmd_45, "qos": 1},

    tpp_mqtt_cmd_enum.tpp_cmd_type_80.value: {"func": tpp_cmd_80, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_81.value: {"func": tpp_cmd_80, "qos": 1},

}

"""
/* #################################################### 数据信息 #######################################################*/
"""
User_Name = None
User_Password = None  # 用户密码
Enterprise_Code = None  # 生产厂商代码
Msg_Header = 0xD07D  # 数据包头
SDK_Info = 0x0F0A0003
SDK_List = [0x0F, 0x0A, 0x00, 0x03]

serial_code = 0x01
End_Service_Code = 0xFF  # 消息最大序列号
Start_Service_Code = 0x00  # 消息最小序列号
Device_ID = "0012240002000605"  # 设备ID（桩编码，资产编码）
Encryption_Flag = None  # 是否加密
connect_status = False  # 连接状态
hand_status = False  # 握手状态
platform_host = "116.85.2.49"  # 平台IP
platform_port = 1884  # 平台端口号
Heartbeat = 0
data_path = "/opt/hhd/Platform.db"
ota_path = "/opt/hhd/dtu20.tar.gz"
syslog_path = '/var/log'  # 替换为实际路径
IS_DEBUG = True
device_start_nums = 0
charge_record_num = 0
gun_qrcode = "https://epower.xiaojukeji.com/epower/static/resources/xcxconf/XIAOJU.101437000."

red_char = "\033[91m"
green_char = "\033[92m"
init_char = "\033[0m"

Platform_ready = False


class Encode_type(Enum):
    BIN = 1
    TIME = 2
    ASCII = 3
    VERSION = 4
    MD5 = 5
    IP = 6
    MAC = 7
    ENCRYPT_VERSION = 8


class Big_Little(Enum):
    BIG = 1
    LITTLE = 2


class DB_Data_Type(Enum):
    DATA_STR = 1
    DATA_INT = 2


class Gun_DC_AC(Enum):
    DC_gun = 1
    AC_gun = 2


tpp_send_data = queue.Queue()
tpp_resv_data = queue.Queue()

ack_data = {
    "serial_code": None,
    "cmd_code": None,
    "sendata": None,
    "send_num": None
}


class msg_108(Enum):
    in_gun = 1
    out_gun = 2
    start_charge = 3
    stop_charge = 4
    cancel_charge = 5
    pause_charge = 6
    recover_charge = 7
    start_delay_fee = 8


class Gun_Status(Enum):
    Idle = 0  # 空闲
    Plugged_in_not_charging = 1  # 插枪未充电
    Charging = 2  # 充电中
    Charging_completed_not_unplugged = 3  # 充电完成未拔枪
    Reserved = 4  # 预约中
    Self_checking = 5  # 自检
    Fault = 6  # 故障
    Stopping = 7  # 停止中


class Gun_Connect_Status(Enum):
    Connect = 1
    Not_Connect = 2
    Start_Charge = 3
    Stop_Charge = 4


class Gun_Car_Connect_Status(Enum):
    Connect = 2
    Not_Connect = 0


Gun_list = []
Gun_Type = Gun_DC_AC.DC_gun.value


class Gun_info:
    def __init__(self, gun_id):
        self.gun_id = gun_id
        self.gun_charge_cost = False
        self.gun_charge_session = False

        self._gun_type = 1
        self._gun_status = Gun_Status.Idle.value
        self._gun_connect_status = Gun_Connect_Status.Not_Connect.value
        self._gun_car_connect_status = Gun_Car_Connect_Status.Not_Connect.value
        self._gun_charge = {}
        self._gun_charge_order = {}
        self._gun_charge_reserve = {}
        self._gun_fault = {}
        self._gun_warn = {}
        self._gun_qr = None
        self._gun_charge_gun_id = [gun_id]

    # 写入
    def set_gun_status(self, gun_status):
        self._gun_status = gun_status
        return self._gun_status

    def set_gun_connect_status(self, gun_connect_status):
        self._gun_connect_status = gun_connect_status
        return self._gun_connect_status

    def set_gun_car_connect_status(self, gun_car_connect_status):
        gun_car_status_dict = {
            0: Gun_Car_Connect_Status.Not_Connect.value,
            1: Gun_Car_Connect_Status.Connect.value
        }.get(gun_car_connect_status)
        self._gun_car_connect_status = gun_car_status_dict
        return self._gun_connect_status

    def set_gun_type(self, gun_type):
        self._gun_type = gun_type
        return self._gun_type

    def set_gun_charge(self, charge_info):
        self._gun_charge.update(charge_info)
        return True

    def empty_gun_charge(self):
        self._gun_charge = {}
        HSyslog.log_info("empty_gun_charge")
        return self._gun_charge

    def copy_gun_charge(self, gun_id):
        gun_charge = Gun_list[gun_id].get_gun_charge()
        self._gun_charge = copy.copy(gun_charge)
        return self._gun_charge

    def set_gun_charge_order(self, charge_info):
        self._gun_charge_order = charge_info
        HSyslog.log_info(self._gun_charge_order)
        return True

    def empty_gun_charge_order(self):
        self._gun_charge_order = {}
        HSyslog.log_info("empty_gun_charge_order")
        return self._gun_charge_order

    def set_gun_charge_reserve(self):
        self._gun_charge_reserve = self._gun_charge_order
        self._gun_charge_reserve.update({"charge_policy": self._gun_charge.get("charge_policy")})
        self._gun_charge_reserve.update({"charge_policy_param": self._gun_charge.get("charge_policy_param")})
        return self._gun_charge_reserve

    def empty_gun_charge__reserve(self):
        self._gun_charge_reserve = {}
        HSyslog.log_info("empty_gun_charge_reserve")
        return self._gun_charge_reserve

    def set_gun_fault(self, fault_info):
        if self._gun_fault != {}:
            for fault_id in self._gun_fault.keys():
                self._gun_fault[fault_id]["status"] = 1
        self._gun_fault.update(fault_info)
        return True

    def set_gun_warn(self, warn_info):
        if self._gun_warn != {}:
            for fault_id in self._gun_warn.keys():
                self._gun_warn[fault_id]["status"] = 1
        self._gun_warn.update(warn_info)
        return True

    def set_gun_qr(self, qr):
        self._gun_qr = qr
        return self._gun_qr

    def set_gun_charge_gun_id(self, gun_list: list):
        self._gun_charge_gun_id = gun_list
        return self._gun_charge_gun_id

    def get_gun_type(self):
        return self._gun_type

    # 获取
    def get_gun_status(self):
        return self._gun_status

    def get_gun_connect_status(self):
        return self._gun_connect_status

    def get_gun_car_connect_status(self):
        return self._gun_car_connect_status

    def get_gun_charge(self, charge_info=None):
        if charge_info is not None:
            if not isinstance(charge_info, str):
                return None
            data = self._gun_charge.get(charge_info, -1)
            if data == -1:
                return None
            return data
        else:
            return self._gun_charge

    def get_gun_charge_order(self, charge_info=None):
        if charge_info is not None:
            if not isinstance(charge_info, str):
                return None
            data = self._gun_charge_order.get(charge_info, -1)
            if data == -1:
                return None
            return data
        else:
            return self._gun_charge_order

    def get_gun_charge_reserve(self, charge_info=None):
        if charge_info is not None:
            if not isinstance(charge_info, str):
                return None
            data = self._gun_charge_reserve.get(charge_info, -1)
            if data == -1:
                return None
            return data
        else:
            return self._gun_charge_reserve

    def get_gun_fault(self, fault_id=None):
        if fault_id is None:
            return self._gun_fault
        else:
            return self._gun_fault.get(fault_id, {})

    def get_gun_warn(self, warn_id=None):
        if warn_id is None:
            return self._gun_warn
        else:
            return self._gun_warn.get(warn_id, {})

    def get_gun_qr(self):
        return self._gun_qr

    def get_gun_charge_gun_id(self):
        return self._gun_charge_gun_id


def get_datatime_YYMMDDHHMMSS(timestamp=""):
    if timestamp == "":
        current_time = datetime.now()
        formatted_time = current_time.strftime("%y%m%d%H%M%S")
    else:
        datetime_obj = datetime.utcfromtimestamp(int(timestamp))
        formatted_time = datetime_obj.strftime('%y%m%d%H%M%S')
    return formatted_time


def get_datetime_timestamp():
    datetime_obj = time.time()
    return int(datetime_obj)


def get_mac_address(interface):
    try:
        mac_bytes = get_DeviceInfo("mac_bytes")
        if mac_bytes is None:
            mac_bytes = open(f"/sys/class/net/{interface}/address").read().strip()
            save_DeviceInfo("mac_bytes", 1, mac_bytes, 0)
        # mac = ":".join([mac_bytes[i:i+2] for i in range(0, 12, 2)])
        return mac_bytes
    except FileNotFoundError:
        return None


INFO_MODEL = Big_Little.LITTLE.value

cleck_code_1 = {
    1: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "sign_interval", "param_type": DB_Data_Type.DATA_INT.value},
    2: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "device_project_type", "param_type": DB_Data_Type.DATA_INT.value},
    3: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "gun_num", "param_type": DB_Data_Type.DATA_INT.value},
    4: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "device_rodom", "param_type": DB_Data_Type.DATA_INT.value},
    5: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "max_vol", "param_type": DB_Data_Type.DATA_INT.value},
    6: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "max_cur", "param_type": DB_Data_Type.DATA_INT.value},
    7: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "max_ac_CP", "param_type": DB_Data_Type.DATA_INT.value},
    8: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "max_charge_power", "param_type": DB_Data_Type.DATA_INT.value},
    9: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "min_charge_power", "param_type": DB_Data_Type.DATA_INT.value},
    10: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "max_acLeakage_cur", "param_type": DB_Data_Type.DATA_INT.value},
    11: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "read_card_type", "param_type": DB_Data_Type.DATA_INT.value},
    12: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "reserve", "param_type": DB_Data_Type.DATA_INT.value},
    13: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "charge_card_nums", "param_type": DB_Data_Type.DATA_INT.value},
    14: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "platform_verification", "param_type": DB_Data_Type.DATA_INT.value},
    15: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "car_card_verification", "param_type": DB_Data_Type.DATA_INT.value},
    16: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "car_vin_bind", "param_type": DB_Data_Type.DATA_INT.value},
    17: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "bms_monpro_vol", "param_type": DB_Data_Type.DATA_INT.value},
    18: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "bms_monpro_temperature", "param_type": DB_Data_Type.DATA_INT.value},
    19: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "charge_is", "param_type": DB_Data_Type.DATA_INT.value},
    20: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "offline_is", "param_type": DB_Data_Type.DATA_INT.value},
    21: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "code303_is", "param_type": DB_Data_Type.DATA_INT.value},
    22: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "earth_ac_wire_is", "param_type": DB_Data_Type.DATA_INT.value},
    23: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "screen_protection_time", "param_type": DB_Data_Type.DATA_INT.value},
    24: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "delay_cost_time", "param_type": DB_Data_Type.DATA_INT.value},
    25: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "radar_is", "param_type": DB_Data_Type.DATA_INT.value},
    26: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "gun_lock_is", "param_type": DB_Data_Type.DATA_INT.value},
    27: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "reserve", "param_type": DB_Data_Type.DATA_INT.value},
    28: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "reserve", "param_type": DB_Data_Type.DATA_INT.value},
    29: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "report_interval", "param_type": DB_Data_Type.DATA_INT.value},
    30: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "heart_interval", "param_type": DB_Data_Type.DATA_INT.value},
    31: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "heart_timeout_num", "param_type": DB_Data_Type.DATA_INT.value},
    32: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "info_interval", "param_type": DB_Data_Type.DATA_INT.value},
    33: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "report_mode", "param_type": DB_Data_Type.DATA_INT.value},
    34: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "server_ip", "param_type": DB_Data_Type.DATA_INT.value},
    35: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "server_port", "param_type": DB_Data_Type.DATA_INT.value},
    36: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "reserve", "param_type": DB_Data_Type.DATA_INT.value},
    37: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "reserve", "param_type": DB_Data_Type.DATA_INT.value},
    38: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "fee_model_show", "param_type": DB_Data_Type.DATA_INT.value},
    39: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "advertisement_wake_time", "param_type": DB_Data_Type.DATA_INT.value},
    40: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "advertisement_scan_time", "param_type": DB_Data_Type.DATA_INT.value},
    41: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "advertisement_stop_time", "param_type": DB_Data_Type.DATA_INT.value},
    42: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "advertisement_idle_type", "param_type": DB_Data_Type.DATA_INT.value},
    43: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "advertisement_idle_time", "param_type": DB_Data_Type.DATA_INT.value},
    44: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "advertisement_start_hour", "param_type": DB_Data_Type.DATA_INT.value},
    45: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "advertisement_start_min", "param_type": DB_Data_Type.DATA_INT.value},
    46: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "advertisement_stop_hour", "param_type": DB_Data_Type.DATA_INT.value},
    47: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "advertisement_stop_min", "param_type": DB_Data_Type.DATA_INT.value},
    48: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "reserve", "param_type": DB_Data_Type.DATA_INT.value},
    49: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "reserve", "param_type": DB_Data_Type.DATA_INT.value},
    50: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "vol_error", "param_type": DB_Data_Type.DATA_INT.value},
    51: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "offline_charge_time", "param_type": DB_Data_Type.DATA_INT.value},
}

cleck_code_3 = {
    1: {"encode": [32, Encode_type.ASCII.value], "is_save_device": None, "param_id": "device_id", "param_type": DB_Data_Type.DATA_STR.value},
    2: {"encode": [8, Encode_type.TIME.value], "is_save_device": None, "param_id": "system_time", "param_type": DB_Data_Type.DATA_STR.value},
    3: {"encode": [8, Encode_type.ASCII.value], "is_save_device": None, "param_id": "admin_password", "param_type": DB_Data_Type.DATA_STR.value},
    4: {"encode": [8, Encode_type.ASCII.value], "is_save_device": None, "param_id": "user_password", "param_type": DB_Data_Type.DATA_STR.value},
    5: {"encode": [6, Encode_type.ASCII.value], "is_save_device": None, "param_id": "mac_addr", "param_type": DB_Data_Type.DATA_STR.value},
    6: {"encode": [16, Encode_type.ASCII.value], "is_save_device": None, "param_id": "Box_transformer_id", "param_type": DB_Data_Type.DATA_STR.value},
    7: {"encode": [1, Encode_type.ASCII.value], "is_save_device": None, "param_id": "gun_id", "param_type": DB_Data_Type.DATA_STR.value},
    8: {"encode": [256, Encode_type.ASCII.value], "is_save_device": None, "param_id": "gun_qrcode", "param_type": DB_Data_Type.DATA_STR.value},
    9: {"encode": [128, Encode_type.ASCII.value], "is_save_device": None, "param_id": "device_llogo", "param_type": DB_Data_Type.DATA_STR.value},
    10: {"encode": [16, Encode_type.ASCII.value], "is_save_device": None, "param_id": "reserve", "param_type": DB_Data_Type.DATA_STR.value},
    11: {"encode": [16, Encode_type.ASCII.value], "is_save_device": None, "param_id": "reserve", "param_type": DB_Data_Type.DATA_STR.value},
    12: {"encode": [256, Encode_type.ASCII.value], "is_save_device": None, "param_id": "user_cost_qrcode", "param_type": DB_Data_Type.DATA_STR.value},
    13: {"encode": [128, Encode_type.ASCII.value], "is_save_device": None, "param_id": "server_com", "param_type": DB_Data_Type.DATA_STR.value},
    14: {"encode": [4, Encode_type.ASCII.value], "is_save_device": None, "param_id": "server_port", "param_type": DB_Data_Type.DATA_STR.value},
    15: {"encode": [256, Encode_type.ASCII.value], "is_save_device": None, "param_id": "device_hlogo", "param_type": DB_Data_Type.DATA_STR.value},
    16: {"encode": [128, Encode_type.ASCII.value], "is_save_device": None, "param_id": "left_qr_word", "param_type": DB_Data_Type.DATA_STR.value},
    17: {"encode": [128, Encode_type.ASCII.value], "is_save_device": None, "param_id": "left_qrcode", "param_type": DB_Data_Type.DATA_STR.value},
    18: {"encode": [128, Encode_type.ASCII.value], "is_save_device": None, "param_id": "right_qr_word", "param_type": DB_Data_Type.DATA_STR.value},
    19: {"encode": [128, Encode_type.ASCII.value], "is_save_device": None, "param_id": "right_qrcode", "param_type": DB_Data_Type.DATA_STR.value},
}

cleck_code_5 = {
    1: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "power_model_start", "param_type": DB_Data_Type.DATA_INT.value},
    2: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "charge_stop", "param_type": DB_Data_Type.DATA_INT.value},
    3: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "reserve", "param_type": DB_Data_Type.DATA_INT.value},
    4: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "charge_ctrl_type", "param_type": DB_Data_Type.DATA_INT.value},
    5: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "reserve", "param_type": DB_Data_Type.DATA_INT.value},
    6: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "reserve", "param_type": DB_Data_Type.DATA_INT.value},
    7: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "res_out_vol", "param_type": DB_Data_Type.DATA_INT.value},
    8: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "res_out_cur", "param_type": DB_Data_Type.DATA_INT.value},
    9: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "charge_mode", "param_type": DB_Data_Type.DATA_INT.value},
    10: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "rev_charge", "param_type": DB_Data_Type.DATA_INT.value},
    11: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "device_reboot", "param_type": DB_Data_Type.DATA_INT.value},
    12: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "update_mode", "param_type": DB_Data_Type.DATA_INT.value},
    13: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "gun_lock_up", "param_type": DB_Data_Type.DATA_INT.value},
    14: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "gun_lock_down", "param_type": DB_Data_Type.DATA_INT.value},
    15: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "update_start", "param_type": DB_Data_Type.DATA_INT.value},
    16: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "use_start", "param_type": DB_Data_Type.DATA_INT.value},
    17: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "report_106", "param_type": DB_Data_Type.DATA_INT.value},
    18: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "report_104", "param_type": DB_Data_Type.DATA_INT.value},
    19: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "cost_suss", "param_type": DB_Data_Type.DATA_INT.value},
    20: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "reconnect", "param_type": DB_Data_Type.DATA_INT.value},
}

cleck_code_501 = {
    1: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "report_106_interval", "param_type": DB_Data_Type.DATA_INT.value},
    2: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "report_104_interval", "param_type": DB_Data_Type.DATA_INT.value},
    3: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "report_102_interval", "param_type": DB_Data_Type.DATA_INT.value},
    4: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "heart_timeout_num", "param_type": DB_Data_Type.DATA_INT.value},
    5: {"encode": [32, Encode_type.ASCII.value], "is_save_device": None, "param_id": "device_id", "param_type": DB_Data_Type.DATA_STR.value},
    6: {"encode": [130, Encode_type.ASCII.value], "is_save_device": None, "param_id": "gun_id_qrcode", "param_type": DB_Data_Type.DATA_STR.value},
    7: {"encode": [64, Encode_type.ASCII.value], "is_save_device": None, "param_id": "server_ip", "param_type": DB_Data_Type.DATA_STR.value},
    8: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "server_port", "param_type": DB_Data_Type.DATA_INT.value},
    9: {"encode": [1, Encode_type.BIN.value], "is_save_device": None, "param_id": "TCU_log_level", "param_type": DB_Data_Type.DATA_INT.value},
    10: {"encode": [1, Encode_type.BIN.value], "is_save_device": None, "param_id": "TCU_log_policy", "param_type": DB_Data_Type.DATA_INT.value},
    11: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "TCU_log_interval", "param_type": DB_Data_Type.DATA_INT.value},

    12: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "501_12", "param_type": DB_Data_Type.DATA_INT.value},
    13: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "501_13", "param_type": DB_Data_Type.DATA_INT.value},
    14: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "501_14", "param_type": DB_Data_Type.DATA_INT.value},
    15: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "501_15", "param_type": DB_Data_Type.DATA_INT.value},
    16: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "501_16", "param_type": DB_Data_Type.DATA_INT.value},
    17: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "501_17", "param_type": DB_Data_Type.DATA_INT.value},
    18: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "501_18", "param_type": DB_Data_Type.DATA_INT.value},
    19: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "501_19", "param_type": DB_Data_Type.DATA_INT.value},
    20: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "501_20", "param_type": DB_Data_Type.DATA_INT.value},
    21: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "501_21", "param_type": DB_Data_Type.DATA_INT.value},
    22: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "501_22", "param_type": DB_Data_Type.DATA_INT.value},
    23: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "501_23", "param_type": DB_Data_Type.DATA_INT.value},
    24: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "501_24", "param_type": DB_Data_Type.DATA_INT.value},
    25: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "501_25", "param_type": DB_Data_Type.DATA_INT.value},
    26: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "501_26", "param_type": DB_Data_Type.DATA_INT.value},
    27: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "501_27", "param_type": DB_Data_Type.DATA_INT.value},
    28: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "501_28", "param_type": DB_Data_Type.DATA_INT.value},
    29: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "501_29", "param_type": DB_Data_Type.DATA_INT.value},
    30: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "501_30", "param_type": DB_Data_Type.DATA_INT.value},
    31: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "501_31", "param_type": DB_Data_Type.DATA_INT.value},
    32: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "501_32", "param_type": DB_Data_Type.DATA_INT.value},
    33: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "501_33", "param_type": DB_Data_Type.DATA_INT.value},
    34: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "501_34", "param_type": DB_Data_Type.DATA_INT.value},
    35: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "501_35", "param_type": DB_Data_Type.DATA_INT.value},
}

cleck_code_507 = {
    0: {"encode": [1, Encode_type.BIN.value], "is_save_device": None, "param_id": "third_platform_is", "param_type": DB_Data_Type.DATA_INT.value},
    1: {"encode": [1, Encode_type.BIN.value], "is_save_device": None, "param_id": "Three_electric_display_is", "param_type": DB_Data_Type.DATA_INT.value},
    2: {"encode": [1, Encode_type.BIN.value], "is_save_device": None, "param_id": "plug_charge_is", "param_type": DB_Data_Type.DATA_INT.value},
    3: {"encode": [1, Encode_type.BIN.value], "is_save_device": None, "param_id": "card_charge_is", "param_type": DB_Data_Type.DATA_INT.value},
    4: {"encode": [1, Encode_type.BIN.value], "is_save_device": None, "param_id": "insulation_inspection_is", "param_type": DB_Data_Type.DATA_INT.value},
    5: {"encode": [1, Encode_type.BIN.value], "is_save_device": None, "param_id": "BSM_failure_stop_charge_is", "param_type": DB_Data_Type.DATA_INT.value},
    6: {"encode": [1, Encode_type.BIN.value], "is_save_device": None, "param_id": "lock_failure_detection_is", "param_type": DB_Data_Type.DATA_INT.value},
    7: {"encode": [1, Encode_type.BIN.value], "is_save_device": None, "param_id": "guard_detection_is", "param_type": DB_Data_Type.DATA_INT.value},
    8: {"encode": [1, Encode_type.BIN.value], "is_save_device": None, "param_id": "auxiliary_power_is", "param_type": DB_Data_Type.DATA_INT.value},
    9: {"encode": [1, Encode_type.BIN.value], "is_save_device": None, "param_id": "BHM_timeout", "param_type": DB_Data_Type.DATA_INT.value},
    10: {"encode": [1, Encode_type.BIN.value], "is_save_device": None, "param_id": "BRM_timeout", "param_type": DB_Data_Type.DATA_INT.value},
    11: {"encode": [1, Encode_type.BIN.value], "is_save_device": None, "param_id": "BCP_timeout", "param_type": DB_Data_Type.DATA_INT.value},
    12: {"encode": [1, Encode_type.BIN.value], "is_save_device": None, "param_id": "BRO_00_timeout", "param_type": DB_Data_Type.DATA_INT.value},
    13: {"encode": [1, Encode_type.BIN.value], "is_save_device": None, "param_id": "BRO_AA_timeout", "param_type": DB_Data_Type.DATA_INT.value},
    14: {"encode": [1, Encode_type.BIN.value], "is_save_device": None, "param_id": "BCL_timeout", "param_type": DB_Data_Type.DATA_INT.value},
    15: {"encode": [1, Encode_type.BIN.value], "is_save_device": None, "param_id": "BCS_timeout", "param_type": DB_Data_Type.DATA_INT.value},
    16: {"encode": [1, Encode_type.BIN.value], "is_save_device": None, "param_id": "BSM_timeout", "param_type": DB_Data_Type.DATA_INT.value},
    17: {"encode": [1, Encode_type.BIN.value], "is_save_device": None, "param_id": "out_vol_threshold", "param_type": DB_Data_Type.DATA_INT.value},
    18: {"encode": [1, Encode_type.BIN.value], "is_save_device": None, "param_id": "start_charging_limit_time_param", "param_type": DB_Data_Type.DATA_INT.value},
    19: {"encode": [1, Encode_type.BIN.value], "is_save_device": None, "param_id": "function_reboot", "param_type": DB_Data_Type.DATA_INT.value},
    20: {"encode": [1, Encode_type.BIN.value], "is_save_device": None, "param_id": "function_power_control", "param_type": DB_Data_Type.DATA_INT.value},
    21: {"encode": [1, Encode_type.BIN.value], "is_save_device": None, "param_id": "function_double_gun_charge", "param_type": DB_Data_Type.DATA_INT.value},
    22: {"encode": [1, Encode_type.BIN.value], "is_save_device": None, "param_id": "function_offline_charhe", "param_type": DB_Data_Type.DATA_INT.value},
}


def get_datatime():
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d-%H:%M:%S")
    return formatted_time


"""
/* #################################################### 数据信息 #######################################################*/
"""

"""
/* ##################################################### 组码 #########################################################*/
"""


def pack(msg, cmd):
    try:
        protocol = Protocol_Decode(msg, cmd)
        return protocol.protocol_message()
    except Exception as e:
        HSyslog.log_info(f"pack error: {msg} {cmd} {e}")


class Protocol_Decode:
    def __init__(self, msg: list, cmd: int):
        self.msg = msg
        self.header_code = info_to_hex(Msg_Header, 2, Encode_type.BIN.value)
        self.length_code = None
        self.info_code = info_to_hex(SDK_Info, 4, Encode_type.BIN.value)
        self.serial_code = None
        self.cmd_code = info_to_hex(cmd, 2, Encode_type.BIN.value)
        self.datas = msg
        self.check_code = None

    def Pprint(self):
        HSyslog.log_info(f"msg: {self.msg}")
        HSyslog.log_info(f"header_code: {self.header_code}")
        HSyslog.log_info(f"length_code: {self.length_code}")
        HSyslog.log_info(f"info_code: {self.info_code}")
        HSyslog.log_info(f"serial_code: {self.serial_code}")
        HSyslog.log_info(f"cmd_code: {self.cmd_code}")
        HSyslog.log_info(f"datas: {self.datas}")
        HSyslog.log_info(f"check_code: {self.check_code}")

    def list_to_bytes(self, msg):
        return bytes(msg)

    def get_serial_code(self):
        global serial_code
        self.serial_code = info_to_hex(serial_code, 4, Encode_type.BIN.value)
        if serial_code >= End_Service_Code:
            serial_code = Start_Service_Code
        else:
            serial_code += 1
        return True

    def get_length_code(self):
        length_code = 2 + 2 + 4 + 4 + 2 + 1 + len(self.datas)
        self.length_code = info_to_hex(length_code, 2, Encode_type.BIN.value)
        return True

    def get_check_code(self):
        if not self.datas:
            self.check_code = 0
            return False
        check_code = 0
        for data in self.datas + self.cmd_code:
            check_code += data
        self.check_code = info_to_hex(check_code % 127, 1, Encode_type.BIN.value)
        return True

    def protocol_message(self):
        self.get_serial_code()
        self.get_length_code()
        self.get_check_code()

        msg = []
        msg += self.header_code
        msg += self.length_code
        msg += self.info_code
        msg += self.serial_code
        msg += self.cmd_code
        msg += self.datas
        msg += self.check_code
        # HSyslog.log_info(f"protocol_message_list: {msg}")
        msg = self.list_to_bytes(msg)
        tpp_send_data.put(msg)
        return msg


def info_to_ascii(info, info_len, info_mode):
    if not isinstance(info, str):  # 如果是整数，转换为单元素列表
        info = str(info)

    info_byte = info.encode('utf-8')
    padding_needed = max(0, info_len - len(info_byte))
    padded_bytes = info_byte + b'\x00' * padding_needed

    if info_mode == Big_Little.BIG.value:
        format_str = f'>{info_len}s'
        info_byte = struct.pack(format_str, padded_bytes)
        info_list = list(info_byte)
        return info_list
    if info_mode == Big_Little.LITTLE.value:
        format_str = f'<{info_len}s'
        info_byte = struct.pack(format_str, padded_bytes)
        info_list = list(info_byte)
        return info_list


def info_to_bin(info, info_len, info_mode):
    if not isinstance(info, int):
        return []
    if info_len < 1:
        raise ValueError("info_len must be greater than 0.")

    byte_length = (info.bit_length() + 7) // 8  # 计算 info 所需的字节数
    if byte_length > info_len:
        raise ValueError(f"info is too large to fit in {info_len} bytes.")

    if info_mode == Big_Little.BIG.value:
        info_bytes = info.to_bytes(info_len, byteorder='big')  # 大端
    elif info_mode == Big_Little.LITTLE.value:
        info_bytes = info.to_bytes(info_len, byteorder='little')  # 小端
    else:
        raise ValueError(f"Invalid info_mode: {info_mode}. Expected 1 (BIG) or 2 (LITTLE).")

    return list(info_bytes)


def info_to_version(info, info_len, info_mode):
    if not isinstance(info, str):
        info = str(info)

    version_list = info[2:].split('.')
    # 处理每个版本号部分并转换为对应的十六进制表示
    if len(version_list) != 3:
        for i in range(0, 3 - len(version_list)):
            version_list.append('0')
    version_array = []

    print(version_list)

    # 处理第一个部分，分高低字节
    first_part = int(version_list[0])
    high_byte = (first_part >> 8) & 0xFF  # 取高字节
    low_byte = first_part & 0xFF  # 取低字节
    version_array.extend([high_byte, low_byte])

    print(version_array)

    # 处理剩余的部分，不分高低字节
    for part in version_list[1:]:
        version_array.append(int(part))

    # 根据端模式调整顺序
    if info_mode == Big_Little.BIG.value:
        version_array = version_array[::-1]

    return version_array


def info_to_time(info, info_len, info_mode):
    info = datetime.fromtimestamp(info).strftime("%Y%m%d%H%M%S")  # 假设最后的 "15" 固定为附加值
    bcd_bytes = bytearray()
    for i in range(0, len(info), 2):
        if i + 1 < len(info):
            bcd_value = (int(info[i]) << 4) | int(info[i + 1])
        else:
            bcd_value = int(info[i]) << 4

        bcd_bytes.append(bcd_value)
    if len(bcd_bytes) < info_len:
        bcd_bytes.extend([0xFF] * (info_len - len(bcd_bytes)))
    bcd_list = list(bcd_bytes[:info_len])
    return bcd_list


def info_to_md5(info, info_len, info_mode):
    if not isinstance(info, str):
        info = str(info)
    if len(info) < 6:
        md5_hash = [0x00] * 32
    elif len(info) > 6:
        md5_hash = [0xFF] * 32
    else:
        md5_hash = []
        info_bytes = hashlib.md5(info.encode()).hexdigest()
        for i in range(0, len(info_bytes), 2):
            md5_hash.append(int(f"0x{info_bytes[i:i + 2]}", 16))
    return md5_hash


def info_to_mac(info, info_len, info_mode):
    if not isinstance(info, str):
        info = str(info)

    # 将MAC地址字符串拆分为字节列表
    mac_bytes = []

    for byte in info:
        mac_bytes.append(ord(byte))

    # 将MAC字节填入到列表并在末尾补零到32字节
    byte_array = mac_bytes + [0] * (32 - len(mac_bytes))

    # 根据端模式调整每6字节的顺序
    if info_mode == Big_Little.BIG.value:
        # 对前面的MAC字节部分每6字节块反转
        byte_array[:len(mac_bytes)] = [byte for i in range(0, len(mac_bytes), 6)
                                       for byte in reversed(byte_array[i:i + 6])]

    return byte_array


def info_to_encrypt_version(info, info_len, info_mode):
    if not isinstance(info, int):
        return []
    if info_len < 1:
        raise ValueError("info_len must be greater than 0.")

    byte_length = (info.bit_length() + 7) // 8  # 计算 info 所需的字节数
    if byte_length > info_len:
        raise ValueError(f"info is too large to fit in {info_len} bytes.")

    info_year = info // 10000
    info_mou = info % 10000 // 100
    info_day = info % 100

    info_bytes = []
    info_bytes += info_year.to_bytes(2, byteorder='big')  # 大端
    info_bytes += info_mou.to_bytes(1, byteorder='big')  # 大端
    info_bytes += info_day.to_bytes(1, byteorder='big')  # 大端

    return info_bytes


def info_to_hex(info, info_len, info_type, info_mode=INFO_MODEL):
    result = None
    try:
        if info_type == Encode_type.ASCII.value:
            result = info_to_ascii(info, info_len, info_mode)
        if info_type == Encode_type.BIN.value:
            result = info_to_bin(info, info_len, info_mode)
        if info_type == Encode_type.TIME.value:
            result = info_to_time(info, info_len, info_mode)
        if info_type == Encode_type.VERSION.value:
            result = info_to_version(info, info_len, info_mode)
        if info_type == Encode_type.MD5.value:
            result = info_to_md5(info, info_len, info_mode)
        if info_type == Encode_type.MAC.value:
            result = info_to_mac(info, info_len, info_mode)
        if info_type == Encode_type.ENCRYPT_VERSION.value:
            result = info_to_encrypt_version(info, info_len, info_mode)

        if result is None:
            HSyslog.log_info(f"{info} --- {info_len} --- {info_type}")
            return [0x00] * info_len
        else:
            # HSyslog.log_info(result)
            return result
    except Exception as e:
        HSyslog.log_info(f"input_data: .{info} .{e}")
        return None


"""
/* ##################################################### 组码 #########################################################*/
"""

"""
/* ##################################################### 解码 #########################################################*/
"""


def unpack(msg):
    try:
        protocol = Protocol_Encode(msg)
        # protocol.Pprint()
        return protocol.protocol_message()
    except Exception as e:
        HSyslog.log_info(f"unpack error: {msg} {e}")


class Protocol_Encode:
    def __init__(self, msg):
        self.msg = self.bytes_to_hex_list(msg.decode('utf-8').encode('iso-8859-1'))
        self.header_code = hex_to_info(self.msg[0:2], Encode_type.BIN.value)
        self.length_code = hex_to_info(self.msg[2:4], Encode_type.BIN.value)
        self.info_code = self.msg[4:8]
        self.serial_code = hex_to_info(self.msg[8:12], Encode_type.BIN.value)
        self.cmd_code = self.msg[12:14]
        self.datas = self.msg[14:-1]
        self.check_code = hex_to_info(self.msg[-1:], Encode_type.BIN.value)
        self.callback_func = None

    def Pprint(self):
        HSyslog.log_info(f"msg: {self.msg}")
        HSyslog.log_info(f"header_code: {self.header_code}")
        HSyslog.log_info(f"length_code: {self.length_code}")
        HSyslog.log_info(f"info_code: {self.info_code}")
        HSyslog.log_info(f"serial_code: {self.serial_code}")
        HSyslog.log_info(f"cmd_code: {self.cmd_code}")
        HSyslog.log_info(f"datas: {self.datas}")
        HSyslog.log_info(f"check_code: {self.check_code}")

    def bytes_to_hex_list(self, msg):
        bytecode_list = list(msg)
        return bytecode_list

    def cleck_header_code(self):
        if self.header_code == Msg_Header:
            return True
        else:
            return False

    def cleck_length_code(self):
        if self.length_code == len(self.msg):
            return True
        else:
            HSyslog.log_info(f"cleck_length_code error: {self.length_code} -- {len(self.msg)}")
            return False

    def cleck_info_code(self):
        if self.info_code == SDK_List:
            return True
        else:
            return True

    def cleck_serial_code(self):
        return self.serial_code

    def cleck_cmd_code(self):
        self.cmd_code = hex_to_info(self.cmd_code, Encode_type.BIN.value)
        if self.cmd_code in tpp_mqtt_cmd_type.keys():
            return True
        else:
            HSyslog.log_info(f"cleck_cmd_code error: {self.cmd_code} -- {self.cmd_code}")
            return False

    def cleck_check_code(self):
        if not self.datas:
            return False
        check_code = 0
        for data in self.datas + self.cmd_code:
            check_code += data

        if self.check_code == check_code % 127:
            return True
        else:
            HSyslog.log_info(f"cleck_check_code error: {self.check_code} -- {check_code % 127}")
            return True

    def cleck_func(self):
        if self.cleck_header_code() and self.cleck_length_code() and self.cleck_info_code() and self.cleck_check_code() and self.cleck_cmd_code():
            self.callback_func = tpp_mqtt_cmd_type.get(self.cmd_code).get("func")
            return True
        else:
            HSyslog.log_info(f"cleck_func error")
            return False

    def protocol_message(self):
        if not self.cleck_func():
            return False
        if not isinstance(self.datas, list):  # 如果是整数，转换为单元素列表
            self.datas = [self.datas]
        result = self.callback_func(self.datas)
        if result == {}:
            return False
        else:
            return True


def ascii_list_to_info(hex_list, hex_mode):
    if not isinstance(hex_list, list):  # 如果是整数，转换为单元素列表
        hex_list = [hex_list]

    packed_bytes = bytes(hex_list)
    result_str = ""
    index = 0
    while index < len(packed_bytes):
        byte = packed_bytes[index]
        if byte == 0:
            break
        result_str += chr(byte)
        index += 1

    return result_str


def bin_list_to_info(hex_list, hex_mode):
    if isinstance(hex_list, int):  # 如果是整数，转换为单元素列表
        hex_list = [hex_list]
    hex_byte = bytes(hex_list)
    format_str = {
        1: 'B',  # 1字节无符号整数
        2: 'H',  # 2字节无符号整数
        4: 'I',  # 4字节无符号整数
        8: 'Q'  # 8字节无符号整数
    }.get(len(hex_list), 'H')  # 默认为8字节

    if hex_mode == Big_Little.BIG.value:
        hex_int = struct.unpack(f">{format_str}", hex_byte)[0]
        return hex_int
    if hex_mode == Big_Little.LITTLE.value:
        hex_int = struct.unpack(f"<{format_str}", hex_byte)[0]
        return hex_int


def time_list_to_info(hex_list: list, hex_mode):
    result_str = ""
    for byte in hex_list:
        high_nibble = (byte >> 4) & 0x0F
        low_nibble = byte & 0x0F

        result_str += str(high_nibble)
        if low_nibble != 0x0F:
            result_str += str(low_nibble)

    if result_str == "0000000000000000":
        return 0
    else:
        dt = datetime.strptime(result_str[:14], "%Y%m%d%H%M%S")
        timestamp = int(dt.timestamp())

    return timestamp


def version_list_to_info(hex_list, hex_mode):
    if isinstance(hex_list, int):  # 如果是整数，转换为单元素列表
        hex_list = [hex_list]
    hex_byte = bytes(hex_list)
    format_str = {
        1: 'B',  # 1字节无符号整数
        2: 'H',  # 2字节无符号整数
        4: 'I',  # 4字节无符号整数
        8: 'Q'  # 8字节无符号整数
    }.get(len(hex_list), 'H')  # 默认为8字节

    if hex_mode == Big_Little.BIG.value:
        hex_int = struct.unpack(f">{format_str}", hex_byte)[0]
        if 9999 < hex_int < 100000:
            hex_str = f"0{str(hex_int)}"
        elif 999 < hex_int < 10000:
            hex_str = f"00{str(hex_int)}"
        elif 99 < hex_int < 1000:
            hex_str = f"000{str(hex_int)}"
        elif 9 < hex_int < 100:
            hex_str = f"0000{str(hex_int)}"
        elif 0 < hex_int < 10:
            hex_str = f"00000{str(hex_int)}"
        elif 0 == hex_int:
            hex_str = f"000000"
        else:
            hex_str = f"{str(hex_int)}"
        hex_str = f"A{hex_str[0:2]}.{hex_str[2:4]}.{hex_str[4:6]}"
        return hex_str
    if hex_mode == Big_Little.LITTLE.value:
        hex_int = struct.unpack(f"<{format_str}", hex_byte)[0]
        if 9999 < hex_int < 100000:
            hex_str = f"0{str(hex_int)}"
        elif 999 < hex_int < 10000:
            hex_str = f"00{str(hex_int)}"
        elif 99 < hex_int < 1000:
            hex_str = f"000{str(hex_int)}"
        elif 9 < hex_int < 100:
            hex_str = f"0000{str(hex_int)}"
        elif 0 < hex_int < 10:
            hex_str = f"00000{str(hex_int)}"
        elif 0 == hex_int:
            hex_str = f"000000"
        else:
            hex_str = f"{str(hex_int)}"
        hex_str = f"A{hex_str[0:2]}.{hex_str[2:4]}.{hex_str[4:6]}"

        return hex_str


def ip_list_to_info(hex_list, hex_mode):
    ip = ""
    for i in range(0, len(hex_list)):
        ip += str(hex_list[i])
        if i == len(hex_list) - 1:
            break
        ip += "."
    return ip


def encrypt_version_list_to_info(hex_list, hex_mode):
    if isinstance(hex_list, int):  # 如果是整数，转换为单元素列表
        hex_list = [hex_list]
    hex_byte_year = bytes(hex_list[0:2])
    hex_byte_mou = bytes([hex_list[2]])
    hex_byte_day = bytes([hex_list[3]])

    hex_int_year = struct.unpack(">H", hex_byte_year)[0]
    hex_int_mou = struct.unpack(">B", hex_byte_mou)[0]
    hex_int_day = struct.unpack(">B", hex_byte_day)[0]

    return hex_int_year * 10000 + hex_int_mou * 100 + hex_int_day


def hex_to_info(hex_list, hex_type, hex_mode=INFO_MODEL):
    if hex_type == Encode_type.ASCII.value:
        return ascii_list_to_info(hex_list, hex_mode)
    if hex_type == Encode_type.BIN.value:
        return bin_list_to_info(hex_list, hex_mode)
    if hex_type == Encode_type.TIME.value:
        return time_list_to_info(hex_list, hex_mode)
    if hex_type == Encode_type.VERSION.value:
        return version_list_to_info(hex_list, hex_mode)
    if hex_type == Encode_type.IP.value:
        return ip_list_to_info(hex_list, hex_mode)
    if hex_type == Encode_type.ENCRYPT_VERSION.value:
        return encrypt_version_list_to_info(hex_list, hex_mode)


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
            soft_version TEXT
        )
    ''')  # 版本号
    cur.execute('''
        CREATE TABLE IF NOT EXISTS DeviceInfo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_id TEXT,
            data_type INTEGER,
            data_str TEXT,
            data_int INTEGER
        )
    ''')  # 参数
    cur.execute('''
        CREATE TABLE IF NOT EXISTS FeeModel (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            num INTEGER,
            type INTEGER,
            start_time INTEGER,
            stop_time INTEGER,
            electric_rate INTEGER,
            service_rate INTEGER,
            delay_rate INTEGER
        )
    ''')  # 费率
    cur.execute('''
            CREATE TABLE IF NOT EXISTS HistoryOrder (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gun_id INTEGER,
                charge_id TEXT,
                device_session_id TEXT,
                cloud_session_id TEXT,
                confirm_is INTEGER
            )
        ''')  # 历史记录
    cur.execute('''
        CREATE TABLE IF NOT EXISTS DeviceOrder (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT,
            gun_type INTEGER,
            gun_id INTEGER,
            charge_id TEXT,
            charge_start_time INTEGER,
            charge_stop_time INTEGER,
            charge_time INTEGER,
            charge_start_soc INTEGER,
            charge_stop_soc INTEGER,
            charge_stop_reason TEXT,
            charge_kwh_amount INTEGER,
            charge_start_meter INTEGER,
            charge_stop_meter INTEGER,
            charge_cost INTEGER,
            charge_card_stop_is INTEGER,
            charge_start_balance INTEGER,
            charge_stop_balance INTEGER,
            charge_server_cost INTEGER,
            pay_offline_is INTEGER,
            charge_policy INTEGER,
            charge_policy_param INTEGER,
            car_vin TEXT,
            car_card TEXT,
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
            start_source INTEGER,
            device_session_id TEXT,
            cloud_session_id TEXT
        )
    ''')  # 记录

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
        if result[2] == DB_Data_Type.DATA_STR.value:
            return result[3]
        if result[2] == DB_Data_Type.DATA_INT.value:
            return result[4]


def save_VerInfoEvt(device_id, device_type, hard_version, soft_version):
    conn = sqlite3.connect(data_path)
    cur = conn.cursor()
    if get_VerInfoEvt(device_type)[1] is None:
        cur.execute(
            '''INSERT INTO VerInfoEvt (device_id, device_type, hard_version, soft_version) VALUES (?, ?, ?, ?)''',
            (device_id, device_type, hard_version, soft_version))
    else:
        cur.execute(
            '''UPDATE VerInfoEvt SET device_id = ?, hard_version = ?, soft_version = ? WHERE device_type = ?''',
            (device_id, hard_version, soft_version, device_type))
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
        return result[3], result[4]


def save_FeeModel(info_list):
    conn = sqlite3.connect(data_path)
    cur = conn.cursor()
    cur.execute('DELETE FROM FeeModel')
    for fee in info_list:
        cur.execute(
            '''INSERT INTO FeeModel (num, type, start_time, stop_time, electric_rate, service_rate, delay_rate) VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (fee.get("num"), fee.get("type"), fee.get("start_time"), fee.get("stop_time"), fee.get("electric_rate"), fee.get("service_rate"), fee.get("delay_rate")))
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
    if not get_DeviceOrder_pa_id(dict_order.get("cloud_session_id")):
        cur.execute(
            '''INSERT INTO DeviceOrder (device_id, gun_type, gun_id, charge_id, charge_start_time, charge_stop_time, charge_time, charge_start_soc, charge_stop_soc, 
            charge_stop_reason, charge_kwh_amount, charge_start_meter, charge_stop_meter, charge_cost, charge_card_stop_is, charge_start_balance, charge_stop_balance, charge_server_cost, 
            pay_offline_is, charge_policy, charge_policy_param, car_vin, car_card, 
            kwh_amount_1, kwh_amount_2, kwh_amount_3, kwh_amount_4, kwh_amount_5, kwh_amount_6, kwh_amount_7, kwh_amount_8, kwh_amount_9, kwh_amount_10, kwh_amount_11, kwh_amount_12, kwh_amount_13, kwh_amount_14, 
            kwh_amount_15, kwh_amount_16, kwh_amount_17, kwh_amount_18, kwh_amount_19, kwh_amount_20, kwh_amount_21, kwh_amount_22, kwh_amount_23, kwh_amount_24, kwh_amount_25, kwh_amount_26, kwh_amount_27, kwh_amount_28, 
            kwh_amount_29, kwh_amount_30, kwh_amount_31, kwh_amount_32, kwh_amount_33, kwh_amount_34, kwh_amount_35, kwh_amount_36, kwh_amount_37, kwh_amount_38, kwh_amount_39, kwh_amount_40, kwh_amount_41, kwh_amount_42, 
            kwh_amount_43, kwh_amount_44, kwh_amount_45, kwh_amount_46, kwh_amount_47, kwh_amount_48, 
            start_source, device_session_id, cloud_session_id) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (dict_order.get("device_id"), dict_order.get("gun_type"), dict_order.get("gun_id"), dict_order.get("charge_id"), dict_order.get("charge_start_time"), dict_order.get("charge_stop_time"),
             dict_order.get("charge_time"), dict_order.get("charge_start_soc"), dict_order.get("charge_stop_soc"), dict_order.get("charge_stop_reason"), dict_order.get("charge_kwh_amount"), dict_order.get("charge_start_meter"),
             dict_order.get("charge_stop_meter"), dict_order.get("charge_cost"), dict_order.get("charge_card_stop_is"), dict_order.get("charge_start_balance"), dict_order.get("charge_stop_balance"), dict_order.get("charge_server_cost"),
             dict_order.get("pay_offline_is"), dict_order.get("charge_policy"), dict_order.get("charge_policy_param"), dict_order.get("car_vin"), dict_order.get("car_card"),
             dict_order.get("kwh_amount")[0], dict_order.get("kwh_amount")[1], dict_order.get("kwh_amount")[2], dict_order.get("kwh_amount")[3], dict_order.get("kwh_amount")[4], dict_order.get("kwh_amount")[5], dict_order.get("kwh_amount")[6], dict_order.get("kwh_amount")[7],
             dict_order.get("kwh_amount")[8], dict_order.get("kwh_amount")[9], dict_order.get("kwh_amount")[10], dict_order.get("kwh_amount")[11], dict_order.get("kwh_amount")[12], dict_order.get("kwh_amount")[13], dict_order.get("kwh_amount")[14], dict_order.get("kwh_amount")[15],
             dict_order.get("kwh_amount")[16], dict_order.get("kwh_amount")[17], dict_order.get("kwh_amount")[18], dict_order.get("kwh_amount")[19], dict_order.get("kwh_amount")[20], dict_order.get("kwh_amount")[21], dict_order.get("kwh_amount")[22], dict_order.get("kwh_amount")[23],
             dict_order.get("kwh_amount")[24], dict_order.get("kwh_amount")[25], dict_order.get("kwh_amount")[26], dict_order.get("kwh_amount")[27], dict_order.get("kwh_amount")[28], dict_order.get("kwh_amount")[29], dict_order.get("kwh_amount")[30], dict_order.get("kwh_amount")[31],
             dict_order.get("kwh_amount")[32], dict_order.get("kwh_amount")[33], dict_order.get("kwh_amount")[34], dict_order.get("kwh_amount")[35], dict_order.get("kwh_amount")[36], dict_order.get("kwh_amount")[37], dict_order.get("kwh_amount")[38], dict_order.get("kwh_amount")[39],
             dict_order.get("kwh_amount")[40], dict_order.get("kwh_amount")[41], dict_order.get("kwh_amount")[42], dict_order.get("kwh_amount")[43], dict_order.get("kwh_amount")[44], dict_order.get("kwh_amount")[45], dict_order.get("kwh_amount")[46], dict_order.get("kwh_amount")[47],
             dict_order.get("start_source"), dict_order.get("device_session_id"), dict_order.get("cloud_session_id")))
    else:
        cur.execute(
            '''UPDATE DeviceOrder SET device_id = ?, gun_type = ?, gun_id = ?, charge_id = ?, charge_start_time = ?, 
            charge_stop_time = ?, charge_time = ?, charge_start_soc = ?, charge_stop_soc = ?, charge_stop_reason = ?, charge_kwh_amount = ?, 
            charge_start_meter = ?, charge_stop_meter = ?, charge_cost = ?, charge_card_stop_is = ?, charge_start_balance = ?, charge_stop_balance = ?, charge_server_cost = ?, 
            pay_offline_is = ?, charge_policy = ?, charge_policy_param = ?, car_vin = ?, car_card = ?, 
            kwh_amount_1 = ?, kwh_amount_2 = ?, kwh_amount_3 = ?, kwh_amount_4 = ?, kwh_amount_5 = ?, kwh_amount_6 = ?, kwh_amount_7 = ?, kwh_amount_8 = ?, 
            kwh_amount_9 = ?, kwh_amount_10 = ?, kwh_amount_11 = ?, kwh_amount_12 = ?, kwh_amount_13 = ?, kwh_amount_14 = ?, kwh_amount_15 = ?, kwh_amount_16 = ?, 
            kwh_amount_17 = ?, kwh_amount_18 = ?, kwh_amount_19 = ?, kwh_amount_20 = ?, kwh_amount_21 = ?, kwh_amount_22 = ?, kwh_amount_23 = ?, kwh_amount_24 = ?, 
            kwh_amount_25 = ?, kwh_amount_26 = ?, kwh_amount_27 = ?, kwh_amount_28 = ?, kwh_amount_29 = ?, kwh_amount_30 = ?, kwh_amount_31 = ?, kwh_amount_32 = ?, 
            kwh_amount_33 = ?, kwh_amount_34 = ?, kwh_amount_35 = ?, kwh_amount_36 = ?, kwh_amount_37 = ?, kwh_amount_38 = ?, kwh_amount_39 = ?, kwh_amount_40 = ?, 
            kwh_amount_41 = ?, kwh_amount_42 = ?, kwh_amount_43 = ?, kwh_amount_44 = ?, kwh_amount_45 = ?, kwh_amount_46 = ?, kwh_amount_47 = ?, kwh_amount_48 = ?, 
            start_source = ?, cloud_session_id = ?
            WHERE device_session_id = ? ''',
            (dict_order.get("device_id"), dict_order.get("gun_type"), dict_order.get("gun_id"),
             dict_order.get("charge_id"), dict_order.get("charge_start_time"), dict_order.get("charge_stop_time"),
             dict_order.get("charge_time"), dict_order.get("charge_start_soc"), dict_order.get("charge_stop_soc"),
             dict_order.get("charge_stop_reason"), dict_order.get("charge_kwh_amount"), dict_order.get("charge_start_meter"),
             dict_order.get("charge_stop_meter"), dict_order.get("charge_cost"), dict_order.get("charge_card_stop_is"),
             dict_order.get("charge_start_balance"), dict_order.get("charge_stop_balance"), dict_order.get("charge_server_cost"),
             dict_order.get("pay_offline_is"), dict_order.get("charge_policy"), dict_order.get("charge_policy_param"),
             dict_order.get("car_vin"), dict_order.get("car_card"),
             dict_order.get("kwh_amount")[0], dict_order.get("kwh_amount")[1], dict_order.get("kwh_amount")[2], dict_order.get("kwh_amount")[3], dict_order.get("kwh_amount")[4], dict_order.get("kwh_amount")[5], dict_order.get("kwh_amount")[6], dict_order.get("kwh_amount")[7],
             dict_order.get("kwh_amount")[8], dict_order.get("kwh_amount")[9], dict_order.get("kwh_amount")[10], dict_order.get("kwh_amount")[11], dict_order.get("kwh_amount")[12], dict_order.get("kwh_amount")[13], dict_order.get("kwh_amount")[14], dict_order.get("kwh_amount")[15],
             dict_order.get("kwh_amount")[16], dict_order.get("kwh_amount")[17], dict_order.get("kwh_amount")[18], dict_order.get("kwh_amount")[19], dict_order.get("kwh_amount")[20], dict_order.get("kwh_amount")[21], dict_order.get("kwh_amount")[22], dict_order.get("kwh_amount")[23],
             dict_order.get("kwh_amount")[24], dict_order.get("kwh_amount")[25], dict_order.get("kwh_amount")[26], dict_order.get("kwh_amount")[27], dict_order.get("kwh_amount")[28], dict_order.get("kwh_amount")[29], dict_order.get("kwh_amount")[30], dict_order.get("kwh_amount")[31],
             dict_order.get("kwh_amount")[32], dict_order.get("kwh_amount")[33], dict_order.get("kwh_amount")[34], dict_order.get("kwh_amount")[35], dict_order.get("kwh_amount")[36], dict_order.get("kwh_amount")[37], dict_order.get("kwh_amount")[38], dict_order.get("kwh_amount")[39],
             dict_order.get("kwh_amount")[40], dict_order.get("kwh_amount")[41], dict_order.get("kwh_amount")[42], dict_order.get("kwh_amount")[43], dict_order.get("kwh_amount")[44], dict_order.get("kwh_amount")[45], dict_order.get("kwh_amount")[46], dict_order.get("kwh_amount")[47],
             dict_order.get("start_source"), dict_order.get("cloud_session_id")))
    conn.commit()
    conn.close()


def get_DeviceOrder_pa_id(cloud_session_id):
    conn = sqlite3.connect(data_path)
    cur = conn.cursor()
    cur.execute('SELECT * FROM DeviceOrder WHERE cloud_session_id = ?', (cloud_session_id,))
    result = cur.fetchone()
    conn.commit()
    conn.close()
    if result is None:
        return {}
    else:
        kwh_amount = []
        for i in range(24, 72):
            kwh_amount.append(result[i])
        info = {
            "device_id": result[1],
            "gun_type": result[2],
            "gun_id": result[3],
            "charge_id": result[4],
            "charge_start_time": result[5],
            "charge_stop_time": result[6],
            "charge_time": result[7],
            "charge_start_soc": result[8],
            "charge_stop_soc": result[9],
            "charge_stop_reason": result[10],
            "charge_kwh_amount": result[11],
            "charge_start_meter": result[12],
            "charge_stop_meter": result[13],
            "charge_cost": result[14],
            "charge_card_stop_is": result[15],
            "charge_start_balance": result[16],
            "charge_stop_balance": result[17],
            "charge_server_cost": result[18],
            "pay_offline_is": result[19],
            "charge_policy": result[20],
            "charge_policy_param": result[21],
            "car_vin": result[22],
            "car_card": result[23],
            "kwh_amount": kwh_amount,
            "start_source": result[-3],
            "device_session_id": result[-2],
            "cloud_session_id": result[-1],
        }
        return info


def get_DeviceOrder_de_id(device_session_id):
    conn = sqlite3.connect(data_path)
    cur = conn.cursor()
    cur.execute('SELECT * FROM DeviceOrder WHERE device_session_id = ?', (device_session_id,))
    result = cur.fetchone()
    conn.commit()
    conn.close()
    if result is None:
        return {}
    else:
        kwh_amount = []
        for i in range(24, 72):
            kwh_amount.append(result[i])
        info = {
            "device_id": result[1],
            "gun_type": result[2],
            "gun_id": result[3],
            "charge_id": result[4],
            "charge_start_time": result[5],
            "charge_stop_time": result[6],
            "charge_time": result[7],
            "charge_start_soc": result[8],
            "charge_stop_soc": result[9],
            "charge_stop_reason": result[10],
            "charge_kwh_amount": result[11],
            "charge_start_meter": result[12],
            "charge_stop_meter": result[13],
            "charge_cost": result[14],
            "charge_card_stop_is": result[15],
            "charge_start_balance": result[16],
            "charge_stop_balance": result[17],
            "charge_server_cost": result[18],
            "pay_offline_is": result[19],
            "charge_policy": result[20],
            "charge_policy_param": result[21],
            "car_vin": result[22],
            "car_card": result[23],
            "kwh_amount": kwh_amount,
            "start_source": result[-3],
            "device_session_id": result[-2],
            "cloud_session_id": result[-1],
        }
        return info


def save_HistoryOrder(dict_info: dict):
    conn = sqlite3.connect(data_path)
    cur = conn.cursor()
    cur.execute(
        '''INSERT INTO HistoryOrder (gun_id, charge_id, device_session_id, cloud_session_id, confirm_is) 
        VALUES (?, ?, ?, ?, ?)''',
        (dict_info.get("gun_id"), dict_info.get("charge_id"), dict_info.get("device_session_id"), dict_info.get("cloud_session_id"), dict_info.get("confirm_is")))
    conn.commit()
    conn.close()


def get_HistoryOrder():
    conn = sqlite3.connect(data_path)
    cur = conn.cursor()
    order_list = []
    cur.execute('SELECT * FROM HistoryOrder')
    result = cur.fetchall()
    conn.commit()
    conn.close()
    for order in result:
        if order[5] == 0:
            info = {
                "gun_id": order[1],
                "charge_id": order[2],
                "device_session_id": order[3],
                "cloud_session_id": order[4],
                "confirm_is": order[5],
            }
            order_list.append(info)
    return order_list


def set_HistoryOrder(dict_info: dict):
    conn = sqlite3.connect(data_path)
    cur = conn.cursor()
    gun_id = dict_info.get("gun_id")
    charge_id = dict_info.get("charge_id")
    confirm_is = dict_info.get("confirm_is")
    cur.execute('SELECT * FROM HistoryOrder WHERE charge_id = ?', (charge_id,))
    result = cur.fetchone()
    if result is None:
        conn.commit()
        conn.close()
        return False
    else:
        if result[1] == gun_id:
            if confirm_is == 1:
                cur.execute('''UPDATE HistoryOrder SET confirm_is = ? WHERE charge_id = ?''', (confirm_is, charge_id))
                HSyslog.log_info(f"{charge_id} confirm: {confirm_is}")
                conn.commit()
                conn.close()
                return True
            else:
                conn.commit()
                conn.close()
                return False
        else:
            conn.commit()
            conn.close()
            return False


"""
/* #################################################### 数据库 #########################################################*/
"""
