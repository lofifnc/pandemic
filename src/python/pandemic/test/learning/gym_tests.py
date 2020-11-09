from pandemic.learning.environment import Pandemic
from pandemic.simulation.model.actions import DriveFerry, CharterFlight, BuildResearchStation


def test_state_to_features():
    env = Pandemic()
    assert env._get_obs().shape == (296,)
    print(env.action_space)
    env.step(1)
    print(env.action_space)


def test_csum():
    assert 102 == Pandemic._csum(1, 2)
    assert 1202 == Pandemic._csum(12, 2)
    assert 101202 == Pandemic._csum(10, 12, 2)

    assert 341202 == Pandemic._csum(34, 12, 2)


def test_encode_action():
    assert (DriveFerry.index, 123) == DriveFerry(1, 23).feature_encode()
    assert (CharterFlight.index, 223) == CharterFlight(2, 23).feature_encode()
    assert (BuildResearchStation.index, 3) == BuildResearchStation(3).feature_encode()


def test_encode_possible_actions():
    print(Pandemic._encode_possible_actions([DriveFerry(1, 23)]))
    print(Pandemic._encode_possible_actions([DriveFerry(1, 23), DriveFerry(2, 34)]))
