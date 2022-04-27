from enum import Enum, auto


class MemorySegment(Enum):
    DATA = auto()
    TEXT = auto()
    NONE = auto()