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

import scenario
import scenario.test

if True:
    from steps.common import LogVerificationStep as _LogVerificationStepImpl  # `LogVerificationStep` used for inheritance.


class KnownIssues110(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        scenario.test.TestCase.__init__(
            self,
            title="Known issue levels & ignored and error issue levels",
            description=(
                "Check that known issues can be declared with an issue level making them behave as errors or be ignored "
                "depending on the --issue-level-error and --issue-level-ignored options. "
                "Check the way things are logged in the console and saved in scenario reports."
            ),
        )
        self.verifies(
            scenario.test.reqs.KNOWN_ISSUES,
            scenario.test.reqs.ERROR_HANDLING,
            scenario.test.reqs.SCENARIO_LOGGING,
            scenario.test.reqs.SCENARIO_REPORT,
        )

        # Default mode
        # ------------

        # When no error nor ignored issue level thresholds are set, known issues are considered as warnings...
        # ...whether their issue level is not set,
        self._addsteps(
            ignored_issue_level=None, error_issue_level=None,
            known_issue_level=None,
            expected_test_status=scenario.ExecutionStatus.WARNINGS,
        )
        # ...or whether it is set.
        self._addsteps(
            ignored_issue_level=None, error_issue_level=None,
            known_issue_level=scenario.test.IssueLevel.TEST,
            expected_test_status=scenario.ExecutionStatus.WARNINGS,
        )

        # Error issue level
        # -----------------

        # When the error issue level threshold is set, known issues with issue level below this threshold are considered as warnings.
        self._addsteps(
            ignored_issue_level=None, error_issue_level=scenario.test.IssueLevel.TEST,
            known_issue_level=scenario.test.IssueLevel.CONTEXT,
            expected_test_status=scenario.ExecutionStatus.WARNINGS,
        )
        # When the known issue level is above this threshold, the known issue is considered as an error.
        self._addsteps(
            ignored_issue_level=None, error_issue_level=scenario.test.IssueLevel.TEST,
            known_issue_level=scenario.test.IssueLevel.SUT,
            expected_test_status=scenario.ExecutionStatus.FAIL,
        )
        # When the known issue level equals this threshold, the known issue is considered as an error.
        self._addsteps(
            ignored_issue_level=None, error_issue_level=scenario.test.IssueLevel.TEST,
            known_issue_level=scenario.test.IssueLevel.TEST,
            expected_test_status=scenario.ExecutionStatus.FAIL,
        )
        # When the known issue level is not set, the known issue is considered as an error by default.
        self._addsteps(
            ignored_issue_level=None, error_issue_level=scenario.test.IssueLevel.TEST,
            known_issue_level=None,
            expected_test_status=scenario.ExecutionStatus.FAIL,
        )

        # Ignored issue level
        # -------------------

        # When the ignored issue level threshold is set, known issues with issue level below this threshold are ignored.
        self._addsteps(
            ignored_issue_level=scenario.test.IssueLevel.TEST, error_issue_level=None,
            known_issue_level=scenario.test.IssueLevel.CONTEXT,
            expected_test_status=scenario.ExecutionStatus.SUCCESS,
        )
        # When the known issue level is above this threshold, the known issue is considered as a warning by default.
        self._addsteps(
            ignored_issue_level=scenario.test.IssueLevel.TEST, error_issue_level=None,
            known_issue_level=scenario.test.IssueLevel.SUT,
            expected_test_status=scenario.ExecutionStatus.WARNINGS,
        )
        # When the known issue level equals this threshold, the known issue is ignored.
        self._addsteps(
            ignored_issue_level=scenario.test.IssueLevel.TEST, error_issue_level=None,
            known_issue_level=scenario.test.IssueLevel.TEST,
            expected_test_status=scenario.ExecutionStatus.SUCCESS,
        )
        # When the known issue level is not set, it is considered as a warning by default.
        self._addsteps(
            ignored_issue_level=scenario.test.IssueLevel.TEST, error_issue_level=None,
            known_issue_level=None,
            expected_test_status=scenario.ExecutionStatus.WARNINGS,
        )

        # Both thresholds
        # ---------------

        # The ignored threshold should normally be set below the error threshold.
        # If so, known issues with issue level above the error threshold are considered as errors.
        self._addsteps(
            ignored_issue_level=scenario.test.IssueLevel.CONTEXT, error_issue_level=scenario.test.IssueLevel.TEST,
            known_issue_level=scenario.test.IssueLevel.SUT,
            expected_test_status=scenario.ExecutionStatus.FAIL,
        )
        # Known issues with issue level between the ignored and error thresholds are considered as warnings.
        self._addsteps(
            ignored_issue_level=scenario.test.IssueLevel.CONTEXT, error_issue_level=scenario.test.IssueLevel.SUT,
            known_issue_level=scenario.test.IssueLevel.TEST,
            expected_test_status=scenario.ExecutionStatus.WARNINGS,
        )
        # Known issues with issue level below the ignored threshold are ignored.
        self._addsteps(
            ignored_issue_level=scenario.test.IssueLevel.TEST, error_issue_level=scenario.test.IssueLevel.SUT,
            known_issue_level=scenario.test.IssueLevel.CONTEXT,
            expected_test_status=scenario.ExecutionStatus.SUCCESS,
        )
        # When the ignored threshold is not below the error threshold, the error threshold is prioritized.
        self._addsteps(
            ignored_issue_level=scenario.test.IssueLevel.TEST, error_issue_level=scenario.test.IssueLevel.TEST,
            known_issue_level=scenario.test.IssueLevel.TEST,
            expected_test_status=scenario.ExecutionStatus.FAIL,
        )

    def _addsteps(
            self,
            ignored_issue_level,  # type: typing.Optional[scenario.AnyIssueLevelType]
            error_issue_level,  # type: typing.Optional[scenario.AnyIssueLevelType]
            known_issue_level,  # type: typing.Optional[scenario.AnyIssueLevelType]
            expected_test_status,  # type: scenario.ExecutionStatus
    ):  # type: (...) -> None
        from steps.common import CheckJsonReportExpectations, CheckScenarioLogExpectations, ExecScenario, ParseScenarioLog

        self.section(
            f"Ignored / error issue level: [{scenario.IssueLevel.getdesc(ignored_issue_level)} - {scenario.IssueLevel.getdesc(error_issue_level)}], "
            f"known issue level: {scenario.IssueLevel.getdesc(known_issue_level)}, "
            f"expected test status: {expected_test_status}"
        )

        # Execution step.
        _1 = self.addstep(ExecScenario(
            scenario.test.paths.KNOWN_ISSUE_DETAILS_SCENARIO,
            config_values={
                scenario.ConfigKey.ISSUE_LEVEL_IGNORED: ignored_issue_level,
                scenario.ConfigKey.ISSUE_LEVEL_ERROR: error_issue_level,
                scenario.test.data.scenarios.KnownIssueDetailsScenario.ConfigKey.LEVEL: known_issue_level,
            },
            generate_report=True,
            expected_return_code=(
                scenario.ErrorCode.TEST_ERROR if expected_test_status == scenario.ExecutionStatus.FAIL
                else scenario.ErrorCode.SUCCESS
            ),
        ))

        # Expectations: check consistency with `expected_test_status`.
        _scenario_expectations = scenario.test.data.scenarioexpectations(
            scenario.test.paths.KNOWN_ISSUE_DETAILS_SCENARIO, config_values=_1.config_values,
            error_details=True,
        )  # type: scenario.test.ScenarioExpectations
        self.assertequal(_scenario_expectations.status, expected_test_status)
        if expected_test_status == scenario.ExecutionStatus.WARNINGS:
            self.assertisnotempty(_scenario_expectations.warnings)
        else:
            self.assertisempty(_scenario_expectations.warnings)
        if expected_test_status == scenario.ExecutionStatus.FAIL:
            self.assertisnotempty(_scenario_expectations.errors)
        else:
            self.assertisempty(_scenario_expectations.errors)

        # Verification steps.
        _2 = self.addstep(ParseScenarioLog(_1))
        self.addstep(CheckScenarioLogExpectations(_2, _scenario_expectations))
        self.addstep(CheckLogDetails(
            exec_step=_2,
            count=(
                0 if expected_test_status == scenario.ExecutionStatus.SUCCESS
                else 2
            ),
        ))
        self.addstep(CheckJsonReportExpectations(_1, _scenario_expectations))


class CheckLogDetails(_LogVerificationStepImpl):
    def __init__(
            self,
            exec_step,  # type: scenario.test.AnyExecutionStepType
            count,  # type: int
    ):  # type: (...) -> None
        _LogVerificationStepImpl.__init__(self, exec_step)

        self.count = count  # type: int

    def step(self):  # type: (...) -> None
        self.STEP("Check log")

        _searched = "Known issue with level"  # type: str
        if self.RESULT(f"The log output gives {self.count} {_searched!r} lines."):
            self.assertlinecount(
                _searched, self.count,
                evidence=True,
            )
