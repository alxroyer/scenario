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
if typing.TYPE_CHECKING:
    from scenario.typing import JSONDict
import scenario.test

# Related steps:
from steps.commonargs import ExecCommonArgs
from .parser import ParseFinalResultsLog


class CheckFinalResultsLogExpectations(scenario.test.VerificationStep):

    class ScenarioData:
        def __init__(
                self,
                scenario_expectations,  # type: scenario.test.ScenarioExpectations
        ):  # type: (...) -> None
            self.expectations = scenario_expectations  # type: scenario.test.ScenarioExpectations
            self.json = None  # type: typing.Optional[JSONDict]

    def __init__(
            self,
            exec_step,  # type: ParseFinalResultsLog
            scenario_expectations,  # type: typing.List[scenario.test.ScenarioExpectations]
    ):  # type: (...) -> None
        scenario.test.VerificationStep.__init__(self, exec_step)

        self.scenario_expectations = scenario_expectations  # type: typing.List[scenario.test.ScenarioExpectations]

        # Analyze expectations.
        self._success_ref = {}  # type: typing.Dict[str, CheckFinalResultsLogExpectations.ScenarioData]
        self._warnings_ref = {}  # type: typing.Dict[str, CheckFinalResultsLogExpectations.ScenarioData]
        self._errors_ref = {}  # type: typing.Dict[str, CheckFinalResultsLogExpectations.ScenarioData]
        for _scenario_expectations in self.scenario_expectations:  # type: scenario.test.ScenarioExpectations
            assert _scenario_expectations.status is not None, "Please tell whether the scenarios are expected to succeed or not"
            _name = str(_scenario_expectations.name)  # type: str
            if _scenario_expectations.status == scenario.ExecutionStatus.SUCCESS:
                self._success_ref[_name] = CheckFinalResultsLogExpectations.ScenarioData(_scenario_expectations)
            elif _scenario_expectations.status == scenario.ExecutionStatus.WARNINGS:
                self._warnings_ref[_name] = CheckFinalResultsLogExpectations.ScenarioData(_scenario_expectations)
            else:
                self._errors_ref[_name] = CheckFinalResultsLogExpectations.ScenarioData(_scenario_expectations)
        self._total_test_count = len(self._success_ref) + len(self._warnings_ref) + len(self._errors_ref)  # type: int

    @property
    def parsed_data(self):  # type: (...) -> ParseFinalResultsLog
        """
        Shortcut to parsed data.
        """
        return self.getexecstep(ParseFinalResultsLog)

    @property
    def doc_only(self):  # type: (...) -> typing.Optional[bool]
        """
        Shortcut to *doc-only* mode.
        """
        return self.getexecstep(ExecCommonArgs).doc_only

    def step(self):  # type: (...) -> None
        self.STEP("Scenario results log output expectations")

        # Useful typed variables.
        _name = ""  # type: str

        # Test list overview.
        self._checktestlist()

        # Statistics consistency.
        self._checkstatsconsistency()

        # Warning and error details.
        for _name in self._warnings_ref:
            self._checkerrordetails(_name, self._warnings_ref[_name], "warning")
            self._checkerrordetails(_name, self._warnings_ref[_name], "error")
        for _name in self._errors_ref:
            self._checkerrordetails(_name, self._errors_ref[_name], "warning")
            self._checkerrordetails(_name, self._errors_ref[_name], "error")

        # Extra info.
        for _name in self._success_ref:
            self._checkextrainfo(self._success_ref[_name])
        for _name in self._warnings_ref:
            self._checkextrainfo(self._warnings_ref[_name])
        for _name in self._errors_ref:
            self._checkextrainfo(self._errors_ref[_name])

    def _checktestlist(self):  # type: (...) -> None
        # Useful typed variables.
        _name = ""  # type: str
        _index = 0  # type: int

        if self.RESULT("The total statistics indicate a total number of tests of %d." % self._total_test_count):
            self.assertjson(
                self.parsed_data.json_total_stats, "tests.total", value=self._total_test_count,
                evidence="Total number of tests",
            )
        if self.RESULT("The total statistics indicate a number of tests with warnings of %d." % len(self._warnings_ref)):
            self.assertjson(
                self.parsed_data.json_total_stats, "tests.warnings", value=len(self._warnings_ref),
                evidence="Number of tests with warnings",
            )
        if self.RESULT("The total statistics indicate a number of tests in error of %d." % len(self._errors_ref)):
            self.assertjson(
                self.parsed_data.json_total_stats, "tests.errors", value=len(self._errors_ref),
                evidence="Number of tests in error",
            )

        if self.RESULT("The output contains %d lines of scenario statistics." % self._total_test_count):
            self.assertlen(
                self.parsed_data.json_scenario_stats, self._total_test_count,
                evidence="Number of scenario statistics lines",
            )

        _index = 0
        if self.RESULT("The %d first line(s) correspond to the successful tests: %s. " % (
                len(self._success_ref),
                ", ".join(["'%s'" % _name for _name in self._success_ref]) if self._success_ref else "(no successful test)",
        )):
            while _index < len(self._success_ref):
                self.assertjson(
                    self.parsed_data.json_scenario_stats[_index], "status", value=str(scenario.ExecutionStatus.SUCCESS),
                    evidence="Scenario #%d: success expected" % (_index + 1),
                )
                _name = self.parsed_data.json_scenario_stats[_index]["name"]
                self.assertin(
                    _name, self._success_ref,
                    err="Unexpected status %s for test '%s'" % (scenario.ExecutionStatus.SUCCESS, _name),
                    evidence="Scenario #%d: '%s'" % (_index + 1, _name),
                )
                # Store the JSON data with the corresponding expectations.
                self._success_ref[_name].json = self.parsed_data.json_scenario_stats[_index]
                _index += 1
            # Check that all successful tests have received their JSON data.
            for _name in self._success_ref:
                self.assertisnotnone(self._success_ref[_name].json, evidence=False)

        if self.RESULT("The %d next line(s) correspond to the tests with warnings: %s." % (
                len(self._warnings_ref),
                ", ".join(["'%s'" % _name for _name in self._warnings_ref]) if self._warnings_ref else "(no test with warnings)",
        )):
            while _index < len(self._success_ref) + len(self._warnings_ref):
                self.assertjson(
                    self.parsed_data.json_scenario_stats[_index], "status", value=str(scenario.ExecutionStatus.WARNINGS),
                    evidence="Scenario #%d: warnings expected" % (_index + 1),
                )
                _name = self.parsed_data.json_scenario_stats[_index]["name"]
                self.assertin(
                    _name, self._warnings_ref,
                    err="Unexpected status %s for test '%s'" % (scenario.ExecutionStatus.WARNINGS, _name),
                    evidence="Scenario #%d: '%s'" % (_index + 1, _name),
                )
                # Store the JSON data with the corresponding expectations.
                self._warnings_ref[_name].json = self.parsed_data.json_scenario_stats[_index]
                _index += 1
            # Check that all tests with warnings have received their JSON data.
            for _name in self._warnings_ref:
                self.assertisnotnone(self._warnings_ref[_name].json, evidence=False)

        if self.RESULT("The %d last line(s) correspond to the tests in error: %s." % (
                len(self._errors_ref),
                ", ".join(["'%s'" % _name for _name in self._errors_ref]) if self._errors_ref else "(no test in error)",
        )):
            while _index < len(self._success_ref) + len(self._warnings_ref) + len(self._errors_ref):
                self.assertjson(
                    self.parsed_data.json_scenario_stats[_index], "status", value=str(scenario.ExecutionStatus.FAIL),
                    evidence="Scenario #%d: failure expected" % (_index + 1),
                )
                _name = self.parsed_data.json_scenario_stats[_index]["name"]
                self.assertin(
                    _name, self._errors_ref,
                    err="Unexpected status %s for test '%s'" % (scenario.ExecutionStatus.FAIL, _name),
                    evidence="Scenario #%d: '%s'" % (_index + 1, _name),
                )
                # Store the JSON data with the corresponding expectations.
                self._errors_ref[_name].json = self.parsed_data.json_scenario_stats[_index]
                _index += 1
            # Check that all tests in error have received their related stats.
            for _name in self._errors_ref:
                self.assertisnotnone(self._errors_ref[_name].json, evidence=False)

    def _checkstatsconsistency(self):  # type: (...) -> None
        # Useful typed variables.
        _name = ""  # type: str
        _index = 0  # type: int
        _check_time_stats = False  # type: bool

        def _checkstats(
                stat_type,  # type: str
        ):  # type: (...) -> bool
            if stat_type.endswith("s"):
                stat_type = stat_type[:-1]
            return any([
                getattr(_scenario_expectations, "%s_stats" % stat_type).total is not None
                for _scenario_expectations in self.scenario_expectations
            ])

        if _checkstats("steps"):
            _check_time_stats = True
            if self.RESULT("The sum of the scenario step statistics corresponds to the total step statistics."):
                _step_stats = scenario.ExecTotalStats()  # type: scenario.ExecTotalStats
                for _index in range(self._total_test_count):
                    if not self.doc_only:
                        _step_stats.executed += self.assertjson(self.parsed_data.json_scenario_stats[_index], "steps.executed", type=int)
                    _step_stats.total += self.assertjson(self.parsed_data.json_scenario_stats[_index], "steps.total", type=int)
                    self.evidence("%s <= '%s'" % (str(_step_stats), self.assertjson(self.parsed_data.json_scenario_stats[_index], "name", type=str)))
                if not self.doc_only:
                    self.assertjson(
                        self.parsed_data.json_total_stats, "steps.executed", value=_step_stats.executed,
                        evidence="Number of steps executed",
                    )
                self.assertjson(
                    self.parsed_data.json_total_stats, "steps.total", value=_step_stats.total,
                    evidence="Total number of steps",
                )

        if _checkstats("actions"):
            _check_time_stats = True
            if self.RESULT("The sum of the scenario action statistics corresponds to the total action statistics."):
                _action_stats = scenario.ExecTotalStats()  # type: scenario.ExecTotalStats
                for _index in range(self._total_test_count):
                    if not self.doc_only:
                        _action_stats.executed += self.assertjson(self.parsed_data.json_scenario_stats[_index], "actions.executed", type=int)
                    _action_stats.total += self.assertjson(self.parsed_data.json_scenario_stats[_index], "actions.total", type=int)
                    self.evidence("%s <= '%s'" % (str(_action_stats), self.assertjson(self.parsed_data.json_scenario_stats[_index], "name", type=str)))
                if not self.doc_only:
                    self.assertjson(
                        self.parsed_data.json_total_stats, "actions.executed", value=_action_stats.executed,
                        evidence="Number of actions executed",
                    )
                self.assertjson(
                    self.parsed_data.json_total_stats, "actions.total", value=_action_stats.total,
                    evidence="Total number of actions",
                )

        if _checkstats("results"):
            _check_time_stats = True
            if self.RESULT("The sum of the scenario expected result statistics corresponds to the total expected result statistics."):
                _result_stats = scenario.ExecTotalStats()  # type: scenario.ExecTotalStats
                for _index in range(self._total_test_count):
                    if not self.doc_only:
                        _result_stats.executed += self.assertjson(self.parsed_data.json_scenario_stats[_index], "results.executed", type=int)
                    _result_stats.total += self.assertjson(self.parsed_data.json_scenario_stats[_index], "results.total", type=int)
                    self.evidence("%s <= '%s'" % (str(_result_stats), self.assertjson(self.parsed_data.json_scenario_stats[_index], "name", type=str)))
                if not self.doc_only:
                    self.assertjson(
                        self.parsed_data.json_total_stats, "results.executed", value=_result_stats.executed,
                        evidence="Number of expected results executed",
                    )
                self.assertjson(
                    self.parsed_data.json_total_stats, "results.total", value=_result_stats.total,
                    evidence="Total number of expected results",
                )

        if _check_time_stats:
            if self.RESULT("The sum of the scenario times corresponds to the total time."):
                _total_time = 0.0  # type: float
                for _index in range(self._total_test_count):
                    _name = self.assertjson(self.parsed_data.json_scenario_stats[_index], "name", type=str)
                    _scenario_time = self.assertjson(self.parsed_data.json_scenario_stats[_index], "time", type=float)  # type: float
                    self.assertgreaterequal(
                        _scenario_time, 0.0,
                        evidence="Scenario time '%s'" % _name,
                    )
                    _total_time += _scenario_time
                    self.evidence("%s <= '%s'" % (scenario.datetime.f2strduration(_total_time), _name))
                self.assertnear(
                    self.assertjson(self.parsed_data.json_total_stats, "time", type=float), _total_time, 0.100,
                    evidence="Total time",
                )

    def _checkerrordetails(
            self,
            test_name,  # type: str
            scenario_data,  # type: CheckFinalResultsLogExpectations.ScenarioData
            error_type,  # type: str
    ):  # type: (...) -> None
        _scenario_expectations = scenario_data.expectations  # type: scenario.test.ScenarioExpectations
        _json_scenario_stats = scenario_data.json or {}  # type: JSONDict
        assert error_type in ("warning", "error")
        _error_expectations_list = (
            _scenario_expectations.warnings if error_type == "warning"
            else _scenario_expectations.errors
        )  # type: typing.Optional[typing.List[scenario.test.ErrorExpectations]]
        _json_path_list = "%ss" % error_type  # type: str

        if _error_expectations_list is not None:
            if self.RESULT("%d %ss are notified for '%s':" % (len(_error_expectations_list), error_type, test_name)):
                self.assertjson(
                    _json_scenario_stats, _json_path_list, type=list, len=len(_error_expectations_list),
                    evidence="Number of %ss" % error_type,
                )
            for _index in range(len(_error_expectations_list)):  # type: int
                _error_expectations = _error_expectations_list[_index]  # type: scenario.test.ErrorExpectations

                self.RESULT("- %s #%d" % (error_type.capitalize(), _index + 1))
                _json_path_error = "%s[%d]" % (_json_path_list, _index)  # type: str
                scenario.logging.pushindentation()

                # Note: `_error_expectations.cls` cannot be checked from JSON data.
                # Only the 'type' field can be checked for known issues.
                if _error_expectations.cls is scenario.KnownIssue:
                    # Just check the error type is set as expected in the error expectations.
                    # The error type is checked right after.
                    assert _error_expectations.error_type == "known-issue"
                if _error_expectations.error_type is not None:
                    if self.RESULT("Error type is %s." % repr(_error_expectations.error_type)):
                        self.assertjson(
                            _json_scenario_stats, _json_path_error + ".type", value=_error_expectations.error_type,
                            evidence="Error type",
                        )
                if _error_expectations.issue_id is not None:
                    if self.RESULT("Issue id is %s." % repr(_error_expectations.issue_id)):
                        self.assertjson(
                            _json_scenario_stats, _json_path_error + ".id", value=_error_expectations.issue_id,
                            evidence="Issue id",
                        )
                if self.RESULT("%s message is %s." % (error_type.capitalize(), repr(_error_expectations.message))):
                    self.assertjson(
                        _json_scenario_stats, _json_path_error + ".message", value=_error_expectations.message,
                        evidence="%s message" % error_type.capitalize(),
                    )
                if _error_expectations.location is not None:
                    if self.RESULT("%s location is %s." % (error_type.capitalize(), repr(_error_expectations.location))):
                        self.assertjson(
                            _json_scenario_stats, _json_path_error + ".location", value=_error_expectations.location,
                            evidence="%s location" % error_type.capitalize(),
                        )

                scenario.logging.popindentation()

    def _checkextrainfo(
            self,
            scenario_data,  # type: CheckFinalResultsLogExpectations.ScenarioData
    ):  # type: (...) -> None
        _scenario_expectations = scenario_data.expectations  # type: scenario.test.ScenarioExpectations
        if _scenario_expectations.attributes is not None:
            assert scenario.ConfigKey.RESULTS_EXTRA_INFO in self.getexecstep(ExecCommonArgs).config_values
            _extra_info_option = self.getexecstep(ExecCommonArgs).config_values[scenario.ConfigKey.RESULTS_EXTRA_INFO] or ""  # type: str
            if not _extra_info_option:
                if self.RESULT("No extra info is displayed with the '%s' scenario." % _scenario_expectations.name):
                    assert scenario_data.json
                    self.assertisempty(
                        scenario_data.json["extra-info"] or "",
                        evidence="'%s' extra info" % _scenario_expectations.name,
                    )
            else:
                for _attribute_name in _extra_info_option.split(","):  # type: str
                    _attribute_name = _attribute_name.strip()
                    self.assertisnotempty(_attribute_name, "Invalid attribute name '%s' in extra info option" % _attribute_name)
                    self.assertin(
                        _attribute_name, _scenario_expectations.attributes,
                        "No such attribute '%s' in '%s' attribute expectations" % (_attribute_name, _scenario_expectations.name),
                    )
                    if self.RESULT("The '%s' attribute of the '%s' scenario, i.e. '%s', is displayed with its extra info."
                                   % (_attribute_name, _scenario_expectations.name, _scenario_expectations.attributes[_attribute_name])):
                        assert scenario_data.json
                        self.assertin(
                            _scenario_expectations.attributes[_attribute_name], scenario_data.json["extra-info"],
                            evidence="'%s' extra info - '%s' attribute" % (_scenario_expectations.name, _attribute_name),
                        )
