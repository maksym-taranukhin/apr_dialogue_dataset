#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import os
from mephisto.operations.operator import Operator
from mephisto.tools.scripts import task_script
from mephisto.operations.hydra_config import build_default_task_config
from mephisto.abstractions.blueprints.parlai_chat.parlai_chat_blueprint import (
    SharedParlAITaskState,
)

from omegaconf import DictConfig
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()

# DEFAULT_TASK_CONFIG = "base"
DEFAULT_TASK_CONFIG = "custom_simple"
# DEFAULT_TASK_CONFIG = "custom_prebuilt"

@dataclass
class ParlAITaskConfig(build_default_task_config(DEFAULT_TASK_CONFIG)):
    model_name: str = field(
        default="gpt2",
        metadata={"help": "The model to use for the chat task"},
    )
    model_params: str = field(
        default="",
        metadata={"help": "Additional parameters to pass to the model"},
    )
    num_turns: int = field(
        default=3,
        metadata={"help": "Number of turns before a conversation is complete"},
    )
    turn_timeout: int = field(
        default=300,
        metadata={
            "help": "Maximum response time before kicking " "a worker out, default 300 seconds"
        },
    )


@task_script(config=ParlAITaskConfig)
def main(operator: "Operator", cfg: DictConfig) -> None:

    world_opt = {
        "num_turns": cfg.num_turns,
        "turn_timeout": cfg.turn_timeout,
        "model_name": cfg.model_name,
        "model_params": cfg.model_params,
        "send_task_data": True,
    }

    custom_bundle_path = cfg.mephisto.blueprint.get("custom_source_bundle", None)
    if custom_bundle_path is not None:
        assert os.path.exists(custom_bundle_path), (
            "Must build the custom bundle with `npm install; npm run dev` from within "
            f"the {cfg.task_dir}/webapp directory in order to demo a custom bundle "
        )

    shared_state = SharedParlAITaskState(world_opt=world_opt, onboarding_world_opt=world_opt)

    operator.launch_task_run(cfg.mephisto, shared_state)
    operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)


if __name__ == "__main__":
    main()
