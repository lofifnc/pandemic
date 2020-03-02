from enum import Enum


class PlayerColor(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3
    WHITE = 4


class Virus(Enum):
    BLUE = 1
    RED = 2
    YELLOW = 3
    BLACK = 4


class MovementAction(Enum):
    def __init__(self, value, command):
        self.value = value
        self.command = command

    DRIVE = (1, "d")
    DIRECT_FLIGHT = (2, "f")
    CHARTER_FLIGHT = (3, "c")
    SHUTTLE_FLIGHT = (4, "s")


class OtherAction(Enum):
    def __init__(self, value, command):
        self.value = value
        self.command = command

    BUILD_RESEARCH_STATION = (1, "b")
    TREAT_DISEASE = (2, "t")
    SHARE_KNOWLEDGE = (3, "s")
    DISCOVER_CURE = (4, "d")
