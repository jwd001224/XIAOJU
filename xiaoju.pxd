import json
import sqlite3
from datetime import *

cdef extern from "string.h":
    char* strncpy(char *dest, const char *src, size_t n)
    size_t strlen(const char *_Str)


cdef extern from r"include/redefine.h":
    ctypedef long               ssize_t
    ctypedef signed int         int32_t
    ctypedef unsigned int       uint32_t
    ctypedef signed short       int16_t
    ctypedef unsigned short     uint16_t
    ctypedef signed char        int8_t
    ctypedef unsigned char      uint8_t
    ctypedef signed long long   int64_t
    ctypedef unsigned long long uint64_t


cdef extern from r"include/protocol.h":
    void * client_refresher(void * client)
    void * xj_mqtt_send_cmd(xj_mqtt_cmd_enum cmd_type, void * cmd, uint16_t time_out, uint8_t Qos)
    void xj_mqtt_disconnect()
    char xj_mqtt_connect(char * addr, int port, char * username, char * password, char * client_identifier, void *(*callback_cmd_received)(void * param, xj_mqtt_cmd_enum cmd_type))
    void xj_mqtt_send_resp(xj_mqtt_cmd_enum cmd_type, void * cmd, uint8_t Qos)
    extern void xj_pal_print_log(xj_log_type type, char * format, ...)
    extern int8_t err_event_info_pop(int8_t flag, uint8_t gun_index, char *err_no)

    ctypedef enum xj_mqtt_cmd_enum:
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

    ctypedef enum xj_log_type:
        xj_log_Null     = 0
        xj_log_message  = 1
        xj_log_remind   = 2
        xj_log_warning  = 3
        xj_log_Error    = 4


cdef extern from r"include/xiaoju_struct.h":
    ctypedef struct st_assembly_param:
        uint16_t param_1
        uint16_t param_2

    ctypedef struct xj_upload_log_param:
        char upload_url[128 + 1]

    ctypedef enum xj_software_upgrade_type:
        xj_software_upgrade_type_charger_software = 0
        xj_software_upgrade_type_middle_ware = 1
        xj_software_upgrade_type_ad = 2

    ctypedef enum xj_software_target_type:
        xj_software_target_type_tcu = 10
        xj_software_target_type_ccu = 11

    ctypedef struct xj_software_upgrade_param:
        xj_software_upgrade_type upgrade_type
        xj_software_target_type target_type
        char url[128 + 1]
        char md5[32 + 1]
        uint32_t    serial_code

    ctypedef struct st_user_vin_send_result:# 用户vin码启动充电回调结果,参考 < 小桔协议 > code41
        uint16_t gun_index # 充电口号 0表示枪1 1表示枪2
        uint8_t charge_user_id[32] # 订单号
        int32_t balance # 账户余额
        uint8_t Request_result # 鉴权结果 0成功 1失败
        uint8_t failure_reasons # 失败原因
        uint32_t remainkon # 剩余里程
        uint32_t dump_energy # 可充电量
        uint32_t residue_degree # 剩余次数
        uint16_t phone # 手机尾号

    ctypedef struct xj_bill_info:
        int8_t gun_index # 枪号
        char charge_user_id[32 + 1] # 订单号
        int16_t charge_start_time_year # 开始充电时间年
        int8_t charge_start_time_month
        int8_t charge_start_time_day
        int8_t charge_start_time_hour
        int8_t charge_start_time_minute
        int8_t charge_start_time_sec
        int16_t charge_end_time_year # 结束充电时间年
        int8_t charge_end_time_month
        int8_t charge_end_time_day
        int8_t charge_end_time_hour
        int8_t charge_end_time_minute
        int8_t charge_end_time_sec
        int16_t charge_time # 累计充电时间
        int8_t start_soc # 开始充电的SOC
        int8_t end_soc # 停止充电的SOC
        char err_no[4 + 1] # 结束充电原因
        uint32_t charge_kwh_amount # 充电电量 单位 0.001kwh
        uint64_t start_charge_kwh_meter # 开始充电时电表读数 uint32->uint64
        uint64_t end_charge_kwh_meter # 结束充电时的电表读数 uin32->uint64
        uint32_t total_charge_fee # 电费      单位: 分
        uint32_t total_service_fee # 服务费     单位: 分
        char car_vin[17 + 1] # VIN码
        uint32_t kwh_amount[48] # 分时电量 uint16->uint32
        int8_t start_type # 起始充电类型


    ctypedef struct st_safety_parameters:  #安全围栏相关参数
        uint16_t safety_12  #默认5 单位0.1V 充电桩预充阶段测量车辆电池电压值与BCP报文中“整车动力蓄电池当前电池电压”差异绝对值大指定电压数值时则停止充电启动流程
        uint16_t safety_13  #默认420 单位0.01V 充电阶段，如果电池是三元锂电池，持续监测BCS/BMV报文中“最高单体动力蓄电池电压”，若超过指定电压数值则立即停止充电；
        uint16_t safety_14  #默认300 单位0.01mv 充电阶段，若电池类型为三元锂电池，持续监测充电过程中三元锂电池中单体最高电压与最低电池差，若大于指定电压数值且持续10s则认为电芯不均衡严重需告警。
        uint16_t safety_15  #默认10 单位秒 充电阶段，持续监测BSM报文中的“最高动力蓄电池温度”是否超过BCP报文中的“最高允许温度”，若是且持续N秒则立即停止充电；
        uint16_t safety_16  #默认10 单位秒 充电阶段，持续监测BMT报文中温度最高值是否超过BCP报文中“最高允许温度”，若是且持续N秒则立即停止充电；
        uint16_t safety_17  #默认5 单位0.1℃/min 充电阶段，充电过程中持续监测并计算动力蓄电池温升速率，若温速率大于N℃/1min则立即停止充电；
        uint16_t safety_18  #默认50 单位℃ 充电阶段，若BSM报文中电池组温度超过N℃则停止充电。
        uint16_t safety_19  #默认50 单位℃ 充电阶段，若BMT报文中电池组温度超过N℃则停止充电。
        st_assembly_param safety_20  #参数1默认10 单位0.1V，参数2默认1 单位min 充电阶段，BCS报文中“充电电压测量值”和充电机直流电表电压测量值差值绝对值超过nV并持续n min则停止充电。
        st_assembly_param safety_21  #参数1默认10 单位0.1V，参数2默认1 单位min 充电阶段，BCS报文中“充电电压测量值”和充电机高压板测量值差异绝对值超过nV并持续1min则停止充电。
        st_assembly_param safety_22  #参数1默认10 单位0.1V，参数2默认1 单位min 充电阶段，充电机直流电表电压测量值和充电机高压板测量值差异绝对值超过nV并持续1min则停止充电。
        uint16_t safety_23  #默认1 单位秒 充电阶段，BCS报文中“充电电流测量值”与充电桩输出电流测量值(>=30A时)之差绝对值超过1%并持续N秒则停止充电。
        uint16_t safety_24  #默认1 单位秒 充电阶段，BCS报文中“充电电流测量值”与充电桩输出电流测量值（<30A时）之差绝对值超过0.3A并持续Ns则停止充电。
        uint16_t safety_25  #默认105 单位0.01倍 充电阶段，当充电电量（从直流电表获取）超过“总能量*(1-初始SOC)*N”时停止充电。
        uint16_t safety_26  #默认5 单位分钟min 充电阶段，起充SOC<50%，充电过程中BCS数据"当前荷电状态SOC"保持不变超过设定的时间中止充电
        uint16_t safety_27  #默认5 单位分钟min 充电阶段，起充SOC<50%，充电过程中BCS数据"充电电压测量值"保持不变超过设定的时间中止充电。
        uint16_t safety_28  #默认5 单位分钟min 充电阶段，起充SOC<50%，充电过程中BCS数据"充电电流测量值"保持不变超过设定的时间中止充电
        uint16_t safety_29  #默认5 单位分钟min 充电阶段，起充SOC<50%，充电过程中BCS数据"最高单体动力蓄电池电压"保持不变超过设定的时间中止充电。
        uint16_t safety_30  #默认5 单位分钟min 充电阶段，起充SOC<50%，充电过程中BSM数据"最高动力蓄电池温度"保持不变超过设定的时间中止充电
        uint16_t safety_31  #默认85 单位℃ 充电阶段，充电连接装置温度超过N℃则开始降功率输出，当温度下降到安全阈值则开始增加输出功率 (充电枪过温)
        st_assembly_param safety_32  #参数1默认100 单位℃ ，参数2默认30 单位秒，充电阶段，当充电连接装置温度超过N℃且持续N s则停止充电；
        uint16_t safety_33  #默认10 单位1V      充电阶段，在绝缘检测阶段通过检测熔断器前后两端的电压，压差超过nV认为是熔断器断路异常或者直接采用带反馈信号的熔断器，一旦检测到熔断器断路则告警且中止充电流程。
        uint16_t safety_34  #默认36 单位1V     充电阶段，一把枪启动充电时，检验别的未充电枪电压若高于nV则中止充电流程。
        uint16_t safety_35  #默认50% 单位1% 参数地址26-30五项截至SOC百分比

    ctypedef struct st_bms_finish_statistical_data:  #结束BMS统计数据
        uint8_t bsd_stop_soc  # 终止荷电状态soc
        int32_t bsd_battery_low_voltage  # BSD-动力蓄电池单体最低电压
        int32_t bsd_battery_high_voltage  # BSD-动力蓄电池单体最高电压
        int32_t bsd_battery_low_temperature  # BSD-动力蓄电池最低温度
        int32_t bsd_battery_high_temperature  # BSD-动力蓄电池最高温度
        int32_t bem_error_spn2560_00  # BEM-接收SPN2560=0x00的充电桩辨识报文超时
        int32_t bem_error_spn2560_aa  # BEM-接收SPN2560=0xaa的充电桩辨识报文超时
        int32_t bem_error_time_sync  # BEM-接收充电桩的时间同步和最大输出能力报文超时
        int32_t bem_error_ready_to_charge  # BEM-接收充电桩完成充电准备报文超时
        int32_t bem_error_receive_status  # BEM-接收充电桩充电状态报文超时
        int32_t bem_error_receive_stop_charge  # BEM-接收充电桩终止充电报文超时
        int32_t bem_error_receive_report  # BEM-接收充电桩充电统计报文超时
        int32_t bem_error_other  # BEM-其他

    ctypedef struct st_off_bms_cst_data:  #中止BMS-CST数据，充电机中止充电
        uint8_t CST_stop_reason  #CST - 充电机中止原因
        uint16_t CST_fault_reason  #CST - 中止充电故障原因
        uint8_t CST_error_reason  #CST - 中止充电错误原因

    ctypedef struct st_off_bms_bst_data:  #中止BMS-BST数据,BMS中止充电
        uint8_t BST_stop_reason  #BST - 充电机中止原因
        uint16_t BST_fault_reason  #BST - 中止充电故障原因
        uint8_t BST_error_reason  #BST - 中止充电错误原因

    ctypedef struct st_bms_basic_info:  #bms 基础信息
        char brm_bms_connect_version[3 + 1]  #BRM-BMS通讯协议版本号
        int32_t brm_battery_type  #电池类型
        int32_t brm_battery_power  #整车动力蓄电池系统额定容量/Ah
        int32_t brm_battery_volt  # 整车动力蓄电池系统额定总电压
        int32_t brm_battery_supplier  # 电池生产厂商
        int32_t brm_battery_seq  # 电池组序号
        int32_t brm_battery_produce_year  # 电池组生厂日期：年
        int32_t brm_battery_produce_month  # 电池组生厂日期：月
        int32_t brm_battery_produce_day  # 电池组生厂日期：日
        int32_t brm_battery_charge_count  # 电池组充电次数
        int32_t brm_battery_property_identification  # 电池组产权标识
        char brm_vin[17 + 1]  # 车辆识别码vin
        char brm_bms_software_version[8 + 1]  # BMS软件版本号
        int32_t bcp_max_voltage  # 单体动力蓄电池最高允许充电电压
        int32_t bcp_max_current  # 最高允许充电电流
        int32_t bcp_max_power  # 动力蓄电池标称总能量
        int32_t bcp_total_voltage  # 最高允许充电总电压
        int32_t bcp_max_temperature  # 最高允许温度
        int32_t bcp_battery_soc  # 整车动力蓄电池荷电状态
        int32_t bcp_battery_soc_current_voltage  # 整车动力蓄电池当前电池电压
        int32_t bro_bms_is_ready  # 是否充电准备好
        uint8_t CRO_isReady  # CRO-充电机是否充电准备好

    ctypedef struct xj_card_auth:
        uint16_t gun_index
        uint8_t card_id[16]  #充电卡卡号
        uint8_t random_id[48]  #随机数
        uint8_t phy_id[4]  #物理卡号

    ctypedef struct st_user_gun_info:  #充电枪实时信息
        int32_t soc_percent  #当前电量SOC 单位1%
        int32_t dc_charge_voltage  #直流充电电压
        int32_t dc_charge_current  #直流充电电流
        int32_t bms_need_voltage  #BMS需求电压
        int32_t bms_need_current  #BMS需求电流
        int32_t ac_a_vol  #交流A相充电电压
        int32_t ac_b_vol  #交流B相充电电压
        int32_t ac_c_vol  #交流C相充电电压
        int32_t ac_a_cur  #交流A相充电电流
        int32_t ac_b_cur  #交流B相充电电流
        int32_t ac_c_cur  #交流C相充电电流
        uint64_t meter_kwh_num  # 当前电表读数 int32->int64#
        int32_t charge_power_kw  #充电功率

    ctypedef struct st_user_bms_info:  #BMS实时信息
        int32_t bcl_voltage_need  # 电压需求 分辨率：0.1V
        int32_t bcl_current_need  # 电流需求      分辨率：0.1A，-400A偏移量
        int32_t bcl_charge_mode  # 充电模式       0x01表示恒压充电，0x02表示恒流充电
        int32_t bcs_test_voltage  # 充电电压测量值          分辨率：0.1V
        int32_t bcs_test_current  # 充电电流测量值          分辨率：0.1A，-400A偏移量
        int32_t bcs_max_single_voltage  # 最高单体动力蓄电池电压              分辨率：0.01V，数据范围: 0~24 V
        int32_t bcs_min_single_voltage  # 最低单体动力蓄电池电压              分辨率：0.01V，数据范围: 0~24 V
        int32_t bcs_max_single_no  # 最高单体动力蓄电池组号              分辨率1/位，范围0-15
        int32_t bcs_current_soc  # 当前荷电状态soc%       分辨率：1%/位，0-100%
        int32_t charge_time_left  # 估算剩余充电时间
        int32_t bsm_single_no  # 最高单体动力蓄电池电压所在编号
        int32_t bsm_max_temperature  # 最高动力蓄电池温度
        int32_t bsm_max_temperature_check_no  # 最高温度检测点编号
        int32_t bsm_min_temperature  # 最低动力蓄电池温度
        int32_t bsm_min_temperature_check_no  # 最低动力蓄电池温度检测点编号
        int32_t bsm_voltage_too_high_or_too_low  # 单体动力蓄电池电压过高或过低
        int32_t bsm_car_battery_soc_too_high_or_too_low  # 整车动力蓄电池荷电状态soc过高或过低
        int32_t bsm_car_battery_charge_over_current  # 动力蓄电池充电过电流
        int32_t bsm_battery_temperature_too_high  # 动力蓄电池温度过高
        int32_t bsm_battery_insulation_state  # 动力蓄电池绝缘状态
        int32_t bsm_battery_connect_state  # 动力蓄电池组输出连接器连接状态
        int32_t bsm_allow_charge  # 允许充电
        int32_t dc_charge_voltage  #直流充电电压
        int32_t dc_charge_current  #直流充电电流

    ctypedef enum xj_bool:
        xj_bool_false = 0
        xj_bool_true = 1

    ctypedef struct xj_error:
        uint8_t gun_index
        char err_no[4 + 1]
        uint32_t err_flag

    ctypedef enum xj_event_type:
        xj_event_gun_pluged_in = 1  # 插枪事件
        xj_event_gun_pluged_out = 2  # 拔枪事件
        xj_event_charge_started = 3  # 启动充电事件
        xj_event_charge_stoped = 4  # 停止充电事件

    ctypedef struct xj_sync_system_time_param:
        uint16_t year
        uint8_t month
        uint8_t day
        uint8_t hour
        uint8_t minute
        uint8_t sec

    ctypedef struct xj_fee_config:  # 整形 单位为分
        uint32_t charge_fee[48]  # 电费
        uint32_t service_fee[48]  # 服务费
        uint32_t demurrage[48]  # 延误费


cdef extern from r"include/xiaoju.h":
    ctypedef struct xj_params:
        char sdk_version[4]  # sdk 版本
        xj_fee_config fee_config  # 费率，包括电费和服务费，都是用分时电价，共48个时段
        char center_svr_addr[128 + 1]  # 中心服务器地址
        uint16_t center_svr_port  # 中心服务器端口号
        char logic_svr_addr[128 + 1]  # 逻辑服务器地址
        uint16_t logic_svr_port  # 逻辑服务器端口号
        uint16_t logic_svr_upload_log_port  # 逻辑服务器上传日志使用端口
        char username[64]  # 登录用户名
        char password[256]  #登录密码
        uint8_t user_version[4]  # 协议版本，对应小桔充电协议中版本域
        char gun_qr_code[4][128]  #充电枪对应二维码
        char mac_addr[32 + 1]  #mac 地址，对应106协议中的充电桩Mac地址或者IMEI码
        char equipment_id[32 + 1]  # 充电桩编码
        uint8_t network_cmd_timeout  #部分协议超时时间，单位为s,默认为5
        uint16_t sign_in_interval  # 签到间隔
        uint16_t gun_cnt  # 充电枪个数
        uint8_t  gun_type  # 枪类型，分为直流和交流
        uint16_t upload_gun_status_interval  # 充电枪状态上传间隔，即104报文上传间隔，默认30s
        uint16_t upload_bms_status_interval  # BMS协议上传间隔，即302报文上传间隔，默认30s
        uint16_t heartbeat_interval  # 心跳上传间隔，默认30s
        uint16_t heartbeat_timeout_check_cnt  # 心跳超时次数，用于判断桩离线，默认为3，也就是3次心跳无回复就认为已经离线
        uint16_t mqtt_ping_interval  #190827 新增mqtt间隔参数
        uint32_t max_power[4]  #最大功率
        uint32_t software_restart_cnt  #软件启动次数
        uint8_t log_level  #日志等级
        uint8_t log_strategy  #日志策略
        uint16_t log_period  #日志上传间隔 单位min
        st_safety_parameters safety_parameters  #安全围栏参数，用户根据参数判断停机

    void _convert_time(int32_t year, int32_t month, int32_t day, int32_t hour, int32_t minute, int32_t sec, char * bcd_timd)
    void _convert_time_back(char * bcd_time, xj_sync_system_time_param * time_param)
    void _persist_xj_params()
    void _restore_persisted_xj_params(xj_params * p)
    int Come_letter_num_len(uint8_t *data)
    xj_bool xj_send_event(uint8_t gun_cnt, xj_event_type type, uint32_t    event_param)
    xj_bool xj_send_error(xj_error * error)
    void xj_send_Electric_meter_warning(uint8_t gun)
    uint8_t QR_code_String(char * QR, const char *charge, const uint8_t gun_num)
    char Check_cpu()
    void touch_send_1102_code(uint8_t update_result, uint8_t *md5, uint32_t serial_code)
    int8_t xj_APP_start(st_user_gun_info * gun_status, st_user_bms_info * bms_status, uint8_t gun_num)
    int8_t xj_send_touch_gun_pluged_in(uint8_t gun_index)
    int8_t xj_send_touch_gun_pluged_out(uint8_t gun_index)
    int8_t xj_send_touch_charge_start(uint8_t gun_index, uint8_t * param)
    int8_t xj_send_touch_charge_stoped(uint8_t gun_index, uint8_t *stop_reason, uint8_t * param)
    int8_t xj_send_touch_warning_occured(uint8_t gun_cnt, uint8_t * warning)
    int8_t xj_send_warning(uint8_t gun_cnt, uint8_t * warning, uint32_t threshold)
    int8_t xj_send_touch_error_occured(uint8_t gun_cnt, uint8_t * err_no)
    int8_t xj_send_touch_error_recovered(uint8_t gun_cnt, uint8_t * err_no)
    int8_t xj_touch_set_equipment_id(uint8_t * ID_str)
    int8_t xj_touch_set_mac_addr(uint8_t * mac_str)
    int8_t xj_send_touch_card_start_charge(xj_card_auth * info)
    int8_t touch_send_bms_basic_info(uint8_t gun, char * charge_user_id, st_bms_basic_info * data)
    int8_t touch_send_bms_cst_data(uint8_t gun, char * charge_user_id, st_off_bms_cst_data * data)
    int8_t touch_send_bms_bst_data(uint8_t gun, char * charge_user_id, st_off_bms_bst_data * data)
    int8_t touch_send_bms_inish_statistical_data(uint8_t gun, char * charge_user_id, st_bms_finish_statistical_data * data)
    uint16_t xj_get_charge_fee(uint8_t time)
    uint16_t xj_get_service_fee(uint8_t time)
    uint16_t xj_get_demurrage(uint8_t time)
    uint32_t xj_get_maxpower(uint8_t gun)
    int8_t get_current_order_number(uint8_t un, int8_t * id)
    int8_t xj_touch_set_mqtt_info(uint8_t * UserName, uint8_t * password)
    int8_t xj_send_vin_start_charge_request(uint8_t gun_cnt, uint8_t * vin)
    void xj_send_touch_vin_charge_reques(uint8_t gun, char * vin)
    void xj_pal_print_log(xj_log_type type, char * format, ... )
    void Printf_TCP_Log(char * buff, int len, char type)
    uint32_t get_current_fee(uint8_t gun)
    const st_safety_parameters * get_xj_safety_parameters()
    int8_t get_gun_qr_code(uint8_t gun, int8_t * QR)
    void err_event_info_init()
    int8_t err_event_info_push(int8_t flag, uint8_t gun_index, char * err_no)
    int8_t err_event_info_pop(int8_t flag, uint8_t gun_index, char * err_no)
    void err_event_info_clr()


cdef extern from r"include/xiaoju_pal.h":
    extern int8_t callback_show_bill(xj_bill_info bill_data,uint8_t gun_cnt)
    extern void callback_display_qr(uint8_t gun_cnt,uint8_t*qr_str,uint16_t len,char* err)
    extern int8_t callback_vin_start_charge_result(st_user_vin_send_result result)
    extern void callback_start_charge(uint8_t gun_cnt,char* err,char* id,uint8_t id_len,uint16_t user_tel)
    extern void callback_stop_charge(uint8_t gun_cnt, char* err)
    extern void callback_set_sys_time(xj_sync_system_time_param time,char* err)
    extern int8_t callback_software_download(xj_software_upgrade_param *param)
    extern int8_t callback_save_bill(char* bill,uint32_t size)
    extern int8_t callback_read_bill(char* bill,uint32_t len)
    extern int8_t callback_upload_log(const xj_upload_log_param* upload_url,char* log_name,uint16_t max_len)
    extern int8_t callback_lock_control(uint8_t gun_cnt,uint8_t type)



cdef st_user_gun_info gun_info
cdef st_user_bms_info bms_info

