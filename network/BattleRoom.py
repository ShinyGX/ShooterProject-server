class BattleRoom(object):
    __sock_list = []
    __id_to_sock = {}

    __frame = 0

    def __init__(self, room_id):
        __room_id = room_id
        self.__is_playing = False

    def add_player(self, cs):
        if cs not in self.__sock_list:
            self.__sock_list.append(cs)
            self.__id_to_sock[len(self.__sock_list)] = cs

        if len(self.__sock_list) == 2:
            self.start_game()

    def start_game(self):
        self.__is_playing = True

    def get_is_playing(self):
        return self.__is_playing



