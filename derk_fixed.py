from gym_derk.envs import DerkEnv, ConnectionLostError
from argparse import ArgumentParser
import numpy as np
import random
import logging
logging.basicConfig(level = logging.INFO)

def agent_update(observations, actions, observation_keys, action_keys):
  if observations[observation_keys.HasFocus.value] > 0 and observations[observation_keys.HeightFront5.value] > -0.5:
    actions[action_keys.Rotate.value] = 0
    actions[action_keys.ChaseFocus.value] = 1
    actions[action_keys.CastingSlot.value] = 1
    actions[action_keys.ChangeFocus.value] = 0
  else:
    actions[action_keys.Rotate.value] = random.random() * 2 - 1
    actions[action_keys.ChaseFocus.value] = 0
    actions[action_keys.CastingSlot.value] = 0
    actions[action_keys.ChangeFocus.value] = random.randint(5, 7)

def main(env_args={ "mode": "server" }):
  env = DerkEnv(**env_args)

  action_n = np.zeros((env.n_agents, len(env.action_keys)))

  while True:
    observation_n = env.reset()
    while True:
      for i in range(env.n_agents):
        agent_update(observation_n[i, :], action_n[i, :], env.observation_keys, env.action_keys)
      observation_n, reward_n, done_n, info = env.step(action_n)
      if all(done_n):
        print("Episode finished")
        break
  env.close()

if __name__ == "__main__":
  parser = ArgumentParser()
  parser.add_argument("-s", "--server", action="store_true", dest="server", default=False)
  parser.add_argument("-c", "--connected", action="store_true", dest="connected", default=False)
  args = parser.parse_args()
  while True:
    try: main({ 'mode': "server" if args.server else ("connected" if args.connected else None) })
    except ConnectionLostError as err:
      print('Connection lost')
      err.env.close()
    if not args.server:
      break
