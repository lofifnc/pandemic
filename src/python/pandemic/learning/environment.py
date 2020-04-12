from collections import defaultdict
from typing import List, Dict, Tuple

import gym
import numpy as np
from gym import Space
from scipy import sparse

from pandemic.simulation.model.actions import ACTION_SPACE_DIM
from pandemic.simulation.model.actions import ActionInterface
from pandemic.simulation.model.enums import GameState
from pandemic.simulation.simulation import Simulation


class PandemicEnvironment(gym.Env):
    def reset(self):
        # TODO: smarter reset
        self._simulation.reset()
        self._action_lookup, self.action_space = self._encode_possible_actions(self._simulation.get_possible_actions())
        self.observation_space = self._get_obs()
        self._steps = 0

    def render(self, mode="human"):
        # TODO: maybe later
        pass

    def __init__(self):
        self._simulation = Simulation()
        self._action_lookup, self.action_space = self._encode_possible_actions(self._simulation.get_possible_actions())
        self.observation_space = self._get_obs()
        self._steps = 0

    def step(self, action: int):
        reward = 0
        if action == 0:
            self._simulation.step(None)
        else:
            self._steps += 1
            self._simulation.step(self._action_lookup[action])
            reward = self._get_reward()

        self._action_lookup, self.action_space = self._encode_possible_actions(self._simulation.get_possible_actions())

        self.observation_space = self._get_obs()

        done = self._simulation.state.game_state != GameState.RUNNING
        # observation, reward, done, info
        return self.observation_space, reward, done, {}

    def _get_reward(self):
        # try to come up with sensible reward
        state = self._simulation.state
        # extremely basic reward each cure -> += 0.25
        # each card of same color for player uncured -> += 0.1
        # each turn -> += 0.001
        card_color_reward = sum(sum(pow(count, 0.01) - 1 for color, count in p.city_colors.items() if not state.cures[color] and count > 1) for p in state.players.values())
        cure_reward = sum(state.cures.values())
        step_reward = self._steps * 0.001

        # each outbreak -> -= 0.2
        outbreak_reward = state.outbreaks * -0.125
        reward = card_color_reward + cure_reward + step_reward + outbreak_reward
        return reward


    @staticmethod
    def _encode_possible_actions(
        possible_actions: List[ActionInterface]
    ) -> Tuple[Dict[int, ActionInterface], np.ndarray]:
        if possible_actions is None or possible_actions == []:
            space = np.zeros(ACTION_SPACE_DIM)
            np.put(space, 0, 1)
            return dict(), space
        lookup = dict()
        features = [0] * ACTION_SPACE_DIM
        bump_dict = defaultdict(int)
        [PandemicEnvironment._insert_action(features, lookup, bump_dict, action) for action in possible_actions]

        return lookup, np.array(features)

    @staticmethod
    def _insert_action(llm, feature_actions, bump_dict, action):
        idx, value = action.feature
        bump_dict[idx] += 1
        bidx = bump_dict[idx] - 1
        feature_actions[bidx] = action
        llm[bidx] = value
        return bidx, value

    @staticmethod
    def __insert_with_shift(feature_actions, index, value):
        if feature_actions.get(index, None) is None:
            feature_actions[index] = value
            return index
        else:
            return PandemicEnvironment.__insert_with_shift(feature_actions, index + 1, value)

    def _get_obs(self) -> np.array:
        state = self._simulation.state
        phase = state.phase
        # normalized outbreaks 1 = bad
        outbreaks = state.outbreaks / 8
        # num_epidemics bigger = badder
        epidemics = state.infection_rate_marker / 7
        # actions left smaller = less
        actions_left = state.actions_left / 4
        # player deck size 0 = game over
        player_deck = len(state.player_deck)
        # size infection discard pile
        infection_discard = len(state.infection_discard_pile)
        # research stations left
        research_stations_left = state.research_stations
        # active player
        active_player = state.active_player

        #######
        # combine single features
        ######

        counts_vector = np.array(
            [
                active_player,
                phase,
                outbreaks,
                epidemics,
                actions_left,
                player_deck,
                infection_discard,
                research_stations_left,
            ]
        )

        # city state [ *researchstation *viral_states ]
        city_feature_tuples = [
            tuple([int(city.has_research_station())]) + tuple(city.viral_state.values())
            for city in state.cities.values()
        ]
        city_feature_vector = np.array(list(sum(zip(*city_feature_tuples), ())))
        # player characters + player locations
        player_feature_tuples = [(id, player.city) for id, player in state.players.items()]
        player_feature_vector = np.array(list(sum(zip(*player_feature_tuples), ())))
        # player cards
        hands_feature_vector = np.ndarray.flatten(
            np.array(
                [
                    PandemicEnvironment.pad_with_zeros(10, np.array(list(player.cards)))
                    for player in state.players.values()
                ]
            )
        )
        # cures
        cures_vector = [int(s) for s in state.cures.values()]

        # list of cubes normalized less is bad
        cubes_stack_vector = np.array(list(c / 24 for c in state.cubes.values()))
        # list of latest outbreaks ?

        return np.concatenate(
            [
                counts_vector,
                city_feature_vector,
                player_feature_vector,
                hands_feature_vector,
                cubes_stack_vector,
                cures_vector,
            ]
        )

    @staticmethod
    def pad_with_zeros(n, array):
        shape = np.shape(array)
        padded_array = np.zeros(n)
        padded_array[: shape[0]] = array
        return padded_array
