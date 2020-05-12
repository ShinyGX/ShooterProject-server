class Singleton(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "__instance"):
            orig = super(Singleton, cls)
            cls.__instance = orig.__new__(cls)

        return cls.__instance
