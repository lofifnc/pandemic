from typing import List, Optional

from operator import gt
from functools import partial
from pandemic.simulation.actions.events import event_action, get_possible_event_actions
from pandemic.simulation.actions.moves import move_player, get_possible_move_actions
from pandemic.simulation.actions.others import throw_card_action, other_action, get_possible_other_actions
from pandemic.simulation.model.actions import (
    ActionInterface,
    Movement,
    Other,
    Event,
    ThrowCard,
)
from pandemic.simulation.model.constants import *
from pandemic.simulation.model.enums import Character, GameState
from pandemic.simulation.state import State, Phase


class Simulation:
    def __init__(self, player_count: int = PLAYER_COUNT):
        self.state = State(player_count)

    def step(self, action: Optional[ActionInterface]):

        if isinstance(action, ThrowCard):
            throw_card_action(self.state, action)
        elif isinstance(action, Event):
            event_action(self.state, action)

        if self.state.phase == Phase.ACTIONS and not isinstance(action, Event):
            self.actions(self.state, action)
        elif self.state.phase == Phase.DRAW_CARDS:
            self.state.draw_cards(action)
        elif self.state.phase == Phase.INFECTIONS:
            self.state.infections(action)
        elif self.state == Phase.EPIDEMIC:
            self.state.epidemic_2nd_part()

    @staticmethod
    def actions(state: State, action: ActionInterface):
        if state.actions_left > 0:
            if isinstance(action, Movement):
                move_player(state, action)
            elif isinstance(action, Other):
                other_action(state, action)
            if all(value for value in state.cures.values()):
                state.game_state = GameState.WIN
            state.actions_left -= 1
        if state.actions_left == 0 and state.phase is Phase.ACTIONS:
            state.actions_left = PLAYER_ACTIONS
            state.phase = Phase.DRAW_CARDS

    def get_possible_actions(self, player: Character = None) -> List[ActionInterface]:
        state = self.state

        if player is None:
            player = state.active_player

        possible_actions: List[ActionInterface] = get_possible_event_actions(state)
        if state.phase is Phase.FORECAST or state.phase is Phase.MOVE_STATION:
            return possible_actions

        # check all players for hand limit and prompt action
        too_many_cards = False
        extend = possible_actions.extend
        for color, p_state in filter(lambda cs: cs[1].num_cards() > 7, state.players.items()):
            too_many_cards = True
            extend(ThrowCard(color, c) for c in p_state.cards)

        if too_many_cards:
            return possible_actions

        if state.phase is Phase.ACTIONS:
            possible_actions.extend(
                get_possible_move_actions(state, player) + get_possible_other_actions(state, player)
            )
        if state.phase is Phase.DRAW_CARDS:
            return possible_actions
        if state.phase is Phase.INFECTIONS:
            return possible_actions
        return possible_actions
