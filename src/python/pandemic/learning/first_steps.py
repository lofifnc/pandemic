import pstats
import time

import cProfile
import io

from pandemic.simulation.model.enums import GameState
from pandemic.simulation.simulation import Simulation
from random import choice


def one_game():
    simulation = Simulation()

    steps = 0
    try:
        while simulation.state.game_state is GameState.RUNNING and steps < 100:
            possible_actions = simulation.get_possible_actions()
            next_action = choice(tuple(possible_actions)) if possible_actions else None
            simulation.step(next_action)
            if any(simulation.state.cures.values()):
                break
            steps += 1
    except IndexError:
        pass

    result = simulation.state.game_state
    # print("game result:", state.get_game_condition())
    # print("steps to result:", steps)
    return (result, steps)


def statement():
    res = GameState.LOST
    start = time.time()
    games_run = 0
    results = list()
    while res != GameState.WIN and games_run < 1000:
        print(games_run)
        res, steps = one_game()
        games_run += 1
        results.append(steps)

    print("min", min(results))
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
