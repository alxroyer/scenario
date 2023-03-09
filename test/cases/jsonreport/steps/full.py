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

import json
import typing

import scenario
import scenario.test
import scenario.text
if typing.TYPE_CHECKING:
    from scenario.typing import JsonDictType

from jsonreport.steps.reportfile import JsonReportFileVerificationStep  # `JsonReportFileVerificationStep` used for inheritance.
if typing.TYPE_CHECKING:
    from scenarioexecution.steps.execution import ExecScenario as _ExecScenarioType


class CheckFullJsonReport(JsonReportFileVerificationStep):

    def __init__(
            self,
            exec_step,  # type: _ExecScenarioType
    ):  # type: (...) -> None
        JsonReportFileVerificationStep.__init__(self, exec_step)

        # Read the reference JSON report file.
        assert len(exec_step.scenario_paths) == 1
        self._json_path_ref = scenario.test.paths.datapath(
            exec_step.scenario_paths[0].name.replace(
                ".py",
                ".doc-only.json" if exec_step.doc_only else ".executed.json"
            ),
        )  # type: scenario.Path
        self.assertisfile(self._json_path_ref)
        self._json_ref = json.loads(self._json_path_ref.read_bytes())  # type: JsonDictType

        #: JSON data read from the report file.
        self.json = {}  # type: JsonDictType

    def step(self):  # type: (...) -> None
        self.STEP("Full scenario report")

        scenario.logging.resetindentation()

        # Read the reference JSON report file.
        if self.doexecute():
            self.debug("step(): _json_ref = %s", scenario.debug.jsondump(self._json_ref, indent=2),
                       extra=self.longtext(max_lines=10))

        # Read the JSON report file.
        if self.ACTION("Read the JSON report file."):
            self.json = json.loads(self.report_path.read_bytes())
            self.debug("%s", scenario.debug.jsondump(self.json, indent=2),
                       extra=self.longtext(max_lines=10))

        # Check the JSON data against reference.
        self.resetindentation()
        self._checkscenario(
            json_scenario=self.json,
            json_scenario_ref=self._json_ref,
        )

    def _checkscenario(
            self,
            json_scenario,  # type: JsonDictType
            json_scenario_ref,  # type: JsonDictType
    ):  # type: (...) -> None
        # Do not debug the ``json_scenario`` content for the top scenario.
        # It's usually been debugged previously.
        if self.doexecute() and ("$schema" not in json_scenario_ref):
            self.debug("_checkscenario(): json_scenario = %s", scenario.debug.jsondump(json_scenario, indent=2),
                       extra=self.longtext(max_lines=20))
            self.debug("_checkscenario(): json_scenario_ref = %s", scenario.debug.jsondump(json_scenario_ref, indent=2),
                       extra=self.longtext(max_lines=10))

        if "$schema" in json_scenario_ref:
            if self.RESULT("The JSON report gives the JSON schema it follows."):
                self.assertjson(
                    json_scenario, "$schema", ref=json_scenario_ref,
                    evidence="Schema reference",
                )

        if self.RESULT(f"The JSON report gives the expected test name: '{self._assertjsonref(json_scenario_ref, 'name', type=str)}'."):
            self.assertjson(
                json_scenario, "name", ref=json_scenario_ref,
                evidence="Test name",
            )

        _attributes_ref = self._assertjsonref(json_scenario_ref, "attributes", type=dict)  # type: JsonDictType
        _attributes_txt = scenario.text.Countable("attribute", _attributes_ref)  # type: scenario.text.Countable
        if self.RESULT(f"The JSON report gives {len(_attributes_txt)} scenario {_attributes_txt}{_attributes_txt.ifany(':', '.')}"):
            self.assertjson(
                json_scenario, "attributes", type=dict, len=len(_attributes_ref),
                evidence="Number of scenario attributes",
            )
        for _attribute_name in _attributes_ref:
            if self.RESULT(f"- {_attribute_name}: {_attributes_ref[_attribute_name]!r}"):
                self.assertjson(
                    json_scenario, f"attributes.{_attribute_name}", ref=json_scenario_ref,
                    evidence=f"Attribute '{_attribute_name}'",
                )

        _step_definitions_ref = self._assertjsonref(json_scenario_ref, "steps", type=list)  # type: typing.List[JsonDictType]
        _steps_txt = scenario.text.Countable("step", _step_definitions_ref)  # type: scenario.text.Countable
        if self.RESULT(f"The number of steps is {len(_steps_txt)}{_steps_txt.ifany(':', '.')}"):
            self.assertjson(
                json_scenario, "steps", type=list, len=len(_step_definitions_ref),
                evidence="Number of steps",
            )
        for _step_definition_index in range(len(_step_definitions_ref)):  # type: int
            self.RESULT(f"- Step #{_step_definition_index + 1}:")
            scenario.logging.pushindentation()
            self._checkstepdefinition(
                json_step_definition=self.testdatafromjson(json_scenario, f"steps[{_step_definition_index}]", type=dict),
                json_step_definition_ref=self._assertjsonref(json_scenario_ref, f"steps[{_step_definition_index}]", type=dict),
            )
            scenario.logging.popindentation()

        if self.RESULT(f"The test status is '{self._assertjsonref(json_scenario_ref, 'status', type=str)}'."):
            self.assertjson(
                json_scenario, "status", ref=json_scenario_ref,
                evidence="Test status",
            )
        self._checkerrors(
            json_obj=json_scenario,
            json_obj_ref=json_scenario_ref,
            jsonpath="errors",
        )
        self._checkerrors(
            json_obj=json_scenario,
            json_obj_ref=json_scenario_ref,
            jsonpath="warnings",
        )

        self._checktimes(
            json_time=self.testdatafromjson(json_scenario, "time", type=dict),
            json_time_ref=self._assertjsonref(json_scenario_ref, "time", type=dict),
        )

        if "stats" in json_scenario_ref:
            if self.RESULT("The report contains statistics information:"):
                _stats = self.assertjson(
                    json_scenario, "stats", type=dict,
                    evidence="Test statistics",
                )  # type: JsonDictType
                self.debug("%s", scenario.debug.jsondump(_stats, indent=2),
                           extra=self.longtext(max_lines=20))

            for _stat_path in ("steps", "actions", "results"):  # type: str
                _executed_stat_types_txt = scenario.text.Countable(
                    _stat_path[:-1],
                    self._assertjsonref(json_scenario_ref, f"stats.{_stat_path}.executed", type=int),
                )  # type: scenario.text.Countable
                if self.RESULT(f"- {len(_executed_stat_types_txt)} {_executed_stat_types_txt} {_executed_stat_types_txt.have} been executed "
                               f"out of {self._assertjsonref(json_scenario_ref, f'stats.{_stat_path}.total', type=int)}"):
                    self.assertjson(
                        json_scenario, f"stats.{_stat_path}.executed", ref=json_scenario_ref,
                        evidence=f"Number of {_executed_stat_types_txt.plural} executed",
                    )
                    self.assertjson(
                        json_scenario, f"stats.{_stat_path}.total", ref=json_scenario_ref,
                        evidence=f"Total number of {_executed_stat_types_txt.plural}",
                    )
        else:
            if self.RESULT("The report contains no statistics information."):
                self.assertnotin(
                    "stats", json_scenario,
                    evidence="Test statistics",
                )

    def _checkstepdefinition(
            self,
            json_step_definition,  # type: JsonDictType
            json_step_definition_ref,  # type: JsonDictType
    ):  # type: (...) -> None
        if self.doexecute():
            self.debug("_checkstepdefinition(): json_step_definition = %s", scenario.debug.jsondump(json_step_definition, indent=2),
                       extra=self.longtext(max_lines=20))
            self.debug("_checkstepdefinition(): json_step_definition_ref = %s", scenario.debug.jsondump(json_step_definition_ref, indent=2),
                       extra=self.longtext(max_lines=10))

        if self.RESULT(f"The step location is '{self._assertjsonref(json_step_definition_ref, 'location', type=str)}'."):
            self.assertjson(
                json_step_definition, "location", ref=json_step_definition_ref,
                evidence="Step location",
            )

        if self.RESULT(f"The step description is {self._assertjsonref(json_step_definition_ref, 'description', type=str)!r}."):
            self.assertjson(
                json_step_definition, "description", ref=json_step_definition_ref,
                evidence="Step description",
            )

        _executions_ref = self._assertjsonref(json_step_definition_ref, "executions", type=list)  # type: typing.List[JsonDictType]
        _executions_txt = scenario.text.Countable("execution", _executions_ref)  # type: scenario.text.Countable
        if self.RESULT(f"The number of step executions is {len(_executions_txt)}{_executions_txt.ifany(':', '.')}"):
            self.assertjson(
                json_step_definition, "executions", type=list, len=len(_executions_ref),
                evidence="Number of executions",
            )
        for _execution_index in range(len(_executions_ref)):  # type: int
            self.RESULT(f"- Step execution #{_execution_index + 1}:")
            scenario.logging.pushindentation()
            self._checkstepexecution(
                json_step_execution=self.testdatafromjson(json_step_definition, f"executions[{_execution_index}]", type=dict),
                json_step_execution_ref=self._assertjsonref(json_step_definition_ref, f"executions[{_execution_index}]", type=dict),
            )
            scenario.logging.popindentation()

        _action_result_definitions_ref = self._assertjsonref(json_step_definition_ref, "actions-results", type=list)  # type: typing.List[JsonDictType]
        _actions_results_txt = scenario.text.Countable("action/result", _action_result_definitions_ref)  # type: scenario.text.Countable
        if self.RESULT(f"The number of actions/results is {len(_actions_results_txt)}{_actions_results_txt.ifany(':', '.')}"):
            self.assertjson(
                json_step_definition, "actions-results", type=list, len=len(_action_result_definitions_ref),
                evidence="Number of actions/results",
            )
        for _action_result_definition_index in range(len(_action_result_definitions_ref)):  # type: int
            self.RESULT(f"- Action/result #{_action_result_definition_index + 1}:")
            scenario.logging.pushindentation()
            self._checkactionresultdefinition(
                json_action_result_definition=self.testdatafromjson(
                    json_step_definition, f"actions-results[{_action_result_definition_index}]", type=dict,
                ),
                json_action_result_definition_ref=self._assertjsonref(
                    json_step_definition_ref, f"actions-results[{_action_result_definition_index}]", type=dict,
                ),
            )
            scenario.logging.popindentation()

    def _checkstepexecution(
            self,
            json_step_execution,  # type: JsonDictType
            json_step_execution_ref,  # type: JsonDictType
    ):  # type: (...) -> None
        if self.doexecute():
            self.debug("_checkstepexecution(): json_step_execution = %s", scenario.debug.jsondump(json_step_execution, indent=2),
                       extra=self.longtext(max_lines=20))
            self.debug("_checkstepexecution(): json_step_execution_ref = %s", scenario.debug.jsondump(json_step_execution_ref, indent=2),
                       extra=self.longtext(max_lines=10))

        if self.RESULT(f"The step execution number is {self._assertjsonref(json_step_execution_ref, 'number')}."):
            self.assertjson(
                json_step_execution, "number", type=int, ref=json_step_execution_ref,
                evidence="Step execution number",
            )

        self._checktimes(
            json_time=self.testdatafromjson(json_step_execution, "time", type=dict),
            json_time_ref=self._assertjsonref(json_step_execution_ref, "time", type=dict),
        )

        self._checkerrors(
            json_obj=json_step_execution,
            json_obj_ref=json_step_execution_ref,
            jsonpath="errors",
        )
        self._checkerrors(
            json_obj=json_step_execution,
            json_obj_ref=json_step_execution_ref,
            jsonpath="warnings",
        )

    def _checkactionresultdefinition(
            self,
            json_action_result_definition,  # type: JsonDictType
            json_action_result_definition_ref,  # type: JsonDictType
    ):  # type: (...) -> None
        if self.doexecute():
            self.debug("_checkactionresultdefinition(): json_action_result_definition = %s",
                       scenario.debug.jsondump(json_action_result_definition, indent=2),
                       extra=self.longtext(max_lines=20))
            self.debug("_checkactionresultdefinition(): json_action_result_definition_ref = %s",
                       scenario.debug.jsondump(json_action_result_definition_ref, indent=2),
                       extra=self.longtext(max_lines=10))

        if self.RESULT(f"The action/result type is {self._assertjsonref(json_action_result_definition_ref, 'type', type=str)}."):
            self.assertjson(
                json_action_result_definition, "type", ref=json_action_result_definition_ref,
                evidence="Action/result type",
            )
        if self.RESULT(f"The action/result description is {self._assertjsonref(json_action_result_definition_ref, 'description', type=str)!r}."):
            self.assertjson(
                json_action_result_definition, "description", ref=json_action_result_definition_ref,
                evidence="Action/result description",
            )

        _executions_ref = self._assertjsonref(json_action_result_definition_ref, "executions")  # type: typing.List[JsonDictType]
        _executions_txt = scenario.text.Countable("execution", _executions_ref)  # type: scenario.text.Countable
        if self.RESULT(f"The number of action/result executions is {len(_executions_txt)}{_executions_txt.ifany(':', '.')}"):
            self.assertjson(
                json_action_result_definition, "executions", type=list, len=len(_executions_ref),
                evidence="Number of executions",
            )
        for _execution_index in range(len(_executions_ref)):  # type: int
            self.RESULT(f"- Action/result execution #{_execution_index + 1}:")
            scenario.logging.pushindentation()
            self._checkactionresultexecution(
                json_action_result_execution=self.testdatafromjson(json_action_result_definition, f"executions[{_execution_index}]", type=dict),
                json_action_result_execution_ref=self._assertjsonref(json_action_result_definition_ref, f"executions[{_execution_index}]", type=dict),
            )
            scenario.logging.popindentation()

    def _checkactionresultexecution(
            self,
            json_action_result_execution,  # type: JsonDictType
            json_action_result_execution_ref,  # type: JsonDictType
    ):  # type: (...) -> None
        if self.doexecute():
            self.debug("_checkactionresultexecution(): json_action_result_execution = %s",
                       scenario.debug.jsondump(json_action_result_execution, indent=2),
                       extra=self.longtext(max_lines=20))
            self.debug("_checkactionresultexecution(): json_action_result_execution_ref = %s",
                       scenario.debug.jsondump(json_action_result_execution_ref, indent=2),
                       extra=self.longtext(max_lines=10))

        self._checktimes(
            json_time=self.testdatafromjson(json_action_result_execution, "time", type=dict),
            json_time_ref=self._assertjsonref(json_action_result_execution_ref, "time", type=dict),
        )

        _evidence_ref = self._assertjsonref(json_action_result_execution_ref, "evidence", type=list)  # type: typing.List[str]
        _evidence_items_txt = scenario.text.Countable("evidence item", _evidence_ref)  # type: scenario.text.Countable
        if self.RESULT(f"The number of evidence items is {len(_evidence_items_txt)}{_evidence_items_txt.ifany(':', '.')}"):
            self.assertjson(
                json_action_result_execution, "evidence", type=list, len=len(_evidence_ref),
                evidence="Number of evidence items",
            )
        scenario.logging.pushindentation()
        for _evidence_index in range(len(_evidence_ref)):  # type: int
            _evidence_item_ref = _evidence_ref[_evidence_index]  # type: str
            _regex = None  # type: typing.Optional[str]
            if _evidence_item_ref.startswith("<regex>") and _evidence_item_ref.endswith("</regex>"):
                _regex = _evidence_item_ref[len("<regex>"):-len("</regex>")]
            if self.RESULT(f"- {_evidence_item_ref!r}"):
                if _regex is not None:
                    self.assertregex(
                        _regex, self.assertjson(json_action_result_execution, f"evidence[{_evidence_index}]", type=str),
                        evidence="Evidence",
                    )
                else:
                    self.assertjson(
                        json_action_result_execution, f"evidence[{_evidence_index}]", type=str, value=_evidence_item_ref,
                        evidence="Evidence",
                    )
        scenario.logging.popindentation()

        self._checkerrors(
            json_obj=json_action_result_execution,
            json_obj_ref=json_action_result_execution_ref,
            jsonpath="errors",
        )
        self._checkerrors(
            json_obj=json_action_result_execution,
            json_obj_ref=json_action_result_execution_ref,
            jsonpath="warnings",
        )

        _json_subscenarios_ref = self._assertjsonref(json_action_result_execution_ref, "subscenarios", type=list)  # type: typing.List[JsonDictType]
        _subscenarios_txt = scenario.text.Countable("subscenario", _json_subscenarios_ref)  # type: scenario.text.Countable
        if self.RESULT(f"The number of subscenarios is {len(_subscenarios_txt)}{_subscenarios_txt.ifany(':', '.')}"):
            self.assertjson(
                json_action_result_execution, "subscenarios", type=list, len=len(_json_subscenarios_ref),
                evidence="Number of subscenarios",
            )
        for _subscenario_index in range(len(_json_subscenarios_ref)):  # type: int
            _json_subscenario_ref = _json_subscenarios_ref[_subscenario_index]  # type: JsonDictType
            self.RESULT(f"- Subscenario #{_subscenario_index + 1}:")
            scenario.logging.pushindentation()
            self._checkscenario(
                json_scenario=self.testdatafromjson(json_action_result_execution, f"subscenarios[{_subscenario_index}]", type=dict),
                json_scenario_ref=_json_subscenario_ref,
            )
            scenario.logging.popindentation()

    def _checktimes(
            self,
            json_time,  # type: JsonDictType
            json_time_ref,  # type: JsonDictType
    ):  # type: (...) -> None
        _start_ref = self.assertjson(json_time_ref, "start")  # type: typing.Optional[str]
        if _start_ref is None:
            if self.RESULT("Start time is not set."):
                self.assertjson(
                    json_time, "start", type=None, value=None,
                    evidence="Start time",
                )
        else:
            if self.RESULT("Start time is set."):
                self.assertjson(
                    json_time, "start", type=str,
                    evidence="Start time",
                )

        _end_ref = self.assertjson(json_time_ref, "end")  # type: typing.Optional[str]
        if _end_ref is None:
            if self.RESULT("End time is not set."):
                self.assertjson(
                    json_time, "end", type=None, value=None,
                    evidence="End time",
                )
        else:
            if self.RESULT("The end time is set."):
                self.assertjson(
                    json_time, "end", type=str,
                    evidence="End time",
                )

        _elapsed_ref = self.assertjson(json_time_ref, "end")  # type: typing.Optional[float]
        if _elapsed_ref is None:
            if self.RESULT("Elapsed time is not set."):
                self.assertjson(
                    json_time, "elapsed", type=None, value=None,
                    evidence="Elapsed",
                )
        else:
            if self.RESULT("Elapsed time is set."):
                self.assertjson(
                    json_time, "elapsed", type=float,
                    evidence="Elapsed",
                )

    def _checkerrors(
            self,
            json_obj,  # type: JsonDictType
            json_obj_ref,  # type: JsonDictType
            jsonpath,  # type: str
    ):  # type: (...) -> None
        _errors_ref = self._assertjsonref(json_obj_ref, jsonpath, type=list)  # type: typing.List[JsonDictType]
        assert jsonpath.endswith("s")
        _errors_txt = scenario.text.Countable(jsonpath[:-1], _errors_ref)  # type: scenario.text.Countable
        if self.RESULT(f"{len(_errors_txt)} {_errors_txt} {_errors_txt.are} registered{_errors_txt.ifany(':', '.')}"):
            self.assertjson(
                json_obj, jsonpath, type=list, len=len(_errors_ref),
                evidence=f"Number of {_errors_txt.plural}",
            )
        for _error_index in range(len(_errors_ref)):  # type: int
            self.RESULT(f"- {_errors_txt.singular.capitalize()} #{_error_index + 1}")
            _jsonpath_error = f"{jsonpath}[{_error_index}]"  # type: str
            scenario.logging.pushindentation()

            if self.RESULT(f"Error type is {self._assertjsonref(_errors_ref[_error_index], 'type')!r}."):
                self.assertjson(
                    json_obj, f"{_jsonpath_error}.type", ref=json_obj_ref,
                    evidence="Error type",
                )
            if self._assertjsonref(_errors_ref[_error_index], "type") == "known-issue":
                if self.RESULT(f"Issue id is {self._assertjsonref(_errors_ref[_error_index], 'id')!r}."):
                    self.assertjson(
                        json_obj, f"{_jsonpath_error}.id", ref=json_obj_ref,
                        evidence="Issue id",
                    )
            if self.RESULT(f"{_errors_txt.singular.capitalize()} message is {self._assertjsonref(_errors_ref[_error_index], 'message')!r}."):
                self.assertjson(
                    json_obj, f"{_jsonpath_error}.message", ref=json_obj_ref,
                    evidence=f"{_errors_txt.singular.capitalize()} message",
                )
            if self.RESULT(f"{_errors_txt.singular.capitalize()} location is {self._assertjsonref(_errors_ref[_error_index], 'location')!r}."):
                self.assertjson(
                    json_obj, f"{_jsonpath_error}.location", ref=json_obj_ref,
                    evidence=f"{_errors_txt.singular.capitalize()} location",
                )

            scenario.logging.popindentation()

    def _assertjsonref(
            self,
            json_ref,  # type: JsonDictType
            jsonpath,  # type: typing.Optional[str]
            type=None,  # type: type  # noqa  ## Shadows built-in name 'type'
            value=None,  # type: typing.Union[int, str]
    ):  # type: (...) -> typing.Any
        """
        .. note:: As it makes the API convenient, we deliberately shadow the built-in with the ``type`` parameter.
        """
        return self.assertjson(
            json_ref, jsonpath=jsonpath, type=type, value=value,
            err=scenario.debug.FmtAndArgs(
                "Invalid JSON ref '%s': error with JSONPath '%s' from %s",
                self._json_path_ref, jsonpath, scenario.debug.saferepr(json_ref, max_length=50),
            ),
            evidence=False,
        )
