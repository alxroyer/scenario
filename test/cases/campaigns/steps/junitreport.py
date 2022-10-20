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
            self.evidence("Campaign report path: '%s'" % self.getexecstep(ExecCampaign).junit_report_path)
            _campaign_execution_read = scenario.campaign_report.readjunitreport(self.getexecstep(ExecCampaign).junit_report_path)
            self.assertisnotnone(
                _campaign_execution_read,
                evidence="Campaign report successfully read",
            )
            assert _campaign_execution_read
            _campaign_execution = _campaign_execution_read

        if self.campaign_expectations.test_suite_expectations is not None:
            if self.RESULT("The report file describes %d test suite(s):" % len(self.campaign_expectations.test_suite_expectations)):
                self.assertlen(
                    _campaign_execution.test_suite_executions, len(self.campaign_expectations.test_suite_expectations),
                    evidence="Number of test suites",
                )

            for _test_suite_index in range(len(self.campaign_expectations.test_suite_expectations)):  # type: int
                self.RESULT("- test suite #%d:" % (_test_suite_index + 1))
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
            if self.RESULT("The test suite file path is '%s'." % test_suite_expectations.test_suite_path):
                self.assertsamepaths(
                    test_suite_execution.test_suite_file.path, test_suite_expectations.test_suite_path,
                    evidence="Test suite file",
                )

        if test_suite_expectations.test_case_expectations is not None:
            if self.RESULT("The test suite describes %d test case(s):" % len(test_suite_expectations.test_case_expectations)):
                self.assertlen(
                    test_suite_execution.test_case_executions, len(test_suite_expectations.test_case_expectations),
                    evidence="Number of test cases",
                )

            for _test_case_index in range(len(test_suite_expectations.test_case_expectations)):  # type: int
                self.RESULT("- test case #%d:" % (_test_case_index + 1))
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
            if self.RESULT("The scenario script path is '%s'." % scenario_expectations.script_path):
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
            if self.RESULT("The test case status is %s." % scenario_expectations.status):
                self.assertequal(
                    test_case_execution.status, scenario_expectations.status,
                    evidence="Status",
                )

        if scenario_expectations.errors is not None:
            if self.RESULT("%d error details are set:" % len(scenario_expectations.errors)):
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
                self.RESULT("- Error #%d:" % (_error_index + 1))
                scenario.logging.pushindentation()
                if _error_expectations.cls is not None:
                    if self.RESULT("Error class is %s." % _error_expectations.cls.__name__):
                        self.assertisinstance(
                            _error, _error_expectations.cls,
                            evidence="Error class",
                        )
                if _error_expectations.error_type is not None:
                    if self.RESULT("Error type is %s." % repr(_error_expectations.error_type)):
                        assert isinstance(_error, scenario.ExceptionError)
                        self.assertequal(
                            _error.exception_type, _error_expectations.error_type,
                            evidence="Error type",
                        )
                if _error_expectations.issue_id is not None:
                    if self.RESULT("Issue id is %s." % repr(_error_expectations.issue_id)):
                        assert isinstance(_error, scenario.KnownIssue)
                        self.assertequal(
                            _error.issue_id, _error_expectations.issue_id,
                            evidence="Issue id",
                        )
                if self.RESULT("Error message is %s." % repr(_error_expectations.message)):
                    self.assertequal(
                        _error.message, _error_expectations.message,
                        evidence="Error message",
                    )
                if _error_expectations.location is not None:
                    if self.RESULT("Error location is %s." % repr(_error_expectations.location)):
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
            _expectation_attr_name = _stat_type[:-1] + "_stats"  # type: str
            if getattr(expectations, _expectation_attr_name).total is not None:
                if self.RESULT("The total number of %s is %d." % (_stat_type, getattr(expectations, _expectation_attr_name).total)):
                    self.assertequal(
                        getattr(execution, _stat_type).total, getattr(expectations, _expectation_attr_name).total,
                        evidence="Total number of %s" % _stat_type,
                    )
            if getattr(expectations, _expectation_attr_name).executed is not None:
                if self.RESULT("The number of %s executed is %d." % (_stat_type, getattr(expectations, _expectation_attr_name).executed)):
                    self.assertequal(
                        getattr(execution, _stat_type).executed, getattr(expectations, _expectation_attr_name).executed,
                        evidence="Total number of steps",
                    )
