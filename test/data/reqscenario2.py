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


class ReqScenario2(scenario.Scenario):

    def __init__(self):  # type: (...) -> None
        # Ensure the requirement database is loaded.
        try:
            scenario.reqs.getreq("REQ-001")
        except KeyError:
            scenario.reqs.load(scenario.test.paths.datapath("reqdb.json"))

        scenario.Scenario.__init__(
            self,
            title="Requirement scenario 2",
        )
        self.verifies(
            ("REQ-001/1", "Justification for REQ-001/1 covered by ReqScenario2"),
            ("REQ-002", ),  # No justification for REQ-002.
        )

        self.addstep(TextStep(description="Foo", actions="Bar", results="Baz")).verifies(
            ("REQ-001/1", "Justification for REQ-001/1 covered by ReqScenario2:step#1"),
        )


class TextStep(scenario.Step):

    def __init__(
            self,
            *,
            description,  # type: str
            actions,  # type: str
            results,  # type: str
    ):  # type: (...) -> None
        scenario.Step.__init__(self)

        self.description = description  # type: str
        self.actions = actions  # type: str
        self.results = results  # type: str

    def step(self):  # type: (...) -> None
        self.STEP(self.description)

        for _action_line in self.actions.splitlines():  # type: str
            self.ACTION(_action_line)
        for _result_line in self.results.splitlines():  # type: str
            self.RESULT(_result_line)
