import pytest

from pandemic.model.enums import Character
from pandemic.model.playerstate import PlayerState
from pandemic.state import State


@pytest.fixture
def less_random_state():
    def create_state(start_player: Character = Character.SCIENTIST):
        state = State()
        player_state = PlayerState()
        player_state._cards = {}
        state._players = {
            start_player: PlayerState(),
            Character.RESEARCHER if start_player.SCIENTIST else start_player.SCIENTIST: PlayerState(),
        }

        state._active_player = start_player
        return state

    return create_state
