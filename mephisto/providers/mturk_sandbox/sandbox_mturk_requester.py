#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.providers.mturk.mturk_requester import MTurkRequester
from mephisto.providers.mturk_sandbox.provider_type import PROVIDER_TYPE

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.database import MephistoDB
    from mephisto.data_model.requester import Requester
    from mephisto.providers.mturk.mturk_datastore import MTurkDatastore


class SandboxMTurkRequester(MTurkRequester):
    """Wrapper around regular requester that handles removing the appended "sandbox" name"""

    def __init__(self, db: "MephistoDB", db_id: str):
        super().__init__(db, db_id)
        self.datastore: "MTurkDatastore" = self.db.get_datastore_for_provider(
            PROVIDER_TYPE
        )
        # Use _requester_name to preserve sandbox behavior which
        # utilizes a different requester_name
        assert self.requester_name.endswith(
            "_sandbox"
        ), f"{self.requester_name} is not a sandbox requester"
        self._requester_name = self.requester_name[:-8]

    def _get_client(self, requester_name: str) -> Any:
        """
        Get an mturk client for usage with mturk_utils
        """
        return self.datastore.get_sandbox_client_for_requester(requester_name)

    def is_sandbox(self) -> bool:
        """
        Determine if this is a requester on sandbox
        """
        return True

    # Required functions for a Requester implementation

    @staticmethod
    def new(db: "MephistoDB", requester_name: str) -> "Requester":
        return SandboxMTurkRequester._register_requester(
            db, requester_name + "_sandbox", PROVIDER_TYPE
        )
