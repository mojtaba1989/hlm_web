import struct
import pandas as pd
import os
from nodes.utils import try_except, get_size
from nodes.ostx_decoder_ import *

@try_except 
def XCOM_converter(file_name, config=None):
    # Config is not used -> just for compatibility
    bin_file_name = file_name.replace(".csv", ".bin")
    tag = file_name.split("/")[-1].split(".")[0].upper()
    if not os.path.exists(bin_file_name):
        return {"status": "error", "message": "File not found"}
    data_list = []
    with open (bin_file_name, 'rb') as f:
        while True:
            hdr = f.read(12)
            if not hdr:
                break
            stamp, length = struct.unpack("<QI", hdr)
            msg = f.read(length)
            ret, unpacked = OSTXDecoder.decode(msg, checksum=True)
            if ret == ReturnCode.Success:
                depacked['time_nsec'] = stamp
                data_list.append(unpacked)
    if not data_list:
        return {"status": "error", "message": f"[{tag}->CSV] No data found - No CSV file created"}
    final = pd.DataFrame(data_list)
    final.to_csv(file_name, index=False)
    return {"status": "success", "message": f"[{tag}->CSV] Successfully created",
            "more": [f"File size: {get_size(bin_file_name)}", f"CSV size: {get_size(file_name)}"]}