import struct


class NetworkOutputStream(object):
    __data = []
    __type = []

    def push_char(self, c):
        self.__data.append(struct.pack("c", chr(c)))
        self.__type.append(1)

    def push_integer(self, i):
        self.__data.append(struct.pack("i", i))
        self.__type.append(1)

    def push_string(self, s):
        st = s.encode("utf-8")
        t = str(len(st)) + "s"
        self.__data.append(struct.pack(t, st))
        self.__type.append(1)

    def push_bool(self, b):
        if b is True:
            self.push_integer(1)
        else:
            self.push_integer(0)

    def push_float(self, d):
        self.__data.append(struct.pack("d", d))
        self.__type.append(1)

    def push_vector3(self, v3):
        self.push_float(v3.x)
        self.push_float(v3.y)
        self.push_float(v3.z)

    def push_quaternion(self, q):
        self.push_float(q.x)
        self.push_float(q.y)
        self.push_float(q.z)
        self.push_float(q.w)

    def push_byte_array(self, byte_array):
        self.__data.append(byte_array)
        self.__type.append(0)

    def flush_stream(self, has_head=True):
        data = bytes()
        for i in range(len(self.__data)):
            if self.__type[i] == 1:
                t = str(len(self.__data[i])) + "s"
                data += struct.pack(t, self.__data[i])
            else:
                if len(self.__data[i]) == 0:
                    continue
                data += self.__data[i]
        data_len = struct.pack("i", len(data))
        self.__data = []
        self.__type = []
        if has_head:
            return data_len + data
        else:
            return data
        # print "Output Data Size:", struct.unpack("i", data_len)[0], "Output Data TotalSize:", len(data + data_len)
        # return data_len + data

    def __push_end_mask(self):
        self.push_char(255)
        self.__type.append(1)
