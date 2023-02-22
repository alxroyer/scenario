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
Scenario logging.
"""

import logging
import typing

from .enumutils import StrEnum  # `StrEnum` used for inheritance.

if typing.TYPE_CHECKING:
    from .actionresultdefinition import ActionResultDefinition as _ActionResultDefinitionType
    from .scenariodefinition import ScenarioDefinition as _ScenarioDefinitionType
    from .scenarioexecution import ScenarioExecution as _ScenarioExecutionType
    from .stepdefinition import StepDefinition as _StepDefinitionType
    from .stepsection import StepSection as _StepSectionType
    from .testerrors import TestError as _TestErrorType


class ScenarioLogging:
    """
    Scenario logging management.
    """

    #: Actions, expected results and evidence lines are right-aligned with the longest 'EVIDENCE: ' pattern.
    ACTION_RESULT_MARGIN = len("  EVIDENCE: ")  # type: int
    #: The scenario stack indentation pattern ensures that the '|' lines are presented the 'ACTION: ' or 'RESULT: ' pattern they relate to.
    SCENARIO_STACK_INDENTATION_PATTERN = "      | "  # type: str

    class _Call(StrEnum):
        """
        :class:`ScenarioLogging` call identifiers.
        """
        BEGIN_SCENARIO = "beginscenario"
        BEGIN_ATTRIBUTES = "beginattributes"
        ATTRIBUTE = "attribute"
        END_ATTRIBUTES = "endattributes"
        STEP_DESCRIPTION = "stepdescription"
        ACTION = "action"
        RESULT = "result"
        END_SCENARIO = "endscenario"

    def __init__(self):  # type: (...) -> None
        """
        Initializes the last call history.
        """
        from .knownissues import KnownIssue

        #: History of this class's method calls.
        #:
        #: Makes it possible to adjust the display depending on the sequence of information.
        self._calls = []  # type: typing.List[ScenarioLogging._Call]

        #: Known issues already displayed.
        self._known_issues = []  # type: typing.List[KnownIssue]

    def beginscenario(
            self,
            scenario_definition,  # type: _ScenarioDefinitionType
    ):  # type: (...) -> None
        """
        Displays the beginning of a scenario execution.

        :param scenario_definition: Scenario being executed.
        """
        from .loggermain import MAIN_LOGGER

        MAIN_LOGGER.rawoutput(f"SCENARIO '{scenario_definition.name}'")
        MAIN_LOGGER.rawoutput("------------------------------------------------")

        self._calls.append(ScenarioLogging._Call.BEGIN_SCENARIO)

    def beginattributes(self):  # type: (...) -> None
        """
        Marks the beginning of scenario attributes.
        """
        self._calls.append(ScenarioLogging._Call.BEGIN_ATTRIBUTES)

    def attribute(
            self,
            name,  # type: str
            value,  # type: str
    ):  # type: (...) -> None
        """
        Display the value of a scenario attribute.

        :param name: Scenario attribute name.
        :param value: Scenario attribute value.

        .. seealso:: :meth:`.scenarioconfig.ScenarioConfig.expectedscenarioattributes()`
        """
        from .loggermain import MAIN_LOGGER

        MAIN_LOGGER.rawoutput(f"  {name}: {value}")

        self._calls.append(ScenarioLogging._Call.ATTRIBUTE)

    def endattributes(self):  # type: (...) -> None
        """
        Marks the end of scenario attributes,
        and the beginning of the test steps by the way.
        """
        from .loggermain import MAIN_LOGGER

        MAIN_LOGGER.rawoutput("")

        self._calls.append(ScenarioLogging._Call.END_ATTRIBUTES)

    def stepsection(
            self,
            step_section,  # type: _StepSectionType
    ):  # type: (...) -> None
        """
        Displays a step section.

        :param step_section:
        :return:
        """
        from .loggermain import MAIN_LOGGER

        # Add space between step sections:
        # - two empty lines when following 'action' or 'result' lines,
        # - only one otherwise.
        if self._calls and (self._calls[-1] in (ScenarioLogging._Call.ACTION, ScenarioLogging._Call.RESULT)):
            MAIN_LOGGER.rawoutput("")
            MAIN_LOGGER.rawoutput("")
        else:
            MAIN_LOGGER.rawoutput("")

        MAIN_LOGGER.rawoutput("------------------------------------------------")
        assert step_section.description is not None
        MAIN_LOGGER.rawoutput(f"  {step_section.description}")
        MAIN_LOGGER.rawoutput("------------------------------------------------")

    def stepdescription(
            self,
            step_definition,  # type: _StepDefinitionType
    ):  # type: (...) -> None
        """
        Displays a step being executed.

        :param step_definition: Step definition being executed.
        """
        from .loggermain import MAIN_LOGGER

        # Add space between two steps.
        MAIN_LOGGER.rawoutput("")

        _step_description = f"STEP#{step_definition.number}"  # type: str
        if step_definition.description is not None:
            _step_description += f": {step_definition.description}"
        _step_description += f" ({step_definition.location.tolongstring()})"
        MAIN_LOGGER.rawoutput(_step_description)
        MAIN_LOGGER.rawoutput("------------------------------------------------")

        self._calls.append(ScenarioLogging._Call.STEP_DESCRIPTION)

    def actionresult(
            self,
            actionresult,  # type: _ActionResultDefinitionType
            description,  # type: str
    ):  # type: (...) -> None
        """
        Displays an action or an expected result being executed.

        :param actionresult: Action or expected result being executed.
        :param description: Action/result description.
        """
        from .actionresultdefinition import ActionResultDefinition
        from .loggermain import MAIN_LOGGER

        if (actionresult.type == ActionResultDefinition.Type.ACTION) and self._calls and (self._calls[-1] == "result"):
            # Add space before an action only after results.
            MAIN_LOGGER.rawoutput("")

        MAIN_LOGGER.rawoutput(f"  {str(actionresult.type).upper():>{self.ACTION_RESULT_MARGIN - 4}}: {MAIN_LOGGER.getindentation()}{description}")

        # Note: `str(actionresult.type)` is either 'ACTION' or 'RESULT'.
        self._calls.append(ScenarioLogging._Call(str(actionresult.type).lower()))

    def error(
            self,
            error,  # type: _TestErrorType
    ):  # type: (...) -> None
        """
        Displays the test exception.

        :param error: Error to display.
        """
        from .knownissues import KnownIssue
        from .loggermain import MAIN_LOGGER
        from .testerrors import ExceptionError

        # Display known issues once only.
        if isinstance(error, KnownIssue):
            for _known_issue in self._known_issues:  # type: KnownIssue
                if _known_issue == error:
                    # Known issue already displayed.
                    return
            # Ok, this known issue has not been displayed yet.
            self._known_issues.append(error)

        # Display the error.
        _log_level = logging.ERROR if error.iserror() else logging.WARNING  # type: int
        if isinstance(error, ExceptionError):
            MAIN_LOGGER.log(_log_level, "")
            MAIN_LOGGER.log(_log_level, "!!! EXCEPTION !!!")
        error.logerror(MAIN_LOGGER, level=_log_level)
        if isinstance(error, ExceptionError):
            MAIN_LOGGER.log(_log_level, "!!! EXCEPTION !!!")
            MAIN_LOGGER.log(_log_level, "")

    def evidence(
            self,
            evidence,  # type: str
    ):  # type: (...) -> None
        """
        Displays an evidence.

        Evidence being saved with the test results shall also be printed out in the console.

        :param evidence: Evidence text.
        """
        from .loggermain import MAIN_LOGGER

        MAIN_LOGGER.rawoutput(f"  {'EVIDENCE':>{self.ACTION_RESULT_MARGIN - 4}}: {MAIN_LOGGER.getindentation()}  -> {evidence}")
        # Do not append 'evidence' to :attr:`_calls` in order not to break the 'action'/'result' sequences.

    def endscenario(
            self,
            scenario_definition,  # type: _ScenarioDefinitionType
    ):  # type: (...) -> None
        """
        Displays the end of a scenario execution.

        :param scenario_definition: Scenario which execution has just finished.

        Resets the :attr:`_known_issues` history for the main scenario.
        """
        from .loggermain import MAIN_LOGGER
        from .scenariostack import SCENARIO_STACK

        MAIN_LOGGER.rawoutput("")
        MAIN_LOGGER.rawoutput(f"END OF '{scenario_definition.name}'")

        # Reset the `_known_issues` history when this is the main scenario.
        if SCENARIO_STACK.ismainscenario(scenario_definition):
            self._known_issues = []

        self._calls.append(ScenarioLogging._Call.END_SCENARIO)

    def displaystatistics(
            self,
            scenario_execution,  # type: _ScenarioExecutionType
    ):  # type: (...) -> None
        """
        Displays the scenario statistics.

        :param scenario_execution: Scenario which execution has just finished.
        """
        from .datetimeutils import f2strduration
        from .loggermain import MAIN_LOGGER

        MAIN_LOGGER.rawoutput("------------------------------------------------")

        # Display warnings and errors (if any).
        for _warning in scenario_execution.warnings:  # type: _TestErrorType
            self.error(_warning)
        for _error in scenario_execution.errors:  # type: _TestErrorType
            self.error(_error)

        # Terminate and display statistics.
        MAIN_LOGGER.rawoutput(f"             Status: {scenario_execution.status}")
        MAIN_LOGGER.rawoutput(f"    Number of STEPs: {scenario_execution.step_stats}")
        MAIN_LOGGER.rawoutput(f"  Number of ACTIONs: {scenario_execution.action_stats}")
        MAIN_LOGGER.rawoutput(f"  Number of RESULTs: {scenario_execution.result_stats}")
        MAIN_LOGGER.rawoutput(f"               Time: {f2strduration(scenario_execution.time.elapsed)}")
        MAIN_LOGGER.rawoutput("")


__doc__ += """
.. py:attribute:: SCENARIO_LOGGING

    Main instance of :class:`ScenarioLogging`.
"""
SCENARIO_LOGGING = ScenarioLogging()  # type: ScenarioLogging
