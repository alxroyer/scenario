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


class CheckFullJsonReport(JsonReportFileVerificationStep):

    def __init__(
            self,
            exec_step,  # type: ExecScenario
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
        self._json_ref = json.loads(self._json_path_ref.read_bytes())  # type: JSONDict

        #: JSON data read from the report file.
        self.json = {}  # type: JSONDict

    def step(self):  # type: (...) -> None
        self.STEP("Full scenario report")

        scenario.logging.resetindentation()

        # Read the reference JSON report file.
        if self.doexecute():
            self.debuglongtext("step(): _json_ref = %s" % json.dumps(self._json_ref, indent=2), max_lines=10)

        # Read the JSON report file.
        if self.ACTION("Read the JSON report file."):
            self.json = json.loads(self.report_path.read_bytes())
            self.debuglongtext(json.dumps(self.json, indent=2), max_lines=10)

        # Check the JSON data against reference.
        self.resetindentation()
        self._checkscenario(
            json_scenario=self.json,
            json_scenario_ref=self._json_ref,
        )

    def _checkscenario(
            self,
            json_scenario,  # type: JSONDict
            json_scenario_ref,  # type: JSONDict
    ):  # type: (...) -> None
        # Do not debug the ``json_scenario`` content for the top scenario.
        # It's usually been debugged previously.
        if self.doexecute() and ("$schema" not in json_scenario_ref):
            self.debuglongtext("_checkscenario(): json_scenario = %s" % json.dumps(json_scenario, indent=2), max_lines=20)
            self.debuglongtext("_checkscenario(): json_scenario_ref = %s" % json.dumps(json_scenario_ref, indent=2), max_lines=10)

        if "$schema" in json_scenario_ref:
            if self.RESULT("The JSON report gives the JSON schema it follows."):
                self.assertjson(
                    json_scenario, "$schema", ref=json_scenario_ref,
                    evidence="Schema reference",
                )

        if self.RESULT("The JSON report gives the expected test name: '%s'." % self._assertjsonref(json_scenario_ref, "name", type=str)):
            self.assertjson(
                json_scenario, "name", ref=json_scenario_ref,
                evidence="Test name",
            )

        _attributes_ref = self._assertjsonref(json_scenario_ref, "attributes", type=dict)  # type: JSONDict
        if self.RESULT("The JSON report gives %d scenario attribute(s):" % len(_attributes_ref)):
            self.assertjson(
                json_scenario, "attributes", type=dict, len=len(_attributes_ref),
                evidence="Number of scenario attributes",
            )
        for _attribute_name in _attributes_ref:
            if self.RESULT("- %s: %s" % (_attribute_name, _attributes_ref[_attribute_name])):
                self.assertjson(
                    json_scenario, "attributes.%s" % _attribute_name, ref=json_scenario_ref,
                    evidence="Attribute '%s'" % _attribute_name,
                )

        _step_definitions_ref = self._assertjsonref(json_scenario_ref, "steps", type=list)  # type: typing.List[JSONDict]
        if self.RESULT("The number of steps is %d%s" % (len(_step_definitions_ref), ":" if len(_step_definitions_ref) > 0 else "")):
            self.assertjson(
                json_scenario, "steps", type=list, len=len(_step_definitions_ref),
                evidence="Number of steps",
            )
        for _step_definition_index in range(len(_step_definitions_ref)):  # type: int
            self.RESULT("- Step #%d:" % (_step_definition_index + 1))
            scenario.logging.pushindentation()
            self._checkstepdefinition(
                json_step_definition=self.testdatafromjson(json_scenario, "steps[%d]" % _step_definition_index, type=dict),
                json_step_definition_ref=self._assertjsonref(json_scenario_ref, "steps[%d]" % _step_definition_index, type=dict),
            )
            scenario.logging.popindentation()

        if self.RESULT("The test status is '%s'." % self._assertjsonref(json_scenario_ref, "status", type=str)):
            self.assertjson(
                json_scenario, "status", ref=json_scenario_ref,
                evidence="Test status",
            )
        self._checkerrors(
            json_obj=json_scenario,
            json_obj_ref=json_scenario_ref,
            json_path="errors",
        )
        self._checkerrors(
            json_obj=json_scenario,
            json_obj_ref=json_scenario_ref,
            json_path="warnings",
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
                )  # type: JSONDict
                self.debuglongtext(json.dumps(_stats, indent=2), max_lines=20)

            for _stat_type in ("steps", "actions", "results"):  # type: str
                if self.RESULT("- %d %s have been executed out of %d" % (
                    self._assertjsonref(json_scenario_ref, "stats.%s.executed" % _stat_type, type=int),
                    _stat_type,
                    self._assertjsonref(json_scenario_ref, "stats.%s.total" % _stat_type, type=int)
                )):
                    self.assertjson(
                        json_scenario, "stats.%s.executed" % _stat_type, ref=json_scenario_ref,
                        evidence="Number of %s executed" % _stat_type,
                    )
                    self.assertjson(
                        json_scenario, "stats.%s.total" % _stat_type, ref=json_scenario_ref,
                        evidence="Total number of %s" % _stat_type,
                    )
        else:
            if self.RESULT("The report contains no statistics information."):
                self.assertnotin(
                    "stats", json_scenario,
                    evidence="Test statistics",
                )

    def _checkstepdefinition(
            self,
            json_step_definition,  # type: JSONDict
            json_step_definition_ref,  # type: JSONDict
    ):  # type: (...) -> None
        if self.doexecute():
            self.debuglongtext("_checkstepdefinition(): json_step_definition = %s" % json.dumps(json_step_definition, indent=2), max_lines=20)
            self.debuglongtext("_checkstepdefinition(): json_step_definition_ref = %s" % json.dumps(json_step_definition_ref, indent=2), max_lines=10)

        if self.RESULT("The step location is '%s'." % self._assertjsonref(json_step_definition_ref, "location", type=str)):
            self.assertjson(
                json_step_definition, "location", ref=json_step_definition_ref,
                evidence="Step location",
            )

        if self.RESULT("The step description is '%s'." % self._assertjsonref(json_step_definition_ref, "description", type=str)):
            self.assertjson(
                json_step_definition, "description", ref=json_step_definition_ref,
                evidence="Step description",
            )

        _executions_ref = self._assertjsonref(json_step_definition_ref, "executions", type=list)  # type: typing.List[JSONDict]
        if self.RESULT("The number of step executions is %d%s" % (len(_executions_ref), ":" if len(_executions_ref) > 0 else ".")):
            self.assertjson(
                json_step_definition, "executions", type=list, len=len(_executions_ref),
                evidence="Number of executions",
            )
        for _execution_index in range(len(_executions_ref)):  # type: int
            self.RESULT("- Step execution #%d:" % (_execution_index + 1))
            scenario.logging.pushindentation()
            self._checkstepexecution(
                json_step_execution=self.testdatafromjson(json_step_definition, "executions[%d]" % _execution_index, type=dict),
                json_step_execution_ref=self._assertjsonref(json_step_definition_ref, "executions[%d]" % _execution_index, type=dict),
            )
            scenario.logging.popindentation()

        _action_result_definitions_ref = self._assertjsonref(json_step_definition_ref, "actions-results", type=list)  # type: typing.List[JSONDict]
        if self.RESULT("The number of actions/results is %d%s" % (
                len(_action_result_definitions_ref),
                ":" if len(_action_result_definitions_ref) > 0 else "",
        )):
            self.assertjson(
                json_step_definition, "actions-results", type=list, len=len(_action_result_definitions_ref),
                evidence="Number of actions/results",
            )
        for _action_result_definition_index in range(len(_action_result_definitions_ref)):  # type: int
            self.RESULT("- Action/result #%d:" % (_action_result_definition_index + 1))
            scenario.logging.pushindentation()
            self._checkactionresultdefinition(
                json_action_result_definition=self.testdatafromjson(
                    json_step_definition, "actions-results[%d]" % _action_result_definition_index, type=dict,
                ),
                json_action_result_definition_ref=self._assertjsonref(
                    json_step_definition_ref, "actions-results[%d]" % _action_result_definition_index, type=dict,
                ),
            )
            scenario.logging.popindentation()

    def _checkstepexecution(
            self,
            json_step_execution,  # type: JSONDict
            json_step_execution_ref,  # type: JSONDict
    ):  # type: (...) -> None
        if self.doexecute():
            self.debuglongtext("_checkstepexecution(): json_step_execution = %s" % json.dumps(json_step_execution, indent=2), max_lines=20)
            self.debuglongtext("_checkstepexecution(): json_step_execution_ref = %s" % json.dumps(json_step_execution_ref, indent=2), max_lines=10)

        if self.RESULT("The step execution number is %d." % self._assertjsonref(json_step_execution_ref, "number")):
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
            json_path="errors",
        )
        self._checkerrors(
            json_obj=json_step_execution,
            json_obj_ref=json_step_execution_ref,
            json_path="warnings",
        )

    def _checkactionresultdefinition(
            self,
            json_action_result_definition,  # type: JSONDict
            json_action_result_definition_ref,  # type: JSONDict
    ):  # type: (...) -> None
        if self.doexecute():
            self.debuglongtext("_checkactionresultdefinition(): json_action_result_definition = %s"
                               % json.dumps(json_action_result_definition, indent=2), max_lines=20)
            self.debuglongtext("_checkactionresultdefinition(): json_action_result_definition_ref = %s"
                               % json.dumps(json_action_result_definition_ref, indent=2), max_lines=10)

        if self.RESULT("The action/result type is %s." % self._assertjsonref(json_action_result_definition_ref, "type", type=str)):
            self.assertjson(
                json_action_result_definition, "type", ref=json_action_result_definition_ref,
                evidence="Action/result type",
            )
        if self.RESULT("The action/result description is '%s'." % self._assertjsonref(json_action_result_definition_ref, "description", type=str)):
            self.assertjson(
                json_action_result_definition, "description", ref=json_action_result_definition_ref,
                evidence="Action/result description",
            )

        _executions_ref = self._assertjsonref(json_action_result_definition_ref, "executions")  # type: typing.List[JSONDict]
        if self.RESULT("The number of action/result executions is %d%s" % (len(_executions_ref), ":" if len(_executions_ref) > 0 else "")):
            self.assertjson(
                json_action_result_definition, "executions", type=list, len=len(_executions_ref),
                evidence="Number of executions",
            )
        for _execution_index in range(len(_executions_ref)):  # type: int
            self.RESULT("- Action/result execution #%d:" % (_execution_index + 1))
            scenario.logging.pushindentation()
            self._checkactionresultexecution(
                json_action_result_execution=self.testdatafromjson(json_action_result_definition, "executions[%d]" % _execution_index, type=dict),
                json_action_result_execution_ref=self._assertjsonref(json_action_result_definition_ref, "executions[%d]" % _execution_index, type=dict),
            )
            scenario.logging.popindentation()

    def _checkactionresultexecution(
            self,
            json_action_result_execution,  # type: JSONDict
            json_action_result_execution_ref,  # type: JSONDict
    ):  # type: (...) -> None
        if self.doexecute():
            self.debuglongtext("_checkactionresultexecution(): json_action_result_execution = %s"
                               % json.dumps(json_action_result_execution, indent=2), max_lines=20)
            self.debuglongtext("_checkactionresultexecution(): json_action_result_execution_ref = %s"
                               % json.dumps(json_action_result_execution_ref, indent=2), max_lines=10)

        self._checktimes(
            json_time=self.testdatafromjson(json_action_result_execution, "time", type=dict),
            json_time_ref=self._assertjsonref(json_action_result_execution_ref, "time", type=dict),
        )

        _evidence_ref = self._assertjsonref(json_action_result_execution_ref, "evidence", type=list)  # type: typing.List[str]
        if self.RESULT("The number of evidence items is %d%s" % (len(_evidence_ref), ":" if len(_evidence_ref) > 0 else ".")):
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
            if self.RESULT("- '%s'" % _evidence_item_ref):
                if _regex is not None:
                    self.assertregex(
                        _regex, self.assertjson(json_action_result_execution, "evidence[%d]" % _evidence_index, type=str),
                        evidence="Evidence",
                    )
                else:
                    self.assertjson(
                        json_action_result_execution, "evidence[%d]" % _evidence_index, type=str, value=_evidence_item_ref,
                        evidence="Evidence",
                    )
        scenario.logging.popindentation()

        self._checkerrors(
            json_obj=json_action_result_execution,
            json_obj_ref=json_action_result_execution_ref,
            json_path="errors",
        )
        self._checkerrors(
            json_obj=json_action_result_execution,
            json_obj_ref=json_action_result_execution_ref,
            json_path="warnings",
        )

        _json_subscenarios_ref = self._assertjsonref(json_action_result_execution_ref, "subscenarios", type=list)  # type: typing.List[JSONDict]
        if self.RESULT("The number of sub-scenarios is %d%s" % (len(_json_subscenarios_ref), ":" if len(_json_subscenarios_ref) > 0 else ":")):
            self.assertjson(
                json_action_result_execution, "subscenarios", type=list, len=len(_json_subscenarios_ref),
                evidence="Number of sub-scenarios",
            )
        for _subscenario_index in range(len(_json_subscenarios_ref)):  # type: int
            _json_subscenario_ref = _json_subscenarios_ref[_subscenario_index]  # type: JSONDict
            self.RESULT("- Sub-scenario #%d:" % (_subscenario_index + 1))
            scenario.logging.pushindentation()
            self._checkscenario(
                json_scenario=self.testdatafromjson(json_action_result_execution, "subscenarios[%d]" % _subscenario_index, type=dict),
                json_scenario_ref=_json_subscenario_ref,
            )
            scenario.logging.popindentation()

    def _checktimes(
            self,
            json_time,  # type: JSONDict
            json_time_ref,  # type: JSONDict
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
            json_obj,  # type: JSONDict
            json_obj_ref,  # type: JSONDict
            json_path,  # type: str
    ):  # type: (...) -> None
        _error_type = json_path[:-1]  # type: str

        _errors_ref = self._assertjsonref(json_obj_ref, json_path, type=list)  # type: typing.List[JSONDict]
        if self.RESULT("%d %s(s) are registered:" % (len(_errors_ref), _error_type)):
            self.assertjson(
                json_obj, json_path, type=list, len=len(_errors_ref),
                evidence="Number of %ss" % _error_type,
            )
        for _error_index in range(len(_errors_ref)):  # type: int
            self.RESULT("- %s #%d" % (_error_type.capitalize(), _error_index + 1))
            _json_path_error = "%s[%d]" % (json_path, _error_index)  # type: str
            scenario.logging.pushindentation()

            if self.RESULT("Error type is %s." % repr(self._assertjsonref(_errors_ref[_error_index], "type"))):
                self.assertjson(
                    json_obj, _json_path_error + ".type", ref=json_obj_ref,
                    evidence="Error type",
                )
            if self._assertjsonref(_errors_ref[_error_index], "type") == "known-issue":
                if self.RESULT("Issue id is %s." % repr(self._assertjsonref(_errors_ref[_error_index], "id"))):
                    self.assertjson(
                        json_obj, _json_path_error + ".id", ref=json_obj_ref,
                        evidence="Issue id",
                    )
            if self.RESULT("%s message is %s." % (_error_type.capitalize(), repr(self._assertjsonref(_errors_ref[_error_index], "message")))):
                self.assertjson(
                    json_obj, _json_path_error + ".message", ref=json_obj_ref,
                    evidence="%s message" % _error_type.capitalize(),
                )
            if self.RESULT("%s location is %s." % (_error_type.capitalize(), repr(self._assertjsonref(_errors_ref[_error_index], "location")))):
                self.assertjson(
                    json_obj, _json_path_error + ".location", ref=json_obj_ref,
                    evidence="%s location" % _error_type.capitalize(),
                )

            scenario.logging.popindentation()

    def _assertjsonref(
            self,
            json_ref,  # type: JSONDict
            json_path,  # type: typing.Optional[str]
            type=None,  # type: type  # noqa  ## Shadows built-in name 'type'
            value=None,  # type: typing.Union[int, str]
    ):  # type: (...) -> typing.Any
        """
        .. note:: As it makes the API convenient, we deliberately shadow the built-in with the ``type`` parameter.
        """
        return self.assertjson(
            json_ref, json_path=json_path, type=type, value=value,
            err="Invalid JSON ref '%s': '%s...', error with path '%s'" % (
                self._json_path_ref,
                scenario.assertionhelpers.saferepr(json_ref, max_length=50),
                json_path,
            ),
            evidence=False,
        )
