class IndexObjectPool(object):
    __objectList = []
    __usedList = []

    __active_count = 0

    def __init__(self, objCount):
        self.__usedList = [False for i in range(objCount)]

    def get_obj(self, obj):
        for i in range(len(self.__usedList)):
            if not self.__usedList[i]:
                if len(self.__objectList) > i:
                    self.__objectList[i] = obj
                else:
                    self.__objectList.append(obj)
                self.__usedList[i] = True
                self.__active_count += 1
                return self.__objectList[i], i

        return None, -1

    def recover(self, index):
        if index >= len(self.__usedList) or index < 0:
            return
        self.__active_count -= 1
        self.__usedList[index] = False

    def get_active_count(self):
        return self.__active_count

    def get(self, i):
        return self.__objectList[i]

    def foreach(self, func):
        for i in range(len(self.__objectList)):
            if self.__usedList[i]:
                func(self.__objectList[i])
