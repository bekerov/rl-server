#!/usr/bin/env python

#https://websockets.readthedocs.io/en/stable/intro.html

import asyncio
import websockets
import json
from rl_train_loop import RLTrainLoop
from quadrotor2d_ddpg import Quadrotor2D

num_actions = 2;
observation_size = 50;

train_loop = RLTrainLoop (num_actions, observation_size)
quadrotor2d = Quadrotor2D (train_loop)

train_loop.set_loss_op (quadrotor2d.get_loss_op ())
train_loop.add_train_ops (quadrotor2d.get_train_ops ())
train_loop.init_vars ()

async def agent_connection(websocket, path):
    while websocket.open:
        req_json = await websocket.recv()
        req = json.loads(req_json)
        # print (req)

        method = req ['method']
        if method == 'act':
            action = quadrotor2d.act (req ['state'])
            await websocket.send(json.dumps(action))
        elif method == 'act_batch':
            actions = quadrotor2d.act_batch (req ['states'])
            await websocket.send(json.dumps(actions))
        elif method == 'store_exp_batch':
            train_loop.store_exp_batch (
                req ['rewards'],
                req ['actions'],
                req ['prev_states'],
                req ['next_states']
            )
            await websocket.send('')

train_loop.train ()

start_server = websockets.serve(agent_connection, 'localhost', 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
train_loop.join ()
