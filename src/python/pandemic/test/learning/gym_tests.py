from pandemic.learning.environment import PandemicEnvironment
from pandemic.test.utils import create_less_random_simulation


def test_state_to_features():
    env = PandemicEnvironment()
    assert env._get_obs().shape == (296,)
