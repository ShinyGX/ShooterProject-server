# encoding=utf-8
import struct
import uuid

import network
import sql
from Log.ConsoleLog import ConsoleLog


def demo():
    # 使用bin_buf = struct.pack(fmt, buf)将buf为二进制数组bin_buf
    # 使用buf = struct.unpack(fmt, bin_buf)将bin_buf二进制数组反转换回buf

    # 整型数 -> 二进制流
    buf1 = (1 << 32) >> 32
    bin_buf1 = struct.pack('i', buf1)  # 'i'代表'integer'
    ret1 = struct.unpack('i', bin_buf1)
    print bin_buf1, '  <====>  ', ret1

    # 浮点数 -> 二进制流
    buf2 = 3.1415
    bin_buf2 = struct.pack('d', buf2)  # 'd'代表'double'
    ret2 = struct.unpack('d', bin_buf2)
    print bin_buf2, '  <====>  ', ret2

    # 字符串 -> 二进制流
    buf3 = 'Hello World'
    bin_buf3 = struct.pack('11s', buf3)  # '11s'代表长度为11的'string'字符数组
    ret3 = struct.unpack('11s', bin_buf3)
    print bin_buf3, '  <====>  ', ret3

    # 结构体 -> 二进制流
    # 假设有一个结构体
    # struct header {
    #   int buf1;
    #   double buf2;
    #   char buf3[11];
    # }
    bin_buf_all = struct.pack('id11s', buf1, buf2, buf3)
    ret_all = struct.unpack('id11s', bin_buf_all)
    print bin_buf_all, '  <====>  ', ret_all

    u = uuid.uuid4()
    max_int64 = 0xFFFFFFFFFFFFFFFF
    packed = struct.pack('>QQ', (u.int >> 64) & max_int64, u.int & max_int64)
    # unpack
    a, b = struct.unpack('>QQ', packed)
    unpacked = (a << 64) | b

    print packed, '  <====>  ', unpacked


if __name__ == "__main__":
    a = [[] for i in range(10)]
    print  a
    # sql.SqlManager.init_sql()
    # server = network.DailyTcpServer()
    # server.start_session()
