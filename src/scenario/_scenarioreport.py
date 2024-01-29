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

"""
Scenario reports.
"""

import typing

if True:
    from ._fastpath import FAST_PATH as _FAST_PATH  # `FAST_PATH` imported once for performance concerns.
    from ._logger import Logger as _LoggerImpl  # `Logger` used for inheritance.
    from ._path import Path as _PathImpl  # `Path` imported once for performance concerns.
    from ._scenariodefinition import ScenarioDefinition as _ScenarioDefinitionImpl  # `ScenarioDefinition` imported once for performance concerns.
    from ._stepdefinition import StepDefinition as _StepDefinitionImpl  # `StepDefinition` imported once for performance concerns.
if typing.TYPE_CHECKING:
    from ._actionresultdefinition import ActionResultDefinition as _ActionResultDefinitionType
    from ._jsondictutils import JsonDictType as _JsonDictType
    from ._path import AnyPathType as _AnyPathType
    from ._path import Path as _PathType
    from ._reqref import ReqRef as _ReqRefType
    from ._reqverifier import ReqVerifier as _ReqVerifierType
    from ._scenariodefinition import ScenarioDefinition as _ScenarioDefinitionType
    from ._stepdefinition import StepDefinition as _StepDefinitionType


class ScenarioReport(_LoggerImpl):
    """
    Scenario report generator.

    Instantiated once with the :data:`SCENARIO_REPORT` singleton.
    """

    #: JSON schema subpath from :attr:`._pkginfo.PackageInfo.repo_url`, for requirement database files.
    JSON_SCHEMA_SUBPATH = "schemas/scenario-report.schema.json"  # type: str

    def __init__(self):  # type: (...) -> None
        """
        Configures logging for the :class:`ScenarioReport` class.
        """
        from ._debugclasses import DebugClass

        _LoggerImpl.__init__(self, log_class=DebugClass.SCENARIO_REPORT)

        #: JSON / YAML report path being written or read.
        self._report_path = _PathImpl()  # type: _PathType

        #: ``True`` to feed automatically the requirement database with verified requirement references.
        self._feed_req_db = False  # type: bool

    def writejsonreport(
            self,
            scenario_definition,  # type: _ScenarioDefinitionType
            report_path,  # type: _AnyPathType
    ):  # type: (...) -> bool
        """
        Deprecated.
        Use :meth:`writescenarioreport()` instead.
        """
        self.warning(f"ScenarioReport.writejsonreport() deprecated, please use ScenarioReport.writescenarioreport() instead")
        try:
            self.writescenarioreport(
                scenario_definition,
                report_path,
            )
            return True
        except Exception as _err:
            self.error(f"Could not write report '{self._report_path}': {_err}")
            self.logexceptiontraceback(_err)
            return False

    def writescenarioreport(
            self,
            scenario_definition,  # type: _ScenarioDefinitionType
            report_path,  # type: _AnyPathType
    ):  # type: (...) -> None
        """
        Generates the scenario report output file for the given scenario execution.

        :param scenario_definition: Scenario to generate the scenario report for.
        :param report_path: Path to write the scenario report into.
        """
        from ._jsondictutils import JsonDict

        try:
            self.resetindentation()
            self.debug("Writing scenario report to '%s'", report_path)

            # Build the JSON content.
            self._report_path = _PathImpl(report_path)
            _json = self._scenario2json(scenario_definition, is_main=True)  # type: _JsonDictType

            # Write the report file.
            JsonDict.writefile(
                schema_subpath=ScenarioReport.JSON_SCHEMA_SUBPATH,
                content=_json,
                output_path=self._report_path,
            )
        finally:
            # Reset logging indentation and member variables.
            self.resetindentation()
            self._report_path = _PathImpl()

    def readjsonreport(
            self,
            report_path,  # type: _AnyPathType
            feed_req_db=False,  # type: bool
    ):  # type: (...) -> typing.Optional[_ScenarioDefinitionType]
        """
        Deprecated.
        Use :meth:`readscenarioreport()` instead.
        """
        self.warning(f"ScenarioReport.readjsonreport() deprecated, please use ScenarioReport.readscenarioreport() instead")
        try:
            return self.readscenarioreport(
                report_path,
                feed_req_db=feed_req_db,
            )
        except Exception as _err:
            self.error(f"Could not read report '{self._report_path}': {_err}")
            self.logexceptiontraceback(_err)
            return None

    def readscenarioreport(
            self,
            report_path,  # type: _AnyPathType
            *,
            feed_req_db=False,  # type: bool
    ):  # type: (...) -> _ScenarioDefinitionType
        """
        Reads the scenario report file.

        :param report_path:
            Scenario report path to read.
        :param feed_req_db:
            ``True`` to feed automatically the requirement database with verified requirement references.
        :return:
            Scenario data read from the scenario report file.
        """
        from ._jsondictutils import JsonDict

        try:
            self.resetindentation()
            self.debug("Reading scenario report from '%s'", report_path)

            # Read the report file.
            self._report_path = _PathImpl(report_path)
            _json = JsonDict.readfile(self._report_path)  # type: _JsonDictType

            # Analyze the JSON content.
            self._feed_req_db = feed_req_db
            _scenario_definition = self._json2scenario(_json)  # type: _ScenarioDefinitionType

            return _scenario_definition
        finally:
            # Reset logging indentation and member variables.
            self.resetindentation()
            self._report_path = _PathImpl()
            self._feed_req_db = False

    def _scenario2json(
            self,
            scenario_definition,  # type: _ScenarioDefinitionType
            is_main,  # type: bool
    ):  # type: (...) -> _JsonDictType
        """
        Scenario report JSON generation.

        :param scenario_definition: Scenario to generate JSON content for.
        :param is_main: True for the main scenario, False otherwise.
        :return: JSON content.
        """
        from ._debugutils import jsondump
        from ._enumutils import isin
        from ._scenarioattributes import CoreScenarioAttributes
        from ._testerrors import TestError

        self.debug("Generating JSON content for scenario %r", scenario_definition)

        with self.pushindentation():
            # Build a JSON object.
            _json_scenario = {}  # type: _JsonDictType  # noqa  ## This dictionary creation sould be rewritten as a dictionary literal

            # Scenario name.
            _json_scenario["name"] = scenario_definition.name

            # Script path.
            _json_scenario["href"] = scenario_definition.script_path.relative_to(self._report_path.parent)

            # Attributes.
            _json_scenario["attributes"] = {}
            for _attribute_name in scenario_definition.getattributenames():  # type: str
                # Skip empty core attributes.
                if isin(_attribute_name, CoreScenarioAttributes) and (not scenario_definition.getattribute(_attribute_name)):
                    continue
                _json_scenario["attributes"][_attribute_name] = str(scenario_definition.getattribute(_attribute_name))

            # Requirements.
            self._reqverifier2json(scenario_definition, _json_scenario)

            # Steps.
            _json_scenario["steps"] = []
            for _step_definition in scenario_definition.steps:  # type: _StepDefinitionType
                _json_scenario["steps"].append(self._step2json(_step_definition))

            if scenario_definition.execution:
                # Status & errors.
                _json_scenario["status"] = str(scenario_definition.execution.status)

                _json_scenario["errors"] = []
                for _error in scenario_definition.execution.errors:  # type: TestError
                    _json_scenario["errors"].append(_error.tojson())

                _json_scenario["warnings"] = []
                for _warning in scenario_definition.execution.warnings:  # type: TestError
                    _json_scenario["warnings"].append(_warning.tojson())

                # Time & statistics.
                _json_scenario["time"] = scenario_definition.execution.time.tojson()

                if is_main:
                    _json_scenario["stats"] = {
                        "steps": scenario_definition.execution.step_stats.tojson(),
                        "actions": scenario_definition.execution.action_stats.tojson(),
                        "results": scenario_definition.execution.result_stats.tojson(),
                    }

        self.debug("JSON content generated for scenario %r: %s", scenario_definition.name, jsondump(_json_scenario, indent=2),
                   extra={self.Extra.LONG_TEXT_MAX_LINES: 20})
        return _json_scenario

    def _json2scenario(
            self,
            json_scenario,  # type: _JsonDictType
    ):  # type: (...) -> _ScenarioDefinitionType
        """
        Scenario data reading from JSON content.

        :param json_scenario: Scenario JSON content to read.
        :return: Scenario data.
        """
        from ._debugutils import jsondump
        from ._scenarioexecution import ScenarioExecution
        from ._stats import TimeStats
        from ._testerrors import TestError

        self.debug("Reading scenario from JSON: %s", jsondump(json_scenario, indent=2),
                   extra={self.Extra.LONG_TEXT_MAX_LINES: 20})

        with self.pushindentation():
            # Create the scenario definition instance.
            _scenario_definition = _ScenarioDefinitionImpl()  # type: _ScenarioDefinitionType

            # Scenario name.
            _scenario_definition.name = json_scenario["name"]
            self.debug("Name: %r", _scenario_definition.name)

            # Script path.
            _scenario_definition.script_path = _PathImpl(json_scenario["href"], relative_to=self._report_path.parent)
            self.debug("Script path: '%s'", _scenario_definition.script_path)

            # Attributes.
            for _attribute_name in json_scenario["attributes"]:  # type: str
                _scenario_definition.setattribute(_attribute_name, json_scenario["attributes"][_attribute_name])

            # Requirements.
            self._json2reqverifier(json_scenario, _scenario_definition)

            # Steps.
            for _json_step_definition in json_scenario["steps"]:  # type: _JsonDictType
                _step_definition = self._json2step(_json_step_definition)  # type: _StepDefinitionType
                _scenario_definition.addstep(_step_definition)

            # Status & errors.
            _scenario_definition.execution = ScenarioExecution(_scenario_definition)
            for _json_error in json_scenario["errors"]:  # type: _JsonDictType
                _scenario_definition.execution.errors.append(TestError.fromjson(_json_error))
                self.debug("Error: %s", _scenario_definition.execution.errors[-1])
            self.debug("Errors: %d", len(_scenario_definition.execution.errors))

            for _json_warning in json_scenario["warnings"]:  # type: _JsonDictType
                _scenario_definition.execution.warnings.append(TestError.fromjson(_json_warning))
                self.debug("Warning: %s", _scenario_definition.execution.warnings[-1])
            self.debug("Warnings: %d", len(_scenario_definition.execution.warnings))

            # Time & statistics.
            _scenario_definition.execution.time = TimeStats.fromjson(json_scenario["time"])
            self.debug("Time statistics: %s", _scenario_definition.execution.time)

        return _scenario_definition

    def _step2json(
            self,
            step_definition,  # type: _StepDefinitionType
    ):  # type: (...) -> _JsonDictType
        """
        Generates JSON content for a step.

        :param step_definition: Step definition (with execution) to generate JSON content for.
        :return: JSON content.
        """
        from ._debugutils import jsondump
        from ._stepexecution import StepExecution
        from ._stepsection import StepSectionDescription
        from ._testerrors import TestError

        self.debug("Generating JSON content for %r", step_definition)

        with self.pushindentation():
            _json_step_definition = {
                "location": step_definition.location.tolongstring(),
                "description": step_definition.description,
            }  # type: _JsonDictType

            # Do not set 'reqs', 'actions-results' and 'executions' lists for step sections.
            if not isinstance(step_definition, StepSectionDescription):
                # Requirements.
                self._reqverifier2json(step_definition, _json_step_definition)

                # Actions / results.
                _json_step_definition["actions-results"] = []
                for _action_result_definition in step_definition.actions_results:  # type: _ActionResultDefinitionType
                    _json_step_definition["actions-results"].append(self._actionresult2json(_action_result_definition))

                # Executions.
                _json_step_definition["executions"] = []
                for _step_execution in step_definition.executions:  # type: StepExecution
                    _json_step_execution = {
                        "number": _step_execution.number,
                        "time": _step_execution.time.tojson(),
                        "errors": [],
                        "warnings": [],
                    }  # type: _JsonDictType

                    for _error in _step_execution.errors:  # type: TestError
                        _json_step_execution["errors"].append(_error.tojson())

                    for _warning in _step_execution.warnings:  # type: TestError
                        _json_step_execution["warnings"].append(_warning.tojson())

                    _json_step_definition["executions"].append(_json_step_execution)

        self.debug("JSON content generated for %r: %s", step_definition, jsondump(_json_step_definition, indent=2),
                   extra={self.Extra.LONG_TEXT_MAX_LINES: 10})
        return _json_step_definition

    def _json2step(
            self,
            json_step_definition,  # type: _JsonDictType
    ):  # type: (...) -> _StepDefinitionType
        """
        Step reading from JSON content.

        :param json_step_definition: Step definition JSON content to read.
        :return: :class:`._stepdefinition.StepDefinition` data.
        """
        from ._debugutils import jsondump
        from ._stats import TimeStats
        from ._stepexecution import StepExecution
        from ._stepsection import StepSectionDescription
        from ._testerrors import TestError

        self.debug("Reading step instance from JSON: %s", jsondump(json_step_definition, indent=2),
                   extra={self.Extra.LONG_TEXT_MAX_LINES: 10})

        with self.pushindentation():
            _step_definition = _StepDefinitionImpl()  # type: _StepDefinitionType

            _step_definition.location = _FAST_PATH.code_location.fromlongstring(json_step_definition["location"])
            self.debug("Location: %s", _step_definition.location.tolongstring())

            _step_definition.description = json_step_definition["description"]
            self.debug("Description: %r", _step_definition.description)

            if ("executions" not in json_step_definition) or ("actions-results" not in json_step_definition):
                # Missing executions and/or actions/results.
                # Replace the general `StepDefinition` instance created above by a `StepSection` one.
                assert _step_definition.description is not None
                _step_definition = StepSectionDescription(_step_definition.description)
            else:
                # Requirements.
                self._json2reqverifier(json_step_definition, _step_definition)

                # Actions / results.
                for _json_action_result_definition in json_step_definition["actions-results"]:  # type: _JsonDictType
                    _action_result_definition = self._json2actionresult(_json_action_result_definition)  # type: _ActionResultDefinitionType
                    _step_definition.addactionresult(_action_result_definition)

                # Executions.
                for _json_step_execution in json_step_definition["executions"]:  # type: _JsonDictType
                    self.debug("Building step execution instance from JSON: %s", jsondump(_json_step_execution, indent=2),
                               extra={self.Extra.LONG_TEXT_MAX_LINES: 10})

                    with self.pushindentation():
                        _step_execution = StepExecution(_step_definition, _json_step_execution["number"])  # type: StepExecution
                        _step_execution.time = TimeStats.fromjson(_json_step_execution["time"])
                        self.debug("Time: %s", _step_execution.time)

                        for _json_error in _json_step_execution["errors"]:  # type: _JsonDictType
                            _step_execution.errors.append(TestError.fromjson(_json_error))
                            self.debug("Error: %s", _step_execution.errors[-1])
                        self.debug("Errors: %d", len(_step_execution.errors))

                        for _json_warning in _json_step_execution["warnings"]:  # type: _JsonDictType
                            _step_execution.warnings.append(TestError.fromjson(_json_warning))
                            self.debug("Warning: %s", _step_execution.warnings[-1])
                        self.debug("Warnings: %d", len(_step_execution.warnings))

                        _step_definition.executions.append(_step_execution)

        return _step_definition

    def _reqverifier2json(
            self,
            req_verifier,  # type: _ReqVerifierType
            json_req_verifier,  # type: _JsonDictType
    ):  # type: (...) -> None
        """
        Generates JSON requirement links for a requirement verifier.

        :param req_verifier: Requirement verifier which JSON content to feed with requirement links. Either a scenario or a step.
        :param json_req_verifier: JSON content to update.
        """
        from ._reqlink import ReqLink

        json_req_verifier["reqs"] = []

        for _req_link in req_verifier.getreqlinks():  # type: ReqLink
            _json_req_link = {"ref": _req_link.req_ref.id}  # type: _JsonDictType

            if _req_link.comments:
                _json_req_link["comments"] = _req_link.comments

            json_req_verifier["reqs"].append(_json_req_link)

    def _json2reqverifier(
            self,
            json_req_verifier,  # type: _JsonDictType
            req_verifier,  # type: _ReqVerifierType
    ):  # type: (...) -> None
        """
        Reads requirement coverage from the JSON content of a requirement verifier.

        :param json_req_verifier: JSON content of a requirement verifier.
        :param req_verifier: Requirement verifier to update. Either a scenario or a step.
        """
        from ._reqdb import REQ_DB
        if typing.TYPE_CHECKING:
            from ._reqtypes import ReqLinkDefType

        # Memo: No 'reqs' until feature #83 has been developped.
        if "reqs" in json_req_verifier:
            for _json_req_link in json_req_verifier["reqs"]:  # type: _JsonDictType
                _req_ref_id = _json_req_link["ref"]  # type: str
                try:
                    _req_ref = REQ_DB.getreqref(_req_ref_id, push_unknown=self._feed_req_db)  # type: _ReqRefType
                except KeyError:
                    if self._feed_req_db:
                        # Requirement reference should have been added automatically.
                        raise
                    else:
                        self.warning(f"Unknown requirement reference {_req_ref_id!r}")
                        continue

                _req_link_def = _req_ref  # type: ReqLinkDefType
                if "comments" in _json_req_link:
                    _req_link_def = (_req_ref, str(_json_req_link["comments"]))

                req_verifier.verifies(_req_link_def)

    def _actionresult2json(
            self,
            action_result_definition,  # type: _ActionResultDefinitionType
    ):  # type: (...) -> _JsonDictType
        """
        Generates JSON content for an action / expected result.

        :param action_result_definition: Action or expected result to generate JSON content for.
        :return: JSON content object.
        """
        from ._actionresultexecution import ActionResultExecution
        from ._debugutils import jsondump
        from ._scenarioexecution import ScenarioExecution
        from ._testerrors import TestError

        self.debug("Generating JSON content for %r", action_result_definition)

        with self.pushindentation():
            _json_action_result_definition = {
                "type": str(action_result_definition.type),
                "description": action_result_definition.description,
                "executions": [],
            }  # type: _JsonDictType

            for _action_result_execution in action_result_definition.executions:  # type: ActionResultExecution
                _json_action_result_execution = {
                    "time": _action_result_execution.time.tojson(),
                    "evidence": _action_result_execution.evidence.copy(),
                    "errors": [],
                    "warnings": [],
                    "subscenarios": [],
                }  # type: _JsonDictType

                for _error in _action_result_execution.errors:  # type: TestError
                    _json_action_result_execution["errors"].append(_error.tojson())

                for _warning in _action_result_execution.warnings:  # type: TestError
                    _json_action_result_execution["warnings"].append(_warning.tojson())

                for _subscenario_execution in _action_result_execution.subscenarios:  # type: ScenarioExecution
                    self.debug("Generating JSON content for subscenario %r", _subscenario_execution.definition)
                    with self.pushindentation("  | "):
                        _json_action_result_execution["subscenarios"].append(self._scenario2json(_subscenario_execution.definition, is_main=False))
                _json_action_result_definition["executions"].append(_json_action_result_execution)

        self.debug("JSON content generated for %r: %s", action_result_definition, jsondump(_json_action_result_definition, indent=2),
                   extra={self.Extra.LONG_TEXT_MAX_LINES: 10})
        return _json_action_result_definition

    def _json2actionresult(
            self,
            json_action_result_definition,  # type: _JsonDictType
    ):  # type: (...) -> _ActionResultDefinitionType
        """
        Action / expected result reading from JSON content.

        :param json_action_result_definition: Action / expected result JSON content to read.
        :return: :class:`._actionresultdefinition.ActionResultDefinition` data.
        """
        from ._actionresultdefinition import ActionResultDefinition
        from ._actionresultexecution import ActionResultExecution
        from ._debugutils import jsondump
        from ._stats import TimeStats
        from ._testerrors import TestError

        self.debug("Reading action/result instance from JSON: %s", jsondump(json_action_result_definition, indent=2),
                   extra={self.Extra.LONG_TEXT_MAX_LINES: 10})

        with self.pushindentation():
            _action_result_type = ActionResultDefinition.Type(json_action_result_definition["type"])  # type: ActionResultDefinition.Type
            self.debug("Type: %s", _action_result_type)

            _action_result_definition = ActionResultDefinition(
                type=_action_result_type,
                description=json_action_result_definition["description"],
            )  # type: ActionResultDefinition
            self.debug("Description: %r", _action_result_definition.description)

            for _json_action_result_execution in json_action_result_definition["executions"]:  # type: _JsonDictType
                self.debug("Reading action/result execution instance from JSON: %s", jsondump(_json_action_result_execution, indent=2),
                           extra={self.Extra.LONG_TEXT_MAX_LINES: 10})

                with self.pushindentation():
                    _action_result_execution = ActionResultExecution(_action_result_definition)  # type: ActionResultExecution

                    _action_result_execution.time = TimeStats.fromjson(_json_action_result_execution["time"])
                    self.debug("Time: %s", _action_result_execution.time)

                    _action_result_execution.evidence = _json_action_result_execution["evidence"].copy()
                    self.debug("Evidence: %r", _action_result_execution.evidence)

                    for _json_error in _json_action_result_execution["errors"]:  # type: _JsonDictType
                        _action_result_execution.errors.append(TestError.fromjson(_json_error))
                        self.debug("Error: %s", _action_result_execution.errors[-1])
                    self.debug("Error: %d", len(_action_result_execution.errors))

                    for _json_warning in _json_action_result_execution["warnings"]:  # type: _JsonDictType
                        _action_result_execution.warnings.append(TestError.fromjson(_json_warning))
                        self.debug("Warning: %s", _action_result_execution.warnings[-1])
                    self.debug("Warning: %d", len(_action_result_execution.warnings))

                    for _json_subscenario in _json_action_result_execution["subscenarios"]:  # type: _JsonDictType
                        with self.pushindentation("  | "):
                            _subscenario_definition = self._json2scenario(_json_subscenario)  # type: _ScenarioDefinitionType
                            if _subscenario_definition.execution:
                                _action_result_execution.subscenarios.append(_subscenario_definition.execution)

                    _action_result_definition.executions.append(_action_result_execution)

        return _action_result_definition


#: Main instance of :class:`ScenarioReport`.
SCENARIO_REPORT = ScenarioReport()  # type: ScenarioReport
