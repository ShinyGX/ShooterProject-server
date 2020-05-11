import threading


class PlayerInfo(object):
    def __init__(self):
        self.id = 0
        self.name = "nan"
        self.is_ready = False
        self.is_empty = True


class BattleRoom(object):
    __room_max_person = 2
    __player_info_list = [PlayerInfo()] * 2

    room_id = 0

    def is_all_ready(self):
        if not self.is_full():
            return False
        for i in range(0, self.__room_max_person):
            if not self.__player_info_list[i].is_ready:
                return False
        return True

    def is_full(self):
        for info in self.__player_info_list:
            if info.is_empty:
                return False
        return True

    def add_player_info(self, name):
        for i in range(0, len(self.__player_info_list)):
            if not self.__player_info_list[i].is_empty:
                continue

            self.__player_info_list[i].is_empty = False
            self.__player_info_list[i].name = name
            return self.__player_info_list[i].id

        return None

    def player_ready(self, client_id):
        self.__player_info_list[client_id].is_ready = True

    def player_cancel(self, client_id):
        self.__player_info_list[client_id].is_empty = True


class BattleRoomHandler(object):
    def __init__(self):
        self.__free = []
        self.__running = []
        self.__mutex = threading.Lock()
        self.__room_id = 0

    def get_room(self, name):
        self.__mutex.acquire()
        if len(self.__free) > 0:
            room = self.__free[len(self.__free) - 1]
            client_id = room.add_player_info(name)
            if room.is_full():
                self.__running.append(room)
                self.__free.pop()
        else:
            room = self.__create_room()

            client_id = room.add_player_info(name)
            if room.is_full():
                self.__running.append(room)
                self.__free.pop()
            else:
                self.__free.append(room)
        self.__mutex.release()

        return room, client_id

    def ready(self, room_id, client_id):
        for r in self.__free:
            if r.room_id == room_id:
                r.player_ready(client_id)
                return True

        return False

    def cancel(self, room_id, client_id):
        for r in self.__free:
            if r.room_id == room_id:
                r.player_cancel(client_id)
                return True
        return False

    def __create_room(self):
        room = BattleRoom()
        room.room_id = self.__room_id
        self.__room_id += 1
        return room
