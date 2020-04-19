import pstats
import time

import cProfile
import io

from pandemic.simulation.model.enums import GameState
from pandemic.learning.environment import PandemicEnvironment
import numpy as np


def random_action(actions):
    idx_nonzero = np.nonzero(actions)[0]
    return np.random.choice(idx_nonzero)


def one_game(env, tactic, max_steps):

    steps = 0
    next_action = tactic(env.action_space)
    _, reward, done, _ = env.step(next_action)

    while not done and (max_steps is None or steps < max_steps):
        next_action = tactic(env.action_space)
        _, reward, done, _ = env.step(next_action)
        if any(env._simulation.state.cures.values()):
            print("found cure !!!")
            break
        steps += 1

    result = reward
    # print("game result:", state.get_game_condition())
    # print("steps to result:", steps)
    env.render()
    env.reset()
    return result, steps


def statement():
    res = GameState.LOST
    start = time.time()
    games_run = 0
    results = list()
    env = PandemicEnvironment(
        num_epidemic_cards=4,
        characters=(5, 7),
        player_deck_shuffle_seed=10,
        infect_deck_shuffle_seed=20,
        epidemic_shuffle_seed=12,
    )
    while res != GameState.WIN and games_run < 100:
        print("game no:", games_run)
        res, steps = one_game(env, random_action, None)
        games_run += 1
        results.append(steps)

    print("min", min(results))
    print("max", max(results))
    print("took seconds", time.time() - start)
    print("games_run:", games_run)


pr = cProfile.Profile()
pr.enable()
statement()
pr.disable()

s = io.StringIO()
sortby = pstats.SortKey.CUMULATIVE
ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
ps.print_stats()
print(s.getvalue())
