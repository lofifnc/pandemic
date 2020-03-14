from typing import Set

from pandemic.model.enums import MovementAction, OtherAction, Virus


class ActionInterface:
    def __init__(self):
        pass

    def to_command(self):
        raise NotImplemented()


class Movement(ActionInterface):

    PREFIX = "m"

    def __init__(self, type: MovementAction, destination: str):
        super().__init__()
        self.type = type
        self.destination = destination

    def to_command(self):
        return f"{self.PREFIX} {self.type.command} {self.destination}"


class Other(ActionInterface):

    PREFIX = "o"

    def __init__(
        self, type: OtherAction, city_id: str, target_virus: Virus = None, cure_card_combination: Set[str] = None, card: str = None
    ):
        super().__init__()
        self.type = type
        self.city_id = city_id
        self.target_virus = target_virus
        self.card = card
        assert cure_card_combination is None or len(cure_card_combination) == 5
        self.cure_card_combination = cure_card_combination

    def to_command(self):
        ending: str = " %s" % (
            self.target_virus or self.card
        ) if self.type != OtherAction.BUILD_RESEARCH_STATION else ""
        return f"{self.PREFIX} {self.type.command} {self.city_id}{ending}"
