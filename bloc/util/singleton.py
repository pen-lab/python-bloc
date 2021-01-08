from typing import Any


class Singleton:
    _singleton: 'Singleton' = None

    def __new__(cls) -> Any:
        if cls._singleton is None:
            cls._singleton = super().__new__(cls)
        return cls._singleton
