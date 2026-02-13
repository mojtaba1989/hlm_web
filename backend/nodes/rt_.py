import struct
from rt_range.ethernet import EthernetParser, PacketType
import pandas as pd
import os
from nodes.utils import try_except, get_size

@try_except 
def NCOM_converter(file_name, config=None):
    # Config is not used -> just for compatibility
    if not os.path.exists(file_name):
        return {"status": "error", "message": "File not found"}
    bin_file_name = file_name.replace(".csv", ".bin")
    data_list = []
    with open (bin_file_name, 'rb') as f:
        while True:
            hdr = f.read(12)
            if not hdr:
                break
            ts, length = struct.unpack("<QI", hdr)
            data = f.read(length)
            try:
                eth = EthernetParser.parse_rt_ethernet(data, PacketType.NCOM)
                for key in eth.keys():
                    eth[key] = str(eth[key])
                eth['timestamp_ns'] = ts
                data_list.append(eth)
            except Exception as e:
                continue
    if not data_list:
        return {"status": "error", "message": "No data found - No CSV file created"}
    final = pd.DataFrame(data_list)
    final.to_csv(file_name, index=False)
    return {"status": "success", "message": "NCOM data converted to CSV",
            "info": [f"File size: {get_size(bin_file_name)}", f"CSV size: {get_size(file_name)}"]}


@try_except
def RCOM_converter(file_name, config=None):
    # Config is not used -> just for compatibility
    if not os.path.exists(file_name):
        return {"status": "error", "message": "File not found"}
    bin_file_name = file_name.replace(".csv", ".bin")
    data_list = []
    with open (bin_file_name, 'rb') as f:
        while True:
            hdr = f.read(12)
            if not hdr:
                break
            ts, length = struct.unpack("<QI", hdr)
            data = f.read(length)
            try:
                eth = EthernetParser.parse_rt_ethernet(data, PacketType.RCOM_extended_range)
                for key in eth.keys():
                    eth[key] = str(eth[key])
                eth['timestamp_ns'] = ts
                data_list.append(eth)
            except Exception as e:
                continue

    if not data_list:
        return {"status": "error", "message": "No data found - No CSV file created"}
    final = pd.DataFrame(data_list)
    final.to_csv(file_name, index=False)
    return {"status": "success", "message": "NCOM data converted to CSV",
            "info": [f"File size: {get_size(bin_file_name)}", f"CSV size: {get_size(file_name)}"]}
    