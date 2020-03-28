from typing import Set, Type

from pandemic.model.actions import ActionInterface
from pandemic.model.enums import Character
from pandemic.model.playerstate import PlayerState
from pandemic.state import State


def create_less_random_state(start_player: Character = Character.SCIENTIST):
    state = State(player_count=2)
    player_state = PlayerState()
    player_state._cards = {}
    state._players = {
        start_player: PlayerState(),
        Character.RESEARCHER if start_player == Character.SCIENTIST else start_player.SCIENTIST: PlayerState(),
    }

    state._active_player = start_player
    return state


def filter_out_events(actions: Set[ActionInterface], clazz: Type) -> Set[ActionInterface]:
    return set(filter(lambda a: not isinstance(a, clazz), actions))

