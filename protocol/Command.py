from Snapshot import *
from network.NetworkOutputStream import NetworkOutputStream

COMMAND_TYPE_INPUT = 0
COMMAND_TYPE_SYNC = 1
COMMAND_TYPE_CONNECTION = 2
COMMAND_TYPE_DISCONNECTION = 3
COMMAND_TYPE_CREATE_NEW_PLAYER = 4


class InputCommand(object):
    __output = NetworkOutputStream()

    def __init__(self):
        self.snapshots = []
        self.snapshotFrameCount = 0

    def deserialize(self, net_input):
        self.snapshotFrameCount = net_input.get_integer()
        count = net_input.get_integer()
        for i in range(count):
            snapshot_type = net_input.get_integer()
            self.snapshots.append(deserialize_snapshot(snapshot_type, net_input))
            # print self.snapshots[i].to_string()

        return self

    def serialize(self):
        self.__output.push_integer(COMMAND_TYPE_INPUT)
        self.__output.push_integer(self.snapshotFrameCount)
        self.__output.push_integer(len(self.snapshots))
        for s in self.snapshots:
            self.__output.push_byte_array(s.serialize())

        return self.__output.flush_stream()


class SyncCommand(object):
    __output = NetworkOutputStream()

    def __init__(self):
        self.syncSnapshots = []

    def serialize(self):
        print "sync serialize"
        self.__output.push_integer(COMMAND_TYPE_SYNC)
        self.__output.push_integer(len(self.syncSnapshots))
        print "sync frame %d" % len(self.syncSnapshots)
        for sl in self.syncSnapshots:
            self.__output.push_integer(len(sl))
            print "sync snapshot size %d" % len(sl)
            for s in sl:
                self.__output.push_byte_array(s.serialize())
                print s.to_string()

        return self.__output.flush_stream()

    def deserialize(self, net_input):
        count = net_input.get_integer()
        self.syncSnapshots = []
        for i in range(count):
            snapshots_len = net_input.get_integer()
            self.syncSnapshots.append([])
            for j in range(snapshots_len):
                snapshot_type = net_input.get_integer()
                s = deserialize_snapshot(snapshot_type, net_input)
                self.syncSnapshots[i].append(s)

        return self


class ConnectionCommand(object):
    __output = NetworkOutputStream()

    def __init__(self):
        self.id = 0

    def serialize(self):
        self.__output.push_integer(COMMAND_TYPE_CONNECTION)
        self.__output.push_integer(self.id)
        return self.__output.flush_stream()

    def deserialize(self, net_input):
        self.id = net_input.get_integer()
        return self


class CreateNewPlayerCommand(object):
    __output = NetworkOutputStream()

    def __init__(self):
        self.id = 0
        self.hp = 100

    def serialize(self):
        self.__output.push_integer(COMMAND_TYPE_CREATE_NEW_PLAYER)
        self.__output.push_integer(self.id)
        self.__output.push_integer(self.hp)
        return self.__output.flush_stream()

    def deserialize(self, net_input):
        self.id = net_input.get_integer()
        self.hp = net_input.get_integer()


def deserialize_snapshot(snapshot_type, net_input):
    if snapshot_type == SNAPSHOT_TYPE_BASE:
        s = Snapshot()
        s.deserialize(net_input)
        return s
    elif snapshot_type == SNAPSHOT_TYPE_MOVE:
        s = Move()
        s.deserialize(net_input)
        return s
    elif snapshot_type == SNAPSHOT_TYPE_ROTATE:
        s = Rotate()
        s.deserialize(net_input)
        return s
    elif snapshot_type == SNAPSHOT_TYPE_SHOOT:
        s = Shoot()
        s.deserialize(net_input)
        return s
    elif snapshot_type == SNAPSHOT_TYPE_DAMAGE:
        s = Damage()
        s.deserialize(net_input)
        return s
    else:
        print "Error Command"
        pass
