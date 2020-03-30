from typing import Set, Type, List

from pandemic.simulation.model.actions import ActionInterface
from pandemic.simulation.model.enums import Character
from pandemic.simulation.model.playerstate import PlayerState
from pandemic.simulation.simulation import Simulation
from pandemic.simulation.state import State


def create_less_random_simulation(start_player: Character = Character.SCIENTIST):
    state = State(player_count=2)
    player_state = PlayerState()
    player_state.clear_cards()
    state.players = {
        start_player: PlayerState(),
        Character.RESEARCHER if start_player == Character.SCIENTIST else start_player.SCIENTIST: PlayerState(),
    }

    state.active_player = start_player
    simulation = Simulation(player_count=2)
    simulation.state = state
    return simulation


def filter_out_events(actions: List[ActionInterface], clazz: Type) -> Set[ActionInterface]:
    return set(filter(lambda a: not isinstance(a, clazz), actions))
