from pandemic.state import State
import pandemic.visualization as viz
import logging

logging.basicConfig(level=logging.INFO)

init_state = State()


def simulation(state: State) -> State:
    state.draw_player_cards()
    state.infect()
    print(state.report())
    return state


viz.Visualization(simulation, init_state)
