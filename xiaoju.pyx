import json

import HSyslog
from xiaoju cimport *

def xiaoju_init(init_json: str):
    cdef result
    init_dict = json.loads(init_json)
    gun_num = init_dict.get("gun_num")
    xj_pal_print_log(xj_log_type.xj_log_message, init_dict.init_log)

    for i in range(0, gun_num):
        result = xj_APP_start(&gun_info, &bms_info, gun_num)
        if result == 0:
            print(f"Start successfully: gun->{i}")
            HSyslog.log_info(f"Start successfully: gun->{i}")
        else:
            print(f"Start Dead: gun->{i}")
            HSyslog.log_info(f"Start Dead: gun->{i}")