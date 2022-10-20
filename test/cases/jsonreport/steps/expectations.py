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
from .reportfile import JsonReportFileVerificationStep


class CheckJsonReportExpectations(JsonReportFileVerificationStep):

    class ScenarioTestedItems:
        def __init__(self):  # type: (...) -> None
            self.step_executions = []  # type: typing.List[JSONDict]
            self.action_result_executions = []  # type: typing.List[JSONDict]

    def __init__(
            self,
            exec_step,  # type: ExecScenario
            scenario_expectations,  # type: scenario.test.ScenarioExpectations
    ):  # type: (...) -> None
        JsonReportFileVerificationStep.__init__(self, exec_step)

        self.scenario_expectations = scenario_expectations  # type: scenario.test.ScenarioExpectations
        #: JSON data read from the report file.
        self.json = {}  # type: JSONDict
        #: For each scenario / sub-scenario executed, memorizes which steps, actions and expected results have already been processed.
        self._scenario_tested_items = []  # type: typing.List[CheckJsonReportExpectations.ScenarioTestedItems]

    def step(self):  # type: (...) -> None
        self.STEP("Scenario report expectations")

        scenario.logging.resetindentation()
        # Read the JSON report file.
        if self.ACTION("Read the JSON report file."):
            self.json = json.loads(self.report_path.read_bytes())
            self.debuglongtext(json.dumps(self.json, indent=2), max_lines=10)

        self.checkjsonreport(self.json, self.scenario_expectations)

    def checkjsonreport(
            self,
            json_scenario,  # type: JSONDict
            scenario_expectations,  # type: scenario.test.ScenarioExpectations
    ):  # type: (...) -> None
        """
        Set in a separate public method from :meth:`step()` so that it can be called by campaign test cases as well.
        """
        scenario.logging.resetindentation()
        self._scenario_tested_items = [CheckJsonReportExpectations.ScenarioTestedItems()]
        self._checkscenario(
            json_scenario=json_scenario,
            scenario_expectations=scenario_expectations,
        )

    def _checkscenario(
            self,
            json_scenario,  # type: JSONDict
            scenario_expectations,  # type: scenario.test.ScenarioExpectations
    ):  # type: (...) -> None
        # Do not debug the ``json_scenario`` content for the top scenario.
        # It has usually been debugged previously.
        if self.doexecute() and (len(self._scenario_tested_items) > 1):
            self.debuglongtext("_checkscenario(): json_scenario = %s" % json.dumps(json_scenario, indent=2), max_lines=20)

        if scenario_expectations.name:
            if self.RESULT("The test name is '%s'." % scenario_expectations.name):
                self.assertjson(
                    json_scenario, "name", value=scenario_expectations.name,
                    evidence="Test name",
                )

        if scenario_expectations.status is not None:
            if self.RESULT("The test status is %s." % scenario_expectations.status):
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
                    if self.RESULT("Statistics report %d %s out of %d executed."
                                   % (_stat_expectations.executed, _stat_expectations.item_type, _stat_expectations.total)):
                        self.assertjson(
                            json_scenario, "stats.%s.executed" % _stat_expectations.item_type, value=_stat_expectations.executed,
                            evidence="Executed",
                        )
                        self.assertjson(
                            json_scenario, "stats.%s.total" % _stat_expectations.item_type, value=_stat_expectations.total,
                            evidence="Total",
                        )
                else:
                    if self.RESULT("Statistics report %d %s definitions." % (_stat_expectations.total, _stat_expectations.item_type)):
                        self.assertjson(
                            json_scenario, "stats.%s.total" % _stat_expectations.item_type, value=_stat_expectations.total,
                            evidence="Total",
                        )

        if scenario_expectations.attributes is not None:
            if self.RESULT("The JSON report gives %d scenario attribute(s):" % len(scenario_expectations.attributes)):
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
            if self.getexecstep(ExecScenario).doc_only:
                if self.RESULT("%d steps are defined:" % len(scenario_expectations.step_expectations)):
                    self.assertjson(
                        json_scenario, "steps", type=list, len=len(scenario_expectations.step_expectations),
                        evidence="Number of steps",
                    )
            else:
                if self.RESULT("%d step executions are described in the report:" % len(scenario_expectations.step_expectations)):
                    _all_step_executions = []  # type: typing.List[JSONDict]
                    for _json_step_definition in self.assertjson(json_scenario, "steps", type=list):  # type: JSONDict
                        _all_step_executions.extend(self.assertjson(_json_step_definition, "executions", type=list))
                    self.assertlen(
                        _all_step_executions, len(scenario_expectations.step_expectations),
                        evidence="Number of step executions",
                    )
            for _step_definition_index in range(len(scenario_expectations.step_expectations)):
                self.RESULT("- Step #%d:" % (_step_definition_index + 1))
                _step_expectations = scenario_expectations.step_expectations[_step_definition_index]  # type: scenario.test.StepExpectations
                _json_searched_step_definition = {}  # type: JSONDict
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
                        self.error("No such %s in %s" % (str(_step_expectations), json.dumps(json_scenario, indent=2)))
                        self.fail("Could not check %s definition" % str(_step_expectations))
                scenario.logging.pushindentation()
                self._checkstepdefinition(
                    json_step_definition=_json_searched_step_definition,
                    step_expectations=scenario_expectations.step_expectations[_step_definition_index],
                )
                scenario.logging.popindentation()
            if not self.getexecstep(ExecScenario).doc_only:
                if self.RESULT("%d step executions have been processed." % len(scenario_expectations.step_expectations)):
                    self.assertlen(
                        self._scenario_tested_items[-1].step_executions, len(scenario_expectations.step_expectations),
                        evidence="Step executions processed",
                    )

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
                            evidence="Error type",
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

    def _checkstepdefinition(
            self,
            json_step_definition,  # type: JSONDict
            step_expectations,  # type: scenario.test.StepExpectations
    ):  # type: (...) -> None
        if self.doexecute():
            self.debuglongtext("_checkstepdefinition(): json_step_definition = %s" % json.dumps(json_step_definition, indent=2), max_lines=20)

        if step_expectations.name:
            if self.RESULT("The step location corresponds to '%s'." % step_expectations.name):
                self.assertendswith(
                    self.assertjson(json_step_definition, "location", type=str), step_expectations.name,
                    evidence="Step location",
                )

        if step_expectations.description:
            if self.RESULT("The step description is '%s'." % step_expectations.description):
                self.assertjson(
                    json_step_definition, "description", type=str, value=step_expectations.description,
                    evidence="Step description",
                )

        if not self.getexecstep(ExecScenario).doc_only:
            _json_searched_step_execution = {}  # type: JSONDict
            if self.doexecute():
                for _json_step_execution in self.assertjson(json_step_definition, "executions", type=list):  # type: JSONDict
                    if _json_step_execution not in self._scenario_tested_items[-1].step_executions:
                        _json_searched_step_execution = _json_step_execution
                        break
                if not _json_searched_step_execution:
                    self.error("No step execution left in %s" % json.dumps(json_step_definition, indent=2))
                    self.fail("Could not check %s execution" % str(step_expectations))
            self._checkstepexecution(
                json_step_execution=_json_searched_step_execution,
                step_expectations=step_expectations,
            )

        if step_expectations.action_result_expectations is not None:
            if self.getexecstep(ExecScenario).doc_only:
                if self.RESULT("%d actions/results are defined:" % len(step_expectations.action_result_expectations)):
                    self.assertjson(
                        json_step_definition, "actions-results", type=list, len=len(step_expectations.action_result_expectations),
                        evidence="Number of actions/results",
                    )
            else:
                if self.RESULT("%d actions/results executions are described in the report:" % len(step_expectations.action_result_expectations)):
                    _all_action_result_executions = []  # type: typing.List[JSONDict]
                    for _json_action_result_definition in self.assertjson(json_step_definition, "actions-results", type=list):  # type: JSONDict
                        _all_action_result_executions.extend(self.assertjson(_json_action_result_definition, "executions", type=list))
                    self.assertlen(
                        _all_action_result_executions, len(step_expectations.action_result_expectations),
                        evidence="Number of step executions",
                    )

            for _action_result_definition_index in range(len(step_expectations.action_result_expectations)):
                self.RESULT("- %s #%d:" % (
                    step_expectations.action_result_expectations[_action_result_definition_index].type,
                    _action_result_definition_index + 1,
                ))
                scenario.logging.pushindentation()
                self._checkactionresultdefinition(
                    json_action_result_definition=self.testdatafromjson(
                        json_step_definition, "actions-results[%d]" % _action_result_definition_index, type=dict,
                    ),
                    action_result_expectations=step_expectations.action_result_expectations[_action_result_definition_index],
                )
                scenario.logging.popindentation()
            if not self.getexecstep(ExecScenario).doc_only:
                if self.RESULT("%d action/result executions have been processed." % len(step_expectations.action_result_expectations)):
                    self.assertlen(
                        self._scenario_tested_items[-1].action_result_executions, len(step_expectations.action_result_expectations),
                        evidence="Action/result executions processed",
                    )

        # Clear the action/result executions memory at the end of the step analysis.
        self._scenario_tested_items[-1].action_result_executions = []

    def _checkstepexecution(
            self,
            json_step_execution,  # type: JSONDict
            step_expectations,  # type: scenario.test.StepExpectations
    ):  # type: (...) -> None
        if self.doexecute():
            self.debuglongtext("_checkstepexecution(): json_step_execution = %s" % json.dumps(json_step_execution, indent=2), max_lines=20)
        self._scenario_tested_items[-1].step_executions.append(json_step_execution)

        if step_expectations.number is not None:
            if self.RESULT("The %s execution number is %d." % (str(step_expectations), step_expectations.number)):
                self.assertjson(
                    json_step_execution, "number", type=int, value=step_expectations.number,
                    evidence="Step execution number",
                )

        if len(self._scenario_tested_items[-1].step_executions) > 1:
            if self.RESULT("The %s execution takes place after the previous one." % str(step_expectations)):
                _previous_step_execution = self._scenario_tested_items[-1].step_executions[-2]  # type: JSONDict
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
            json_action_result_definition,  # type: JSONDict
            action_result_expectations,  # type: scenario.test.ActionResultExpectations
    ):  # type: (...) -> None
        if self.doexecute():
            self.debuglongtext("_checkactionresultdefinition(): json_action_result_definition = %s"
                               % json.dumps(json_action_result_definition, indent=2), max_lines=20)

        _type_desc = "action" if action_result_expectations.type == scenario.ActionResult.Type.ACTION else "expected result"  # type: str

        if self.RESULT("The action/result type is %s." % action_result_expectations.type):
            self.assertjson(
                json_action_result_definition, "type", type=str, value=str(action_result_expectations.type),
                evidence="Action/result type",
            )

        if self.RESULT("The %s description is '%s'." % (_type_desc, action_result_expectations.description)):
            self.assertjson(
                json_action_result_definition, "description", type=str, value=action_result_expectations.description,
                evidence="%s description" % _type_desc.capitalize(),
            )

        if not self.getexecstep(ExecScenario).doc_only:
            _json_searched_action_result_execution = {}  # type: JSONDict
            if self.doexecute():
                for _json_action_resut_execution in self.assertjson(json_action_result_definition, "executions", type=list):  # type: JSONDict
                    if _json_action_resut_execution not in self._scenario_tested_items[-1].action_result_executions:
                        _json_searched_action_result_execution = _json_action_resut_execution
                        break
                if not _json_searched_action_result_execution:
                    self.error("No %s execution in %s" % (_type_desc, json.dumps(json_action_result_definition, indent=2)))
                    self.fail("Could not check %s execution" % _type_desc)
            self._checkactionresultexecution(
                json_action_result_execution=_json_searched_action_result_execution,
                action_result_expectations=action_result_expectations,
            )
        else:
            if action_result_expectations.subscenario_expectations is not None:
                self.assertisempty(action_result_expectations.subscenario_expectations, "Unexpected list of subscenarios for a --doc-only execution")
                if self.RESULT("No sub-scenario has been executed."):
                    self.assertisempty(
                        self.assertjson(
                            json_action_result_definition, "executions", type=list,
                            evidence="Sub-scenario executions",
                        ),
                        evidence=False,
                    )

    def _checkactionresultexecution(
            self,
            json_action_result_execution,  # type: JSONDict
            action_result_expectations,  # type: scenario.test.ActionResultExpectations
    ):  # type: (...) -> None
        if self.doexecute():
            self.debuglongtext("_checkactionresultexecution(): json_action_result_execution = %s"
                               % json.dumps(json_action_result_execution, indent=2), max_lines=20)
        self._scenario_tested_items[-1].action_result_executions.append(json_action_result_execution)

        _type_desc = "action" if action_result_expectations.type == scenario.ActionResult.Type.ACTION else "expected result"  # type: str
        _type_math_desc = str(action_result_expectations.type).capitalize()  # type: str

        if self.RESULT("The %s execution times are bound in the current step execution time." % _type_desc):
            assert self._scenario_tested_items[-1].step_executions
            _step_execution = self._scenario_tested_items[-1].step_executions[-1]  # type: JSONDict
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
                evidence="%s start" % _type_math_desc,
            )  # type: str
            _action_result_execution_end = self.assertjson(
                json_action_result_execution, "time.end", type=str,
                evidence="%s end" % _type_math_desc,
            )  # type: str
            self.assertlessequal(
                _step_execution_start, _action_result_execution_start,
                evidence="Step.start <= %s.start" % _type_math_desc,
            )
            self.assertlessequal(
                _action_result_execution_start, _action_result_execution_end,
                evidence="%s.start <= %s.end" % (_type_math_desc, _type_math_desc),
            )
            self.assertlessequal(
                _action_result_execution_end, _step_execution_end,
                evidence="%s.end <= Step.end" % _type_math_desc,
            )

        if action_result_expectations.subscenario_expectations is not None:
            if self.RESULT("%d sub-scenario(s) has(have) been executed:" % len(action_result_expectations.subscenario_expectations)):
                self.assertjson(
                    json_action_result_execution, "subscenarios", type=list, len=len(action_result_expectations.subscenario_expectations),
                    evidence="Number of sub-scenarios",
                )
            for _subscenario_expectation_index in range(len(action_result_expectations.subscenario_expectations)):  # type: int
                self.RESULT("- Sub-scenario #%d:" % (_subscenario_expectation_index + 1))
                scenario.logging.pushindentation()
                self._scenario_tested_items.append(CheckJsonReportExpectations.ScenarioTestedItems())
                self._checkscenario(
                    json_scenario=self.testdatafromjson(json_action_result_execution, "subscenarios[%d]" % _subscenario_expectation_index, type=dict),
                    scenario_expectations=action_result_expectations.subscenario_expectations[_subscenario_expectation_index],
                )
                self._scenario_tested_items.pop()
                scenario.logging.popindentation()
