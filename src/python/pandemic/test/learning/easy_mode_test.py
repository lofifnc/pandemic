from pandemic.simulation.model.actions import DriveFerry, DiscoverCure, ChooseCard
from pandemic.simulation.model.enums import Character, GameState
from pandemic.simulation.simulation import Simulation
from pandemic.learning.easy_mode import easy_state


def test_easy_mode_play_trough():
    env = Simulation(
        characters={Character.QUARANTINE_SPECIALIST, Character.SCIENTIST},
        num_epidemic_cards=4,
        player_deck_shuffle_seed=5,
        infect_deck_shuffle_seed=10,
        epidemic_shuffle_seed=12,
    )

    env.state.internal_state = easy_state

    ## test
    env.step(DriveFerry(player=5, destination=48))
    env.step(DriveFerry(player=5, destination=34))
    env.step(DriveFerry(player=5, destination=48))
    env.step(DriveFerry(player=5, destination=2))
    env.step(None)
    env.step(None)
    env.step(None)
    env.step(None)

    env.step(DiscoverCure(target_virus=3))
    env.get_possible_actions()
    env.step(ChooseCard(player=7, card=40))
    env.step(ChooseCard(player=7, card=25))
    env.step(ChooseCard(player=7, card=19))
    env.step(ChooseCard(player=7, card=17))
    env.step(DriveFerry(player=7, destination=48))
    env.step(DriveFerry(player=7, destination=29))
    env.step(DriveFerry(player=7, destination=2))
    env.step(None)
    env.step(None)
    env.step(None)
    env.step(None)

    env.step(DiscoverCure(target_virus=1))
    env.get_possible_actions()
    env.step(ChooseCard(player=5, card=1))
    env.step(ChooseCard(player=5, card=38))
    env.step(ChooseCard(player=5, card=10))
    env.step(ChooseCard(player=5, card=43))
    env.step(ChooseCard(player=5, card=24))
    env.step(DriveFerry(player=5, destination=48))
    env.step(DriveFerry(player=5, destination=29))
    env.step(DriveFerry(player=5, destination=2))
    env.step(None)
    env.step(None)
    env.step(None)
    env.step(None)

    env.step(DriveFerry(player=7, destination=48))
    env.step(DriveFerry(player=7, destination=34))
    env.step(DriveFerry(player=7, destination=48))
    env.step(DriveFerry(player=7, destination=2))
    env.step(None)
    env.step(None)
    env.step(None)
    env.step(None)

    env.step(DriveFerry(player=5, destination=48))
    env.step(DriveFerry(player=5, destination=34))
    env.step(DriveFerry(player=5, destination=48))
    env.step(DriveFerry(player=5, destination=2))
    env.step(None)
    env.step(None)
    env.step(None)
    env.step(None)

    env.step(DiscoverCure(target_virus=2))
    env.get_possible_actions()
    env.step(ChooseCard(player=7, card=42))
    env.step(ChooseCard(player=7, card=4))
    env.step(ChooseCard(player=7, card=44))
    env.step(ChooseCard(player=7, card=13))
    env.step(DriveFerry(player=7, destination=48))
    env.step(DriveFerry(player=7, destination=29))
    env.step(DriveFerry(player=7, destination=2))
    env.step(None)
    env.step(None)
    env.step(None)
    env.step(None)
    env.get_possible_actions()
    env.step(DiscoverCure(target_virus=4))
    env.get_possible_actions()
    env.get_possible_actions()
    env.step(ChooseCard(player=5, card=32))
    env.step(ChooseCard(player=5, card=3))
    env.step(ChooseCard(player=5, card=37))
    env.step(ChooseCard(player=5, card=8))
    env.step(ChooseCard(player=5, card=9))
    assert env.state.game_state == GameState.WIN
