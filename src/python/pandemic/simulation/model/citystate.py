from typing import Set, Dict

from pandemic.simulation.model.city_id import City
from pandemic.simulation.model.enums import Virus


class CityState:
    def __init__(
        self,
        name: str,
        lat: float,
        lon: float,
        color: Virus,
        text_alignment: str = "left",
        research_station: bool = False,
    ):
        self.name = name
        self.lat = lat
        self.lon = lon
        self._viral_state = {Virus.BLUE: 0, Virus.RED: 0, Virus.YELLOW: 0, Virus.BLACK: 0}
        self.text_alignment = text_alignment
        assert isinstance(color, Virus)
        self.color = color
        self.neighbors: Set[City] = set()
        self._research_station = research_station

    def get_viral_state(self) -> Dict[Virus, int]:
        return self._viral_state

    def add_neighbor(self, neighbor: City):
        self.neighbors.add(neighbor)

    @property
    def viral_state(self) -> Dict[Virus, int]:
        return self._viral_state

    def inc_infection(self, color: Virus = None) -> bool:
        if color is None:
            color = self.color

        if self._viral_state[color] < 3:
            self._viral_state[color] += 1
            return False
        else:
            # outbreak!
            return True

    def dec_infection(self, color: Virus = None) -> bool:
        if color is None:
            color = self.color

        if self._viral_state[color] > 0:
            self._viral_state[color] -= 1
            return False
        else:
            # treated
            return True

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

    @property
    def text_offset(self):
        return 2 if self.text_alignment == "left" else -2

    def __str__(self):
        return f"{self.name} {self.lat}:{self.lon}"

    def has_research_station(self) -> bool:
        return self._research_station

    def build_research_station(self):
        self._research_station = True

    def remove_research_station(self):
        self._research_station = False
