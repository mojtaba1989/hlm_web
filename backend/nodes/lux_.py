import numpy as np
import socket
import struct
import time

from nodes.utils import get_size

def DAQ_bin_to_csv(csv_file_name, logger=None):
    if logger: logger.logger.info("DAQ BIN to CSV: Converting DAQ binary data to CSV...")
    if csv_file_name is None:
        if logger: logger.logger.error("DAQ BIN to CSV: No data found - No CSV file created")
        return

    bin_file_name = csv_file_name.replace(".csv", ".bin")
    rows = []   # will hold (N, 9) blocks
    freq = 1612.8
    dt = int(1.0/freq * 1e9)
    N = 16
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
        if logger: logger.logger.error("DAQ BIN to CSV: No data found - No CSV file created")
        return
    data = np.vstack(rows)
    np.savetxt(
        csv_file_name,
        data,
        delimiter=",",
        fmt=["%d"] + ["%.6f"] * 8,
        header="time_nsec,ch1,ch2,ch3,ch4,ch5,ch6,ch7,ch8",
        comments=""
    )
    if logger:
        logger.logger.info(f"DAQ BIN to CSV: Conversion complete {csv_file_name}")
        logger.logger.info(f"DAQ BIN to CSV: processing time: {time.time()-tic:.3f}s")
        logger.logger.info(f"DAQ BIN to CSV: binary file size: {get_size(bin_file_name)}")
        logger.logger.info(f"DAQ BIN to CSV: csv file size: {get_size(csv_file_name)}")
        logger.logger.info(f"DAQ BIN to CSV: test duration: {(data[-1, 0] - data[0, 0])/1e9:.3f}s")
    return

class lux_streamer:
    def __init__(self, logger=None):
        self.logger = logger
        self.socket = None
        self.IP = "10.0.0.105"
        self.PORT = 5555
        self.daq_format = '<128d'
        self.size = struct.calcsize(self.daq_format) + 4
        self.logger.logger.info("DAQ Stream: Node initialized")

    def init_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.IP, self.PORT))
        self.socket.settimeout(1)
        self.failed_to_get = 0
        self.logger.logger.info("DAQ Stream: Socket initialized")    

    def get(self):
        if self.socket is None:
            self.init_socket()
            self.logger.logger.info("DAQ Stream: Running")
        try:
            msg = self.socket.recv(2048)
        except socket.timeout:
            self.logger.logger.warning(f"DAQ Stream: Failed to acquire DAQ data - Please check connection")
            json_data = {f"s{i}": 0 for i in range(8)}
            json_data["ts"] = time.time()
            return json_data
        msg = self.socket.recv(2048)
        if len(msg) != self.size:
            json_data = {f"s{i}": 0 for i in range(8)}
            json_data["ts"] = time.time()
            return json_data
        arr = np.frombuffer(msg[4:], dtype=">f8").reshape(8, 16)
        arr = np.mean(arr, axis=1).tolist()
        json_data = {f"s{i}": arr[i] for i in range(8)}
        json_data["ts"] = time.time()
        return json_data
    
    def stop(self):
        if self.socket:
            self.socket.close()
            self.socket = None
            self.logger.logger.info("DAQ Stream: Stopped") 
            