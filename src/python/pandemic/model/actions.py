from typing import FrozenSet, List, Tuple

from pandemic.model.city_id import EventCard, City, Card
from pandemic.model.enums import MovementAction, OtherAction, Virus, PlayerColor
from pandemic.utils import iterable_to_string


class ActionInterface:
    def __init__(self):
        pass

    def to_command(self):
        raise NotImplemented()


class Movement(ActionInterface):
    PREFIX = "m"

    def __init__(self, type: MovementAction, destination: City):
        super().__init__()
        self.type = type
        self.destination = destination

    def to_command(self):
        return f"{self.PREFIX} {self.type.command} {self.destination.name}"

    def __repr__(self):
        return f"{self.type.name}: {self.destination}"

    def __eq__(self, o: object) -> bool:
        return self.__class__ == o.__class__ and self.__key() == o.__key()

    def __hash__(self) -> int:
        return hash(self.__key())

    def __key(self):
        return (self.type, self.destination)


class Other(ActionInterface):

    PREFIX = "o"

    def __init__(
        self,
        type: OtherAction,
        city: City,
        target_virus: Virus = None,
        cure_card_combination: FrozenSet[City] = None,
        player: PlayerColor = None,
        card: City = None,
        target_player: PlayerColor = None,
    ):
        super().__init__()
        self.type = type
        self.city = city
        self.target_virus = target_virus
        self.card = card
        self.player = player
        assert (
            cure_card_combination is None
            or len(cure_card_combination) == 5
            and isinstance(cure_card_combination, frozenset)
        )
        self.cure_card_combination = cure_card_combination
        self.target_player = target_player

    def to_command(self):
        if self.type == OtherAction.SHARE_KNOWLEDGE:
            ending = f"{self.card} {self.player.name} {self.target_player.name}"
        elif self.type == OtherAction.DISCOVER_CURE:
            ending = f"{self.target_virus.name} {iterable_to_string(self.cure_card_combination)}"
        elif self.type == OtherAction.TREAT_DISEASE:
            ending = self.target_virus.name
        else:
            ending = ""
        return f"{self.PREFIX} {self.type.command} {self.city.name} {ending}"

    def __eq__(self, o: object) -> bool:
        return self.__class__ == o.__class__ and self.__key() == o.__key()

    def __hash__(self) -> int:
        return hash(self.__key())

    def __key(self):
        return (
            self.type,
            self.target_virus,
            self.cure_card_combination,
            self.city,
            self.target_player,
            self.card,
            self.player,
        )


class Event(ActionInterface):

    PREFIX = "e"

    def __init__(
        self,
        type: EventCard,
        player: PlayerColor,
        discard_card: City = None,
        target_player: PlayerColor = None,
        destination: City = None,
        forecast: Tuple[City] = None,
    ):
        super().__init__()
        self.type = type
        self.player = player
        self.discard_card = discard_card
        self.target_player = target_player
        self.destination = destination
        self.forecast = forecast

    def to_command(self):
        if self.type == EventCard.FORECAST:
            ending = iterable_to_string(self.forecast)
        elif self.type == EventCard.GOVERNMENT_GRANT:
            ending = self.destination.name
        elif self.type == EventCard.AIRLIFT:
            ending = f"{self.target_player.name} {self.destination.name}"
        elif self.type == EventCard.RESILIENT_POPULATION:
            ending = self.discard_card.name
        else:
            ending = ""

        return f"{self.PREFIX} {self.type.command} {self.player} {ending}"

    def __eq__(self, o: object) -> bool:
        return self.__class__ == o.__class__ and self.__key() == o.__key()

    def __hash__(self) -> int:
        return hash(self.__key())

    def __key(self):
        return (self.type, self.player, self.target_player, self.discard_card, self.destination, self.forecast)


class ThrowCard(ActionInterface):

    PREFIX = "t"

    def __init__(self, player: PlayerColor, card: Card):
        super().__init__()
        self.player = player
        self.card = card

    def to_command(self):

        return f"{self.PREFIX} {self.player.name.lower()} {self.card.name.lower()}"

    def __eq__(self, o: object) -> bool:
        return self.__class__ == o.__class__ and self.__key() == o.__key()

    def __hash__(self) -> int:
        return hash(self.__key())

    def __key(self):
        return self.card, self.player
