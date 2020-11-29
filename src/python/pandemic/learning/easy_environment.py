from typing import Tuple, Dict, List

import numpy as np

from pandemic.learning.environment import Pandemic
from pandemic.simulation.model.actions import ActionInterface


class EasyPandemic(Pandemic):

    def _get_done(self):
        return self._get_reward(self._simulation.state.internal_state) != 0

    @staticmethod
    def _get_reward(state) -> float:
        if state.game_state == 1:
            if any(any(count == 4 for color, count in p.city_colors.items()) for p in state.players.values()):
                return 1
            return 0
        elif state.game_state == 2:
            return 1
        else:
            return -1

    @staticmethod
    def _encode_possible_actions(
        possible_actions: List[ActionInterface],
    ) -> Tuple[Dict[int, ActionInterface], np.ndarray]:
        return Pandemic._encode_possible_actions(possible_actions)