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

import scenario.test


class ScenarioReport061(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        from scenarioreport.steps.full import CheckFullScenarioReport
        from steps.common import ExecScenario

        scenario.test.TestCase.__init__(
            self,
            title="Scenario report long texts --doc-only",
            description="Check the scenario report is generated as expected for a scenario with long texts, executed with the --doc-only option set.",
        )
        self.verifies(
            scenario.test.reqs.SCENARIO_REPORT,
            (scenario.test.reqs.ATTRIBUTES, "Long texts for scenario descriptions"),
            (scenario.test.reqs.SCENARIO_EXECUTION, "Long texts for actions & expected results"),
            (scenario.test.reqs.REQUIREMENT_MANAGEMENT, "Long texts for requirements link comments"),
            # No EVIDENCE: No evidence saved in reports in --doc-only.
            scenario.test.reqs.DOC_ONLY,
        )

        self.addstep(ExecScenario(scenario.test.paths.LONG_TEXTS_SCENARIO, doc_only=True, generate_report=True))
        self.knownissue(
            level=scenario.test.IssueLevel.TEST, id="#83",
            message="Verification missing for requirement link comments",
        )
        self.addstep(CheckFullScenarioReport(ExecScenario.getinstance()))
