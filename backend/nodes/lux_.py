import numpy as np
import socket
import struct
import time
import threading

from nodes.utils import try_except, get_size
from nodes.core import core_ as core


class lux_recorder:
    def __init__(self):
        self.socket = None
        self.IP = "10.0.0.105"
        self.PORT = 5555
        self.running = False
        self.thread = None
        self.daq_format = '<128d'
        self.rec_format = '<QI'
        self.size = struct.calcsize(self.daq_format) + 4
        self.file_name = None
        self.failed_to_get = 0
        self.max_failed = 10

    def init_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.IP, self.PORT))
        self.socket.settimeout(1)
        self.failed_to_get = 0
    
    def loop_(self):
        if not self.file_name:
            return
        bin_file = self.file_name.replace(".csv", ".bin")
        with open(bin_file, "wb") as f:
            while self.running:
                try:
                    msg, addr = self.socket.recvfrom(2048)
                except socket.timeout:
                    core.logger.logger.warning(f"Attempt {self.failed_to_get}/{self.max_failed} - Failed to get DAQ data")
                    self.failed_to_get += 1
                    if self.failed_to_get > self.max_failed:
                        core.logger.logger.error("Maximum attempts reached - Failed to get DAQ data - Closing socket")
                        self.stop()
                    continue
                if len(msg) != self.size:
                    continue
                header = struct.pack("<QI", time.time_ns(), len(msg))
                f.write(header)
                f.write(msg)
                self.failed_to_get = 0

    def start(self):
        if self.running:
            return
        if not self.file_name:
            return
        self.bin_file_name = self.file_name.replace(".csv", ".bin")
        self.running = True
        self.init_socket()
        self.thread = threading.Thread(target=self.loop_, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.socket:
            self.socket.close()
            self.socket = None
        if self.thread:
            self.thread.join()
            self.thread = None
        

    def get(self):
        if self.socket is None:
            self.init_socket()
        try:
            msg = self.socket.recv(2048)
        except socket.timeout:
            core.logger.logger.warning(f"Attempt {self.failed_to_get}/{self.max_failed} - Failed to get DAQ data")
            self.failed_to_get += 1
            if self.failed_to_get > self.max_failed:
                core.logger.logger.error("Maximum attempts reached - Failed to get DAQ data - Closing socket")
                self.stop()
            
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
                    
    def convert_to_csv(self):
        if self.bin_file_name is None:
            return
        rows = []   # will hold (N, 9) blocks
        freq = 1612.8
        dt = int(1.0/freq * 1e9)
        N = 16
        tic = time.time()
        with open(self.bin_file_name, "rb") as f:
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

        data = np.vstack(rows)
        np.savetxt(
            self.file_name,
            data,
            delimiter=",",
            fmt=["%d"] + ["%.6f"] * 8,
            header="time_nsec,ch1,ch2,ch3,ch4,ch5,ch6,ch7,ch8",
            comments=""
        )
        return({
            "processing time": f"{time.time()-tic:.3f}s",
            "binary file size": get_size(self.bin_file_name),
            "csv file size": get_size(self.file_name),
            "test duration": f"{(data[-1, 0] - data[0, 0])/1e9:.3f}s"
        })
            

