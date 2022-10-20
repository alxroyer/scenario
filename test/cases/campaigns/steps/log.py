# -*- coding: utf-8 -*-

# Copyright 2020-2022 Alexis Royer <https://github.com/Alexis-ROYER/scenario>
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

# Related steps:
from steps.logverifications import LogVerificationStep
from .execution import ExecCampaign


class CheckCampaignLogExpectations(LogVerificationStep):

    def __init__(
            self,
            exec_step,  # type: ExecCampaign
            campaign_expectations,  # type: scenario.test.CampaignExpectations
    ):  # type: (...) -> None
        LogVerificationStep.__init__(self, exec_step)

        self.campaign_expectations = campaign_expectations  # type: scenario.test.CampaignExpectations

    def step(self):  # type: (...) -> None
        self.STEP("Campaign log output")

        self.RESULT("The campaign has executed every test described by the test suite file(s).")
        _expected_test_cases_in_error = []  # type: typing.List[scenario.test.ScenarioExpectations]
        _expected_test_cases_with_warnings = []  # type: typing.List[scenario.test.ScenarioExpectations]
        assert self.campaign_expectations.all_test_case_expectations
        for _test_case_expectations in self.campaign_expectations.all_test_case_expectations:  # type: scenario.test.ScenarioExpectations
            if self.RESULT("- '%s'" % _test_case_expectations.script_path):
                self.assertline(
                    "Executing '%s'" % _test_case_expectations.script_path,
                    evidence="'%s' execution" % _test_case_expectations.script_path,
                )
            if _test_case_expectations.status == scenario.ExecutionStatus.WARNINGS:
                _expected_test_cases_with_warnings.append(_test_case_expectations)
            elif _test_case_expectations.status != scenario.ExecutionStatus.SUCCESS:
                _expected_test_cases_in_error.append(_test_case_expectations)

        if self.RESULT("The campaign output displays %d tests case(s) in error:" % (len(_expected_test_cases_in_error))):
            self.assertlinecount(
                "ERROR    FAIL", len(_expected_test_cases_in_error),
                evidence="Number of test cases in error",
            )
            self.assertline(
                "Number of tests in error: %d" % len(_expected_test_cases_in_error),
                evidence="Number of test cases in error",
            )
        for _expected_test_case_in_error in _expected_test_cases_in_error:  # type: scenario.test.ScenarioExpectations
            if self.RESULT("- '%s'" % _expected_test_case_in_error.script_path):
                # This assertion checks error notifications at the end of the log output.
                self.assertline(
                    "ERROR    %s" % _expected_test_case_in_error.name,
                    evidence="Test case in error",
                )
            self._checktestcaseerrors(_expected_test_case_in_error)

        if self.RESULT("The campaign output displays %d tests case(s) with warnings:" % (len(_expected_test_cases_with_warnings))):
            self.assertlinecount(
                "WARNING  WARNINGS", len(_expected_test_cases_with_warnings),
                evidence="Number of test cases with warnings",
            )
            self.assertline(
                "Number of tests with warnings: %d" % len(_expected_test_cases_with_warnings),
                evidence="Number of test cases with warnings",
            )
        for _expected_test_case_with_warnings in _expected_test_cases_with_warnings:  # type: scenario.test.ScenarioExpectations
            if self.RESULT("- '%s'" % _expected_test_case_with_warnings.script_path):
                # This assertion checks warning notifications at the end of the log output.
                self.assertline(
                    "WARNING  %s" % _expected_test_case_with_warnings.name,
                    evidence="Test case with warnings",
                )
            self._checktestcaseerrors(_expected_test_case_with_warnings)

    def _checktestcaseerrors(
            self,
            scenario_expectations,  # type: scenario.test.ScenarioExpectations
    ):  # type: (...) -> None
        if scenario_expectations.errors is not None:
            self.RESULT("  with %d errors:" % len(scenario_expectations.errors))
            for _error_expectations in scenario_expectations.errors:  # type: scenario.test.ErrorExpectations
                _error_pattern = "%s: %s: %s" % (
                    _error_expectations.location,
                    _error_expectations.error_type,
                    _error_expectations.message,
                )  # type: str
                if self.RESULT("  - error %s (notified twice)" % _error_pattern):
                    # Notified twice: a first time while the tests are being executed, and a second with the final results display.
                    self.assertlinecount(
                        _error_pattern, 2,
                        evidence="Test error details",
                    )

        if scenario_expectations.warnings is not None:
            self.RESULT("  with %d warnings:" % len(scenario_expectations.warnings))
            for _warning_expectations in scenario_expectations.warnings:  # type: scenario.test.ErrorExpectations
                assert _warning_expectations.error_type == "known-issue", "Only known issues"
                _warning_pattern = "%s: Issue %s! %s" % (
                    _warning_expectations.location,
                    _warning_expectations.issue_id,
                    _warning_expectations.message,
                )  # type: str
                if self.RESULT("  - warning %s (notified twice)" % _warning_pattern):
                    # Notified twice: a first time while the tests are being executed, and a second with the final results display.
                    self.assertlinecount(
                        _warning_pattern, 2,
                        evidence="Test warning details",
                    )
