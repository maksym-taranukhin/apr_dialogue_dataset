#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

try:
    from detoxify import Detoxify
except ImportError:
    print("Need to have detoxify to use this demo. For example: pip install detoxify")
    exit(1)

import random
from mephisto.operations.operator import Operator
from mephisto.tools.data_browser import DataBrowser
from mephisto.tools.scripts import (
    build_custom_bundle,
    task_script,
)
from mephisto.abstractions.database import MephistoDB

from mephisto.abstractions.blueprints.remote_procedure.remote_procedure_blueprint import (
    SharedRemoteProcedureTaskState,
    RemoteProcedureAgentState,
)
from mephisto.abstractions.blueprint import SharedTaskState
from omegaconf import DictConfig
from typing import Any, Dict, Optional


def build_tasks(num_tasks):
    """
    Create a set of tasks you want annotated
    """
    # NOTE These form the init_data for a task
    tasks = []
    for x in range(num_tasks):
        tasks.append(
            {
                "index": x,
                "local_value_key": x,
            }
        )
    return tasks


def determine_toxicity(text: str):
    return Detoxify("original").predict(text)["toxicity"]


@task_script(default_config_file="launch_with_local")
def main(operator: Operator, cfg: DictConfig) -> None:
    tasks = build_tasks(cfg.num_tasks)

    def calculate_toxicity(
        _request_id: str, args: Dict[str, Any], agent_state: RemoteProcedureAgentState
    ) -> Dict[str, Any]:
        return {
            "toxicity": str(determine_toxicity(args["text"])),
        }

    def get_current_tips(
        _request_id: str, args: Dict[str, Any], agent_state: RemoteProcedureAgentState
    ) -> Dict[str, Any]:
        return {"currentTips": operator.get_current_tips(cfg.mephisto, shared_state)}

    def add_tip_to_agent_metadata(
        _request_id: str, args: Dict[str, Any], agent_state: RemoteProcedureAgentState
    ):
        tip_text = args["tipText"]
        operator.update_current_agent_state_metadata(
            str(random.random()), args["agentId"]
        )
        return {}

    function_registry = {
        "determine_toxicity": calculate_toxicity,
        "get_current_tips": get_current_tips,
        "add_tip_for_review": add_tip_to_agent_metadata,
    }

    shared_state = SharedRemoteProcedureTaskState(
        static_task_data=tasks,
        function_registry=function_registry,
    )

    task_dir = cfg.task_dir
    build_custom_bundle(task_dir)
    operator.launch_task_run(cfg.mephisto, shared_state)
    operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)


if __name__ == "__main__":
    main()
