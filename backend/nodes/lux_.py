import numpy as np
import socket
import struct
import time

from nodes.utils import get_size

def DAQ_bin_to_csv(csv_file_name, logger=None, config=None):
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
    header = ["time_nsec"]
    for i in range(8):
        header.append(config.get(f'DAQ.Channel_map.{i}')[0])
    header = ",".join(header)
    np.savetxt(
        csv_file_name,
        data,
        delimiter=",",
        fmt=["%d"] + ["%.6f"] * 8,
        header=header,
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
    def __init__(self, logger=None, config=None):
        self.logger = logger
        self.config = config
        self.socket = None
        self.IP = self.config.get('DAQ.IP')
        self.PORT = self.config.get('DAQ.PORT')
        self.daq_format = '<128d'
        self.size = struct.calcsize(self.daq_format) + 4
        self.logger.logger.info("DAQ Stream: Node initialized")

    def init_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.IP, self.PORT))
        self.socket.settimeout(1)
        self.logger.logger.info("DAQ Stream: Socket initialized")

    def pack_data(self, data=[0]*8):
        tmp = {"ts": time.time()}
        for i in range(8):
            if self.config.get(f'DAQ.Channel_map.{i}')[0] != '':
                tmp[self.config.get(f'DAQ.Channel_map.{i}')[0]] = data[i]
        return tmp

    def get(self):
        if self.socket is None:
            self.init_socket()
            self.logger.logger.info("DAQ Stream: Running")
        try:
            msg = self.socket.recv(2048)
        except socket.timeout:
            self.logger.logger.warning(f"DAQ Stream: Failed to acquire DAQ data - Please check connection")
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
            self.logger.logger.info("DAQ Stream: Stopped") 
            