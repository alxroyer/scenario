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
import scenario.text

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

        self.RESULT("The campaign has executed every test described by the test suite file(s):")
        _expected_test_cases_in_error = []  # type: typing.List[scenario.test.ScenarioExpectations]
        _expected_test_cases_with_warnings = []  # type: typing.List[scenario.test.ScenarioExpectations]
        assert self.campaign_expectations.all_test_case_expectations
        for _test_case_expectations in self.campaign_expectations.all_test_case_expectations:  # type: scenario.test.ScenarioExpectations
            assert _test_case_expectations.script_path
            if self.RESULT(f"- {self.test_case.getpathdesc(_test_case_expectations.script_path)}"):
                self.assertline(
                    f"Executing '{_test_case_expectations.script_path}'",
                    evidence=f"{self.test_case.getpathdesc(_test_case_expectations.script_path)} execution",
                )
            if _test_case_expectations.status == scenario.ExecutionStatus.WARNINGS:
                _expected_test_cases_with_warnings.append(_test_case_expectations)
            elif _test_case_expectations.status != scenario.ExecutionStatus.SUCCESS:
                _expected_test_cases_in_error.append(_test_case_expectations)

        _test_cases_txt = scenario.text.Countable("test case", _expected_test_cases_in_error)  # type: scenario.text.Countable
        if self.RESULT(f"The campaign output displays {len(_test_cases_txt)} {_test_cases_txt} in error{_test_cases_txt.ifany(':', '.')}"):
            self.assertlinecount(
                "ERROR    FAIL", len(_expected_test_cases_in_error),
                evidence="Number of test cases in error",
            )
            self.assertline(
                f"Number of tests in error: {len(_expected_test_cases_in_error)}",
                evidence="Number of test cases in error",
            )
        for _expected_test_case_in_error in _expected_test_cases_in_error:  # type: scenario.test.ScenarioExpectations
            assert _expected_test_case_in_error.script_path
            if self.RESULT(f"- {self.test_case.getpathdesc(_expected_test_case_in_error.script_path)}"):
                # This assertion checks error notifications at the end of the log output.
                self.assertline(
                    f"ERROR    {_expected_test_case_in_error.name}",
                    evidence="Test case in error",
                )
            scenario.logging.pushindentation()
            self._checktestcaseerrors(_expected_test_case_in_error)
            scenario.logging.popindentation()

        _test_cases_txt = scenario.text.Countable("test case", _expected_test_cases_with_warnings)  # Type already declared above.
        if self.RESULT(f"The campaign output displays {len(_test_cases_txt)} {_test_cases_txt} with warnings{_test_cases_txt.ifany(':', '.')}"):
            self.assertlinecount(
                "WARNING  WARNINGS", len(_expected_test_cases_with_warnings),
                evidence="Number of test cases with warnings",
            )
            self.assertline(
                f"Number of tests with warnings: {len(_expected_test_cases_with_warnings)}",
                evidence="Number of test cases with warnings",
            )
        for _expected_test_case_with_warnings in _expected_test_cases_with_warnings:  # type: scenario.test.ScenarioExpectations
            assert _expected_test_case_with_warnings.script_path
            if self.RESULT(f"- {self.test_case.getpathdesc(_expected_test_case_with_warnings.script_path)}"):
                # This assertion checks warning notifications at the end of the log output.
                self.assertline(
                    f"WARNING  {_expected_test_case_with_warnings.name}",
                    evidence="Test case with warnings",
                )
            scenario.logging.pushindentation()
            self._checktestcaseerrors(_expected_test_case_with_warnings)
            scenario.logging.popindentation()

    def _checktestcaseerrors(
            self,
            scenario_expectations,  # type: scenario.test.ScenarioExpectations
    ):  # type: (...) -> None
        if scenario_expectations.errors:  # Not `None` AND not empty.
            _errors_txt = scenario.text.Countable("error", scenario_expectations.errors)  # type: scenario.text.Countable
            self.RESULT(f"{len(_errors_txt)} {_errors_txt} {_errors_txt.are} expected{_errors_txt.ifany(':', '.')}")
            for _error_expectations in scenario_expectations.errors:  # type: scenario.test.ErrorExpectations
                if self.RESULT(f"- error {_error_expectations.loggingtext()!r} (notified twice)"):
                    # Notified twice: a first time while the tests are being executed, and a second with the final results display.
                    self.assertlinecount(
                        _error_expectations.loggingtext(), 2,
                        evidence="Test error details",
                    )

        if scenario_expectations.warnings:  # Not `None` AND not empty.
            _warnings_txt = scenario.text.Countable("warning", scenario_expectations.warnings)  # type: scenario.text.Countable
            self.RESULT(f"{len(_warnings_txt)} {_warnings_txt} {_warnings_txt.are} expected{_warnings_txt.ifany(':', '.')}")
            for _warning_expectations in scenario_expectations.warnings:  # type: scenario.test.ErrorExpectations
                assert _warning_expectations.error_type == "known-issue", "Only known issues"
                if self.RESULT(f"- warning {_warning_expectations.loggingtext()!r} (notified twice)"):
                    # Notified twice: a first time while the tests are being executed, and a second with the final results display.
                    self.assertlinecount(
                        _warning_expectations.loggingtext(), 2,
                        evidence="Test warning details",
                    )
