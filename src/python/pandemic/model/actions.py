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
        self, type: OtherAction, city: str, target_virus: Virus = None, card: str = None
    ):
        super().__init__()
        self.type = type
        self.city = city
        self.target_virus = target_virus
        self.card = card

    def to_command(self):
        ending: str = " %s" % (
            self.target_virus or self.card
        ) if self.type != OtherAction.BUILD_RESEARCH_STATION else ""
        return f"{self.PREFIX} {self.type.command} {self.city}{ending}"
