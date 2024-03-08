#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import copy
from typing import Dict

from omegaconf import DictConfig
import parlai.utils.logging as logging
from parlai.core.agents import create_agent
from parlai.core.message import Message
from parlai.core.params import ParlaiParser
from examples.model_chat.constants import AGENT_1


class TurkLikeAgent:
    """
    Will act like a Turker but actually contains a bot agent.
    """

    def __init__(self, opt, model_name, model_agent, num_turns, semaphore=None):
        self.opt = opt
        self.model_agent = model_agent
        self.id = AGENT_1
        self.num_turns = num_turns
        self.turn_idx = 0
        self.semaphore = semaphore
        self.worker_id = model_name
        self.hit_id = 'none'
        self.assignment_id = 'none'
        self.some_agent_disconnected = False
        self.hit_is_abandoned = False
        self.hit_is_returned = False
        self.disconnected = False
        self.hit_is_expired = False

    def act(self, timeout=None):
        _ = timeout  # The model doesn't care about the timeout
        if self.semaphore:
            with self.semaphore:
                act_out = self.model_agent.act()
        else:
            act_out = self.model_agent.act()
        act_out = Message(act_out)

        assert ('episode_done' not in act_out) or (not act_out['episode_done'])
        self.turn_idx += 1
        return Message(act_out)

    def observe(self, observation, increment_turn: bool = True):
        """
        Need to protect the observe also with a semaphore for composed models where an
        act() may be called within an observe()
        """
        new_ob = copy.deepcopy(observation)
        if self.semaphore:
            with self.semaphore:
                self.model_agent.observe(new_ob)
        else:
            self.model_agent.observe(new_ob)

        if increment_turn:
            self.turn_idx += 1

    def shutdown(self):
        pass

    def reset(self):
        self.model_agent.reset()

    @staticmethod
    def get_bot_agents(
        args: DictConfig, model_opts: Dict[str, str]
    ) -> Dict[str, dict]:
        """
        Return shared bot agents.

        Pass in model opts with the `model_opts` arg, where `model_opts` is a dictionary
        whose keys are model names and whose values are strings that specify model
        params (i.e. `--model image_seq2seq`).
        """
        processed_opts = {}
        for name, opt_string in model_opts.items():
            parser = ParlaiParser(True, True)
            processed_opts[name] = parser.parse_args(opt_string.split())

        # Load and share all model agents
        logging.info(
            f'Got {len(list(processed_opts.keys()))} models: {processed_opts.keys()}.'
        )
        shared_bot_agents = {}
        for model_name, model_opt in processed_opts.items():
            logging.info('\n\n--------------------------------')
            logging.info(f'model_name: {model_name}, opt_dict: {model_opt}')
            model_agent = create_agent(model_opt, requireModelExists=True)
            shared_bot_agents[model_name] = model_agent.share()
        return shared_bot_agents
