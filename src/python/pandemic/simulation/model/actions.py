from dataclasses import dataclass, InitVar
from typing import Tuple, List

from pandemic.simulation.model.city_id import City, Card
from pandemic.simulation.model.enums import Virus, Character


def _csum(nums: List[int]):
    return sum((n * pow(100, idx) for idx, n in enumerate(nums)), 0)

@dataclass(unsafe_hash=True)
class ActionInterface:
    index = None

    def __post_init__(self):
        self.feature = self.index, self.csum()

    def to_command(self):
        raise NotImplementedError()

    def _key(self) -> List[int]:
        raise NotImplementedError()

    def csum(self) -> float:
        raise NotImplementedError()


@dataclass(unsafe_hash=True)
class Movement(ActionInterface):
    PREFIX = "m"

    command = None
    index = None
    dim = None
    player: Character
    destination: City

    def to_command(self):
        return f"{self.PREFIX} {self.command} {self.destination} {self.player}"

    def csum(self) -> float:
        return self.player * 100 + self.destination


@dataclass(unsafe_hash=True)
class DriveFerry(Movement):
    command = "d"
    index = 1
    dim = 4 * 6


@dataclass(unsafe_hash=True)
class DirectFlight(Movement):
    command = "f"
    index = DriveFerry.index + DriveFerry.dim
    dim = 4 * 7


@dataclass(unsafe_hash=True)
class CharterFlight(Movement):
    command = "c"
    index = DriveFerry.index + DriveFerry.dim
    dim = 4 * 47


@dataclass(unsafe_hash=True)
class ShuttleFlight(Movement):
    command = "s"
    index = CharterFlight.index + CharterFlight.dim
    dim = 4 * 5


@dataclass(unsafe_hash=True)
class Dispatch(Movement):
    command = "d"
    index = ShuttleFlight.index + ShuttleFlight.dim
    dim = 4 * 3


@dataclass(unsafe_hash=True)
class OperationsFlight(Movement):
    command = "o"
    index = Dispatch.index + Dispatch.dim
    dim = 48 * 7

    discard_card: City

    def to_command(self):
        return f"{super().to_command()} {self.discard_card}"

    def csum(self) -> float:
        return self.player * 10000 + self.destination * 100 + self.discard_card


#################
# Other Actions #
#################


class Other(ActionInterface):
    PREFIX = "o"


@dataclass(unsafe_hash=True)
class ShareKnowledge(Other):
    index = OperationsFlight.index + OperationsFlight.dim
    dim = 3 + 3

    player: Character
    card: City
    target_player: Character

    def to_command(self):
        return f"{self.PREFIX} s {self.player}  {self.card} {self.target_player}"

    def csum(self) -> float:
        return self.player * 10000 + self.card * 100 + self.target_player


@dataclass(unsafe_hash=True)
class TreatDisease(Other):
    index = ShareKnowledge.index + ShareKnowledge.dim
    dim = 4

    city: City
    target_virus: Virus

    def to_command(self):
        return f"{self.PREFIX} t {self.city} {self.target_virus}"

    def csum(self) -> float:
        return self.city * 100 + self.target_virus


@dataclass(unsafe_hash=True)
class DiscoverCure(Other):
    index = TreatDisease.index + TreatDisease.dim
    dim = 1

    target_virus: Virus

    def to_command(self):
        return f"{self.PREFIX} d {self.target_virus}"

    def csum(self) -> float:
        return self.target_virus


@dataclass(unsafe_hash=True)
class BuildResearchStation(Other):
    index = DiscoverCure.index + DiscoverCure.dim
    dim = 1

    city: City

    def to_command(self):
        return f"{self.PREFIX} b {self.city}"

    def csum(self) -> float:
        return self.city


@dataclass(unsafe_hash=True)
class ReserveCard(Other):
    index = BuildResearchStation.index + BuildResearchStation.dim
    dim = 1

    card: Card

    def to_command(self):
        return f"{self.PREFIX} r {self.card}"

    def csum(self) -> float:
        return self.card


######################
# Event Card Actions #
######################


@dataclass(unsafe_hash=True)
class Event(ActionInterface):
    PREFIX = "e"

    player: int


@dataclass(unsafe_hash=True)
class MoveResearchStation(Event):
    index = ReserveCard.index + ReserveCard.dim
    dim = 6

    player: int
    move_from: int

    def to_command(self):
        return f"{self.PREFIX} m ${self.player} {self.move_from}"

    def csum(self) -> float:
        return self.player * 100 + self.move_from


@dataclass(unsafe_hash=True)
class Forecast(Event):
    index = MoveResearchStation.index + MoveResearchStation.dim
    dim = 1

    def to_command(self):
        return f"{self.PREFIX} f ${self.player}"

    def csum(self) -> float:
        return 1


@dataclass(unsafe_hash=True)
class GovernmentGrant(Event):
    index = Forecast.index + Forecast.dim
    dim = 47

    target_city: City

    def to_command(self):
        return f"{self.PREFIX} g ${self.player} ${self.target_city}"

    def csum(self) -> float:
        return self.player * 100 + self.target_city


@dataclass(unsafe_hash=True)
class Airlift(Event):
    index = GovernmentGrant.index + GovernmentGrant.dim
    dim = 48 * 4

    target_player: Character
    destination: City

    def to_command(self):
        return f"{self.PREFIX} g ${self.player} ${self.target_player} " f"${self.destination}"

    def csum(self) -> float:
        return self.player * 100 + self.target_player * 100 + self.destination


@dataclass(unsafe_hash=True)
class ResilientPopulation(Event):
    index = Airlift.index + Airlift.dim
    dim = 1

    discard_city: City

    def to_command(self):
        return f"{self.PREFIX} r ${self.player} ${self.discard_city}"

    def csum(self) -> float:
        return self.player * 100 + self.discard_city


@dataclass(unsafe_hash=True)
class OneQuietNight(Event):
    index = ResilientPopulation.index + ResilientPopulation.dim
    dim = 1

    def to_command(self):
        return f"{self.PREFIX} q ${self.player}"

    def csum(self) -> float:
        return self.player * 100


@dataclass(unsafe_hash=True)
class DiscardCard(ActionInterface):
    index = OneQuietNight.index + OneQuietNight.dim
    dim = 9

    PREFIX = "t"

    player: Character
    card: Card

    def to_command(self):
        return f"{self.PREFIX} {self.player} {self.card}"

    def csum(self) -> float:
        return self.player * 100 + self.card


@dataclass(unsafe_hash=True)
class ChooseCard(ActionInterface):
    index = DiscardCard.index + DiscardCard.dim
    dim = 7

    PREFIX = "t"

    player: Character
    card: Card

    def to_command(self):
        return f"{self.PREFIX} {self.player} {self.card}"

    def csum(self) -> float:
        return self.player * 100 + self.card


ACTION_SPACE_DIM = (
    DriveFerry.dim
    + DirectFlight.dim
    + CharterFlight.dim
    + ShuttleFlight.dim
    + Dispatch.dim
    + OperationsFlight.dim
    + ShareKnowledge.dim
    + TreatDisease.dim
    + DiscoverCure.dim
    + BuildResearchStation.dim
    + ReserveCard.dim
    + MoveResearchStation.dim
    + Forecast.dim
    + GovernmentGrant.dim
    + Airlift.dim
    + ResilientPopulation.dim
    + OneQuietNight.dim
    + DiscardCard.dim
    + ChooseCard.dim
)
