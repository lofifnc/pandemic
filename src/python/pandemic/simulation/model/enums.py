from enum import Enum


class Character:
    CONTINGENCY_PLANNER = 1  # "CONTINGENCY"
    DISPATCHER = 2  # DISPATCHER
    MEDIC = 3  # MEDIC
    OPERATIONS_EXPERT = 4  # OPERATIONS EXPERT
    QUARANTINE_SPECIALIST = 5  # QUARANTINE SPECIALIST
    RESEARCHER = 6  # RESEARCHER
    SCIENTIST = 7  # SCIENTIST

    __members__ = {1, 2, 3, 4, 5, 6, 7}

    __colors = {1: "teal", 2: "pink", 3: "orange", 4: "green", 5: "darkgreen", 6: "brown", 7: "white"}

    @staticmethod
    def color(c: int) -> str:
        return Character.__colors[c]


class Virus:
    BLUE = 1
    RED = 2
    YELLOW = 3
    BLACK = 4


class GameState:
    RUNNING = 1
    WIN = 2
    LOST = 3
