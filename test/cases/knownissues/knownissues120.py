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


class KnownIssues120(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        from steps.common import CheckJsonReportExpectations, CheckScenarioLogExpectations, ExecScenario, ParseScenarioLog

        scenario.test.TestCase.__init__(
            self,
            title="Known errors & test continuation",
            description=(
                "Check that known issues considered as errors don't break the test execution "
                "without requiring a *continue-on-error* option."
            ),
            features=[scenario.test.features.KNOWN_ISSUES, scenario.test.features.ERROR_HANDLING],
        )

        # Execution step.
        self.addstep(ExecScenario(
            # No known issue levels => all known issues considered as errors.
            scenario.test.paths.KNOWN_ISSUES_SCENARIO,
            config_values={
                scenario.ConfigKey.ISSUE_LEVEL_ERROR: scenario.test.IssueLevel.SUT,
            },
            generate_report=True,
            expected_return_code=scenario.ErrorCode.TEST_ERROR,
        ))

        # Expectations:
        _scenario_expectations_errors = scenario.test.data.scenarioexpectations(
            scenario.test.paths.KNOWN_ISSUES_SCENARIO, config_values=ExecScenario.getinstance().config_values,
            # Check all steps are executed.
            steps=True, stats=True,
            # Check known errors.
            error_details=True,
        )  # type: scenario.test.ScenarioExpectations
        self.assertisempty(_scenario_expectations_errors.warnings)
        self.assertisnotempty(_scenario_expectations_errors.errors)
        # Expect the same number of errors as warnings when the error issue level is not set.
        _scenario_expectations_warnings = scenario.test.data.scenarioexpectations(
            scenario.test.paths.KNOWN_ISSUES_SCENARIO,
            error_details=True,
        )  # type: scenario.test.ScenarioExpectations
        self.assertisnotempty(_scenario_expectations_warnings.warnings)
        self.assertisempty(_scenario_expectations_warnings.errors)
        self.assertequal(
            len(self.assertisnotnone(_scenario_expectations_errors.errors)),
            len(self.assertisnotnone(_scenario_expectations_warnings.warnings)),
        )

        # Verification steps.
        self.addstep(ParseScenarioLog(ExecScenario.getinstance()))
        self.addstep(CheckScenarioLogExpectations(ParseScenarioLog.getinstance(), _scenario_expectations_errors))
        self.addstep(CheckJsonReportExpectations(ExecScenario.getinstance(), _scenario_expectations_errors))
