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
import json
import typing

import scenario
import scenario.test
import scenario.text
if typing.TYPE_CHECKING:
    from scenario._typing import JsonDictType as _JsonDictType  # noqa  ## Access to protected module

if True:
    from .reportfile import JsonReportFileVerificationStep as _JsonReportFileVerificationStepImpl  # `JsonReportFileVerificationStep` used for inheritance.
if typing.TYPE_CHECKING:
    from scenarioexecution.steps.execution import ExecScenario as _ExecScenarioType


class _JsonItems:
    """
    Class that implements a list of JSON dictionaries,
    but compares them on basis of their ids.
    """

    def __init__(self):  # type: (...) -> None
        self._items = []  # type: typing.List[_JsonDictType]

    def __contains__(
            self,
            item,  # type: _JsonDictType
    ):  # type: (...) -> bool
        for _item in self._items:  # type: _JsonDictType
            if id(item) == id(_item):
                return True
        return False

    def __getitem__(
            self,
            item,  # type: int
    ):  # type: (...) -> _JsonDictType
        """
        :param item: Position only (no ``slice``, usage restriction assumed)
        :return: Single JSON dictionary (restriction).
        """
        return self._items[item]

    def __iter__(self):  # type: (...) -> typing.Iterator[_JsonDictType]
        return iter(self._items)

    def __len__(self):  # type: () -> int
        return len(self._items)

    def append(
            self,
            item,  # type: _JsonDictType
    ):  # type: (...) -> None
        self._items.append(item)

    def clear(self):  # type: (...) -> None
        self._items.clear()


class _ScenarioTestedItems:

    def __init__(self):  # type: (...) -> None
        self.step_executions = _JsonItems()  # type: _JsonItems
        self.action_result_executions = _JsonItems()  # type: _JsonItems


class CheckJsonReportExpectations(_JsonReportFileVerificationStepImpl):

    def __init__(
            self,
            exec_step,  # type: _ExecScenarioType
            scenario_expectations,  # type: scenario.test.ScenarioExpectations
    ):  # type: (...) -> None
        _JsonReportFileVerificationStepImpl.__init__(self, exec_step)

        self.scenario_expectations = scenario_expectations  # type: scenario.test.ScenarioExpectations
        #: JSON data read from the report file.
        self.json = {}  # type: _JsonDictType
        #: For each scenario / subscenario executed, memorizes which steps, actions and expected results have already been processed.
        self._scenario_tested_items = []  # type: typing.List[_ScenarioTestedItems]

    def step(self):  # type: (...) -> None
        self.STEP("Scenario report expectations")

        scenario.logging.resetindentation()
        # Read the JSON report file.
        if self.ACTION("Read the JSON report file."):
            self.json = json.loads(self.report_path.read_bytes())
            self.debug("%s", scenario.debug.jsondump(self.json, indent=2),
                       extra=self.longtext(max_lines=10))

        self.checkjsonreport(self.json, self.scenario_expectations)

    def checkjsonreport(
            self,
            json_scenario,  # type: _JsonDictType
            scenario_expectations,  # type: scenario.test.ScenarioExpectations
    ):  # type: (...) -> None
        """
        Set in a separate public method from :meth:`step()` so that it can be called by campaign test cases as well.
        """
        scenario.logging.resetindentation()
        self._scenario_tested_items = [_ScenarioTestedItems()]
        self._checkscenario(
            json_scenario=json_scenario,
            scenario_expectations=scenario_expectations,
        )

    def _checkscenario(
            self,
            json_scenario,  # type: _JsonDictType
            scenario_expectations,  # type: scenario.test.ScenarioExpectations
    ):  # type: (...) -> None
        from steps.common import ExecScenario

        # Do not debug the ``json_scenario`` content for the top scenario.
        # It has usually been debugged previously.
        if self.doexecute() and (len(self._scenario_tested_items) > 1):
            self.debug("_checkscenario(): json_scenario = %s", scenario.debug.jsondump(json_scenario, indent=2),
                       extra=self.longtext(max_lines=20))

        if scenario_expectations.name:
            if self.RESULT(f"The test name is '{scenario_expectations.name}'."):
                self.assertjson(
                    json_scenario, "name", value=scenario_expectations.name,
                    evidence="Test name",
                )

        if scenario_expectations.status is not None:
            if self.RESULT(f"The test status is {scenario_expectations.status}."):
                self.assertjson(
                    json_scenario, "status", value=str(scenario_expectations.status),
                    evidence="Test status",
                )
        self._checkscenarioerrors(json_scenario, "errors", scenario_expectations.errors)
        self._checkscenarioerrors(json_scenario, "warnings", scenario_expectations.warnings)

        for _stat_expectations in (
            scenario_expectations.step_stats,
            scenario_expectations.action_stats,
            scenario_expectations.result_stats,
        ):  # type: scenario.test.StatExpectations
            if _stat_expectations.total is not None:
                if _stat_expectations.executed is not None:
                    _stat_types_txt = scenario.text.Countable(_stat_expectations.item_type, _stat_expectations.executed)  # type: scenario.text.Countable
                    if self.RESULT(f"Statistics report {len(_stat_types_txt)} executed {_stat_types_txt} out of {_stat_expectations.total}."):
                        self.assertjson(
                            json_scenario, f"stats.{_stat_expectations.item_type}.executed", type=int, value=_stat_expectations.executed,
                            evidence="Executed",
                        )
                        self.assertjson(
                            json_scenario, f"stats.{_stat_expectations.item_type}.total", type=int, value=_stat_expectations.total,
                            evidence="Total",
                        )
                else:
                    _stat_type_definitions_txt = scenario.text.Countable(f"{_stat_expectations.item_type} definition", _stat_expectations.total) \
                        # type: scenario.text.Countable
                    if self.RESULT(f"Statistics report {len(_stat_type_definitions_txt)} {_stat_type_definitions_txt}."):
                        self.assertjson(
                            json_scenario, f"stats.{_stat_expectations.item_type}.total", type=int, value=_stat_expectations.total,
                            evidence="Total",
                        )

        if scenario_expectations.attributes is not None:
            _attributes_txt = scenario.text.Countable("attribute", scenario_expectations.attributes)  # type: scenario.text.Countable
            if self.RESULT(f"The JSON report gives {len(_attributes_txt)} scenario {_attributes_txt}{_attributes_txt.ifany(':', '.')}"):
                self.assertjson(
                    json_scenario, "attributes", type=dict, len=len(scenario_expectations.attributes),
                    evidence="Number of scenario attributes",
                )
            for _attribute_name in scenario_expectations.attributes:
                if self.RESULT(f"- {_attribute_name}: {scenario_expectations.attributes[_attribute_name]!r}"):
                    self.assertjson(
                        json_scenario, f"attributes.{_attribute_name}", value=scenario_expectations.attributes[_attribute_name],
                        evidence=f"Attribute '{_attribute_name}'",
                    )

        if scenario_expectations.step_expectations is not None:
            _steps_txt = scenario.text.Countable("step", scenario_expectations.step_expectations)  # type: scenario.text.Countable
            _executions_txt = scenario.text.Countable("execution", scenario_expectations.step_expectations)  # type: scenario.text.Countable

            if self.getexecstep(ExecScenario).doc_only:
                if self.RESULT(f"{len(_steps_txt)} {_steps_txt} {_steps_txt.are} defined{_steps_txt.ifany(':', '.')}"):
                    self.assertjson(
                        json_scenario, "steps", type=list, len=len(scenario_expectations.step_expectations),
                        evidence="Number of steps",
                    )
            else:
                if self.RESULT(f"{len(_executions_txt)} step {_executions_txt} {_executions_txt.are} described in the report{_executions_txt.ifany(':', '.')}"):
                    _all_step_executions = []  # type: typing.List[_JsonDictType]
                    for _json_step_definition in self.assertjson(json_scenario, "steps", type=list):  # type: _JsonDictType
                        _all_step_executions.extend(self.assertjson(_json_step_definition, "executions", type=list))
                    self.assertlen(
                        _all_step_executions, len(scenario_expectations.step_expectations),
                        evidence="Number of step executions",
                    )
            for _step_definition_index in range(len(scenario_expectations.step_expectations)):
                self.RESULT(f"- Step #{_step_definition_index + 1}:")
                _step_expectations = scenario_expectations.step_expectations[_step_definition_index]  # type: scenario.test.StepExpectations
                _json_searched_step_definition = {}  # type: _JsonDictType
                if self.doexecute():
                    for _json_step_definition in self.assertjson(json_scenario, "steps", type=list):  # type already defined above
                        if _step_expectations.name:
                            if not self.assertjson(_json_step_definition, "location", type=str).endswith(_step_expectations.name):
                                continue
                        if _step_expectations.description:
                            if self.assertjson(_json_step_definition, "description", type=str) != _step_expectations.description:
                                continue
                        _json_searched_step_definition = _json_step_definition
                        break
                    if not _json_searched_step_definition:
                        self.error("No such %s in %s", _step_expectations, scenario.debug.jsondump(json_scenario, indent=2),
                                   extra=self.longtext(max_lines=10))
                        self.fail(f"Could not check {_step_expectations} definition")
                scenario.logging.pushindentation()
                self._checkstepdefinition(
                    json_step_definition=_json_searched_step_definition,
                    step_expectations=scenario_expectations.step_expectations[_step_definition_index],
                )
                scenario.logging.popindentation()
            if not self.getexecstep(ExecScenario).doc_only:
                if self.RESULT(f"{len(_executions_txt)} step {_executions_txt} {_executions_txt.have} been processed."):
                    self.assertlen(
                        self._scenario_tested_items[-1].step_executions, len(scenario_expectations.step_expectations),
                        evidence="Step executions processed",
                    )

    def _checkscenarioerrors(
            self,
            json_scenario,  # type: _JsonDictType
            jsonpath,  # type: str
            error_expectation_list,  # type: typing.Optional[typing.List[scenario.test.ErrorExpectations]]
    ):  # type: (...) -> None
        assert jsonpath.endswith("s")
        _errors_txt = scenario.text.Countable(jsonpath[:-1], error_expectation_list or 0)  # type: scenario.text.Countable

        if error_expectation_list is not None:
            if self.RESULT(f"{len(_errors_txt)} {_errors_txt} {_errors_txt.are} set{_errors_txt.ifany(':', '.')}"):
                self.assertjson(
                    json_scenario, jsonpath, type=list, len=len(error_expectation_list),
                    evidence=f"Number of {_errors_txt.plural}",
                )
            for _error_index in range(len(error_expectation_list)):  # type: int
                _error_expectations = error_expectation_list[_error_index]  # type: scenario.test.ErrorExpectations
                self.RESULT(f"- {_errors_txt.singular.capitalize()} #{_error_index + 1}:")
                _jsonpath_error = f"{jsonpath}[{_error_index}]"  # type: str
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
                            json_scenario, f"{_jsonpath_error}.type", value=_error_expectations.error_type,
                            evidence="Error type",
                        )

                # Level.
                if _error_expectations.level is scenario.test.NOT_SET:
                    if self.RESULT("Issue level is not set."):
                        self.assertjson(
                            json_scenario, f"{_jsonpath_error}.level", count=0,
                            evidence="Issue level",
                        )
                elif isinstance(_error_expectations.level, (int, enum.IntEnum)):
                    if self.RESULT(f"Issue level is {scenario.IssueLevel.getdesc(_error_expectations.level)}"):
                        self.assertjson(
                            json_scenario, f"{_jsonpath_error}.level", value=_error_expectations.level,
                            evidence="Issue level",
                        )

                # Id.
                if _error_expectations.id is scenario.test.NOT_SET:
                    if self.RESULT("Issue id is not set."):
                        self.assertjson(
                            json_scenario, f"{_jsonpath_error}.id", count=0,
                            evidence="Issue id",
                        )
                elif isinstance(_error_expectations.id, str):
                    if self.RESULT(f"Issue id is {_error_expectations.id!r}."):
                        self.assertjson(
                            json_scenario, f"{_jsonpath_error}.id", value=_error_expectations.id,
                            evidence="Issue id",
                        )

                # URL.
                if _error_expectations.url is scenario.test.NOT_SET:
                    if self.RESULT("URL is not set."):
                        self.assertjson(
                            json_scenario, f"{_jsonpath_error}.url", count=0,
                            evidence="URL",
                        )
                elif isinstance(_error_expectations.url, str):
                    if self.RESULT(f"URL is {_error_expectations.url!r}."):
                        self.assertjson(
                            json_scenario, f"{_jsonpath_error}.url", value=_error_expectations.url,
                            evidence="URL",
                        )

                # Message.
                if self.RESULT(f"{_errors_txt.singular.capitalize()} message is {_error_expectations.message!r}."):
                    self.assertjson(
                        json_scenario, f"{_jsonpath_error}.message", value=_error_expectations.message,
                        evidence=f"{_errors_txt.singular.capitalize()} message",
                    )

                # Location.
                if _error_expectations.location is not None:
                    if self.RESULT(f"{_errors_txt.singular.capitalize()} location is {_error_expectations.location!r}."):
                        self.assertjson(
                            json_scenario, f"{_jsonpath_error}.location", value=_error_expectations.location,
                            evidence=f"{_errors_txt.singular.capitalize()} location",
                        )

                scenario.logging.popindentation()

    def _checkstepdefinition(
            self,
            json_step_definition,  # type: _JsonDictType
            step_expectations,  # type: scenario.test.StepExpectations
    ):  # type: (...) -> None
        from steps.common import ExecScenario

        if self.doexecute():
            self.debug("_checkstepdefinition(): json_step_definition = %s", scenario.debug.jsondump(json_step_definition, indent=2),
                       extra=self.longtext(max_lines=20))

        if step_expectations.name:
            if self.RESULT(f"The step location corresponds to '{step_expectations.name}'."):
                self.assertendswith(
                    self.assertjson(json_step_definition, "location", type=str), step_expectations.name,
                    evidence="Step location",
                )

        if step_expectations.description:
            if self.RESULT(f"The step description is {step_expectations.description!r}."):
                self.assertjson(
                    json_step_definition, "description", type=str, value=step_expectations.description,
                    evidence="Step description",
                )

        if not self.getexecstep(ExecScenario).doc_only:
            _json_searched_step_execution = {}  # type: _JsonDictType
            if self.doexecute():
                for _json_step_execution in self.assertjson(json_step_definition, "executions", type=list):  # type: _JsonDictType
                    if _json_step_execution not in self._scenario_tested_items[-1].step_executions:
                        _json_searched_step_execution = _json_step_execution
                        break
                if not _json_searched_step_execution:
                    self.error("No step execution left in %s", scenario.debug.jsondump(json_step_definition, indent=2),
                               extra=self.longtext(max_lines=10))
                    self.fail(f"Could not check {step_expectations} execution")
            self._checkstepexecution(
                json_step_execution=_json_searched_step_execution,
                step_expectations=step_expectations,
            )

        if step_expectations.action_result_expectations is not None:
            _actions_results_txt = scenario.text.Countable("action/result", step_expectations.action_result_expectations)  # type: scenario.text.Countable
            _executions_txt = scenario.text.Countable("execution", step_expectations.action_result_expectations)  # type: scenario.text.Countable

            if self.getexecstep(ExecScenario).doc_only:
                if self.RESULT(f"{len(_actions_results_txt)} {_actions_results_txt} {_actions_results_txt.are} defined{_actions_results_txt.ifany(':', '.')}"):
                    self.assertjson(
                        json_step_definition, "actions-results", type=list, len=len(step_expectations.action_result_expectations),
                        evidence="Number of actions/results",
                    )
            else:
                if self.RESULT(f"{len(_executions_txt)} action/result {_executions_txt} "
                               f"{_executions_txt.are} described in the report{_executions_txt.ifany(':', '.')}"):
                    _all_action_result_executions = []  # type: typing.List[_JsonDictType]
                    for _json_action_result_definition in self.assertjson(json_step_definition, "actions-results", type=list):  # type: _JsonDictType
                        _all_action_result_executions.extend(self.assertjson(_json_action_result_definition, "executions", type=list))
                    self.assertlen(
                        _all_action_result_executions, len(step_expectations.action_result_expectations),
                        evidence="Number of step executions",
                    )

            for _action_result_definition_index in range(len(step_expectations.action_result_expectations)):
                self.RESULT(f"- {step_expectations.action_result_expectations[_action_result_definition_index].type} #{_action_result_definition_index + 1}:")
                scenario.logging.pushindentation()
                self._checkactionresultdefinition(
                    json_action_result_definition=self.testdatafromjson(
                        json_step_definition, f"actions-results[{_action_result_definition_index}]", type=dict,
                    ),
                    action_result_expectations=step_expectations.action_result_expectations[_action_result_definition_index],
                )
                scenario.logging.popindentation()
            if not self.getexecstep(ExecScenario).doc_only:
                if self.RESULT(f"{len(_executions_txt)} action/result {_executions_txt} {_executions_txt.have} been processed."):
                    self.assertlen(
                        self._scenario_tested_items[-1].action_result_executions, len(step_expectations.action_result_expectations),
                        evidence="Action/result executions processed",
                    )

        # Clear the action/result executions memory at the end of the step analysis.
        self._scenario_tested_items[-1].action_result_executions.clear()

    def _checkstepexecution(
            self,
            json_step_execution,  # type: _JsonDictType
            step_expectations,  # type: scenario.test.StepExpectations
    ):  # type: (...) -> None
        if self.doexecute():
            self.debug("_checkstepexecution(): json_step_execution = %s", scenario.debug.jsondump(json_step_execution, indent=2),
                       extra=self.longtext(max_lines=20))
        self._scenario_tested_items[-1].step_executions.append(json_step_execution)

        if step_expectations.number is not None:
            if self.RESULT(f"The {step_expectations} execution number is {step_expectations.number}."):
                self.assertjson(
                    json_step_execution, "number", type=int, value=step_expectations.number,
                    evidence="Step execution number",
                )

        if len(self._scenario_tested_items[-1].step_executions) > 1:
            if self.RESULT(f"The {step_expectations} execution takes place after the previous one."):
                _previous_step_execution = self._scenario_tested_items[-1].step_executions[-2]  # type: _JsonDictType
                _previous_end = self.assertjson(
                    _previous_step_execution, "time.end", type=str,
                    evidence="Previous step end",
                )  # type: str
                _start = self.assertjson(
                    json_step_execution, "time.start", type=str,
                    evidence="Current step start",
                )  # type: str
                self.assertlessequal(
                    _previous_end, _start,
                    evidence="Previous.end <= Current.start",
                )

    def _checkactionresultdefinition(
            self,
            json_action_result_definition,  # type: _JsonDictType
            action_result_expectations,  # type: scenario.test.ActionResultExpectations
    ):  # type: (...) -> None
        from steps.common import ExecScenario

        if self.doexecute():
            self.debug("_checkactionresultdefinition(): json_action_result_definition = %s", scenario.debug.jsondump(json_action_result_definition, indent=2),
                       extra=self.longtext(max_lines=20))

        _type_desc = "action" if action_result_expectations.type == scenario.ActionResult.Type.ACTION else "expected result"  # type: str

        if self.RESULT(f"The action/result type is {action_result_expectations.type}."):
            self.assertjson(
                json_action_result_definition, "type", type=str, value=str(action_result_expectations.type),
                evidence="Action/result type",
            )

        if self.RESULT(f"The {_type_desc} description is {action_result_expectations.description!r}."):
            self.assertjson(
                json_action_result_definition, "description", type=str, value=action_result_expectations.description,
                evidence=f"{_type_desc.capitalize()} description",
            )

        if not self.getexecstep(ExecScenario).doc_only:
            _json_searched_action_result_execution = {}  # type: _JsonDictType
            if self.doexecute():
                for _json_action_resut_execution in self.assertjson(json_action_result_definition, "executions", type=list):  # type: _JsonDictType
                    if _json_action_resut_execution not in self._scenario_tested_items[-1].action_result_executions:
                        _json_searched_action_result_execution = _json_action_resut_execution
                        break
                if not _json_searched_action_result_execution:
                    self.error("No %s execution in %s", _type_desc, scenario.debug.jsondump(json_action_result_definition, indent=2),
                               extra=self.longtext(max_lines=10))
                    self.fail(f"Could not check {_type_desc} execution")
            self._checkactionresultexecution(
                json_action_result_execution=_json_searched_action_result_execution,
                action_result_expectations=action_result_expectations,
            )
        else:
            if action_result_expectations.subscenario_expectations is not None:
                self.assertisempty(action_result_expectations.subscenario_expectations, "Unexpected list of subscenarios for a --doc-only execution")
                if self.RESULT("No subscenario has been executed."):
                    self.assertisempty(
                        self.assertjson(
                            json_action_result_definition, "executions", type=list,
                            evidence="Subscenario executions",
                        ),
                        evidence=False,
                    )

    def _checkactionresultexecution(
            self,
            json_action_result_execution,  # type: _JsonDictType
            action_result_expectations,  # type: scenario.test.ActionResultExpectations
    ):  # type: (...) -> None
        if self.doexecute():
            self.debug("_checkactionresultexecution(): json_action_result_execution = %s", scenario.debug.jsondump(json_action_result_execution, indent=2),
                       extra=self.longtext(max_lines=20))
        self._scenario_tested_items[-1].action_result_executions.append(json_action_result_execution)

        _type_desc = "action" if action_result_expectations.type == scenario.ActionResult.Type.ACTION else "expected result"  # type: str
        _type_math_desc = str(action_result_expectations.type).capitalize()  # type: str

        if self.RESULT(f"The {_type_desc} execution times are bound in the current step execution time."):
            assert self._scenario_tested_items[-1].step_executions
            _step_execution = self._scenario_tested_items[-1].step_executions[-1]  # type: _JsonDictType
            _step_execution_start = self.assertjson(
                _step_execution, "time.start", type=str,
                evidence="Step start",
            )  # type: str
            _step_execution_end = self.assertjson(
                _step_execution, "time.end", type=str,
                evidence="Step end",
            )  # type: str
            _action_result_execution_start = self.assertjson(
                json_action_result_execution, "time.start", type=str,
                evidence=f"{_type_math_desc} start",
            )  # type: str
            _action_result_execution_end = self.assertjson(
                json_action_result_execution, "time.end", type=str,
                evidence=f"{_type_math_desc} end",
            )  # type: str
            self.assertlessequal(
                _step_execution_start, _action_result_execution_start,
                evidence=f"Step.start <= {_type_math_desc}.start",
            )
            self.assertlessequal(
                _action_result_execution_start, _action_result_execution_end,
                evidence=f"{_type_math_desc}.start <= {_type_math_desc}.end",
            )
            self.assertlessequal(
                _action_result_execution_end, _step_execution_end,
                evidence=f"{_type_math_desc}.end <= Step.end",
            )

        if action_result_expectations.subscenario_expectations is not None:
            _subscenarios_txt = scenario.text.Countable("subscenario", action_result_expectations.subscenario_expectations)  # type: scenario.text.Countable
            if self.RESULT(f"{len(_subscenarios_txt)} {_subscenarios_txt} {_subscenarios_txt.have} been executed{_subscenarios_txt.ifany(':', '.')}"):
                self.assertjson(
                    json_action_result_execution, "subscenarios", type=list, len=len(action_result_expectations.subscenario_expectations),
                    evidence="Number of subscenarios",
                )
            for _subscenario_expectation_index in range(len(action_result_expectations.subscenario_expectations)):  # type: int
                self.RESULT(f"- Subscenario #{_subscenario_expectation_index + 1}:")
                scenario.logging.pushindentation()
                self._scenario_tested_items.append(_ScenarioTestedItems())
                self._checkscenario(
                    json_scenario=self.testdatafromjson(json_action_result_execution, f"subscenarios[{_subscenario_expectation_index}]", type=dict),
                    scenario_expectations=action_result_expectations.subscenario_expectations[_subscenario_expectation_index],
                )
                self._scenario_tested_items.pop()
                scenario.logging.popindentation()
