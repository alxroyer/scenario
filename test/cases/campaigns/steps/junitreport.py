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
from .execution import ExecCampaign


class CheckCampaignJunitReport(scenario.test.VerificationStep):

    def __init__(
            self,
            exec_step,  # type: ExecCampaign
            campaign_expectations,  # type: scenario.test.CampaignExpectations
    ):  # type: (...) -> None
        scenario.test.VerificationStep.__init__(self, exec_step)

        self.campaign_expectations = campaign_expectations  # type: scenario.test.CampaignExpectations

    def step(self):  # type: (...) -> None
        self.STEP("JUnit report")

        scenario.logging.resetindentation()

        _campaign_execution = scenario.CampaignExecution(outdir=None)  # type: scenario.CampaignExecution
        if self.ACTION("Read the .xml campaign report file."):
            self.evidence(f"Campaign report path: '{self.getexecstep(ExecCampaign).junit_report_path}'")
            _campaign_execution_read = scenario.campaign_report.readjunitreport(self.getexecstep(ExecCampaign).junit_report_path)
            self.assertisnotnone(
                _campaign_execution_read,
                evidence="Campaign report successfully read",
            )
            assert _campaign_execution_read
            _campaign_execution = _campaign_execution_read

        if self.campaign_expectations.test_suite_expectations is not None:
            _test_suites_txt = scenario.text.Countable("test suite", self.campaign_expectations.test_suite_expectations)  # type: scenario.text.Countable
            if self.RESULT(f"The report file describes {len(_test_suites_txt)} {_test_suites_txt}{_test_suites_txt.ifany(':', '.')}"):
                self.assertlen(
                    _campaign_execution.test_suite_executions, len(self.campaign_expectations.test_suite_expectations),
                    evidence="Number of test suites",
                )

            for _test_suite_index in range(len(self.campaign_expectations.test_suite_expectations)):  # type: int
                self.RESULT(f"- test suite #{_test_suite_index + 1}:")
                scenario.logging.pushindentation()
                self._checktestsuite(
                    self.testdatafromlist(
                        _campaign_execution.test_suite_executions, _test_suite_index,
                        default=scenario.TestSuiteExecution(campaign_execution=_campaign_execution, test_suite_path=None),
                    ),
                    self.campaign_expectations.test_suite_expectations[_test_suite_index],
                )
                scenario.logging.popindentation()

            if self.RESULT("The report file gives the campaign execution time, which is mainly explained by the test suite times."):
                self.assertgreater(
                    _campaign_execution.time.elapsed, 0.0,
                    evidence="Campaign execution time",
                )
                _sum = sum([x.time.elapsed or 0.0 for x in _campaign_execution.test_suite_executions])  # type: float
                self.assertgreaterequal(
                    _campaign_execution.time.elapsed, _sum,
                    evidence="Campaign execution time vs sum of test suite times",
                )
                self.assertnear(
                    _campaign_execution.time.elapsed, _sum, _sum * 0.1,
                    evidence="Campaign execution time vs sum of test suite times",
                )

            self._checkstats(
                execution=_campaign_execution,
                expectations=self.campaign_expectations,
            )

    def _checktestsuite(
            self,
            test_suite_execution,  # type: scenario.TestSuiteExecution
            test_suite_expectations,  # type: scenario.test.TestSuiteExpectations
    ):  # type: (...) -> None
        if self.RESULT("The report gives the test suite file."):
            self.assertisfile(
                test_suite_execution.test_suite_file.path,
                evidence="Test suite file",
            )
        if test_suite_expectations.test_suite_path:
            if self.RESULT(f"The test suite file path is '{test_suite_expectations.test_suite_path}'."):
                self.assertsamepaths(
                    test_suite_execution.test_suite_file.path, test_suite_expectations.test_suite_path,
                    evidence="Test suite file",
                )

        if test_suite_expectations.test_case_expectations is not None:
            _test_cases_txt = scenario.text.Countable("test case", test_suite_expectations.test_case_expectations)  # type: scenario.text.Countable
            if self.RESULT(f"The test suite describes {len(_test_cases_txt)} {_test_cases_txt}{_test_cases_txt.ifany(':', '.')}"):
                self.assertlen(
                    test_suite_execution.test_case_executions, len(test_suite_expectations.test_case_expectations),
                    evidence="Number of test cases",
                )

            for _test_case_index in range(len(test_suite_expectations.test_case_expectations)):  # type: int
                self.RESULT(f"- test case #{_test_case_index + 1}:")
                scenario.logging.pushindentation()
                self._checktestcase(
                    self.testdatafromlist(
                        test_suite_execution.test_case_executions, _test_case_index,
                        default=scenario.TestCaseExecution(test_suite_execution=test_suite_execution, script_path=None),
                    ),
                    test_suite_expectations.test_case_expectations[_test_case_index],
                )
                scenario.logging.popindentation()

        if self.RESULT("The report file gives the start time for the test suite."):
            self.assertisnotnone(
                test_suite_execution.time.start,
                evidence="Test suite start time",
            )

        if self.RESULT("The report file gives the test suite execution time, which is mainly explained by the test case times."):
            self.assertgreater(
                test_suite_execution.time.elapsed, 0.0,
                evidence="Test suite execution time",
            )
            _sum = sum([x.time.elapsed or 0.0 for x in test_suite_execution.test_case_executions])  # type: float
            self.assertgreaterequal(
                test_suite_execution.time.elapsed, _sum,
                evidence="Test suite execution time vs sum of test case times",
            )
            self.assertnear(
                test_suite_execution.time.elapsed, _sum, _sum * 0.1,
                evidence="Test suite execution time vs sum of test case times",
            )

        self._checkstats(
            execution=test_suite_execution,
            expectations=test_suite_expectations,
        )

    def _checktestcase(
            self,
            test_case_execution,  # type: scenario.TestCaseExecution
            scenario_expectations,  # type: scenario.test.ScenarioExpectations
    ):  # type: (...) -> None
        if self.RESULT("The report gives the script path of the scenario executed."):
            self.assertisfile(
                test_case_execution.script_path,
                evidence="Script path",
            )
        if scenario_expectations.script_path:
            if self.RESULT(f"The scenario script path is '{scenario_expectations.script_path}'."):
                self.assertsamepaths(
                    test_case_execution.script_path, scenario_expectations.script_path,
                    evidence="Script path",
                )

        if self.RESULT("The report gives the scenario log output."):
            self.assertisfile(
                test_case_execution.log.path,
                evidence="Log output",
            )
        if self.RESULT("The report gives the scenario report."):
            self.assertisfile(
                test_case_execution.json.path,
                evidence="JSON report",
            )

        if scenario_expectations.status is not None:
            if self.RESULT(f"The test case status is {scenario_expectations.status}."):
                self.assertequal(
                    test_case_execution.status, scenario_expectations.status,
                    evidence="Status",
                )

        if scenario_expectations.errors is not None:
            _details_txt = scenario.text.Countable("detail", scenario_expectations.errors)  # type: scenario.text.Countable
            if self.RESULT(f"{len(_details_txt)} error {_details_txt} {_details_txt.are} set{_details_txt.ifany(':', '.')}"):
                self.assertlen(
                    test_case_execution.errors, len(scenario_expectations.errors),
                    evidence="number of errors",
                )
            for _error_index in range(len(scenario_expectations.errors)):  # type: int
                _error_expectations = scenario_expectations.errors[_error_index]  # type: scenario.test.ErrorExpectations
                _error = self.testdatafromlist(
                    test_case_execution.errors, _error_index,
                    default=scenario.TestError(message=""),
                )  # type: scenario.TestError
                self.RESULT(f"- Error #{_error_index + 1}:")
                scenario.logging.pushindentation()
                if _error_expectations.cls is not None:
                    if self.RESULT(f"Error class is {_error_expectations.cls.__name__}."):
                        self.assertisinstance(
                            _error, _error_expectations.cls,
                            evidence="Error class",
                        )
                if _error_expectations.error_type is not None:
                    if self.RESULT(f"Error type is {_error_expectations.error_type!r}."):
                        assert isinstance(_error, scenario.ExceptionError)
                        self.assertequal(
                            _error.exception_type, _error_expectations.error_type,
                            evidence="Error type",
                        )
                if _error_expectations.id is not None:
                    if self.RESULT(f"Issue id is {_error_expectations.id!r}."):
                        assert isinstance(_error, scenario.KnownIssue)
                        self.assertequal(
                            _error.id, _error_expectations.id,
                            evidence="Issue id",
                        )
                if self.RESULT(f"Error message is {_error_expectations.message!r}."):
                    self.assertequal(
                        _error.message, _error_expectations.message,
                        evidence="Error message",
                    )
                if _error_expectations.location is not None:
                    if self.RESULT(f"Error location is {_error_expectations.location!r}."):
                        self.assertequal(
                            _error.location.tolongstring() if _error.location else None, _error_expectations.location,
                            evidence="Error location",
                        )
                scenario.logging.popindentation()

        if self.RESULT("The report gives the execution time."):
            self.assertgreater(
                test_case_execution.time.elapsed, 0.0,
                evidence="Execution time",
            )

        self._checkstats(
            execution=test_case_execution,
            expectations=scenario_expectations,
        )

    def _checkstats(
            self,
            execution,  # type: typing.Union[scenario.CampaignExecution, scenario.TestSuiteExecution, scenario.TestCaseExecution]
            expectations,  # type: typing.Union[scenario.test.CampaignExpectations, scenario.test.TestSuiteExpectations, scenario.test.ScenarioExpectations]
    ):  # type: (...) -> None
        if self.RESULT("The report gives the total number of steps."):
            self.assertgreater(
                execution.steps.total, 0,
                evidence="Total number of steps",
            )
        if self.RESULT("The report gives the total number of actions and results."):
            self.assertgreater(
                execution.actions.total + execution.results.total, 0,
                evidence="Total number of actions and results",
            )
        for _stat_type in ("steps", "actions", "results"):  # type: str
            _stat_expectations = getattr(expectations, _stat_type[:-1] + "_stats")  # type: scenario.test.StatExpectations
            _stats = getattr(execution, _stat_type) if self.doexecute() else None  # type: typing.Optional[scenario.ExecTotalStats]
            _stat_types_txt = scenario.text.Countable(_stat_type[:-1], None)  # type: scenario.text.Countable
            if _stat_expectations.total is not None:
                if self.RESULT(f"The total number of {_stat_types_txt.plural} is {_stat_expectations.total}."):
                    assert _stats
                    self.assertequal(
                        _stats.total, _stat_expectations.total,
                        evidence=f"Total number of {_stat_types_txt.plural}",
                    )
            if _stat_expectations.executed is not None:
                if self.RESULT(f"The number of {_stat_types_txt.plural} executed is {_stat_expectations.executed}."):
                    assert _stats
                    self.assertequal(
                        _stats.executed, _stat_expectations.executed,
                        evidence=f"Total number of {_stat_types_txt.plural}",
                    )
