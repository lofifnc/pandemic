import itertools

import gym
import numpy as np
from gym import Space

from pandemic.simulation.model.enums import GameState
from pandemic.simulation.simulation import Simulation


class PandemicEnvironment(gym.Env):
    def reset(self):
        # TODO: smarter reset
        pass

    def render(self, mode="human"):
        # TODO: maybe later
        pass

    def __init__(self):
        self._simulation = Simulation()

    def step(self, action):
        self._simulation.step(None)

        observation = self._get_obs()

        done = self._simulation.state.game_state != GameState.RUNNING
        # observation, reward, done, info
        reward = None  # TODO: figure out a reward
        return observation, reward, done, {}

    @property
    def action_space(self) -> Space:
        return self._simulation.get_possible_actions()

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
                    PandemicEnvironment.pad_with_zeros(8, np.array(list(player.cards)))
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
