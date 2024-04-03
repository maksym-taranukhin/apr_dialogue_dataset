#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from joblib import Parallel, delayed
from langchain_community.document_loaders import DataFrameLoader
from langchain_community.embeddings import FakeEmbeddings, HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import FAISS
from parlai.core.agents import create_agent_from_shared
from parlai.core.worlds import validate
from parlai.crowdsourcing.utils.worlds import CrowdOnboardWorld, CrowdTaskWorld

from examples.parlai_model_chat_task.bot_agent import TurkLikeAgent
from dotenv import load_dotenv, find_dotenv

load_dotenv()

DATA_DIR = find_dotenv().replace(".env", "") / Path(os.getenv("DATA_DIR", "data"))
KB_PATH = DATA_DIR / "kb" / "docs.csv"
df = pd.read_csv(KB_PATH).fillna("")
KB_DOCS = DataFrameLoader(df, page_content_column="text").load()
KB_DOCS_NUM = len(KB_DOCS)

MODEL_NAME = "BAAI/bge-small-en"
MODEL_KWARGS = {"device": "cpu"}
ENCODE_KWARGS = {"normalize_embeddings": True}
embeddings = HuggingFaceBgeEmbeddings(
    model_name=MODEL_NAME, model_kwargs=MODEL_KWARGS, encode_kwargs=ENCODE_KWARGS
)

db = FAISS.from_documents(KB_DOCS, embeddings)


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
        self.max_turns = opt.get("max_turns", 4)
        self.current_turns = 0
        self.send_task_data = opt.get("send_task_data", False)
        self.opt = opt
        self.retrived_documents = []

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
                        dialogue_history = agent.model_agent.history.gpt3Agent.turns
                        self.documents = self.retrive_documents(dialogue_history)
                    # Handle user regeneration request.
                    elif (
                        "task_data" in acts[index]
                        and "messageToSend" in acts[index]["task_data"]
                        and acts[index]["task_data"]["messageToSend"].startswith("REGENERATE:")
                    ):
                        self.handle_regeneration(agent)
                        return

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

    def handle_regeneration(self, agent):
        """
        Handle the logic for regenerating a message in response to a user request.
        """
        # Find the last message in the bot's dialogue history and remove it.
        for agent in self.agents:
            if isinstance(agent, TurkLikeAgent):
                history = agent.model_agent.history.gpt3Agent.turns.split("\n")[:-1]
                agent.model_agent.history.gpt3Agent.turns = "\n".join(history)
                
                # Roll back the turn count by 2 to account for the bot's last message and the user's request.
                self.current_turns -= 1
                self.parley()

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

    def retrive_documents(self, query):
        return [
            {
                "id": i,
                "text": d.page_content,
                "score": float(score),
                **d.metadata,
            }
            for i, (d, score) in enumerate(db.similarity_search_with_score(query, k=KB_DOCS_NUM))
        ]


def get_bot_worker(opt: Dict[str, Any]) -> TurkLikeAgent:
    """
    Return a bot agent.
    Agent behaves like a crowdsource worker but actually wraps around a dialogue model.
    """
    num_turns = opt["num_turns"]
    bot_agent = TurkLikeAgent.get_bot_agents(
        args=opt, model_opts={opt["model_name"]: opt["model_params"]}
    )
    model_agent = create_agent_from_shared(bot_agent[opt["model_name"]])
    model_agent.id = "User"

    bot_worker = TurkLikeAgent(
        opt,
        model_name=opt["model_name"],
        model_agent=model_agent,
        num_turns=num_turns,
        # semaphore=semaphore,
    )

    bot_worker.agent_id = "User"

    # message = {
    #     "id": "System",
    #     "episode_done": False,
    #     "text": "You are an air passenger. You are chatting with a customer service agent."
    # }

    # # The bot seeing its persona does not count as a "turn"
    # bot_worker.observe(validate(message), increment_turn=False)

    return bot_worker


def make_onboarding_world(opt, agent):
    return MultiAgentDialogOnboardWorld(opt, agent)


def validate_onboarding(data):
    """Check the contents of the data to ensure they are valid"""
    print(f"Validating onboarding data {data}")
    return True


def make_world(opt, agents):
    bot_worker = get_bot_worker(opt=opt)

    if len(agents) == 1:
        agents[0].agent_id = "Agent"
    else:
        for idx, agent in enumerate(agents):
            agent.agent_id = f"Agent {idx + 1}"

    _agents = [bot_worker] + agents
    return MultiAgentDialogWorld(opt=opt, agents=_agents)


def get_world_params():
    return {"agent_count": 1}
