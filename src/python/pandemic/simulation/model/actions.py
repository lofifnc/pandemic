from dataclasses import dataclass
from typing import FrozenSet, Tuple

from pandemic.simulation.model.city_id import City, Card
from pandemic.simulation.model.enums import Virus, Character
from pandemic.simulation.utils import iterable_to_string


class ActionInterface:
    def to_command(self):
        raise NotImplemented()


@dataclass(frozen=True)
class Movement(ActionInterface):
    PREFIX = "m"

    command = None
    player: Character
    destination: City

    def to_command(self):
        return f"{self.PREFIX} {self.command} {self.destination} {self.player}"


@dataclass(frozen=True)
class DriveFerry(Movement):
    command = "d"


@dataclass(frozen=True)
class DirectFlight(Movement):
    command = "f"


@dataclass(frozen=True)
class CharterFlight(Movement):
    command = "c"


@dataclass(frozen=True)
class ShuttleFlight(Movement):
    command = "s"


@dataclass(frozen=True)
class Dispatch(Movement):
    command = "d"


@dataclass(frozen=True)
class OperationsFlight(Movement):
    command = "o"
    discard_card: City

    def to_command(self):
        return f"{super().to_command()} {self.discard_card}"


#################
# Other Actions #
#################


class Other(ActionInterface):
    PREFIX = "o"


@dataclass(frozen=True)
class ShareKnowledge(Other):
    player: Character
    card: City
    target_player: Character

    def to_command(self):
        return f"{self.PREFIX} s {self.player}  {self.card} {self.target_player}"


@dataclass(frozen=True)
class TreatDisease(Other):
    city: City
    target_virus: Virus

    def to_command(self):
        return f"{self.PREFIX} t {self.city} {self.target_virus}"


@dataclass(frozen=True)
class DiscoverCure(Other):
    target_virus: Virus

    def to_command(self):
        return f"{self.PREFIX} d {self.target_virus}"


@dataclass(frozen=True)
class BuildResearchStation(Other):
    city: City

    def to_command(self):
        return f"{self.PREFIX} b {self.city}"


@dataclass(frozen=True)
class ReserveCard(Other):
    card: Card

    def to_command(self):
        return f"{self.PREFIX} r {self.card}"


######################
# Event Card Actions #
######################


@dataclass(frozen=True)
class Event(ActionInterface):
    PREFIX = "e"

    player: Character


@dataclass(frozen=True)
class MoveResearchStation(Event):
    player: Character
    move_from: City

    def to_command(self):
        return f"{self.PREFIX} m ${self.player} {self.move_from}"


@dataclass(frozen=True)
class Forecast(Event):
    def to_command(self):
        return f"{self.PREFIX} f ${self.player}"


@dataclass(frozen=True)
class GovernmentGrant(Event):
    target_city: City

    def to_command(self):
        return f"{self.PREFIX} g ${self.player} ${self.target_city}"


@dataclass(frozen=True)
class Airlift(Event):
    target_player: Character
    destination: City

    def to_command(self):
        return f"{self.PREFIX} g ${self.player} ${self.target_player} " f"${self.destination}"


@dataclass(frozen=True)
class ResilientPopulation(Event):
    discard_city: City

    def to_command(self):
        return f"{self.PREFIX} r ${self.player} ${self.discard_city}"


@dataclass(frozen=True)
class OneQuietNight(Event):
    def to_command(self):
        return f"{self.PREFIX} q ${self.player}"


@dataclass(frozen=True)
class DiscardCard(ActionInterface):
    PREFIX = "t"

    player: Character
    card: Card

    def to_command(self):
        return f"{self.PREFIX} {self.player} {self.card}"


@dataclass(frozen=True)
class ChooseCard(ActionInterface):
    PREFIX = "t"

    player: Character
    card: Card

    def to_command(self):
        return f"{self.PREFIX} {self.player} {self.card}"
