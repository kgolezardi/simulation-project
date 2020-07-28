import enum


class Event(enum.Enum):
    ENTER = 0
    RECEPTION_READY = 1
    DOCTOR_READY = 2
    BORED_IN_RECEPTION = 3
    BORED_IN_ROOM = 4


class Log(enum.Enum):
    ENTER = 0
    EXIT = 1
