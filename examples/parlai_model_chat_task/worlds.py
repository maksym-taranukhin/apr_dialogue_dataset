#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Any, Dict, List, Optional, Tuple
import random

from parlai.crowdsourcing.utils.worlds import CrowdOnboardWorld, CrowdTaskWorld
from parlai.core.agents import create_agent_from_shared
from parlai.core.worlds import validate
from joblib import Parallel, delayed

from examples.parlai_model_chat_task.bot_agent import TurkLikeAgent

class MultiAgentDialogOnboardWorld(CrowdOnboardWorld):
    def __init__(self, opt, agent):
        super().__init__(opt, agent)
        self.opt = opt

    def parley(self):
        self.agent.agent_id = "Onboarding Agent"
        self.agent.observe({"id": "System", "text": "Welcome onboard!"})
        x = self.agent.act(timeout=self.opt["turn_timeout"])
        self.agent.observe(
            {
                "id": "System",
                "text": "Thank you for your input! Please wait while "
                "we match you with another worker...",
                "episode_done": True,
            }
        )
        self.episodeDone = True


class MultiAgentDialogWorld(CrowdTaskWorld):
    """
    Basic world where each agent gets a turn in a round-robin fashion, receiving as
    input the actions of all other agents since that agent last acted.
    """

    def __init__(self, opt, agents=None, shared=None):
        # Add passed in agents directly.
        self.agents = agents
        self.acts = [None] * len(agents)
        self.episodeDone = False
        self.max_turns = opt.get("max_turns", 2)
        self.current_turns = 0
        self.send_task_data = opt.get("send_task_data", False)
        self.opt = opt
        self.retrived_documents = []
        for idx, agent in enumerate(self.agents):
            agent.agent_id = f"Speaker {idx + 1}"

    def parley(self):
        """
        For each agent, get an observation of the last action each of the other agents took.
        Then take an action yourself.
        """

        acts = self.acts
        self.current_turns += 1
        for index, agent in enumerate(self.agents):
            try:
                acts[index] = agent.act(timeout=self.opt["turn_timeout"])
                if self.send_task_data:

                    # if the agent is a bot also retrive documents and send them
                    if isinstance(agent, TurkLikeAgent):
                        # get mock documents by generation 5 random documents
                        self.documents = [
                            {
                                "id": i,
                                "title": f"Document {i}",
                                "text": f"Text {i}",
                                "score": random.random(),
                            }
                            for i in range(5)
                        ]

                    acts[index].force_set(
                        "task_data",
                        {
                            "retrieved_documents": self.documents,
                            "last_acting_agent": agent.agent_id,
                            "current_dialogue_turn": self.current_turns,
                            "utterance_count": self.current_turns + index,
                        },
                    )
            except TypeError:
                acts[index] = agent.act()  # not MTurkAgent

            if acts[index]["episode_done"]:
                self.episodeDone = True

            for other_agent in self.agents:
                if other_agent != agent:
                    other_agent.observe(validate(acts[index]))

        if self.current_turns >= self.max_turns:
            self.episodeDone = True
            for agent in self.agents:
                agent.observe(
                    {
                        "id": "Coordinator",
                        "text": "Please fill out the form to complete the chat:",
                        "task_data": {
                            "respond_with_form": [
                                {
                                    "type": "choices",
                                    "question": "How much did you enjoy talking to this user?",
                                    "choices": [
                                        "Not at all",
                                        "A little",
                                        "Somewhat",
                                        "A lot",
                                    ],
                                },
                                {
                                    "type": "choices",
                                    "question": "Do you think this user is a bot or a human?",
                                    "choices": [
                                        "Definitely a bot",
                                        "Probably a bot",
                                        "Probably a human",
                                        "Definitely a human",
                                    ],
                                },
                                {"type": "text", "question": "Enter any comment here"},
                            ]
                        },
                    }
                )
                agent.act()  # Request a response
            for agent in self.agents:  # Ensure you get the response
                form_result = agent.act(timeout=self.opt["turn_timeout"])

    def prep_save_data(self, agent):
        """Process and return any additional data from this world you may want to store"""
        return {"example_key": "example_value"}

    def episode_done(self):
        return self.episodeDone

    def shutdown(self):
        """
        Shutdown all mturk agents in parallel, otherwise if one mturk agent is
        disconnected then it could prevent other mturk agents from completing.
        """
        global shutdown_agent

        def shutdown_agent(agent):
            try:
                agent.shutdown(timeout=None)
            except Exception:
                agent.shutdown()  # not MTurkAgent

        Parallel(n_jobs=len(self.agents), backend="threading")(
            delayed(shutdown_agent)(agent) for agent in self.agents
        )


def get_bot_worker(opt: Dict[str, Any]) -> TurkLikeAgent:
    """
    Return a bot agent.
    Agent behaves like a crowdsource worker but actually wraps around a dialogue model.
    """
    num_turns = opt["num_turns"]
    bot_agent = TurkLikeAgent.get_bot_agents(args=opt, model_opts={opt['model_name']: opt["model_params"]})
    model_agent = create_agent_from_shared(bot_agent[opt["model_name"]])

    bot_worker = TurkLikeAgent(
        opt,
        model_name=opt["model_name"],
        model_agent=model_agent,
        num_turns=num_turns,
        # semaphore=semaphore,
    )

    message = {
        "id": "System",
        "episode_done": False,
        "text": "You are an air passenger. You are chatting with a customer service agent."
    }

    # The bot seeing its persona does not count as a "turn"
    bot_worker.observe(validate(message), increment_turn=False)

    return bot_worker


def make_onboarding_world(opt, agent):
    return MultiAgentDialogOnboardWorld(opt, agent)


def validate_onboarding(data):
    """Check the contents of the data to ensure they are valid"""
    print(f"Validating onboarding data {data}")
    return True


def make_world(opt, agents):
    bot_worker = get_bot_worker(opt=opt)
    _agents = [bot_worker] + agents
    return MultiAgentDialogWorld(
        opt=opt,
        agents=_agents)


def get_world_params():
    return {"agent_count": 1}
