from Vector import Vector3
from Vector import Quaternion
from network.NetworkOutputStream import NetworkOutputStream
from network.NetworkInputStream import NetworkInputStream

SNAPSHOT_TYPE_BASE = 0
SNAPSHOT_TYPE_MOVE = 1
SNAPSHOT_TYPE_ROTATE = 2
SNAPSHOT_TYPE_SHOOT = 3
SNAPSHOT_TYPE_DAMAGE = 4


class Snapshot(object):
    __output = NetworkOutputStream()

    def __init__(self):
        self.id = -1
        self.frame = -1
        self.fromHost = False

    def serialize(self):
        self.__output.push_integer(SNAPSHOT_TYPE_BASE)
        self.__output.push_integer(self.id)
        self.__output.push_integer(self.frame)
        self.__output.push_bool(self.fromHost)
        return self.__output.flush_stream(False)

    def deserialize(self, net_input):
        self.id = net_input.get_integer()
        self.frame = net_input.get_integer()
        self.fromHost = net_input.get_bool()


class Move(Snapshot):
    __output = NetworkOutputStream()

    def __init__(self):
        super(Move, self).__init__()
        self.velocity = Vector3()
        self.position = Vector3()

    def serialize(self):
        self.__output.push_integer(SNAPSHOT_TYPE_MOVE)
        self.__output.push_integer(self.id)
        self.__output.push_integer(self.frame)
        self.__output.push_bool(self.fromHost)
        self.__output.push_vector3(self.velocity)
        self.__output.push_vector3(self.position)
        return self.__output.flush_stream(False)

    def deserialize(self, net_input):
        self.id = net_input.get_integer()
        self.frame = net_input.get_integer()
        self.fromHost = net_input.get_bool()
        self.velocity = net_input.get_vector3()
        self.position = net_input.get_vector3()

    def to_string(self):
        return "[id:" + str(self.id) + ",frame:" + str(self.frame) + \
               ",fromHost:" + str(self.fromHost) + \
               ",velocity:(" + str(self.velocity.x) + "," + str(self.velocity.y) + "," + str(self.velocity.z) + ")" + \
               ",position:(" + str(self.position.x) + "," + str(self.position.y) + "," + str(
            self.position.z) + ")" + "]"


class Rotate(Snapshot):
    __output = NetworkOutputStream()

    def __init__(self):
        super(Rotate, self).__init__()
        self.velocity = Vector3()
        self.rotation = Quaternion()

    def serialize(self):
        self.__output.push_integer(SNAPSHOT_TYPE_ROTATE)
        self.__output.push_integer(self.id)
        self.__output.push_integer(self.frame)
        self.__output.push_bool(self.fromHost)
        self.__output.push_vector3(self.velocity)
        self.__output.push_quaternion(self.rotation)
        return self.__output.flush_stream(False)

    def deserialize(self, net_input):
        self.id = net_input.get_integer()
        self.frame = net_input.get_integer()
        self.fromHost = net_input.get_bool()
        self.velocity = net_input.get_vector3()
        self.rotation = net_input.get_quaternion()


class Shoot(Snapshot):
    __output = NetworkOutputStream()

    def __init__(self):
        super(Shoot, self).__init__()
        self.position = Vector3()
        self.rotation = Quaternion()

    def serialize(self):
        self.__output.push_integer(SNAPSHOT_TYPE_SHOOT)
        self.__output.push_integer(self.id)
        self.__output.push_integer(self.frame)
        self.__output.push_bool(self.fromHost)
        self.__output.push_vector3(self.position)
        self.__output.push_quaternion(self.rotation)
        return self.__output.flush_stream(False)

    def deserialize(self, net_input):
        self.id = net_input.get_integer()
        self.frame = net_input.get_integer()
        self.fromHost = net_input.get_bool()
        self.position = net_input.get_vector3()
        self.rotation = net_input.get_quaternion()


class Damage(Snapshot):
    __output = NetworkOutputStream()

    def __init__(self):
        super(Damage, self).__init__()
        self.hp = 0

    def serialize(self):
        self.__output.push_integer(SNAPSHOT_TYPE_DAMAGE)
        self.__output.push_integer(self.id)
        self.__output.push_integer(self.frame)
        self.__output.push_bool(self.fromHost)
        self.__output.push_integer(self.hp)
        return self.__output.flush_stream(False)

    def deserialize(self, net_input):
        self.id = net_input.get_integer()
        self.frame = net_input.get_integer()
        self.fromHost = net_input.get_bool()
        self.hp = net_input.get_integer()
