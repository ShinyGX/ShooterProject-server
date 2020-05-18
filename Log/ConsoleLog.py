from core import Singleton


class ConsoleLog(Singleton):
    def __init__(self):
        self.__log = ""

    def set_log(self, log):
        self.__log += log

    def show_log(self):
        print "\r %s" % self.__log,
