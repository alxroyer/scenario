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

if True:
    from ._enumutils import StrEnum as _StrEnumImpl  # `StrEnum` used for inheritance.
    from ._fastpath import FAST_PATH as _FAST_PATH  # `FAST_PATH` imported once for performance concerns.
    from ._knownissues import KnownIssue as _KnownIssueImpl  # `KnownIssue` used for inheritance.
if typing.TYPE_CHECKING:
    from ._actionresultdefinition import ActionResultDefinition as _ActionResultDefinitionType
    from ._knownissues import KnownIssue as _KnownIssueType
    from ._req import Req as _ReqType
    from ._scenariodefinition import ScenarioDefinition as _ScenarioDefinitionType
    from ._scenarioexecution import ScenarioExecution as _ScenarioExecutionType
    from ._stepdefinition import StepDefinition as _StepDefinitionType
    from ._stepsection import StepSectionDescription as _StepSectionDescriptionType
    from ._testerrors import TestError as _TestErrorType


class ScenarioLogging:
    """
    Scenario logging management.

    Instantiated once with the :data:`SCENARIO_LOGGING` singleton.
    """

    #: Actions, expected results and evidence lines are right-aligned with the longest 'EVIDENCE: ' pattern.
    ACTION_RESULT_MARGIN = len("  EVIDENCE: ")  # type: int
    #: The scenario stack indentation pattern ensures that the '|' lines are presented the 'ACTION: ' or 'RESULT: ' pattern they relate to.
    SCENARIO_STACK_INDENTATION_PATTERN = "      | "  # type: str

    class _Call(_StrEnumImpl):
        """
        :class:`ScenarioLogging` call identifiers.
        """
        BEGIN_SCENARIO = "beginscenario"
        BEGIN_HEADING_INFO = "beginheadinginfo"
        ATTRIBUTE = "attribute"
        REQ_COVERAGE = "reqcoverage"
        END_HEADING_INFO = "endheadinginfo"
        STEP_DESCRIPTION = "stepdescription"
        ACTION = "action"
        RESULT = "result"
        END_SCENARIO = "endscenario"

    def __init__(self):  # type: (...) -> None
        """
        Initializes the last call history.
        """
        #: History of this class's method calls.
        #:
        #: Makes it possible to adjust the display depending on the sequence of information.
        self._calls = []  # type: typing.List[ScenarioLogging._Call]

        #: Known issues already displayed.
        self._known_issues = []  # type: typing.List[_KnownIssueType]

    def beginscenario(
            self,
            scenario_definition,  # type: _ScenarioDefinitionType
    ):  # type: (...) -> None
        """
        Displays the beginning of a scenario execution.

        :param scenario_definition: Scenario being executed.
        """
        _FAST_PATH.main_logger.rawoutput(f"SCENARIO '{scenario_definition.name}'")
        _FAST_PATH.main_logger.rawoutput("------------------------------------------------")

        self._calls.append(ScenarioLogging._Call.BEGIN_SCENARIO)

    def beginheadinginfo(self):  # type: (...) -> None
        """
        Marks the beginning of scenario heading information.
        """
        self._calls.append(ScenarioLogging._Call.BEGIN_HEADING_INFO)

    def attribute(
            self,
            name,  # type: str
            value,  # type: str
    ):  # type: (...) -> None
        """
        Display the value of a scenario attribute.

        :param name: Scenario attribute name.
        :param value: Scenario attribute value.

        .. seealso:: :meth:`._scenarioconfig.ScenarioConfig.expectedscenarioattributes()`
        """
        if len(value.splitlines()) <= 1:
            # One-line display.
            _FAST_PATH.main_logger.rawoutput(f"  {name}: {value}")
        else:
            # Multiline display.
            _FAST_PATH.main_logger.rawoutput(f"  {name}:")
            self._displaylongtext(left="    ", long_text=value)

        self._calls.append(ScenarioLogging._Call.ATTRIBUTE)

    def reqcoverage(
            self,
            scenario_definition,  # type: _ScenarioDefinitionType
    ):  # type: (...) -> None
        """
        Displays requirement coverage for the scenario, if any.

        :param scenario_definition: Scenario to display requirement verifications for.
        """
        _reqs = list(scenario_definition.getreqs(walk_steps=True))  # type: typing.Sequence[_ReqType]
        if _reqs:
            if not any([_req.title for _req in _reqs]):
                # Display requirement identifiers in a single line, separated with commas.
                _FAST_PATH.main_logger.rawoutput("  VERIFIES: " + ", ".join([_req.id for _req in _reqs]))
            else:
                # Display each requirement on a separate line, with its title when available.
                _FAST_PATH.main_logger.rawoutput("  VERIFIES:")
                for _req in _reqs:  # type: _ReqType
                    if _req.title:
                        _FAST_PATH.main_logger.rawoutput(f"    {_req.id}: {_req.title}")
                    else:
                        _FAST_PATH.main_logger.rawoutput(f"    {_req.id}")

        self._calls.append(ScenarioLogging._Call.REQ_COVERAGE)

    def endheadinginfo(self):  # type: (...) -> None
        """
        Marks the beginning of scenario heading information,
        and the beginning of the test steps by the way.
        """
        _FAST_PATH.main_logger.rawoutput("")

        self._calls.append(ScenarioLogging._Call.END_HEADING_INFO)

    def stepsectiondescription(
            self,
            step_section_description,  # type: _StepSectionDescriptionType
    ):  # type: (...) -> None
        """
        Displays a step section.

        :param step_section_description: Step section description step.
        """
        # Add space between step sections:
        # - two empty lines when following 'action' or 'result' lines,
        # - only one otherwise.
        if self._calls and (self._calls[-1] in (ScenarioLogging._Call.ACTION, ScenarioLogging._Call.RESULT)):
            _FAST_PATH.main_logger.rawoutput("")
            _FAST_PATH.main_logger.rawoutput("")
        else:
            _FAST_PATH.main_logger.rawoutput("")

        _FAST_PATH.main_logger.rawoutput("------------------------------------------------")
        _FAST_PATH.main_logger.rawoutput(f"  {step_section_description.description}")
        _FAST_PATH.main_logger.rawoutput("------------------------------------------------")

    def stepdescription(
            self,
            step_definition,  # type: _StepDefinitionType
    ):  # type: (...) -> None
        """
        Displays a step being executed.

        :param step_definition: Step definition being executed.
        """
        # Add space between two steps.
        _FAST_PATH.main_logger.rawoutput("")

        _step_description = f"STEP#{step_definition.number}"  # type: str
        if step_definition.description is not None:
            _step_description += f": {step_definition.description}"
        _step_description += f" ({step_definition.location.tolongstring()})"
        _FAST_PATH.main_logger.rawoutput(_step_description)
        _FAST_PATH.main_logger.rawoutput("------------------------------------------------")

        self._calls.append(ScenarioLogging._Call.STEP_DESCRIPTION)

    def actionresult(
            self,
            actionresult,  # type: _ActionResultDefinitionType
    ):  # type: (...) -> None
        """
        Displays an action or an expected result being executed.

        :param actionresult: Action or expected result being executed.
        """
        from ._actionresultdefinition import ActionResultDefinition

        if (actionresult.type == ActionResultDefinition.Type.ACTION) and self._calls and (self._calls[-1] == "result"):
            # Add space before an action only after results.
            _FAST_PATH.main_logger.rawoutput("")

        self._displaylongtext(
            left=f"  {str(actionresult.type).upper():>{self.ACTION_RESULT_MARGIN - 4}}: {_FAST_PATH.main_logger.getindentation()}",
            long_text=actionresult.description,
        )

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
        from ._testerrors import ExceptionError

        # Display known issues once only.
        if isinstance(error, _KnownIssueImpl):
            if any([_known_issue == error for _known_issue in self._known_issues]):
                # Known issue already displayed.
                return
            # Ok, this known issue has not been displayed yet.
            self._known_issues.append(error)

        # Display the error.
        _log_level = logging.ERROR if error.iserror() else logging.WARNING  # type: int
        if isinstance(error, ExceptionError):
            _FAST_PATH.main_logger.log(_log_level, "")
            _FAST_PATH.main_logger.log(_log_level, "!!! EXCEPTION !!!")
        error.logerror(_FAST_PATH.main_logger, level=_log_level)
        if isinstance(error, ExceptionError):
            _FAST_PATH.main_logger.log(_log_level, "!!! EXCEPTION !!!")
            _FAST_PATH.main_logger.log(_log_level, "")

    def evidence(
            self,
            evidence,  # type: str
    ):  # type: (...) -> None
        """
        Displays an evidence.

        Evidence being saved with the test results shall also be printed out in the console.

        :param evidence: Evidence text.
        """
        self._displaylongtext(
            left=f"  {'EVIDENCE':>{self.ACTION_RESULT_MARGIN - 4}}: {_FAST_PATH.main_logger.getindentation()}  -> ",
            long_text=evidence,
        )

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
        _FAST_PATH.main_logger.rawoutput("")
        _FAST_PATH.main_logger.rawoutput(f"END OF '{scenario_definition.name}'")

        # Reset the `_known_issues` history when this is the main scenario.
        if _FAST_PATH.scenario_stack.ismainscenario(scenario_definition):
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
        from ._datetimeutils import f2strduration

        _FAST_PATH.main_logger.rawoutput("------------------------------------------------")

        # Display warnings and errors (if any).
        for _warning in scenario_execution.warnings:  # type: _TestErrorType
            self.error(_warning)
        for _error in scenario_execution.errors:  # type: _TestErrorType
            self.error(_error)

        # Terminate and display statistics.
        _FAST_PATH.main_logger.rawoutput(f"             Status: {scenario_execution.status}")
        _FAST_PATH.main_logger.rawoutput(f"    Number of STEPs: {scenario_execution.step_stats}")
        _FAST_PATH.main_logger.rawoutput(f"  Number of ACTIONs: {scenario_execution.action_stats}")
        _FAST_PATH.main_logger.rawoutput(f"  Number of RESULTs: {scenario_execution.result_stats}")
        _FAST_PATH.main_logger.rawoutput(f"               Time: {f2strduration(scenario_execution.time.elapsed)}")
        _FAST_PATH.main_logger.rawoutput("")

    def _displaylongtext(
            self,
            left,  # type: str
            long_text,  # type: str
    ):  # type: (...) -> None
        """
        Displays long text.

        :param left:
            Left part of the first line.

            Determines the length of left blank indentation for consecutive lines.
        :param long_text:
            Long text to display, possibly on several lines.
        """
        for _line in long_text.splitlines():  # type: str
            if _line or left.strip():
                # Regular line display.
                _FAST_PATH.main_logger.rawoutput(f"{left}{_line}")
            else:
                # Avoid printing out the left blank indentation only.
                _FAST_PATH.main_logger.rawoutput("")

            # Replace `left` by blank indentation for consecutive lines.
            left = " " * len(left)


#: Main instance of :class:`ScenarioLogging`.
SCENARIO_LOGGING = ScenarioLogging()  # type: ScenarioLogging
