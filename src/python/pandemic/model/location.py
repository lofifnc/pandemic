from typing import Set, List, Dict

from pandemic.model.enums import Virus


class Location:
    def __init__(
        self, name: str, lat: float, lon: float, color: Virus, text_alignment="left"
    ):
        self._name = name
        self._lat = lat
        self._lon = lon
        self._viral_state = {
            Virus.BLUE: 0,
            Virus.RED: 0,
            Virus.YELLOW: 0,
            Virus.BLACK: 0,
        }
        self.text_alignment = text_alignment
        assert isinstance(color, Virus)
        self._color = color
        self._neighbors: Set[str] = set()

    def get_color(self) -> Virus:
        return self._color

    def get_display_color(self) -> str:
        return self._color.name.lower()

    def get_name(self) -> str:
        return self._name

    def get_lat(self) -> float:
        return self._lat

    def get_lon(self) -> float:
        return self._lon

    def get_viral_state(self) -> Dict[Virus, int]:
        return self._viral_state

    def add_neighbor(self, neighbor: str):
        self._neighbors.add(neighbor)

    """
        Increment the infection marker in the color of location.
        :returns True if outbreak happens
    """

    def inc_infection(self, color: Virus = None) -> bool:
        if color is None:
            color = self._color

        if self._viral_state[color] < 3:
            self._viral_state[color] += 1
            return False
        else:
            # outbreak!
            return True

    def dec_infection(self, color: Virus = None) -> bool:
        if color is None:
            color = self._color

        if self._viral_state[color] > 0:
            self._viral_state[color] -= 1
            return False
        else:
            # treated
            return True

    def get_neighbors(self) -> Set[str]:
        return self._neighbors

    def format_infection_state(self) -> str:
        state = ""
        if self._viral_state[Virus.RED] > 0:
            state += f"re{self._viral_state[Virus.RED]} "
        if self._viral_state[Virus.BLUE] > 0:
            state += f"bu{self._viral_state[Virus.BLUE]} "
        if self._viral_state[Virus.BLACK] > 0:
            state += f"bl{self._viral_state[Virus.BLACK]} "
        if self._viral_state[Virus.YELLOW] > 0:
            state += f"ye{self._viral_state[Virus.YELLOW]} "
        return state

    def get_text_offset(self):
        return 2 if self.text_alignment == "left" else -2

    def __str__(self):
        return f"{self._name} {self._lat}:{self._lon}"
