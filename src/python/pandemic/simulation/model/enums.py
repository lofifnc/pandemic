from enum import Enum


class Character(bytes, Enum):
    def __new__(cls, value, color):
        obj = bytes.__new__(cls, [value])
        obj._value_ = value
        obj.color = color
        return obj

    CONTINGENCY_PLANNER = (1, "teal")  # "CONTINGENCY"
    DISPATCHER = (2, "pink")  # DISPATCHER
    MEDIC = (3, "orange")  # MEDIC
    OPERATIONS_EXPERT = (4, "green")  # OPERATIONS EXPERT
    QUARANTINE_SPECIALIST = (5, "darkgreen")  # QUARANTINE SPECIALIST
    RESEARCHER = (6, "brown")  # RESEARCHER
    SCIENTIST = (7, "white")  # SCIENTIST


class Virus(Enum):
    BLUE = 1
    RED = 2
    YELLOW = 3
    BLACK = 4


class GameState(Enum):
    RUNNING = 1
    WIN = 2
    LOST = 3
