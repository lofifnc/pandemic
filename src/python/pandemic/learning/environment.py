import gym
import numpy as np
from gym import Space

from pandemic.simulation.model.enums import GameState
from pandemic.simulation.simulation import Simulation


class PandemicEnvironment(gym.Env):

    def reset(self):
        # TODO: smarter reset
        pass

    def render(self, mode='human'):
        # TODO: maybe later
        pass

    def __init__(self):
        self._simulation = Simulation()

    def step(self, action):
        self._simulation.step(None)

        observation = self._get_obs()

        done = self._simulation.state.game_state != GameState.RUNNING
        # observation, reward, done, info
        reward = None # TODO: figure out a reward
        return observation, reward, False, {}

    @property
    def action_space(self) -> Space:
        return self._simulation.get_possible_actions()

    def _get_obs(self):
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
        # research stations
        # ?
        # cubes in cities
        # ?
        # list of latest outbreaks ?
        # list of cubes
        # list of players
        # player locations



        return np.array([])

