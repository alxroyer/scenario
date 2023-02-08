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
from scenarioexecution.steps.execution import ExecScenario
from .parser import ParseScenarioLog


class CheckScenarioLogExpectations(scenario.test.VerificationStep):

    def __init__(
            self,
            exec_step,  # type: ParseScenarioLog
            scenario_expectations,  # type: scenario.test.ScenarioExpectations
    ):  # type: (...) -> None
        scenario.test.VerificationStep.__init__(self, exec_step)

        self.scenario_expectations = scenario_expectations  # type: scenario.test.ScenarioExpectations

    def step(self):  # type: (...) -> None
        self.STEP("Scenario log output expectations")

        scenario.logging.resetindentation()

        if self.doexecute():
            self.debug("%s", scenario.debug.jsondump(self.getexecstep(ParseScenarioLog).json_main_scenario, indent=2),
                       extra=self.longtext(max_lines=None))
        self._checkscenario(self.getexecstep(ParseScenarioLog).json_main_scenario, self.scenario_expectations)

    def _checkscenario(
            self,
            json_scenario,  # type: JSONDict
            scenario_expectations,  # type: scenario.test.ScenarioExpectations
    ):  # type: (...) -> None

        if scenario_expectations.name:
            if self.RESULT(f"The test name is '{scenario_expectations.name}'."):
                self.assertjson(
                    json_scenario, "name", value=scenario_expectations.name,
                    evidence="Test name",
                )

        if scenario_expectations.status is not None:
            if self.RESULT(f"The test status is '{scenario_expectations.status}'."):
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
                            evidence="Executed count",
                        )
                        self.assertjson(
                            json_scenario, f"stats.{_stat_expectations.item_type}.total", type=int, value=_stat_expectations.total,
                            evidence="Total count",
                        )
                else:
                    _stat_type_definitions_txt = scenario.text.Countable(f"{_stat_expectations.item_type} definition", _stat_expectations.total) \
                        # type: scenario.text.Countable
                    if self.RESULT(f"Statistics report {len(_stat_type_definitions_txt)} {_stat_type_definitions_txt}."):
                        self.assertjson(
                            json_scenario, f"stats.{_stat_expectations.item_type}.total", type=int, value=_stat_expectations.total,
                            evidence="Total count",
                        )

        if scenario_expectations.attributes is not None:
            _attributes_txt = scenario.text.Countable("attribute", scenario_expectations.attributes)  # type: scenario.text.Countable
            if self.RESULT(f"The scenario has {len(_attributes_txt)} {_attributes_txt}{_attributes_txt.ifany(':', '.')}"):
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
            if self.RESULT(f"{len(_steps_txt)} {_steps_txt} "
                           f"{(_steps_txt.are + ' defined') if self.getexecstep(ExecScenario).doc_only else (_steps_txt.have + ' been executed')}"
                           f"{_steps_txt.ifany(':', '.')}"):
                self.assertjson(
                    json_scenario, "steps", type=list, len=len(scenario_expectations.step_expectations),
                    evidence="Number of steps",
                )

            for _step_definition_index in range(len(scenario_expectations.step_expectations)):  # type: int
                self.RESULT(f"- Step #{_step_definition_index + 1}:")
                scenario.logging.pushindentation()
                self._checkstep(
                    json_step=self.testdatafromjson(json_scenario, f"steps[{_step_definition_index}]", type=dict),
                    step_expectations=scenario_expectations.step_expectations[_step_definition_index],
                )
                scenario.logging.popindentation()

    def _checkscenarioerrors(
            self,
            json_scenario,  # type: JSONDict
            jsonpath,  # type: str
            error_expectation_list,  # type: typing.Optional[typing.List[scenario.test.ErrorExpectations]]
    ):  # type: (...) -> None
        if error_expectation_list is not None:
            assert jsonpath.endswith("s")
            _errors_txt = scenario.text.Countable(jsonpath[:-1], error_expectation_list)  # type: scenario.text.Countable
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
                            evidence=f"Error type",
                        )

                # Level.
                if _error_expectations.level is scenario.test.NOT_SET:
                    if self.RESULT("Issue level is not set."):
                        self.assertjson(
                            json_scenario, f"{_jsonpath_error}.level", count=0,
                            evidence="Issue level",
                        )
                elif isinstance(_error_expectations.level, (int, enum.IntEnum)):
                    if self.RESULT(f"Issue level is {scenario.IssueLevel.getdesc(_error_expectations.level)}."):
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

    def _checkstep(
            self,
            json_step,  # type: JSONDict
            step_expectations,  # type: scenario.test.StepExpectations
    ):  # type: (...) -> None
        if step_expectations.name:
            if self.RESULT(f"The step name is '{step_expectations.name}'."):
                self.assertendswith(
                    self.assertjson(json_step, "name", type=str), step_expectations.name,
                    evidence="Step name",
                )

        if step_expectations.description:
            if self.RESULT(f"The step description is {step_expectations.description!r}."):
                self.assertjson(
                    json_step, "description", type=str, value=step_expectations.description,
                    evidence="Step description",
                )

        if step_expectations.action_result_expectations is not None:
            _actions_results_txt = scenario.text.Countable("action/result", step_expectations.action_result_expectations)  # type: scenario.text.Countable
            if self.RESULT(f"{len(_actions_results_txt)} {_actions_results_txt} {_actions_results_txt.are} defined{_actions_results_txt.ifany(':', '.')}"):
                self.assertjson(
                    json_step, "actions-results", type=list, len=len(step_expectations.action_result_expectations),
                    evidence="Number of actions/results",
                )

            for _action_result_definition_index in range(len(step_expectations.action_result_expectations)):
                self.RESULT(f"- {step_expectations.action_result_expectations[_action_result_definition_index].type} #{_action_result_definition_index + 1}:")
                scenario.logging.pushindentation()
                self._checkactionresult(
                    json_action_result=self.testdatafromjson(json_step, f"actions-results[{_action_result_definition_index}]", type=dict),
                    action_result_expectations=step_expectations.action_result_expectations[_action_result_definition_index],
                )
                scenario.logging.popindentation()

    def _checkactionresult(
            self,
            json_action_result,  # type: JSONDict
            action_result_expectations,  # type: scenario.test.ActionResultExpectations
    ):  # type: (...) -> None
        _type_desc = "action" if action_result_expectations.type == scenario.ActionResult.Type.ACTION else "expected result"  # type: str

        if self.RESULT(f"The action/result type is {action_result_expectations.type}."):
            self.assertjson(
                json_action_result, "type", value=str(action_result_expectations.type),
                evidence="Action/result type",
            )

        if self.RESULT(f"The {_type_desc} description is {action_result_expectations.description!r}."):
            self.assertjson(
                json_action_result, "description", type=str, value=action_result_expectations.description,
                evidence=f"{_type_desc.capitalize()} description",
            )

        if action_result_expectations.subscenario_expectations is not None:
            _subscenarios_txt = scenario.text.Countable("sub-scenario", action_result_expectations.subscenario_expectations)  # type: scenario.text.Countable
            if self.RESULT(f"{len(_subscenarios_txt)} {_subscenarios_txt} {_subscenarios_txt.have} been executed{_subscenarios_txt.ifany(':', '.')}"):
                self.assertjson(
                    json_action_result, "subscenarios", type=list, len=len(action_result_expectations.subscenario_expectations),
                    evidence="Number of sub-scenarios",
                )
            for _subscenario_index in range(len(action_result_expectations.subscenario_expectations)):  # type: int
                self.RESULT(f"- Sub-scenario #{_subscenario_index + 1}:")
                scenario.logging.pushindentation()
                self._checkscenario(
                    json_scenario=self.testdatafromjson(json_action_result, f"subscenarios[{_subscenario_index}]", type=dict),
                    scenario_expectations=action_result_expectations.subscenario_expectations[_subscenario_index],
                )
                scenario.logging.popindentation()
