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

import scenario.reqs
import scenario.test


class ScenarioReport071(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        from scenarioreport.steps.full import CheckFullScenarioReport
        from steps.common import ExecScenario

        scenario.test.TestCase.__init__(
            self,
            title="Scenario report action/result indentation --doc-only",
            description=(
                "Check the scenario report saves main logger indentation at the beginning of ACTION/RESULT texts, "
                "when executed with the --doc-only option."
            ),
        )
        self.verifies(
            scenario.reqs.SCENARIO_REPORT,
            (scenario.reqs.SCENARIO_LOGGING_ACTION_RESULT_INDENTATION, "Main logger indentation saved in scenario reports for actions and results."),
            scenario.reqs.DOC_ONLY,
        )

        self.addstep(ExecScenario(scenario.test.paths.LOGGING_INDENTATION_SCENARIO, doc_only=True, generate_report=True))
        self.addstep(CheckFullScenarioReport(ExecScenario.getinstance()))
