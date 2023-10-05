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


class Stats021(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        from steps.common import CheckJsonReportExpectations, CheckScenarioLogExpectations, ExecScenario, ParseScenarioLog

        scenario.test.TestCase.__init__(
            self,
            title="Statistics failing scenario --doc-only",
            description="Check scenario execution statistics for a failing scenario executed with the --doc-only option set.",
        )
        self.verifies(
            scenario.test.reqs.STATISTICS,
            scenario.test.reqs.ERROR_HANDLING,
            scenario.test.reqs.DOC_ONLY,
        )

        # Scenario execution.
        self.addstep(ExecScenario(scenario.test.paths.FAILING_SCENARIO, generate_report=True, doc_only=True))

        # Scenario expectations.
        _scenario_expectations = scenario.test.data.scenarioexpectations(
            scenario.test.paths.FAILING_SCENARIO,
            doc_only=True,
            error_details=True, stats=True,
        )  # type: scenario.test.ScenarioExpectations

        # Verifications: check statistics in the log output and in the JSON report.
        self.addstep(ParseScenarioLog(ExecScenario.getinstance()))
        self.addstep(CheckScenarioLogExpectations(ParseScenarioLog.getinstance(), _scenario_expectations))
        self.addstep(CheckJsonReportExpectations(ExecScenario.getinstance(), _scenario_expectations))
