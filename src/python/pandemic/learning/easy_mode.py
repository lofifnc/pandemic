from pandemic.simulation.model import constants
from pandemic.simulation.model.actions import DriveFerry, DiscoverCure, ChooseCard
from pandemic.simulation.model.city_id import Card
from pandemic.simulation.model.enums import Character, Virus
from pandemic.simulation.simulation import Simulation


def replace_card(list, x, y):
    return [y if e == x else e for e in list]


def switch_player_card(s, player, x, y):
    s.players[player].remove_card(x)
    s.players[player].add_card(y)
    s.player_deck = replace_card(s.player_deck, y, x)


def swap_elements(list, x, y):
    index1 = list.index(x)
    index2 = list.index(y)
    list[index1], list[index2] = list[index2], list[index1]

_env = Simulation(
    characters={Character.QUARANTINE_SPECIALIST, Character.SCIENTIST},
    num_epidemic_cards=4,
    player_deck_shuffle_seed=5,
    infect_deck_shuffle_seed=10,
    epidemic_shuffle_seed=12,
)


_state = _env.state.internal_state
_state.active_player = 5
switch_player_card(_state, Character.QUARANTINE_SPECIALIST, 17, 1)
switch_player_card(_state, Character.QUARANTINE_SPECIALIST, 23, 10)
switch_player_card(_state, Character.QUARANTINE_SPECIALIST, 2, 24)

switch_player_card(_state, Character.SCIENTIST, 57, 17)
switch_player_card(_state, Character.SCIENTIST, 56, 40)


swap_elements(_state.player_deck, 38, 8)
swap_elements(_state.player_deck, 7, 3)
swap_elements(_state.player_deck, 42, 7)
swap_elements(_state.player_deck, 37, 44)
swap_elements(_state.player_deck, 7, 8)
swap_elements(_state.player_deck, 57, 4)
swap_elements(_state.player_deck, 54, 13)
swap_elements(_state.player_deck, 59, 9)
swap_elements(_state.player_deck, 32, 7)
swap_elements(_state.player_deck, 56, 41)
swap_elements(_state.player_deck, 57, 5)

easy_state = _state