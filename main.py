#!/bin/python3
import inspect
import sys
import time

import HDevice
import HPlatform
import HStategrid
import HSyslog
import HHhdlist


def main():
    try:
        HStategrid.datadb_init()
        # HStategrid.disable_network_interface("eth0")
        # HStategrid.disable_network_interface("eth1")
        # HStategrid.disable_network_interface("eth2")
        HHhdlist.save_json_config({"Platform_type": "XIAOJU"})
        while True:
            if HStategrid.get_DeviceInfo("device_id") is None or HStategrid.get_DeviceInfo("device_id") == "":
                device_id = HHhdlist.read_json_config("deviceCode")
                if device_id is None or device_id == "":
                    time.sleep(10)
                else:
                    HStategrid.Device_ID = device_id
                    HStategrid.save_DeviceInfo("device_id", HStategrid.DB_Data_Type.DATA_STR.value, device_id, 0)
                    break
            else:
                HStategrid.Device_ID = HStategrid.get_DeviceInfo("device_id")
                break
        HDevice.hhd_init()
        HPlatform.tpp_init(HStategrid.platform_host, HStategrid.platform_port)
        while True:
            time.sleep(86400)
    except Exception as e:
        HSyslog.log_info(f"main error: {e}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
    except KeyboardInterrupt:
        sys.exit()