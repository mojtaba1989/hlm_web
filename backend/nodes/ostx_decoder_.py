import struct
import math
from enum import Enum
import pandas as pd
import time

class Type:
    @classmethod
    class Byte:
        is_integer = True
        size = 1
        signed = True
        invalid = 0x80

    @classmethod
    class UByte:
        is_integer = True
        size = 1
        signed = False
        invalid = 0xFF

    @classmethod
    class Short:
        is_integer = True
        size = 2
        signed = True
        invalid = 0x8000

    @classmethod
    class UShort:
        is_integer = True
        size = 2
        signed = False
        invalid = 0xFFFF

    @classmethod
    class Word:
        is_integer = True
        size = 3
        signed = True
        invalid = 0x800000

    @classmethod
    class UWord:
        is_integer = True
        size = 3
        signed = False
        invalid = 0xFFFFFF

    @classmethod
    class Long:
        is_integer = True
        size = 4
        signed = True
        invalid = 0x80000000

    @classmethod
    class ULong:
        is_integer = True
        size = 4
        signed = False
        invalid = 0xFFFFFFFF

    @classmethod
    class int64:
        is_integer = True
        size = 8
        signed = True
        invalid = 0x8000000000000000

    @classmethod
    class Uint64:
        is_integer = True
        size = 8
        signed = False
        invalid = 0xFFFFFFFFFFFFFFFF

    @classmethod
    class Float:
        is_integer = False
        size = 4
        signed = True
        invalid = 0x80000000

    @classmethod
    class Double:
        is_integer = False
        size = 8
        signed = True
        invalid = 0x8000000000000000

class MsgType:
    Unknown = 0xFF
    NCOM = 0xE7
    RCOM = 0x57

class ReturnCode(Enum):
    Unknown = 0
    Success = 1
    CheckSumFail = 2
    TypeMismatch = 3
    LenMismatch = 4
    Forbidden = 5
    BadDecode = 6
    
class OSTXDecoder():
    @staticmethod
    def from_bytes(buffer, start, type=Type.Byte, scale=1, check_valid=False)-> tuple[int, int]:
        if type.is_integer:
            res = int.from_bytes(buffer[start:start+type.size], byteorder='little', signed=type.signed)
            if check_valid and buffer == type.invalid:
                res = pd.NA
        elif type == Type.Float:
            res = struct.unpack('<f', buffer[start:start+type.size])[0]
        elif type == Type.Double:
            res = struct.unpack('<d', buffer[start:start+type.size])[0]
        return res * scale, start + type.size
    
    @staticmethod
    def check_type(buffer, type: MsgType)-> bool:
        if buffer[0] == type:
            return True
        return False
    
    @staticmethod
    def get_type(buffer)-> MsgType:
        if buffer[0] == MsgType.NCOM:
            return MsgType.NCOM
        if buffer[0] == MsgType.RCOM:
            return MsgType.RCOM
        else:
            return MsgType.Unknown
    
    @classmethod
    def decode(cls, buffer, type=MsgType.Unknown, checksum=False)-> tuple[ReturnCode, dict[str, any]]:
        if type == MsgType.Unknown:
            type = cls.get_type(buffer)
        if type == MsgType.RCOM:
            return cls.decode_rcom(buffer, checksum)
        if type == MsgType.NCOM:
            return cls.decode_ncom_full(buffer, checksum)
        pass

    @classmethod
    def decode_ncom_full(cls, buffer, checksum=False)-> tuple[ReturnCode, dict[str, any]]:
        ret, msg = cls.decode_ncom(buffer, checksum)
        if ret != ReturnCode.Success:
            return ret, {}
        ret, msg['Batch_A'] = cls.decode_ncom_BatchA(msg['Batch_A'])
        if ret != ReturnCode.Success:
            return ret, {}
        ret, msg['Batch_B'] = cls.decode_ncom_BatchB(msg['Batch_B'])
        if ret != ReturnCode.Success:
            return ret, {}
        return ReturnCode.Success, {**msg['Batch_A'], **msg['Batch_B']}
    @classmethod
    def decode_ncom(cls, buffer, checksum=False)-> tuple[ReturnCode, dict[str, any]]:
        if len(buffer) != 72:
            return ReturnCode.LenMismatch, {}
        if not cls.check_type(buffer, MsgType.NCOM):
            return ReturnCode.TypeMismatch, {}
        res = struct.unpack('>B20s2b38s2b8sb', buffer)
        if res[2]==11:
            return ReturnCode.Forbidden, {}
        if not checksum:
            return ReturnCode.Success, {
                'Sync': hex(res[0]),
                'Batch_A': res[1],
                'Nav_stat': res[2],
                'Checksum_1': res[3],
                'Batch_B': res[4],
                'Checksum_2': res[5],
                'Stat_chan': res[6],
                'Batch_S': res[7],
                'Checksum_3': res[8],
                }

        # Checksum1
        if sum(buffer[1:22])%256 != res[3]:
            return ReturnCode.CheckSumFail, {}
        # Checksum2
        if sum(buffer[1:61])%256 != res[5]:
            return ReturnCode.CheckSumFail, {}
        # Checksum3
        if sum(buffer[1:71])%256 != res[8]:
            return ReturnCode.CheckSumFail, {}
        return ReturnCode.Success, {
                'Batch_A': res[1],
                'Batch_B': res[4],
                }

    @classmethod
    def decode_ncom_BatchA(cls, buffer)-> tuple[ReturnCode, dict[str, any]]:
        if len(buffer) != 20:
            return ReturnCode.LenMismatch, {}
        idx = 0
        Time, idx       = cls.from_bytes(buffer, idx, Type.Short, scale=1e-3)
        Accel_x, idx    = cls.from_bytes(buffer, idx, Type.Word, scale=1e-4)
        Accel_y, idx    = cls.from_bytes(buffer, idx, Type.Word, scale=1e-4)
        Accel_z, idx    = cls.from_bytes(buffer, idx, Type.Word, scale=1e-4)
        Gyro_x, idx     = cls.from_bytes(buffer, idx, Type.Word, scale=1e-5)
        Gyro_y, idx     = cls.from_bytes(buffer, idx, Type.Word, scale=1e-5)
        Gyro_z, idx     = cls.from_bytes(buffer, idx, Type.Word, scale=1e-5)
        if idx != 20:
            return ReturnCode.BadDecode, {}
        return ReturnCode.Success, {
            'Time[s]'               : Time,
            'Acceleration_x[m/s/s]' : Accel_x,
            'Acceleration_y[m/s/s]' : Accel_y,
            'Acceleration_z[m/s/s]' : Accel_z,
            'Angular_rate_x[rad/s]' : Gyro_x,
            'Angular_rate_y[rad/s]' : Gyro_y,
            'Angular_rate_z[rad/s]' : Gyro_z,
            }
    
    @classmethod
    def decode_ncom_BatchB(cls, buffer)-> tuple[ReturnCode, dict[str, any]]:
        if len(buffer) != 38:
            return ReturnCode.LenMismatch, {}
        idx = 0
        Lattitude, idx      = cls.from_bytes(buffer, idx, Type.Double)
        Longitude, idx      = cls.from_bytes(buffer, idx, Type.Double)
        Altitude, idx       = cls.from_bytes(buffer, idx, Type.Float)
        North_velocity, idx = cls.from_bytes(buffer, idx, Type.Word, scale=1e-4)
        East_velocity, idx  = cls.from_bytes(buffer, idx, Type.Word, scale=1e-4)
        Down_velocity, idx  = cls.from_bytes(buffer, idx, Type.Word, scale=1e-4)
        Heading, idx        = cls.from_bytes(buffer, idx, Type.Word, scale=1e-6)
        Pitch, idx          = cls.from_bytes(buffer, idx, Type.Word, scale=1e-6)
        Roll, idx           = cls.from_bytes(buffer, idx, Type.Word, scale=1e-6)
        if idx != 38:
            return ReturnCode.BadDecode, {}
        
        return ReturnCode.Success, {
            'Lattitude[deg]'        : math.degrees(Lattitude),
            'Longitude[deg]'        : math.degrees(Longitude),
            'Altitude[m]'           : Altitude,
            'North_velocity[m/s]'   : North_velocity,
            'East_velocity[m/s]'    : East_velocity,
            'Down_velocity[m/s]'    : Down_velocity,
            'Heading[rad]'          : Heading,
            'Pitch[rad]'            : Pitch,
            'Roll[rad]'             : Roll,
            }
    
    @classmethod
    def decode_rcom(cls, buffer, checksum=False)-> tuple[ReturnCode, dict[str, any]]:
        if len(buffer) != 189:
            return ReturnCode.LenMismatch, {}
        if checksum and sum(buffer[1:188])%256 != buffer[188]:
            return ReturnCode.CheckSumFail, {}
        if not cls.check_type(buffer, MsgType.RCOM):
            return ReturnCode.TypeMismatch, {}
        res = {}
        res['Target_number']                                        = cls.from_bytes(buffer, 6, Type.UByte)[0]
        res['Total_number_of_targets']                              = cls.from_bytes(buffer, 7, Type.UByte)[0]
        res['Lateral_range[m]']                                     = cls.from_bytes(buffer, 8, Type.Long, scale=1e-3, check_valid=True)[0]
        res['Longitudinal_range[m]']                                = cls.from_bytes(buffer, 12, Type.Long, scale=1e-3, check_valid=True)[0]
        res['Lateral_range_rate[m/s]']                              = cls.from_bytes(buffer, 16, Type.Short, scale=1e-2, check_valid=True)[0]
        res['Longitudinal_range_rate[m/s]']                         = cls.from_bytes(buffer, 18, Type.Short, scale=1e-2, check_valid=True)[0]
        res['Hunter_measurement_point_position_x_from_target[m]']   = cls.from_bytes(buffer, 20, Type.Long, scale=1e-3, check_valid=True)[0]
        res['Hunter_measurement_point_position_y_from_target[m]']   = cls.from_bytes(buffer, 24, Type.Long, scale=1e-3, check_valid=True)[0]
        res['Target_measurement_point_position_x[m]']               = cls.from_bytes(buffer, 28, Type.Long, scale=1e-3, check_valid=True)[0]
        res['Target_measurement_point_position_y[m]']               = cls.from_bytes(buffer, 32, Type.Long, scale=1e-3, check_valid=True)[0]
        res['Heading_angle_of_hunter[deg]']                         = cls.from_bytes(buffer, 36, Type.UShort, scale=1e-2, check_valid=True)[0]
        res['Heading_angle_of_target[deg]']                         = cls.from_bytes(buffer, 38, Type.UShort, scale=1e-2, check_valid=True)[0]
        res['Resultant_range[m]']                                   = cls.from_bytes(buffer, 114, Type.ULong, scale=1e-3, check_valid=True)[0]
        return ReturnCode.Success, res

# EXAMPLE
if __name__ == '__main__':
    t_start = time.time()
    data_list = []
    with open(r'tests/20260218T024/rcom.bin', 'rb') as f:
        while True:
            header = f.read(12)
            if not header:
                break
            stamp, length = struct.unpack("<QI", header)
            msg = f.read(length)
            ret, depacked = OSTXDecoder.decode(msg, checksum=True)
            if ret == ReturnCode.Success:
                depacked['time_nsec'] = stamp
                data_list.append(depacked)

    df = pd.DataFrame(data_list)
    df.to_csv('RCOM_decoded.csv', index=False)
    t_end = time.time()
    print(f"Time: {t_end-t_start}")
    print(df.head())