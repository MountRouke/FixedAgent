from gym_derk import DerkSession, DerkAgentServer, DerkAppInstance
from argparse import ArgumentParser
import numpy as np
import random
import asyncio
import logging

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

async def run_session(env: DerkSession):
  action_n = np.zeros((env.n_agents, len(env.action_keys)))

  while True:
    observation_n = await env.reset()
    while not env.done:
      for i in range(env.n_agents):
        agent_update(observation_n[i, :], action_n[i, :], env.observation_keys, env.action_keys)
      observation_n, reward_n, done_n, info = await env.step(action_n)

if __name__ == "__main__":
  logging.basicConfig(level = logging.INFO)
  parser = ArgumentParser()
  parser.add_argument("-s", "--server", action="store_true", dest="server", default=False)
  parser.add_argument("-c", "--connected", action="store_true", dest="connected", default=False)
  args = parser.parse_args()
  server = DerkAgentServer(run_session, port=8789 if args.server else 8788)
  asyncio.get_event_loop().run_until_complete(server.start())
  if args.server:
    asyncio.get_event_loop().run_forever()
  else:
    app = DerkAppInstance(browser_logs=True)
    asyncio.get_event_loop().run_until_complete(app.start())
    asyncio.get_event_loop().run_until_complete(
      app.run_session(agent_hosts='dual_local' if args.connected else 'single_local')
    )
