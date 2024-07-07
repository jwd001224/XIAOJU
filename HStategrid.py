import queue
from enum import Enum

serial_code = 0x00000000
Enterprise_code = 0x7DD0

xj_send_data = queue.Queue()
xj_resv_data = queue.Queue()

ack_data = {
    "serial_code": None,
    "cmd_code": None,
    "send_data": None,
    "send_num": None
}


def get_check_sum(data, cmd):
    return hex((sum(data) + cmd) % 127)


def get_byte_count(data: str):
    hex_bytes = bytes.fromhex(data)
    byte_count = len(hex_bytes)
    return byte_count


def protocol_base(d_data: dict):  # 设备发送，平台接收
    global serial_code
    if serial_code == 0xffffffff:
        serial_code = 0x00000000

    info = {
        "header_code": Enterprise_code,
        "length_code": 2 + 2 + 4 + 4 + 2 + 1,
        "version_code": 0x000A0003,
        "serial_code": serial_code,
        "cmd_code": d_data.get("cmd_code"),
        "check_code": get_check_sum(d_data.get("data"), d_data.get("cdm_code")),
        "datas": d_data.get("cdm_code"),
    }
    return info


class Protocol:
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

    def cleck_qos(self):
        for cmd, func in xj_mqtt_cmd_type.items():
            if cmd == self.cleck_cmd():
                self.qos = func["func"]


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
    int.from_bytes(p_data[-4:], byteorder='little')
    info = {
        "cmd_type": p_data[4],
        "cmd_num": p_data[9],
        "cmd_len": p_data[10:12],
        "start_addr": p_data[5:9],
        "data": p_data[12:],
        "serial_code": p_data[0:4]
    }
    return info


def xj_cmd_2(d_data: dict):  # 设备发送，平台接收
    equipment_id = d_data.get("equipment_id")
    cmd_type = d_data.get("cmd_type")
    cmd_num = d_data.get("cmd_num")
    result = d_data.get("result")
    start_addr = d_data.get("start_addr")
    data = d_data.get("data")
    serial_code = d_data.get("serial_code")
    data_len = d_data.get("data_len")  # 用于记录要发送查询的数据长度  ，但实际协议中并没有该字段

    msg = None

    return msg


def xj_cmd_3(p_data: list):  # 平台发送，设备接收
    info = {
        "cmd_type": p_data[4],
        "start_addr": p_data[5:9],
        "cmd_num": p_data[10],
        "cmd_len": p_data[9:11],
        "data": p_data[11:p_data[10] + 1],
        "serial_code": p_data[0:4]
    }
    return info


def xj_cmd_4(d_data: dict):  # 设备发送，平台接收
    equipment_id = d_data.get("equipment_id")
    cmd_type = d_data.get("cmd_type")
    result = d_data.get("result")
    start_addr = d_data.get("start_addr")
    data = d_data.get("data")
    serial_code = d_data.get("serial_code")
    dataLen = d_data.get("dataLen")  # 用于记录要发送查询的数据长度  ，但实际协议中并没有该字段

    msg = None

    return msg


def xj_cmd_5(p_data: list):  # 平台发送，设备接收
    info = {
        "gun_index": p_data[4],
        "addr": p_data[5:9],
        "cmd_num": p_data[10],
        "cmd_len": p_data[9:11],
        "cmd_param": p_data[11:p_data[10] + 1],
        "serial_code": p_data[0:4]
    }
    return info


def xj_cmd_6(d_data: dict):  # 设备发送，平台接收
    equipment_id = d_data.get("equipment_id")
    gun_index = d_data.get("gun_index")
    addr = d_data.get("addr")
    cmd_num = d_data.get("cmd_num")
    result = d_data.get("result")
    serial_code = d_data.get("serial_code")


def xj_cmd_7(p_data: list):  # 平台发送，设备接收
    info = {
        "user_tel": p_data[0],
        "gun_index": p_data[4],
        "charge_type": p_data[5:9],
        "charge_policy": p_data[10],
        "charge_policy_param": p_data[9:11],
        "book_time": p_data[11:p_data[10] + 1],
        "book_delay_time": p_data[0:4],
        "charge_user_id": p_data[4],
        "allow_offline_charge": p_data[5:9],
        "allow_offline_charge_kw_amout": p_data[10],
        "charge_delay_fee": p_data[9:11],
        "charge_delay_wait_time": p_data[11:p_data[10] + 1],
        "serial_code": p_data[0:4],
    }
    return info


def xj_cmd_8(d_data: dict):  # 设备发送，平台接收
    equipment_id = d_data.get("equipment_id")
    gun_index = d_data.get("gun_index")
    result = d_data.get("result")
    charge_user_id = d_data.get("charge_user_id")
    serial_code = d_data.get("serial_code")


def xj_cmd_11(p_data: list):  # 平台发送，设备接收
    info = {
        "equipment_id": p_data[0],
        "gun_index": p_data[4],
        "charge_seq": p_data[5:9],
        "serial_code": p_data[10],
    }
    return info


def xj_cmd_12(d_data: dict):  # 设备发送，平台接收
    equipment_id = d_data.get("equipment_id")
    gun_index = d_data.get("gun_index")
    charge_seq = d_data.get("charge_seq")
    result = d_data.get("result")
    serial_code = d_data.get("serial_code")


def xj_cmd_23(p_data: list):  # 平台发送，设备接收
    info = {
        "equipment_id": p_data[0],
        "gun_index": p_data[4],
        "lock_type": p_data[5:9],
        "serial_code": p_data[10],
    }
    return info


def xj_cmd_24(d_data: dict):  # 设备发送，平台接收
    equipment_id = d_data.get("equipment_id")
    gun_index = d_data.get("gun_index")
    result = d_data.get("result")
    serial_code = d_data.get("serial_code")


def xj_cmd_33(p_data: list):  # 平台发送，设备接收
    info = {
        "equipment_id": p_data[0],
        "gun_index": p_data[4],
        "auth_result": p_data[5:9],
        "card_money": p_data[10],
    }
    return info


def xj_cmd_35(p_data: list):  # 平台发送，设备接收
    info = {
        "gun_index": p_data[0],
        "equipment_id": p_data[4],
        "card_id": p_data[5:9],
        "result": p_data[10],
    }
    return info


def xj_cmd_41(p_data: list):  # 平台发送，设备接收
    info = {
        "equipment_id": p_data[0],
        "gun_index": p_data[4],
        "charge_user_id": p_data[5:9],
        "vin": p_data[10],
        "balance": p_data[0],
        "Request_result": p_data[4],
        "failure_reasons": p_data[5:9],
        "remainkon": p_data[10],
        "dump_energy": p_data[0],
        "residue_degree": p_data[4],
        "phone": p_data[5:9],
        "serial_code": p_data[10],
    }
    return info


def xj_cmd_34(d_data: dict):  # 设备发送，平台接收
    equipment_id = d_data.get("equipment_id")
    gun_index = d_data.get("gun_index")
    card_id = d_data.get("result")
    random_id = d_data.get("serial_code")
    phy_card_id = d_data.get("equipment_id")
    serial_code = d_data.get("gun_index")


def xj_cmd_36(d_data: dict):  # 设备发送，平台接收
    equipment_id = d_data.get("equipment_id")
    gun_index = d_data.get("gun_index")
    card_id = d_data.get("result")
    serial_code = d_data.get("serial_code")


def xj_cmd_40(d_data: dict):  # 设备发送，平台接收
    equipment_id = d_data.get("equipment_id")
    gun_index = d_data.get("gun_index")
    vin = d_data.get("result")
    serial_code = d_data.get("serial_code")


def xj_cmd_101(p_data: list):  # 平台发送，设备接收
    info = {
        "heart_index": p_data[0],
    }
    return info


def xj_cmd_102(d_data: dict):  # 设备发送，平台接收
    equipment_id = d_data.get("equipment_id")
    heart_index = d_data.get("gun_index")


def xj_cmd_103(p_data: list):  # 平台发送，设备接收
    info = {
        "gun_index": p_data[0],
        "charge_user_id": p_data[4],
        "charge_card_account": p_data[5:9],
        "accountEnoughFlag": p_data[10],
    }
    return info


def xj_cmd_104(p_data: list):  # 平台发送，设备接收
    info = {
        "equipment_id": p_data[0],
        "gun_cnt": p_data[4],
        "gun_index": p_data[5:9],
        "gun_type": p_data[10],
        "work_stat": p_data[0],
        "soc_percent": p_data[4],
        "alarm_stat": p_data[5:9],
        "car_connection_stat": p_data[10],
        "cumulative_charge_fee": p_data[0],
        "dc_charge_voltage": p_data[4],
        "dc_charge_current": p_data[5:9],
        "bms_need_voltage": p_data[10],
        "bms_need_current": p_data[0],
        "bms_charge_mode": p_data[4],
        "ac_a_vol": p_data[5:9],
        "ac_b_vol": p_data[10],
        "ac_c_vol": p_data[0],
        "ac_a_cur": p_data[4],
        "ac_b_cur": p_data[5:9],
        "ac_c_cur": p_data[10],
        "charge_full_time_left": p_data[5:9],
        "charged_sec": p_data[10],
        "cum_charge_kwh_amount": p_data[0],
        "before_charge_meter_kwh_num": p_data[4],
        "now_meter_kwh_num": p_data[5:9],
        "start_charge_type": p_data[10],
        "charge_policy": p_data[5:9],
        "book_flag": p_data[10],
        "charge_user_id": p_data[0],
        "book_timeout_min": p_data[4],
        "book_start_charge_time": p_data[5:9],
        "before_charge_card_account": p_data[10],
        "charge_power_kw": p_data[5:9],
    }
    return info


def xj_cmd_105(p_data: list):  # 平台发送，设备接收
    info = {
        "reserve1": p_data[0],
        "reserve2": p_data[4],
        "time": p_data[5:9],
    }
    return info


def xj_cmd_106(d_data: dict):  # 设备发送，平台接收
    charge_mode_num = d_data.get("equipment_id")
    charge_mode_rate = d_data.get("gun_index")
    equipment_id = d_data.get("equipment_id")
    offline_charge_flag = d_data.get("gun_index")
    stake_version = d_data.get("equipment_id")
    stake_type = d_data.get("gun_index")
    stake_start_times = d_data.get("equipment_id")
    data_up_mode = d_data.get("gun_index")
    sign_interval = d_data.get("equipment_id")
    reserve = d_data.get("gun_index")
    gun_index = d_data.get("equipment_id")
    heartInterval = d_data.get("gun_index")
    heart_out_times = d_data.get("equipment_id")
    stake_charge_record_num = d_data.get("gun_index")
    stake_systime = d_data.get("equipment_id")
    stake_last_charge_time = d_data.get("gun_index")
    stake_last_start_time = d_data.get("equipment_id")
    signCode = d_data.get("gun_index")
    mac = d_data.get("equipment_id")
    ccu_version = d_data.get("gun_index")


def xj_cmd_107(p_data: list):  # 平台发送，设备接收
    info = {
        "equipment_id": p_data[0],
        "gun_index": p_data[4],
        "event_name": p_data[5:9],
    }
    return info


def xj_cmd_108(d_data: dict):  # 设备发送，平台接收
    gun_index = d_data.get("equipment_id")
    event_addr = d_data.get("gun_index")
    event_param = d_data.get("equipment_id")
    charge_user_id = d_data.get("gun_index")


def xj_cmd_113(p_data: list):  # 平台发送，设备接收
    info = {
        "url": (p_data[4:-4][:p_data[4:-4].find(b'\x00')] if p_data[4:-4].find(b'\x00') != -1 else p_data[4:-4]).
        decode('utf-8', errors='ignore'),
        "port": int.from_bytes(p_data[-4:], byteorder='little'),
    }
    return info


def xj_cmd_114(d_data: dict):  # 设备发送，平台接收
    equipment_id = d_data.get("equipment_id")


def xj_cmd_117(p_data: list):  # 平台发送，设备接收
    info = {
        "equipment_id": p_data[0],
        "gun_index": p_data[4],
        "errCode": p_data[4],
    }
    return info


def xj_cmd_118(d_data: dict):  # 设备发送，平台接收
    equipment_id = d_data.get("equipment_id")
    gun_index = d_data.get("gun_index")
    err_code = d_data.get("err_code")
    err_status = d_data.get("err_status")


def xj_cmd_119(p_data: list):  # 平台发送，设备接收
    info = {
        "equipment_id": p_data[0],
        "gun_index": p_data[4],
        "warning_code": p_data[4],
    }
    return info


def xj_cmd_120(d_data: dict):  # 设备发送，平台接收
    equipment_id = d_data.get("equipment_id")
    gun_index = d_data.get("gun_index")
    warning_code = d_data.get("err_code")
    charge_user_id = d_data.get("err_status")
    type = d_data.get("type")
    threshold = d_data.get("threshold")
    retain = d_data.get("retain")
    err_status = d_data.get("err_status")


def xj_cmd_301(p_data: list):  # 平台发送，设备接收
    info = {
        "equipment_id": p_data[0],
        "gun_index": p_data[4],
    }
    return info


def xj_cmd_302(d_data: dict):  # 设备发送，平台接收
    gun_index = d_data.get("equipment_id")
    equipment_id = d_data.get("gun_index")
    work_stat = d_data.get("err_code")
    car_connect_stat = d_data.get("err_status")
    brm_bms_connect_version = d_data.get("type")
    brm_battery_type = d_data.get("threshold")
    brm_battery_power = d_data.get("retain")
    brm_battery_voltage = d_data.get("err_status")
    brm_battery_supplier = d_data.get("equipment_id")
    brm_battery_seq = d_data.get("gun_index")
    brm_battery_produce_year = d_data.get("err_code")
    brm_battery_produce_month = d_data.get("err_status")
    brm_battery_produce_day = d_data.get("type")
    brm_battery_charge_count = d_data.get("threshold")
    brm_battery_property_identification = d_data.get("retain")
    brm_vin = d_data.get("err_status")
    brm_BMS_version = d_data.get("equipment_id")
    bcp_max_voltage = d_data.get("gun_index")
    bcp_max_current = d_data.get("err_code")
    bcp_max_power = d_data.get("err_status")
    bcp_total_voltage = d_data.get("type")
    bcp_max_temperature = d_data.get("threshold")
    bcp_battery_soc = d_data.get("retain")
    bcp_battery_soc_current_voltage = d_data.get("err_status")
    bro_BMS_isReady = d_data.get("equipment_id")
    bcl_voltage_need = d_data.get("gun_index")
    bcl_current_need = d_data.get("err_code")
    bcl_charge_mode = d_data.get("err_status")
    bcs_test_voltage = d_data.get("type")
    bcs_test_current = d_data.get("threshold")
    bcs_max_single_voltage = d_data.get("retain")
    bcs_max_single_no = d_data.get("err_status")
    bcs_current_soc = d_data.get("equipment_id")
    last_charge_time = d_data.get("gun_index")
    bsm_single_no = d_data.get("err_code")
    bsm_max_temperature = d_data.get("err_status")
    bsm_max_temperature_check_no = d_data.get("type")
    bsm_min_temperature = d_data.get("threshold")
    bsm_min_temperature_check_no = d_data.get("retain")
    bsm_voltage_too_high_or_too_low = d_data.get("err_status")
    bsm_car_battery_soc_too_high_or_too_low = d_data.get("err_status")
    bsm_car_battery_charge_over_current = d_data.get("type")
    bsm_battery_temperature_too_high = d_data.get("threshold")
    bsm_battery_insulation_state = d_data.get("retain")
    bsm_battery_connect_state = d_data.get("err_status")
    bsm_allow_charge = d_data.get("equipment_id")
    bst_BMS_soc_target = d_data.get("gun_index")
    bst_BMS_voltage_target = d_data.get("err_code")
    bst_single_voltage_target = d_data.get("err_status")
    bst_finish = d_data.get("type")
    bst_isolation_error = d_data.get("threshold")
    bst_connect_over_temperature = d_data.get("retain")
    bst_BMS_over_temperature = d_data.get("err_status")
    bst_connect_error = d_data.get("retain")
    bst_battery_over_temperature = d_data.get("err_status")
    bst_high_voltage_relay_error = d_data.get("err_status")
    bst_point2_test_error = d_data.get("type")
    bst_other_error = d_data.get("threshold")
    bst_current_too_high = d_data.get("retain")
    bst_voltage_too_high = d_data.get("err_status")
    bst_stop_soc = d_data.get("equipment_id")
    bsd_battery_low_voltage = d_data.get("gun_index")
    bsd_battery_high_voltage = d_data.get("err_code")
    bsd_battery_low_temperature = d_data.get("err_status")
    bsd_battery_high_temperature = d_data.get("type")
    error_68 = d_data.get("threshold")
    error_69 = d_data.get("retain")
    error_70 = d_data.get("err_status")
    error_71 = d_data.get("threshold")
    error_72 = d_data.get("retain")
    error_73 = d_data.get("err_status")
    error_74 = d_data.get("threshold")
    error_75 = d_data.get("retain")


def xj_cmd_303(p_data: list):  # 平台发送，设备接收
    info = {
        "serial_code": p_data[0],
        "gun_index": p_data[4],
        "equipment_id": p_data[0],
        "charge_user_id": p_data[4],
    }
    return info


def xj_cmd_304(d_data: dict):  # 设备发送，平台接收
    serial_code = d_data.get("equipment_id")
    gun_index = d_data.get("gun_index")
    equipment_id = d_data.get("err_code")
    charge_user_id = d_data.get("err_status")
    work_stat = d_data.get("type")
    brm_bms_connect_version = d_data.get("threshold")
    brm_battery_type = d_data.get("retain")
    brm_battery_power = d_data.get("err_status")
    brm_battery_voltage = d_data.get("equipment_id")
    brm_battery_supplier = d_data.get("gun_index")
    brm_battery_seq = d_data.get("err_code")
    brm_battery_produce_year = d_data.get("err_status")
    brm_battery_produce_month = d_data.get("type")
    brm_battery_produce_day = d_data.get("threshold")
    brm_battery_charge_count = d_data.get("retain")
    brm_battery_property_identification = d_data.get("err_status")
    brm_vin = d_data.get("equipment_id")
    brm_BMS_version = d_data.get("gun_index")
    bcp_max_voltage = d_data.get("err_code")
    bcp_max_current = d_data.get("err_status")
    bcp_max_power = d_data.get("type")
    bcp_total_voltage = d_data.get("threshold")
    bcp_max_temperature = d_data.get("err_status")
    bcp_battery_soc = d_data.get("type")
    bcp_battery_soc_current_voltage = d_data.get("threshold")
    bro_BMS_isReady = d_data.get("retain")
    CRO_isReady = d_data.get("err_status")


def xj_cmd_305(p_data: list):  # 平台发送，设备接收
    info = {
        "serial_code": p_data[0],
        "gun_index": p_data[4],
        "equipment_id": p_data[0],
        "charge_user_id": p_data[4],
    }
    return info


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


def xj_cmd_307(p_data: list):  # 平台发送，设备接收
    info = {
        "serial_code": p_data[0],
        "gun_index": p_data[4],
        "equipment_id": p_data[0],
        "charge_user_id": p_data[4],
    }
    return info


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
    info = {
        "serial_code": p_data[0],
        "gun_index": p_data[4],
        "equipment_id": p_data[0],
        "charge_user_id": p_data[4],
    }
    return info


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
    info = {
        "serial_code": p_data[0],
        "gun_index": p_data[4],
        "equipment_id": p_data[0],
        "charge_user_id": p_data[4],
    }
    return info


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
    info = {
        "gun_index": p_data[0],
        "user_id": p_data[4],
        "serial_code": p_data[0],
    }
    return info


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
    info = {
        "gun_index": p_data[0],
        "user_id": p_data[4],
        "serial_code": p_data[0],
    }
    return info


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
    info = {
        "equipment_id": p_data[0],
        "log_name": p_data[4],
        "serial_code": p_data[0],
    }
    return info


def xj_cmd_410(d_data: dict):  # 设备发送，平台接收
    equipment_id = d_data.get("equipment_id")
    log_name = d_data.get("gun_index")
    serial_code = d_data.get("err_code")


def xj_cmd_501(p_data: list):  # 平台发送，设备接收
    info = {
        "serial_code": p_data[0],
        "cmd_len": p_data[4],
        "data": p_data[0],
    }
    return info


def xj_cmd_502(d_data: dict):  # 设备发送，平台接收
    serial_code = d_data.get("equipment_id")
    success_number = d_data.get("gun_index")
    equipment_id = d_data.get("err_code")
    set_result = d_data.get("err_code")


def xj_cmd_503(p_data: list):  # 平台发送，设备接收
    info = {
        "serial_code": p_data[0],
        "equipment_id": p_data[4],
        "data_len": p_data[0],
        "data": p_data[0],
    }
    return info


def xj_cmd_504(d_data: dict):  # 设备发送，平台接收
    serial_code = d_data.get("equipment_id")
    equipment_id = d_data.get("gun_index")
    set_result = d_data.get("err_code")


def xj_cmd_509(p_data: list):  # 平台发送，设备接收
    info = {
        "equipment_id": p_data[0],
        "log_name": p_data[4],
        "serial_code": p_data[0],
    }
    return info


def xj_cmd_510(d_data: dict):  # 设备发送，平台接收
    equipment_id = d_data.get("equipment_id")
    log_name = d_data.get("gun_index")
    serial_code = d_data.get("err_code")


def xj_cmd_801(p_data: list):  # 平台发送，设备接收
    info = {
        "key_len": p_data[0],
        "key_datas": p_data[4],
        "equipment_id": p_data[0],
        "encrypted_type": p_data[0],
        "encrypted_version": p_data[4],
        "serial_code": p_data[0],
    }
    return info


def xj_cmd_802(d_data: dict):  # 设备发送，平台接收
    key_len = d_data.get("equipment_id")
    key_datas = d_data.get("gun_index")
    equipment_id = d_data.get("err_code")
    encrypted_type = d_data.get("equipment_id")
    encrypted_version = d_data.get("gun_index")
    serial_code = d_data.get("err_code")


def xj_cmd_1101(p_data: list):  # 平台发送，设备接收
    info = {
        "soft_type": p_data[0],
        "soft_param": p_data[4],
        "download_url": p_data[0],
        "md5": p_data[0],
        "serial_code": p_data[4],
    }
    return info


def xj_cmd_1102(d_data: dict):  # 设备发送，平台接收
    update_result = d_data.get("equipment_id")
    md5 = d_data.get("gun_index")
    serial_code = d_data.get("err_code")
    encrypted_type = d_data.get("equipment_id")
    encrypted_version = d_data.get("gun_index")
    serial_code = d_data.get("err_code")


def xj_cmd_1303(p_data: list):  # 平台发送，设备接收
    info = {
        "cmd_type": p_data[0],
        "fee_data": p_data[4],
        "serial_code": p_data[0],
    }
    return info


def xj_cmd_1304(d_data: dict):  # 设备发送，平台接收
    fee_data = d_data.get("equipment_id")
    serial_code = d_data.get("gun_index")


def xj_cmd_1305(p_data: list):  # 平台发送，设备接收
    info = {
        "cmd_type": p_data[0],
        "gun_index": p_data[4],
        "fee_data": p_data[0],
        "serial_code": p_data[0],
    }
    return info


def xj_cmd_1306(d_data: dict):  # 设备发送，平台接收
    cmd_type = d_data.get("equipment_id")
    gun_index = d_data.get("gun_index")
    fee_data = d_data.get("equipment_id")
    serial_code = d_data.get("gun_index")


def xj_cmd_1309(p_data: list):  # 平台发送，设备接收
    info = {
        "serial_code": p_data[0],
        "data_len": p_data[4],
        "class_num": p_data[0],
        "data": p_data[0],
    }
    return info


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


def utf8_to_iso(utf8_data):
    iso_data = bytearray()
    i = 0
    while i < len(utf8_data):
        if utf8_data[i] < 0x80:
            iso_data.append(utf8_data[i])
            i += 1
        elif utf8_data[i] == 0xc2:
            iso_data.append(utf8_data[i + 1])
            i += 2
        elif utf8_data[i] == 0xc3:
            iso_data.append(utf8_data[i + 1] + 0x40)
            i += 2
        else:
            # Handle other cases if needed
            i += 1  # Skip invalid UTF-8 sequences

    return iso_data


def recv_buf_check(datas, protocol):
    if len(datas) < 13 or len(datas) > 1025:
        return False

    xor_value = get_check_sum(datas[:-1])
    if xor_value != datas[-1]:
        print(f"xor check failed, xor: {xor_value}, recv: {datas[-1]}")
        return False

    count = 0
    protocol.header_code = datas[count]
    count += 1
    protocol.length_code = datas[count]
    count += 1
    protocol.version_code = datas[count]
    count += 1
    protocol.serial_code = datas[count]
    count += 1
    protocol.cmd_code = datas[count]
    count += 1
    protocol.check_code = datas[-1]

    if protocol.header_code != Enterprise_code:
        print(f"header check failed, header: {Enterprise_code}, recv: {protocol.header_code}")
        return False

    if protocol.length_code != len(datas):
        print(f"length check failed, length: {len(datas)}, recv: {protocol.length_code}")
        return False

    return True
