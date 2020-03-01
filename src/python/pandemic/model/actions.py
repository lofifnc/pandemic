from pandemic.model.enums import MovementAction, OtherAction, Virus


class ActionInterface:
    def __init__(self):
        pass


class Movement(ActionInterface):

    def __init__(self, type: MovementAction, destination: str):
        super().__init__()
        self.type = type
        self.destination = destination


class Other(ActionInterface):

    def __init__(self, type: OtherAction, city: str, target_virus: Virus = None):
        super().__init__()
        self.type = type
        self.city = city
        self.target_virus = target_virus
