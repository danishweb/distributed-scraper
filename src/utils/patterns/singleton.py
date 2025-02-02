from typing import Dict, Type


class SingletonMeta(type):
    __instances: Dict[Type, object] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instances:
            cls.__instances[cls] = super().__call__(*args, **kwargs)
        return cls.__instances[cls]