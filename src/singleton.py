import typing


class SingletonBehavior:
    __instance: typing.Optional[typing.Self] = None

    @classmethod
    def get_instance(cls, *args, **kwargs) -> typing.Self:
        if not cls.__instance:
            cls.__instance = cls(*args, **kwargs)
        return cls.__instance
