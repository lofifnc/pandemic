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
    MOVE = 1
    DIRECT_FLIGHT = 2
    CHARTER_FLIGHT = 3
    SHUTTLE_FLIGHT = 4


class OtherAction(Enum):
    BUILD_RESEARCH_STATION = 1
    TREAT_DISEASE = 2
    SHARE_KNOWLEDGE = 3
    DISCOVER_CURE = 4