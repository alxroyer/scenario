# -*- coding: utf-8 -*-

# Copyright 2020-2023 Alexis Royer <https://github.com/alxroyer/scenario>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import scenario
import scenario.test


class ReqScenario1(scenario.Scenario):

    def __init__(self):  # type: (...) -> None
        # Ensure the requirement database is loaded.
        try:
            scenario.req_db.getreq("REQ-001")
        except KeyError:
            scenario.req_db.load(scenario.test.paths.datapath("reqdb.json"))

        scenario.Scenario.__init__(
            self,
            title="Requirement scenario 1",
        )
        self.verifies(
            "REQ-001",
        )
