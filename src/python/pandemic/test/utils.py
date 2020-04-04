from typing import Set, Type, List

from pandemic.simulation.model.actions import ActionInterface, ChooseCard
from pandemic.simulation.model.enums import Character
from pandemic.simulation.model.playerstate import PlayerState, City
from pandemic.simulation.simulation import Simulation
from pandemic.simulation.state import State


def create_less_random_simulation(start_player: Character = Character.SCIENTIST):
    state = State(player_count=2)
    player_state = PlayerState()
    player_state.clear_cards()
    state.players = {
        start_player: PlayerState(),
        Character.RESEARCHER if start_player == Character.SCIENTIST else Character.SCIENTIST: PlayerState(),
    }

    state.active_player = start_player
    simulation = Simulation(player_count=2)
    simulation.state = state
    return simulation


def filter_out_events(actions: List[ActionInterface], clazz: Type) -> Set[ActionInterface]:
    return set(filter(lambda a: not isinstance(a, clazz), actions))


def cure_virus(simulation: Simulation,
               cure_card_combination: List[City],
               player: Character):
    choices = {ChooseCard(player, card) for card in cure_card_combination}
    assert choices == set(simulation.get_possible_actions())
    for card in cure_card_combination:
        na = ChooseCard(player, card)
        assert na in simulation.get_possible_actions()
        simulation.step(na)