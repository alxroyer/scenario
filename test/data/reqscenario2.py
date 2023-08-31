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


class ReqScenario2(scenario.Scenario):

    def __init__(self):  # type: (...) -> None
        from reqdb import loadreqdb

        # Ensure the requirement database is loaded.
        loadreqdb()

        scenario.Scenario.__init__(
            self,
            title="Requirement scenario 2",
        )
        self.covers("REQ-001/1")
        self.covers("REQ-002")
