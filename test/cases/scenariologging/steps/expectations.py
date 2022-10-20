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

import json
import typing

import scenario
if typing.TYPE_CHECKING:
    from scenario.typing import JSONDict
import scenario.test

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
            self.debuglongtext(json.dumps(self.getexecstep(ParseScenarioLog).json_main_scenario, indent=2), max_lines=None)
        self._checkscenario(self.getexecstep(ParseScenarioLog).json_main_scenario, self.scenario_expectations)

    def _checkscenario(
            self,
            json_scenario,  # type: JSONDict
            scenario_expectations,  # type: scenario.test.ScenarioExpectations
    ):  # type: (...) -> None

        if scenario_expectations.name:
            if self.RESULT("The test name is '%s'." % scenario_expectations.name):
                self.assertjson(
                    json_scenario, "name", value=scenario_expectations.name,
                    evidence="Test name",
                )

        if scenario_expectations.status is not None:
            if self.RESULT("The test status is '%s'." % scenario_expectations.status):
                self.assertjson(
                    json_scenario, "status", value=str(scenario_expectations.status),
                    evidence="Test status",
                )
        self._checkscenarioerrors(json_scenario, "errors", scenario_expectations.errors)
        self._checkscenarioerrors(json_scenario, "warnings", scenario_expectations.warnings)

        for _stat_ref in (
            scenario_expectations.step_stats,
            scenario_expectations.action_stats,
            scenario_expectations.result_stats,
        ):  # type: scenario.test.StatExpectations
            if _stat_ref.total is not None:
                if _stat_ref.executed is not None:
                    if self.RESULT("Statistics report %d %s out of %d executed." % (_stat_ref.executed, _stat_ref.item_type, _stat_ref.total)):
                        self.assertjson(
                            json_scenario, "stats.%s.executed" % _stat_ref.item_type, value=_stat_ref.executed,
                            evidence="Executed count",
                        )
                        self.assertjson(
                            json_scenario, "stats.%s.total" % _stat_ref.item_type, value=_stat_ref.total,
                            evidence="Total count",
                        )
                else:
                    if self.RESULT("Statistics report %d %s definitions." % (_stat_ref.total, _stat_ref.item_type)):
                        self.assertjson(
                            json_scenario, "stats.%s.total" % _stat_ref.item_type, value=_stat_ref.total,
                            evidence="Total count",
                        )

        if scenario_expectations.attributes is not None:
            if self.RESULT("The scenario has %d attribute(s):" % len(scenario_expectations.attributes)):
                self.assertjson(
                    json_scenario, "attributes", type=dict, len=len(scenario_expectations.attributes),
                    evidence="Number of scenario attributes",
                )
            for _attribute_name in scenario_expectations.attributes:
                if self.RESULT("- %s: %s" % (_attribute_name, scenario_expectations.attributes[_attribute_name])):
                    self.assertjson(
                        json_scenario, "attributes.%s" % _attribute_name, value=scenario_expectations.attributes[_attribute_name],
                        evidence="Attribute '%s'" % _attribute_name,
                    )

        if scenario_expectations.step_expectations is not None:
            if self.RESULT("%d steps %s:" % (
                len(scenario_expectations.step_expectations),
                "are defined" if self.getexecstep(ExecScenario).doc_only else "have been executed",
            )):
                self.assertjson(
                    json_scenario, "steps", type=list, len=len(scenario_expectations.step_expectations),
                    evidence="Number of steps",
                )

            for _step_definition_index in range(len(scenario_expectations.step_expectations)):  # type: int
                self.RESULT("- Step #%d:" % (_step_definition_index + 1))
                scenario.logging.pushindentation()
                self._checkstep(
                    json_step=self.testdatafromjson(json_scenario, "steps[%d]" % _step_definition_index, type=dict),
                    step_expectations=scenario_expectations.step_expectations[_step_definition_index],
                )
                scenario.logging.popindentation()

    def _checkscenarioerrors(
            self,
            json_scenario,  # type: JSONDict
            json_path,  # type: str
            error_expectation_list,  # type: typing.Optional[typing.List[scenario.test.ErrorExpectations]]
    ):  # type: (...) -> None
        _error_type = json_path[:-1]  # type: str

        if error_expectation_list is not None:
            if self.RESULT("%d %s(s) are set:" % (len(error_expectation_list), _error_type)):
                self.assertjson(
                    json_scenario, json_path, type=list, len=len(error_expectation_list),
                    evidence="Number of %ss" % _error_type,
                )
            for _error_index in range(len(error_expectation_list)):  # type: int
                _error_expectations = error_expectation_list[_error_index]  # type: scenario.test.ErrorExpectations
                self.RESULT("- %s #%d:" % (_error_type.capitalize(), _error_index + 1))
                _json_path_error = "%s[%d]" % (json_path, _error_index)  # type: str
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
                            json_scenario, _json_path_error + ".type", value=_error_expectations.error_type,
                            evidence="%s type" % _error_type.capitalize(),
                        )
                if _error_expectations.issue_id is not None:
                    if self.RESULT("Issue id is %s." % repr(_error_expectations.issue_id)):
                        self.assertjson(
                            json_scenario, _json_path_error + ".id", value=_error_expectations.issue_id,
                            evidence="Issue id",
                        )
                if self.RESULT("%s message is %s." % (_error_type.capitalize(), repr(_error_expectations.message))):
                    self.assertjson(
                        json_scenario, _json_path_error + ".message", value=_error_expectations.message,
                        evidence="%s message" % _error_type.capitalize(),
                    )
                if _error_expectations.location is not None:
                    if self.RESULT("%s location is %s." % (_error_type.capitalize(), repr(_error_expectations.location))):
                        self.assertjson(
                            json_scenario, _json_path_error + ".location", value=_error_expectations.location,
                            evidence="%s location" % _error_type.capitalize(),
                        )

                scenario.logging.popindentation()

    def _checkstep(
            self,
            json_step,  # type: JSONDict
            step_expectations,  # type: scenario.test.StepExpectations
    ):  # type: (...) -> None
        if step_expectations.name:
            if self.RESULT("The step name is '%s'." % step_expectations.name):
                self.assertendswith(
                    self.assertjson(json_step, "name", type=str), step_expectations.name,
                    evidence="Step name",
                )

        if step_expectations.description:
            if self.RESULT("The step description is '%s'." % step_expectations.description):
                self.assertjson(
                    json_step, "description", type=str, value=step_expectations.description,
                    evidence="Step description",
                )

        if step_expectations.action_result_expectations is not None:
            if self.RESULT("%d actions/results are defined:" % len(step_expectations.action_result_expectations)):
                self.assertjson(
                    json_step, "actions-results", type=list, len=len(step_expectations.action_result_expectations),
                    evidence="Number of actions/results",
                )

            for _action_result_definition_index in range(len(step_expectations.action_result_expectations)):
                self.RESULT("- %s #%d:" % (
                    step_expectations.action_result_expectations[_action_result_definition_index].type,
                    _action_result_definition_index + 1,
                ))
                scenario.logging.pushindentation()
                self._checkactionresult(
                    json_action_result=self.testdatafromjson(json_step, "actions-results[%d]" % _action_result_definition_index, type=dict),
                    action_result_expectations=step_expectations.action_result_expectations[_action_result_definition_index],
                )
                scenario.logging.popindentation()

    def _checkactionresult(
            self,
            json_action_result,  # type: JSONDict
            action_result_expectations,  # type: scenario.test.ActionResultExpectations
    ):  # type: (...) -> None
        _type_desc = "action" if action_result_expectations.type == scenario.ActionResult.Type.ACTION else "expected result"  # type: str

        if self.RESULT("The action/result type is %s." % action_result_expectations.type):
            self.assertjson(
                json_action_result, "type", value=str(action_result_expectations.type),
                evidence="Action/result type",
            )

        if self.RESULT("The %s description is '%s'." % (_type_desc, action_result_expectations.description)):
            self.assertjson(
                json_action_result, "description", type=str, value=action_result_expectations.description,
                evidence="%s description" % _type_desc.capitalize(),
            )

        if action_result_expectations.subscenario_expectations is not None:
            if self.RESULT("%d sub-scenario(s) has(have) been executed:" % len(action_result_expectations.subscenario_expectations)):
                self.assertjson(
                    json_action_result, "subscenarios", type=list, len=len(action_result_expectations.subscenario_expectations),
                    evidence="Number of sub-scenarios",
                )
            for _subscenario_index in range(len(action_result_expectations.subscenario_expectations)):  # type: int
                self.RESULT("- Sub-scenario #%d:" % (_subscenario_index + 1))
                scenario.logging.pushindentation()
                self._checkscenario(
                    json_scenario=self.testdatafromjson(json_action_result, "subscenarios[%d]" % _subscenario_index, type=dict),
                    scenario_expectations=action_result_expectations.subscenario_expectations[_subscenario_index],
                )
                scenario.logging.popindentation()
