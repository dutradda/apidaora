from typing import ClassVar


class ClassController:
    path: ClassVar[str]

    def __init_subclass__(cls, path: str) -> None:
        cls.path = path
