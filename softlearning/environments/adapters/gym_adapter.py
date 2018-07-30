"""Implements a GymAdapter that converts Gym envs in a SoftlearningEnv."""

import gym
from gym.wrappers.dict import FlattenDictWrapper

from rllab.core.serializable import Serializable

from .softlearning_env import SoftlearningEnv
from softlearning.environments.gym.wrappers import NormalizeActionWrapper
from softlearning.environments.gym.mujoco.sawyer import SawyerReachTorqueEnv


GYM_ENVIRONMENTS = {
    'swimmer': {
        'default': lambda: gym.envs.make('Swimmer-v2')
    },
    'ant': {
        'default': lambda: gym.envs.make('Ant-v2')
    },
    'humanoid': {
        'default': lambda: gym.envs.make('Humanoid-v2'),
        'standup': lambda: gym.envs.make('HumanoidStandup-v2')
    },
    'hopper': {
        'default': lambda: gym.envs.make('Hopper-v2')
    },
    'half-cheetah': {
        'default': lambda: gym.envs.make('HalfCheetah-v2')
    },
    'walker': {
        'default': lambda: gym.envs.make('Walker2d-v2')
    },
    'sawyer-torque': {
        'reach': SawyerReachTorqueEnv
    }
}


class GymAdapter(SoftlearningEnv):
    """Adapter to convert Gym environment into standard."""

    def __init__(self,
                 domain,
                 task,
                 *args,
                 normalize=True,
                 observation_keys=None,
                 **kwargs):
        Serializable.quick_init(self, locals())
        self.observation_keys = observation_keys
        super(GymAdapter, self).__init__(domain, task, *args, **kwargs)

        env = GYM_ENVIRONMENTS[domain][task](*args, **kwargs)
        if isinstance(env.observation_space, gym.spaces.Dict):
            keys = (
                observation_keys or list(env.observation_space.spaces.keys()))
            env = FlattenDictWrapper(env, keys)
        # Remove the TimeLimit wrapper that sets 'done = True' when
        # the time limit specified for each environment has been passed and
        # therefore the environment is not Markovian (terminal condition
        # depends on time rather than state).
        if normalize:
            env = NormalizeActionWrapper(env)

        self._env = env.env

    @property
    def observation_space(self):
        observation_space = self._env.observation_space

        if len(observation_space.shape) > 1:
            raise NotImplementedError(
                "Observation space ({}) is not flat, make sure to check the"
                " implemenation. ".format(observation_space))

        return observation_space

    @property
    def action_space(self, *args, **kwargs):
        action_space = self._env.action_space
        if len(action_space.shape) > 1:
            raise NotImplementedError(
                "Action space ({}) is not flat, make sure to check the"
                " implemenation. ".format(action_space))
        return action_space

    def step(self, action, *args, **kwargs):
        # TODO(hartikainen): refactor this to always return OrderedDict,
        # such that the observation for all the envs is consistent. Right now
        # Some of the gym envs return np.array whereas other return dict.
        #
        # Something like:
        # observation = OrderedDict()
        # observation['observation'] = env.step(action, *args, **kwargs)
        # return observation

        return self._env.step(action, *args, **kwargs)

    def reset(self, *args, **kwargs):
        return self._env.reset(*args, **kwargs)

    def render(self, *args, **kwargs):
        return self._env.render(*args, **kwargs)

    def close(self, *args, **kwargs):
        return self._env.close(*args, **kwargs)

    def seed(self, *args, **kwargs):
        return self._env.seed(*args, **kwargs)

    def unwrapped(self, *args, **kwargs):
        return self._env.unwrapped(*args, **kwargs)

    def copy(self, *args, **kwargs):
        return self._env.copy(*args, **kwargs)

    def get_param_values(self, *args, **kwargs):
        raise NotImplementedError

    def set_param_values(self, *args, **kwargs):
        raise NotImplementedError
