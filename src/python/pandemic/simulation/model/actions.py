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
        return f"{self.PREFIX} {self.command} {self.destination.name.lower()} {self.player.name.lower()}"


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
        return f"{super().to_command()} {self.discard_card.name.lower()}"


@dataclass(frozen=True)
class OperationsExpertCharterFlight(Movement):
    discard_card: City

    def to_command(self):
        return (
            f"{self.PREFIX} {self.type.command} {self.destination.name.lower()}"
            f" {self.player.name.lower()} {self.discard_card.name.lower()}"
        )


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
        return f"{self.PREFIX} s {self.player.name.lower()}  {self.card.name.lower()} {self.target_player.name.lower()}"


@dataclass(frozen=True)
class TreatDisease(Other):
    city: City
    target_virus: Virus

    def to_command(self):
        return f"{self.PREFIX} t {self.city.name.lower()} {self.target_virus.name.lower()}"


@dataclass(frozen=True)
class DiscoverCure(Other):
    card_combination: FrozenSet[City]
    target_virus: Virus

    def to_command(self):
        return f"{self.PREFIX} d {self.target_virus.name.lower()} {iterable_to_string(self.card_combination)}"


@dataclass(frozen=True)
class BuildResearchStation(Other):
    city: City

    def to_command(self):
        return f"{self.PREFIX} b {self.city.name.lower()}{' ' + self.move_from.name.lower() if self.move_from else ''}"


@dataclass(frozen=True)
class ReserveCard(Other):
    card: Card

    def to_command(self):
        return f"{self.PREFIX} r {self.card.name.lower()}"


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
        return f"{self.PREFIX} m ${self.player.name.lower()} {self.move_from.name.lower()}"


@dataclass(frozen=True)
class Forecast(Event):
    def to_command(self):
        return f"{self.PREFIX} f ${self.player.name.lower()}"


@dataclass(frozen=True)
class ForecastOrder(Event):
    forecast: Tuple[City]

    def to_command(self):
        return f"{self.PREFIX} f ${self.player.name.lower()} ${iterable_to_string(self.forecast)}"


@dataclass(frozen=True)
class GovernmentGrant(Event):
    target_city: City

    def to_command(self):
        return f"{self.PREFIX} g ${self.player.name.lower()} ${self.target_city.name.lower()}"


@dataclass(frozen=True)
class Airlift(Event):
    target_player: Character
    destination: City

    def to_command(self):
        return (
            f"{self.PREFIX} g ${self.player.name.lower()} ${self.target_player.name.lower()} "
            f"${self.destination.name.lower()}"
        )


@dataclass(frozen=True)
class ResilientPopulation(Event):
    discard_city: City

    def to_command(self):
        return f"{self.PREFIX} r ${self.player.name.lower()} ${self.discard_city.name.lower()}"


@dataclass(frozen=True)
class OneQuietNight(Event):
    def to_command(self):
        return f"{self.PREFIX} q ${self.player.name.lower()}"


@dataclass(frozen=True)
class ThrowCard(ActionInterface):
    PREFIX = "t"

    player: Character
    card: Card

    def to_command(self):
        return f"{self.PREFIX} {self.player.name.lower()} {self.card.name.lower()}"
