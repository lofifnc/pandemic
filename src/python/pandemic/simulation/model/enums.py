class Character:
    CONTINGENCY_PLANNER = 1
    DISPATCHER = 2
    MEDIC = 3
    OPERATIONS_EXPERT = 4
    QUARANTINE_SPECIALIST = 5
    RESEARCHER = 6
    SCIENTIST = 7

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

    __colors = {1: "blue", 2: "red", 3: "yellow", 4: "black"}

    @staticmethod
    def color(c: int) -> str:
        return Virus.__colors[c]


class GameState:
    RUNNING = 1
    WIN = 2
    LOST = 3
