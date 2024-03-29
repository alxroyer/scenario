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

import enum
import typing

import scenario
if typing.TYPE_CHECKING:
    from scenario.typing import JSONDict
import scenario.test
import scenario.text

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
            scenario_expectations,  # type: typing.Sequence[scenario.test.ScenarioExpectations]
    ):  # type: (...) -> None
        scenario.test.VerificationStep.__init__(self, exec_step)

        self.scenario_expectations = scenario_expectations  # type: typing.Sequence[scenario.test.ScenarioExpectations]

        # Expectations analysis.
        self._success_ref = {}  # type: typing.Dict[str, CheckFinalResultsLogExpectations.ScenarioData]
        self._warnings_ref = {}  # type: typing.Dict[str, CheckFinalResultsLogExpectations.ScenarioData]
        self._errors_ref = {}  # type: typing.Dict[str, CheckFinalResultsLogExpectations.ScenarioData]
        for _scenario_expectations in self.scenario_expectations:  # type: scenario.test.ScenarioExpectations
            assert _scenario_expectations.script_path is not None, "Please give a path for the scenario expectations"
            _name = self._mkname(_scenario_expectations.script_path)
            assert _scenario_expectations.status is not None, "Please tell whether the scenarios are expected to succeed or not"
            if _scenario_expectations.status == scenario.ExecutionStatus.SUCCESS:
                self._success_ref[_name] = CheckFinalResultsLogExpectations.ScenarioData(_scenario_expectations)
            elif _scenario_expectations.status == scenario.ExecutionStatus.WARNINGS:
                self._warnings_ref[_name] = CheckFinalResultsLogExpectations.ScenarioData(_scenario_expectations)
            else:
                self._errors_ref[_name] = CheckFinalResultsLogExpectations.ScenarioData(_scenario_expectations)
        self._total_test_count = len(self._success_ref) + len(self._warnings_ref) + len(self._errors_ref)  # type: int

    def _mkname(
            self,
            path,  # type: typing.Union[str, scenario.Path]
    ):  # type: (...) -> str
        if isinstance(path, str):
            path = scenario.Path(path, relative_to=scenario.test.paths.MAIN_PATH)
        return self.test_case.getpathdesc(path)

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
        self.STEP("Final results log output expectations")

        # Useful typed variables.
        _name = ""  # type: str

        # Test list overview.
        self._checktestlist()

        # Statistics consistency.
        self._checkstatsconsistency()

        # Warning and error details.
        for _name in self._warnings_ref:
            self.RESULT(f"Scenario {_name}:")
            scenario.logging.pushindentation()
            self._checkerrordetails(_name, self._warnings_ref[_name], jsonpath="warnings")
            self._checkerrordetails(_name, self._warnings_ref[_name], jsonpath="errors")
            scenario.logging.popindentation()
        for _name in self._errors_ref:
            self.RESULT(f"Scenario {_name}:")
            scenario.logging.pushindentation()
            self._checkerrordetails(_name, self._errors_ref[_name], jsonpath="warnings")
            self._checkerrordetails(_name, self._errors_ref[_name], jsonpath="errors")
            scenario.logging.popindentation()

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

        if self.RESULT(f"The total statistics indicate a total number of tests of {self._total_test_count}."):
            self.assertjson(
                self.parsed_data.json_total_stats, "tests.total", value=self._total_test_count,
                evidence="Total number of tests",
            )
        if self.RESULT(f"The total statistics indicate a number of tests with warnings of {len(self._warnings_ref)}."):
            self.assertjson(
                self.parsed_data.json_total_stats, "tests.warnings", value=len(self._warnings_ref),
                evidence="Number of tests with warnings",
            )
        if self.RESULT(f"The total statistics indicate a number of tests in error of {len(self._errors_ref)}."):
            self.assertjson(
                self.parsed_data.json_total_stats, "tests.errors", value=len(self._errors_ref),
                evidence="Number of tests in error",
            )

        if self.RESULT(f"The output contains {self._total_test_count} lines of scenario statistics."):
            self.assertlen(
                self.parsed_data.json_scenario_stats, self._total_test_count,
                evidence="Number of scenario statistics lines",
            )

        _index = 0
        if self.RESULT(f"The {len(self._success_ref)} first line(s) correspond to the successful tests"
                       f"{f', i.e {scenario.text.commalist(self._success_ref)}:' if self._success_ref else '.'}"):
            while _index < len(self._success_ref):
                self.evidence(f"Line #{_index + 1}:")
                self.assertjson(
                    self.parsed_data.json_scenario_stats[_index], "status", value=str(scenario.ExecutionStatus.SUCCESS),
                    evidence="- Status",
                )
                _name = self._mkname(self.parsed_data.json_scenario_stats[_index]["name"])
                self.assertin(
                    _name, self._success_ref,
                    err=f"Unexpected status {scenario.ExecutionStatus.SUCCESS} for test '{_name}'",
                    evidence="- Name v/s status",
                )
                # Store the JSON data with the corresponding expectations.
                self._success_ref[_name].json = self.parsed_data.json_scenario_stats[_index]
                _index += 1
            # Check that all successful tests have received their JSON data.
            for _name in self._success_ref:
                self.assertisnotnone(self._success_ref[_name].json, evidence=False)

        if self.RESULT(f"The {len(self._warnings_ref)} next line(s) correspond to the tests with warnings"
                       f"{f', i.e. {scenario.text.commalist(self._warnings_ref)}:' if self._warnings_ref else '.'}"):
            while _index < len(self._success_ref) + len(self._warnings_ref):
                self.evidence(f"Line #{_index + 1}:")
                self.assertjson(
                    self.parsed_data.json_scenario_stats[_index], "status", value=str(scenario.ExecutionStatus.WARNINGS),
                    evidence="- Status",
                )
                _name = self._mkname(self.parsed_data.json_scenario_stats[_index]["name"])
                self.assertin(
                    _name, self._warnings_ref,
                    err=f"Unexpected status {scenario.ExecutionStatus.WARNINGS} for test '{_name}'",
                    evidence="- Name v/s status",
                )
                # Store the JSON data with the corresponding expectations.
                self._warnings_ref[_name].json = self.parsed_data.json_scenario_stats[_index]
                _index += 1
            # Check that all tests with warnings have received their JSON data.
            for _name in self._warnings_ref:
                self.assertisnotnone(self._warnings_ref[_name].json, evidence=False)

        if self.RESULT(f"The {len(self._errors_ref)} last line(s) correspond to the tests in error"
                       f"{f', i.e. {scenario.text.commalist(self._errors_ref)}:' if self._errors_ref else '.'}"):
            while _index < len(self._success_ref) + len(self._warnings_ref) + len(self._errors_ref):
                self.evidence(f"Line #{_index + 1}:")
                self.assertjson(
                    self.parsed_data.json_scenario_stats[_index], "status", value=str(scenario.ExecutionStatus.FAIL),
                    evidence="- Status",
                )
                _name = self._mkname(self.parsed_data.json_scenario_stats[_index]["name"])
                self.assertin(
                    _name, self._errors_ref,
                    err=f"Unexpected status {scenario.ExecutionStatus.FAIL} for test '{_name}'",
                    evidence="- Name v/s status",
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
                getattr(_scenario_expectations, f"{stat_type}_stats").total is not None
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
                    self.evidence(f"{_step_stats} <= '{self.assertjson(self.parsed_data.json_scenario_stats[_index], 'name', type=str)}'")
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
                    self.evidence(f"{_action_stats} <= '{self.assertjson(self.parsed_data.json_scenario_stats[_index], 'name', type=str)}'")
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
                    self.evidence(f"{_result_stats} <= '{self.assertjson(self.parsed_data.json_scenario_stats[_index], 'name', type=str)}'")
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
                    _name = self._mkname(self.assertjson(self.parsed_data.json_scenario_stats[_index], "name", type=str))
                    _scenario_time = self.assertjson(self.parsed_data.json_scenario_stats[_index], "time", type=float)  # type: float
                    self.assertgreaterequal(
                        _scenario_time, 0.0,
                        evidence=f"Scenario time {_name}",
                    )
                    _total_time += _scenario_time
                    self.evidence(f"{scenario.datetime.f2strduration(_total_time)} <= {_name}")
                self.assertnear(
                    self.assertjson(self.parsed_data.json_total_stats, "time", type=float), _total_time, 0.100,
                    evidence="Total time",
                )

    def _checkerrordetails(
            self,
            test_name,  # type: str
            scenario_data,  # type: CheckFinalResultsLogExpectations.ScenarioData
            jsonpath,  # type: str
    ):  # type: (...) -> None
        _scenario_expectations = scenario_data.expectations  # type: scenario.test.ScenarioExpectations
        _json_scenario_stats = scenario_data.json or {}  # type: JSONDict
        assert jsonpath in ("warnings", "errors")
        _error_expectations_list = None  # type: typing.Optional[typing.List[scenario.test.ErrorExpectations]]
        if jsonpath == "warnings":
            _error_expectations_list = _scenario_expectations.warnings
        if jsonpath == "errors":
            _error_expectations_list = _scenario_expectations.errors

        if _error_expectations_list is not None:
            assert jsonpath.endswith("s")
            _errors_txt = scenario.text.Countable(jsonpath[:-1], _error_expectations_list)  # type: scenario.text.Countable
            if self.RESULT(f"{len(_errors_txt)} {_errors_txt} {_errors_txt.are} notified{_errors_txt.ifany(':', '.')}"):
                self.assertjson(
                    _json_scenario_stats, jsonpath, type=list, len=len(_error_expectations_list),
                    evidence=f"Number of {_errors_txt.plural}",
                )
            for _index in range(len(_error_expectations_list)):  # type: int
                _error_expectations = _error_expectations_list[_index]  # type: scenario.test.ErrorExpectations

                self.RESULT(f"- {_errors_txt.singular.capitalize()} #{_index + 1}:")
                _jsonpath_error = f"{jsonpath}[{_index}]"  # type: str
                scenario.logging.pushindentation()

                # Type.
                # Note: `_error_expectations.cls` cannot be checked from JSON data.
                # Only the 'type' field can be checked for known issues.
                if _error_expectations.cls is scenario.KnownIssue:
                    # Just check the error type is set as expected in the error expectations.
                    # The error type is checked right after.
                    assert _error_expectations.error_type == "known-issue"
                if _error_expectations.error_type is not None:
                    if self.RESULT(f"Error type is {_error_expectations.error_type!r}."):
                        self.assertjson(
                            _json_scenario_stats, f"{_jsonpath_error}.type", value=_error_expectations.error_type,
                            evidence="Error type",
                        )

                # Level.
                if _error_expectations.level is scenario.test.NOT_SET:
                    if self.RESULT("Issue level is not set."):
                        self.assertjson(
                            _json_scenario_stats, f"{_jsonpath_error}.level", count=0,
                            evidence="Issue level",
                        )
                elif isinstance(_error_expectations.level, (int, enum.IntEnum)):
                    if self.RESULT(f"Issue level is {scenario.IssueLevel.getdesc(_error_expectations.level)}."):
                        self.assertjson(
                            _json_scenario_stats, f"{_jsonpath_error}.level", value=_error_expectations.level,
                            evidence="Issue level",
                        )

                # Id.
                if _error_expectations.id is scenario.test.NOT_SET:
                    if self.RESULT("Issue id is not set."):
                        self.assertjson(
                            _json_scenario_stats, f"{_jsonpath_error}.id", count=0,
                            evidence="Issue id",
                        )
                elif isinstance(_error_expectations.id, str):
                    if self.RESULT(f"Issue id is {_error_expectations.id!r}."):
                        self.assertjson(
                            _json_scenario_stats, f"{_jsonpath_error}.id", value=_error_expectations.id,
                            evidence="Issue id",
                        )

                # URL.
                if _error_expectations.url is scenario.test.NOT_SET:
                    if self.RESULT("URL is not set."):
                        self.assertjson(
                            _json_scenario_stats, f"{_jsonpath_error}.url", count=0,
                            evidence="URL",
                        )
                elif isinstance(_error_expectations.url, str):
                    if self.RESULT(f"URL is {_error_expectations.url!r}."):
                        self.assertjson(
                            _json_scenario_stats, f"{_jsonpath_error}.url", value=_error_expectations.url,
                            evidence="URL",
                        )

                # Message.
                if self.RESULT(f"{_errors_txt.singular.capitalize()} message is {_error_expectations.message!r}."):
                    self.assertjson(
                        _json_scenario_stats, f"{_jsonpath_error}.message", value=_error_expectations.message,
                        evidence=f"{_errors_txt.singular.capitalize()} message",
                    )

                # Location.
                if _error_expectations.location is not None:
                    if self.RESULT(f"{_errors_txt.singular.capitalize()} location is {_error_expectations.location!r}."):
                        self.assertjson(
                            _json_scenario_stats, f"{_jsonpath_error}.location", value=_error_expectations.location,
                            evidence=f"{_errors_txt.singular.capitalize()} location",
                        )

                scenario.logging.popindentation()

    def _checkextrainfo(
            self,
            scenario_data,  # type: CheckFinalResultsLogExpectations.ScenarioData
    ):  # type: (...) -> None
        _scenario_expectations = scenario_data.expectations  # type: scenario.test.ScenarioExpectations
        if _scenario_expectations.attributes is not None:
            assert scenario.ConfigKey.RESULTS_EXTRA_INFO in self.getexecstep(ExecCommonArgs).config_values
            _extra_info_option = scenario.test.configvalues.getstr(
                self.getexecstep(ExecCommonArgs).config_values, scenario.ConfigKey.RESULTS_EXTRA_INFO,
                default="",
            )  # type: str
            if not _extra_info_option:
                if self.RESULT(f"No extra info is displayed with the '{_scenario_expectations.name}' scenario."):
                    assert scenario_data.json
                    self.assertisempty(
                        scenario_data.json["extra-info"] or "",
                        evidence=f"'{_scenario_expectations.name}' extra info",
                    )
            else:
                for _attribute_name in _extra_info_option.split(","):  # type: str
                    _attribute_name = _attribute_name.strip()
                    self.assertisnotempty(_attribute_name, f"Invalid attribute name '{_attribute_name}' in extra info option")
                    self.assertin(
                        _attribute_name, _scenario_expectations.attributes,
                        f"No such attribute '{_attribute_name}' in '{_scenario_expectations.name}' attribute expectations",
                    )
                    if self.RESULT(f"The '{_attribute_name}' attribute of the '{_scenario_expectations.name}' scenario, "
                                   f"i.e. {_scenario_expectations.attributes[_attribute_name]!r}, "
                                   "is displayed with its extra info."):
                        assert scenario_data.json
                        self.assertin(
                            _scenario_expectations.attributes[_attribute_name], scenario_data.json["extra-info"],
                            evidence=f"'{_scenario_expectations.name}' extra info - '{_attribute_name}' attribute",
                        )
