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
Statistics class module.
"""

import json
import sys
import typing

# `ActionResultDefinition` used in method signatures.
from .actionresultdefinition import ActionResultDefinition
# `Logger` used for inheritance.
from .logger import Logger
# `ScenarioDefinition` used in method signatures.
from .scenarioexecution import ScenarioDefinition
# `StepDefinition` used in method signatures.
from .stepdefinition import StepDefinition

if typing.TYPE_CHECKING:
    # `AnyPathType` used in method signatures.
    # Type declared for type checking only.
    from .path import AnyPathType
    # `JSONDict` used in method signatures.
    # Type declared for type checking only.
    from .typing import JSONDict


class ScenarioReport(Logger):
    """
    JSON report generator.
    """

    def __init__(self):  # type: (...) -> None
        """
        Configures logging for the :class:`ScenarioReport` class.
        """
        from .debugclasses import DebugClass
        from .path import Path

        Logger.__init__(self, log_class=DebugClass.SCENARIO_REPORT)

        #: JSON report path being written or read.
        self._json_path = Path()  # type: Path

    def writejsonreport(
            self,
            scenario_definition,  # type: ScenarioDefinition
            json_path,  # type: AnyPathType
    ):  # type: (...) -> bool
        """
        Generates the JSON report output file for the given scenario execution.

        :param scenario_definition: Scenario to generate the JSON report for.
        :param json_path: Path to write the JSON report into.
        :return: ``True`` for success, ``False`` otherwise.
        """
        from .loggermain import MAIN_LOGGER
        from .path import Path

        try:
            self.resetindentation()
            self.debug("Writing scenario execution to JSON report '%s'", json_path)

            # Build the JSON content.
            self._json_path = Path(json_path)
            _json = self._scenario2json(scenario_definition, is_main=True)  # type: JSONDict

            # Write the JSON file.
            Path(json_path).write_text(json.dumps(_json, indent=2), encoding="utf-8")

            return True
        except Exception as _err:
            MAIN_LOGGER.error(f"Could not write JSON report '{json_path}': {_err}")
            self.debug("Exception", exc_info=sys.exc_info())
            return False
        finally:
            self.resetindentation()

    def readjsonreport(
            self,
            json_path,  # type: AnyPathType
    ):  # type: (...) -> typing.Optional[ScenarioDefinition]
        """
        Reads the JSON report file.

        :param json_path: JSON file path to read.
        :return:
            Scenario data read from the JSON report file.
            ``None`` when the file could not be read, or its content could not be parsed successfully.
        """
        from .loggermain import MAIN_LOGGER
        from .path import Path

        try:
            self.resetindentation()
            self.debug("Reading scenario execution from JSON report '%s'", json_path)

            # Read the JSON file.
            _json = json.loads(Path(json_path).read_bytes())  # type: JSONDict

            # Analyze the JSON content.
            self._json_path = Path(json_path)
            _scenario_definition = self._json2scenario(_json)  # type: ScenarioDefinition

            return _scenario_definition
        except Exception as _err:
            MAIN_LOGGER.error(f"Could not read JSON report '{json_path}': {_err}")
            self.debug("Exception", exc_info=sys.exc_info())
            return None
        finally:
            self.resetindentation()

    def _scenario2json(
            self,
            scenario_definition,  # type: ScenarioDefinition
            is_main,  # type: bool
    ):  # type: (...) -> JSONDict
        """
        Scenario report JSON generation.

        :param scenario_definition: Scenario to generate the JSON report for.
        :param is_main: True for the main scenario, False otherwise.
        :return: JSON report object.
        """
        from .debugutils import jsondump
        from .path import Path
        from .testerrors import TestError

        self.debug("Generating JSON report for scenario %r", scenario_definition)
        self.pushindentation()

        # Build a JSON object.
        _json_scenario = {}  # type: JSONDict

        # JSON schema.
        if is_main:
            _json_scenario["$schema"] = "https://github.com/alxroyer/scenario/blob/master/schema/scenario-report-v1.schema.json"

        # Scenario name.
        _json_scenario["name"] = scenario_definition.name

        # Script path.
        _main_path = Path.getmainpath() or Path.cwd()  # type: Path
        if scenario_definition.script_path.is_relative_to(_main_path):
            _json_scenario["href"] = scenario_definition.script_path.relative_to(_main_path)
        else:
            _json_scenario["href"] = scenario_definition.script_path.abspath

        # Attributes.
        _json_scenario["attributes"] = {}
        for _attribute_name in scenario_definition.getattributenames():  # type: str
            _json_scenario["attributes"][_attribute_name] = str(scenario_definition.getattribute(_attribute_name))

        # Steps.
        _json_scenario["steps"] = []
        for _step_definition in scenario_definition.steps:  # type: StepDefinition
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

        self.popindentation()
        self.debug("JSON report generated for scenario %r: %s", scenario_definition.name, jsondump(_json_scenario, indent=2),
                   extra=self.longtext(max_lines=20))
        return _json_scenario

    def _json2scenario(
            self,
            json_scenario,  # type: JSONDict
    ):  # type: (...) -> ScenarioDefinition
        """
        Scenario data reading from JSON report.

        :param json_scenario: Scenario JSON report to read.
        :return: Scenario data.
        """
        from .debugutils import jsondump
        from .path import Path
        from .scenarioexecution import ScenarioExecution
        from .stats import TimeStats
        from .testerrors import TestError

        self.debug("Reading scenario from JSON: %s", jsondump(json_scenario, indent=2),
                   extra=self.longtext(max_lines=20))
        self.pushindentation()

        # Create the scenario definition instance.
        _scenario_definition = ScenarioDefinition()  # type: ScenarioDefinition

        # Scenario name.
        _scenario_definition.name = json_scenario["name"]
        self.debug("Name: %r", _scenario_definition.name)

        # Script path.
        _scenario_definition.script_path = Path(json_scenario["href"], relative_to=Path.getmainpath() or Path.cwd())
        self.debug("Script path: '%s'", _scenario_definition.script_path)

        # Attributes.
        for _attribute_name in json_scenario["attributes"]:  # type: str
            _scenario_definition.setattribute(_attribute_name, json_scenario["attributes"][_attribute_name])

        # Steps.
        for _json_step_definition in json_scenario["steps"]:  # type: JSONDict
            _step_definition = self._json2step(_json_step_definition)  # type: StepDefinition
            _scenario_definition.addstep(_step_definition)

        # Status & errors.
        _scenario_definition.execution = ScenarioExecution(_scenario_definition)
        for _json_error in json_scenario["errors"]:  # type: JSONDict
            _scenario_definition.execution.errors.append(TestError.fromjson(_json_error))
            self.debug("Error: %s", _scenario_definition.execution.errors[-1])
        self.debug("Errors: %d", len(_scenario_definition.execution.errors))

        for _json_warning in json_scenario["warnings"]:  # type: JSONDict
            _scenario_definition.execution.warnings.append(TestError.fromjson(_json_warning))
            self.debug("Warning: %s", _scenario_definition.execution.warnings[-1])
        self.debug("Warnings: %d", len(_scenario_definition.execution.warnings))

        # Time & statistics.
        _scenario_definition.execution.time = TimeStats.fromjson(json_scenario["time"])
        self.debug("Time statistics: %s", _scenario_definition.execution.time)

        self.popindentation()
        return _scenario_definition

    def _step2json(
            self,
            step_definition,  # type: StepDefinition
    ):  # type: (...) -> JSONDict
        """
        Generates the JSON report for a step.

        :param step_definition: Step definition (with execution) to generate the JSON report for.
        :return: JSON report object.
        """
        from .debugutils import jsondump
        from .stepexecution import StepExecution
        from .stepsection import StepSectionDescription
        from .testerrors import TestError

        self.debug("Generating JSON report for %r", step_definition)
        self.pushindentation()

        _json_step_definition = {
            "location": step_definition.location.tolongstring(),
            "description": step_definition.description,
        }  # type: JSONDict

        # Do not set 'executions' and 'actions-results' lists for step sections.
        if not isinstance(step_definition, StepSectionDescription):
            _json_step_definition["executions"] = []
            for _step_execution in step_definition.executions:  # type: StepExecution
                _json_step_execution = {
                    "number": _step_execution.number,
                    "time": _step_execution.time.tojson(),
                    "errors": [],
                    "warnings": [],
                }  # type: JSONDict

                for _error in _step_execution.errors:  # type: TestError
                    _json_step_execution["errors"].append(_error.tojson())

                for _warning in _step_execution.warnings:  # type: TestError
                    _json_step_execution["warnings"].append(_warning.tojson())

                _json_step_definition["executions"].append(_json_step_execution)

            _json_step_definition["actions-results"] = []
            for _action_result_definition in step_definition.actions_results:  # type: ActionResultDefinition
                _json_step_definition["actions-results"].append(self._actionresult2json(_action_result_definition))

        self.popindentation()
        self.debug("JSON report generated for %r: %s", step_definition, jsondump(_json_step_definition, indent=2),
                   extra=self.longtext(max_lines=10))
        return _json_step_definition

    def _json2step(
            self,
            json_step_definition,  # type: JSONDict
    ):  # type: (...) -> StepDefinition
        """
        Step reading from JSON report.

        :param json_step_definition: Step definition JSON report to read.
        :return: :class:`.stepdefinition.StepDefinition` data.
        """
        from .debugutils import jsondump
        from .locations import CodeLocation
        from .stats import TimeStats
        from .stepexecution import StepExecution
        from .stepsection import StepSectionDescription
        from .testerrors import TestError

        self.debug("Reading step instance from JSON: %s", jsondump(json_step_definition, indent=2),
                   extra=self.longtext(max_lines=10))
        self.pushindentation()

        _step_definition = StepDefinition()  # type: StepDefinition

        _step_definition.location = CodeLocation.fromlongstring(json_step_definition["location"])
        self.debug("Location: %s", _step_definition.location.tolongstring())

        _step_definition.description = json_step_definition["description"]
        self.debug("Description: %r", _step_definition.description)

        if ("executions" not in json_step_definition) or ("actions-results" not in json_step_definition):
            # Missing executions and/or actions/results.
            # Replace the general `StepDefinition` instance created above by a `StepSection` one.
            assert _step_definition.description is not None
            _step_definition = StepSectionDescription(_step_definition.description)
        else:
            for _json_step_execution in json_step_definition["executions"]:  # type: JSONDict
                self.debug("Building step execution instance from JSON: %s", jsondump(_json_step_execution, indent=2),
                           extra=self.longtext(max_lines=10))
                self.pushindentation()

                _step_execution = StepExecution(_step_definition, _json_step_execution["number"])  # type: StepExecution
                _step_execution.time = TimeStats.fromjson(_json_step_execution["time"])
                self.debug("Time: %s", _step_execution.time)

                for _json_error in _json_step_execution["errors"]:  # type: JSONDict
                    _step_execution.errors.append(TestError.fromjson(_json_error))
                    self.debug("Error: %s", _step_execution.errors[-1])
                self.debug("Errors: %d", len(_step_execution.errors))

                for _json_warning in _json_step_execution["warnings"]:  # type: JSONDict
                    _step_execution.warnings.append(TestError.fromjson(_json_warning))
                    self.debug("Warning: %s", _step_execution.warnings[-1])
                self.debug("Warnings: %d", len(_step_execution.warnings))

                _step_definition.executions.append(_step_execution)
                self.popindentation()

            for _json_action_result_definition in json_step_definition["actions-results"]:  # type: JSONDict
                _action_result_definition = self._json2actionresult(_json_action_result_definition)  # type: ActionResultDefinition
                _step_definition.addactionresult(_action_result_definition)

        self.popindentation()
        return _step_definition

    def _actionresult2json(
            self,
            action_result_definition,  # type: ActionResultDefinition
    ):  # type: (...) -> JSONDict
        """
        Generates the JSON report for an action / expected result.

        :param action_result_definition: Action or expected result to generate the JSON report for.
        :return JSON: JSON report object.
        """
        from .actionresultexecution import ActionResultExecution
        from .debugutils import jsondump
        from .scenarioexecution import ScenarioExecution
        from .testerrors import TestError

        self.debug("Generating JSON report for %r", action_result_definition)
        self.pushindentation()

        _json_action_result_definition = {
            "type": str(action_result_definition.type),
            "description": action_result_definition.description,
            "executions": [],
        }  # type: JSONDict

        for _action_result_execution in action_result_definition.executions:  # type: ActionResultExecution
            _json_action_result_execution = {
                "time": _action_result_execution.time.tojson(),
                "evidence": _action_result_execution.evidence.copy(),
                "errors": [],
                "warnings": [],
                "subscenarios": [],
            }  # type: JSONDict

            for _error in _action_result_execution.errors:  # type: TestError
                _json_action_result_execution["errors"].append(_error.tojson())

            for _warning in _action_result_execution.warnings:  # type: TestError
                _json_action_result_execution["warnings"].append(_warning.tojson())

            for _subscenario_execution in _action_result_execution.subscenarios:  # type: ScenarioExecution
                try:
                    self.debug("Generation JSON report sor subscenario %r", _subscenario_execution.definition)
                    self.pushindentation("  | ")
                    _json_action_result_execution["subscenarios"].append(self._scenario2json(_subscenario_execution.definition, is_main=False))
                finally:
                    self.popindentation("  | ")
            _json_action_result_definition["executions"].append(_json_action_result_execution)

        self.popindentation()
        self.debug("JSON report generated for %r: %s", action_result_definition, jsondump(_json_action_result_definition, indent=2),
                   extra=self.longtext(max_lines=10))
        return _json_action_result_definition

    def _json2actionresult(
            self,
            json_action_result_definition,  # type: JSONDict
    ):  # type: (...) -> ActionResultDefinition
        """
        Action / expected result reading from JSON report.

        :param json_action_result_definition: Action / expected result JSON report to read.
        :return: :class:`.actionresultdefinition.ActionResultDefinition` data.
        """
        from .actionresultexecution import ActionResultExecution
        from .debugutils import jsondump
        from .stats import TimeStats
        from .testerrors import TestError

        self.debug("Reading action/result instance from JSON: %s", jsondump(json_action_result_definition, indent=2),
                   extra=self.longtext(max_lines=10))
        self.pushindentation()

        _action_result_type = ActionResultDefinition.Type.ACTION  # type: ActionResultDefinition.Type
        for _action_result_type in ActionResultDefinition.Type:
            if str(_action_result_type) == json_action_result_definition["type"]:
                break
        self.debug("Type: %s", _action_result_type)

        _action_result_definition = ActionResultDefinition(
            type=_action_result_type,
            description=json_action_result_definition["description"],
        )  # type: ActionResultDefinition
        self.debug("Description: %r", _action_result_definition.description)

        for _json_action_result_execution in json_action_result_definition["executions"]:  # type: JSONDict
            self.debug("Reading action/result execution instance from JSON: %s", jsondump(_json_action_result_execution, indent=2),
                       extra=self.longtext(max_lines=10))
            self.pushindentation()

            _action_result_execution = ActionResultExecution(_action_result_definition)  # type: ActionResultExecution

            _action_result_execution.time = TimeStats.fromjson(_json_action_result_execution["time"])
            self.debug("Time: %s", _action_result_execution.time)

            _action_result_execution.evidence = _json_action_result_execution["evidence"].copy()
            self.debug("Evidence: %r", _action_result_execution.evidence)

            for _json_error in _json_action_result_execution["errors"]:  # type: JSONDict
                _action_result_execution.errors.append(TestError.fromjson(_json_error))
                self.debug("Error: %s", _action_result_execution.errors[-1])
            self.debug("Error: %d", len(_action_result_execution.errors))

            for _json_warning in _json_action_result_execution["warnings"]:  # type: JSONDict
                _action_result_execution.warnings.append(TestError.fromjson(_json_warning))
                self.debug("Warning: %s", _action_result_execution.warnings[-1])
            self.debug("Warning: %d", len(_action_result_execution.warnings))

            for _json_subscenario in _json_action_result_execution["subscenarios"]:  # type: JSONDict
                try:
                    self.pushindentation("  | ")
                    _subscenario_definition = self._json2scenario(_json_subscenario)  # type: ScenarioDefinition
                    if _subscenario_definition.execution:
                        _action_result_execution.subscenarios.append(_subscenario_definition.execution)
                finally:
                    self.popindentation("  | ")

            _action_result_definition.executions.append(_action_result_execution)
            self.popindentation()

        self.popindentation()
        return _action_result_definition


__doc__ += """
.. py:attribute:: SCENARIO_REPORT

    Main instance of :class:`ScenarioReport`.
"""
SCENARIO_REPORT = ScenarioReport()  # type: ScenarioReport
