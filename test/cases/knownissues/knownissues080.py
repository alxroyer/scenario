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

import typing

import scenario.test


class KnownIssues080(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        from steps.common import CheckFinalResultsLogExpectations, ExecScenario, ParseFinalResultsLog

        scenario.test.TestCase.__init__(
            self,
            title="Known issues & multiple scenarios",
            description="Check that known issues are displayed in multiple scenario results.",
        )
        self.covers(
            scenario.test.reqs.KNOWN_ISSUES,
            scenario.test.reqs.MULTIPLE_SCENARIO_EXECUTION,
        )

        # Execution step.
        self.addstep(ExecScenario(
            [scenario.test.paths.SIMPLE_SCENARIO, scenario.test.paths.KNOWN_ISSUE_DETAILS_SCENARIO],
        ))

        # Expectations.
        _scenario_expectations = [
            scenario.test.data.scenarioexpectations(
                scenario.test.paths.SIMPLE_SCENARIO,
                error_details=True,
            ),
            scenario.test.data.scenarioexpectations(
                scenario.test.paths.KNOWN_ISSUE_DETAILS_SCENARIO,
                error_details=True,
            ),
        ]  # type: typing.List[scenario.test.ScenarioExpectations]

        # Verification steps.
        self.addstep(ParseFinalResultsLog(ExecScenario.getinstance()))
        self.addstep(CheckFinalResultsLogExpectations(ParseFinalResultsLog.getinstance(), _scenario_expectations))
