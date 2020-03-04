from typing import Set, Dict

from pandemic.model.actions import ActionInterface
from pandemic.state import State


class Simulation:
    def __init__(self):
        self.state = State()
        self._moves: Dict[str, ActionInterface] = {}
        self.get_possible_moves()

    def perform_action(self, command_string: str = None) -> State:
        if command_string is None:
            return self.state
        self.state.turn(self._moves[command_string])
        print(self.state.report())
        return self.state

    def get_possible_moves(self) -> Set[str]:
        self._moves = {
            move.to_command(): move for move in self.state.get_possible_moves()
        }
        return set(self._moves.keys())
