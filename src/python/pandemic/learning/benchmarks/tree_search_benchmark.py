import cProfile
import io
import pstats

from pandemic.learning.easy_mode import easy_state
from pandemic.learning.mcts_state import PandemicMctsState, PandemicTreeSearchState
from pandemic.learning.tree_search import TreeSearch
from pandemic.simulation.model.enums import Character
from pandemic.simulation.simulation import Simulation


env = Simulation(
    characters={Character.RESEARCHER, Character.CONTINGENCY_PLANNER},
    player_deck_shuffle_seed=5,
    infect_deck_shuffle_seed=10,
    epidemic_shuffle_seed=12,
)

env.state.internal_state = easy_state
initial_state = PandemicTreeSearchState(env, env.state.internal_state)
tree_search = TreeSearch(time_limit=5 * 60 * 1000, report_steps=100, exploration_constant=0.7, D=10)

pr = cProfile.Profile()
pr.enable()

tree_search.search(initial_state=initial_state)


pr.disable()

s = io.StringIO()
sortby = pstats.SortKey.CUMULATIVE
ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
ps.print_stats()
print(s.getvalue())
