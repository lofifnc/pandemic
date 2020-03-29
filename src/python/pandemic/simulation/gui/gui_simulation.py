from typing import Set, Dict

from pandemic.simulation.model.actions import ActionInterface
from pandemic.simulation.simulation import Simulation
from pandemic.simulation.state import State


class GuiSimulation:
    def __init__(self):
        self.simulation = Simulation()
        self._moves: Dict[str, ActionInterface] = {}
        self.get_possible_moves()

    def perform_action(self, command_string: str = None) -> State:
        if command_string is None:
            return self.simulation.state

        self.simulation.step(self._moves[command_string])
        moves = self.simulation.get_possible_actions()
        while not moves:
            moves = self.simulation.step(None)
        print(self.simulation.state.report())
        return self.simulation.state

    def get_possible_moves(self) -> Set[str]:
        self._moves = {move.to_command(): move for move in self.simulation.get_possible_actions()}
        return set(self._moves.keys())
