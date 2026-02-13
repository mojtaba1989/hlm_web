import numpy as np
import socket
import struct
import time

from nodes.utils import get_size

def DAQ_bin_to_csv(file_name=None, config=None):
    if file_name is None:
        return {"status": "error", "message": "No file name provided"}

    if config is None:
        return {"status": "error", "message": "No config provided"}

    bin_file_name = file_name.replace(".csv", ".bin")
    rows = []   # will hold (N, 9) blocks
    freq = config.get('DAQ.FREQUENCY')
    dt = int(1.0/freq * 1e9)
    N = config.get('DAQ.BUFFER_SIZE')
    tic = time.time()
    with open(bin_file_name, "rb") as f:
        while True:
            hdr = f.read(12)
            if not hdr:
                break

            ts, n = struct.unpack("<QI", hdr)
            payload = f.read(n)
            arr = np.frombuffer(payload[4:], dtype=">f8").reshape(8, 16).T
            tcol = ts - np.arange(N-1, -1, -1) * dt
            tcol = tcol.reshape(-1, 1)
            block = np.hstack((tcol, arr))
            rows.append(block)
    if not rows:
        return {"status": "error", "message": "No data found - No CSV file created"}
    data = np.vstack(rows)
    header = ["time_nsec"]
    for i in range(8):
        tag = config.get(f'DAQ.CHANNEL_MAP.{i}')
        if tag is None or tag == "":
            tag = f'Null_{i}'
        header.append(tag)
    header = ",".join(header)
    np.savetxt(
        file_name,
        data,
        delimiter=",",
        fmt=["%d"] + ["%.6f"] * 8,
        header=header,
        comments=""
    )
    return {"status": "success", "message": "Conversion complete", "info": [
        f"DAQ BIN to CSV: Conversion complete {file_name}",
        f"DAQ BIN to CSV: processing time: {time.time()-tic:.3f}s",
        f"DAQ BIN to CSV: binary file size: {get_size(bin_file_name)}",
        f"DAQ BIN to CSV: csv file size: {get_size(file_name)}",
        f"DAQ BIN to CSV: test duration: {(data[-1, 0] - data[0, 0])/1e9:.3f}s"
    ]}

class lux_streamer:
    def __init__(self, logger=None, config=None):
        self.set_logger(logger)
        self.config = config
        self.socket = None
        self.IP = self.config.get('DAQ.IP/NETMASK').split("/")[0]
        self.PORT = self.config.get('DAQ.PORT')
        self.daq_format = '<128d'
        self.size = struct.calcsize(self.daq_format) + 4
        self.info("DAQ Stream: Node initialized")

    def set_logger(self, logger):
        def _noop(*args, **kwargs):
            pass
        base = getattr(logger, "logger", None)
        self.info = getattr(base, "info", _noop)
        self.warning = getattr(base, "warning", _noop)
        self.error = getattr(base, "error", _noop)

    def init_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.IP, self.PORT))
        self.socket.settimeout(1)
        self.info("DAQ Stream: Socket initialized")

    def pack_data(self, data=[0]*8):
        tmp = {}
        for i in range(8):
            if self.config.get(f'DAQ.Channel_map.{i}') != '':
                tmp[self.config.get(f'DAQ.Channel_map.{i}')] = data[i]
        return tmp

    def get(self):
        if self.socket is None:
            self.init_socket()
            self.info("DAQ Stream: Running")
        try:
            msg = self.socket.recv(2048)
        except socket.timeout:
            self.warning(f"DAQ Stream: Failed to acquire DAQ data - Please check connection")
            return self.pack_data()
        except:
            self.warning(f"DAQ Stream: Failed to acquire DAQ data - Please check connection")
            return self.pack_data()
        msg = self.socket.recv(2048)
        if len(msg) != self.size:
            return self.pack_data()
        arr = np.frombuffer(msg[4:], dtype=">f8").reshape(8, 16)
        arr = np.mean(arr, axis=1).tolist()
        return self.pack_data(arr)
    
    def stop(self):
        if self.socket:
            self.socket.close()
            self.socket = None
            self.info("DAQ Stream: Stopped") 
            