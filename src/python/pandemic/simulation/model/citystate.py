from dataclasses import dataclass, field
from typing import Set, Dict, List

from pandemic.simulation.model.city_id import City
from pandemic.simulation.model.enums import Virus


@dataclass
class CityState:

    viral_state: Dict[int, int] = field(
        default_factory=lambda: {Virus.BLUE: 0, Virus.RED: 0, Virus.YELLOW: 0, Virus.BLACK: 0}
    )
    research_station: bool = False

    def inc_infection(self, color: Virus) -> bool:
        if self.viral_state[color] < 3:
            self.viral_state[color] += 1
            return False
        else:
            # outbreak!
            return True

    def dec_infection(self, color: Virus = None) -> bool:
        if color is None:
            color = self.color

        if self.viral_state[color] > 0:
            self.viral_state[color] -= 1
            return False
        else:
            # treated
            return True

    def format_infection_state(self) -> str:
        state = ""
        if self.viral_state[Virus.RED] > 0:
            state += f"re{self.viral_state[Virus.RED]} "
        if self.viral_state[Virus.BLUE] > 0:
            state += f"bu{self.viral_state[Virus.BLUE]} "
        if self.viral_state[Virus.BLACK] > 0:
            state += f"bl{self.viral_state[Virus.BLACK]} "
        if self.viral_state[Virus.YELLOW] > 0:
            state += f"ye{self.viral_state[Virus.YELLOW]} "
        return state

    # @property
    # def text_offset(self):
    #     return 2 if self.text_alignment == "left" else -2
    #
    # def __str__(self):
    #     return f"{self.name} {self.lat}:{self.lon}"

    def has_research_station(self) -> bool:
        return self.research_station

    def build_research_station(self):
        self.research_station = True

    def remove_research_station(self):
        self.research_station = False
