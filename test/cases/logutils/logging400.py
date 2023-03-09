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

import typing

import scenario
import scenario.test

from steps.common import LogVerificationStep  # `LogVerificationStep` used for inheritance.
if typing.TYPE_CHECKING:
    from steps.common import ExecScenario as _ExecScenarioType


class Logging400(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        from steps.common import ExecScenario

        scenario.test.TestCase.__init__(
            self,
            title="Scenario logging indentation",
            objective="Check that action, result and evidence log lines are indented in a manner that helps reading the scenario execution log.",
            features=[scenario.test.features.SCENARIO_LOGGING],
        )

        self.addstep(ExecScenario(
            scenario.test.paths.SCENARIO_LOGGING_SCENARIO,
            config_values={scenario.ConfigKey.LOG_COLOR_ENABLED: False},
        ))
        self.addstep(CheckStepIndentation(ExecScenario.getinstance()))
        self.addstep(CheckLoggingOutOfActionResult(ExecScenario.getinstance()))
        self.addstep(CheckActionResult(ExecScenario.getinstance()))
        self.addstep(CheckActionResultLogging(ExecScenario.getinstance()))
        self.addstep(CheckEvidence(ExecScenario.getinstance()))


class CheckStepIndentation(LogVerificationStep):

    def __init__(
            self,
            exec_step,  # type: _ExecScenarioType
    ):  # type: (...) -> None
        LogVerificationStep.__init__(self, exec_step)

        self.step_indentation = 0  # type: int

    def step(self):  # type: (...) -> None
        self.STEP("Find step indentation")

        if self.ACTION("Find out the left offset for the 'STEP' pattern."):
            _step_line = self.assertline(
                "STEP#1: Scenario logging",
                evidence="Step line",
            )  # type: str
            self.step_indentation = _step_line.find("STEP")
            self.evidence(f"Step indentation: {self.step_indentation}")


class CheckLoggingOutOfActionResult(LogVerificationStep):

    def step(self):  # type: (...) -> None
        self.STEP("Log lines indentation out of action / result blocks")

        _loggings_before = []  # type: typing.List[str]
        _loggings_after = []  # type: typing.List[str]
        if self.ACTION("Search for logging lines before and after actions and expected results."):
            _loggings_before = self.assertlines(
                "Logging before actions/results",
                evidence="Logging before",
            )
            _loggings_after = self.assertlines(
                "Logging after actions/results",
                evidence="Logging after",
            )
        if self.RESULT("The logging lines start with potential indentation, then their log level."):
            for _logging_before in _loggings_before:  # type: str
                self.assertregex(
                    "^ *DEBUG ", _logging_before,
                    evidence="Logging before format",
                )
            for _logging_after in _loggings_after:  # type: str
                self.assertregex(
                    "^ *DEBUG ", _logging_after,
                    evidence="Logging after format",
                )
        if self.RESULT("Logging lines before actions and expected results are displayed without indentation."):
            for _logging_before in _loggings_before:  # Type already declared before.
                self.assertequal(
                    _logging_before.find("DEBUG"), 0,
                    evidence="Logging before indentation",
                )
        if self.RESULT("Logging lines after actions and expected results have hazardous margin "
                       "(no way to determine whether the last loggings are inside or outside the last action or expected result block)."):
            for _logging_after in _loggings_after:  # Type already declared before.
                self.assertgreaterequal(
                    _logging_after.find("DEBUG"), 0,
                    evidence="Logging after indentation",
                )


class CheckActionResult(LogVerificationStep):

    def __init__(
            self,
            exec_step,  # type: _ExecScenarioType
    ):  # type: (...) -> None
        LogVerificationStep.__init__(self, exec_step)

        self.action_text_indentation = 0  # type: int
        self.result_text_indentation = 0  # type: int

    def step(self):  # type: (...) -> None
        self.STEP("Action / result indentation")

        _action = ""  # type: str
        _result = ""  # type: str
        if self.ACTION("Search for the action and expected result lines in the scenario output."):
            _action = self.assertline(
                "This is a sample action.",
                evidence="Action line",
            )
            _result = self.assertline(
                "This is a sample expected result.",
                evidence="Expected result line",
            )
        if self.RESULT("Action and expected result lines start with potential indentation, then their respective 'ACTION:' and 'RESULT:' pattern, "
                       "directly followed by their text."):
            self.assertregex(
                "^ *ACTION: [A-Z]", _action,
                evidence="Action line format",
            )
            self.assertregex(
                "^ *RESULT: [A-Z]", _result,
                evidence="Expected result line format",
            )
        if self.RESULT("'ACTION:' and 'RESULT:' patterns are indented below the 'STEP' block they belong to."):
            self.assertgreater(
                _action.find("ACTION: "), CheckStepIndentation.getinstance().step_indentation,
                evidence="Action indentation v/s step indentation",
            )
            self.assertgreater(
                _result.find("RESULT: "), CheckStepIndentation.getinstance().step_indentation,
                evidence="Expected result indentation v/s step indentation",
            )
        if self.RESULT("'ACTION:' and 'RESULT:' patterns are right-aligned, "
                       "i.e. action and expected result texts have the same indentation."):
            self.action_text_indentation = _action.find("ACTION: ") + len("ACTION: ")
            self.evidence(f"Action text indentation: {self.action_text_indentation}")
            self.result_text_indentation = _result.find("RESULT: ") + len("RESULT: ")
            self.evidence(f"Expected result text indentation: {self.result_text_indentation}")
            self.assertequal(
                self.action_text_indentation, self.result_text_indentation,
                evidence="Action text v/s expected result text indentation",
            )


class CheckActionResultLogging(LogVerificationStep):

    def step(self):  # type: (...) -> None
        self.STEP("Action / result logging indentation")

        _action_logging = ""  # type: str
        _result_logging = ""  # type: str
        if self.ACTION("Search for action / expected result logging lines in the scenario output."):
            _action_logging = self.assertline(
                "Action logging",
                evidence="Action logging",
            )
            _result_logging = self.assertline(
                "Expected result logging",
                evidence="Expected result logging",
            )
        if self.RESULT("The logging lines start with potential indentation, then their log level."):
            self.assertregex(
                "^ *DEBUG ", _action_logging,
                evidence="Action logging format",
            )
            self.assertregex(
                "^ *DEBUG ", _result_logging,
                evidence="Expected result logging format",
            )
        if self.RESULT("Action / expected result logging lines are indented below the action and expected result texts they belong to."):
            self.assertgreater(
                _action_logging.find("DEBUG"), CheckActionResult.getinstance().action_text_indentation,
                evidence="Action logging v/s action text indentation",
            )
            self.assertgreater(
                _result_logging.find("DEBUG"), CheckActionResult.getinstance().result_text_indentation,
                evidence="Expected result logging v/s expected result text indentation",
            )


class CheckEvidence(LogVerificationStep):

    def step(self):  # type: (...) -> None
        self.STEP("Evidence indentation")

        _action_evidence = ""  # type: str
        _result_evidence = ""  # type: str
        if self.ACTION("Search for evidence lines in the scenario output."):
            _action_evidence = self.assertline(
                "Action evidence.",
                evidence="Action evidence",
            )
            _result_evidence = self.assertline(
                "Expected result evidence.",
                evidence="Expected result evidence",
            )
        if self.RESULT("Evidence lines start with potential indentation, then the 'EVIDENCE:' pattern, followed by the '->' pattern, "
                       "which introduces the evidence text."):
            self.assertregex(
                "^ *EVIDENCE:  *-> [A-Z]", _action_evidence,
                evidence="Action evidence format",
            )
            self.assertregex(
                "^ *EVIDENCE:  *-> [A-Z]", _result_evidence,
                evidence="Expected result evidence format",
            )
        if self.RESULT("'EVIDENCE:' patterns are indented below the 'STEP' block they belong to."):
            self.assertgreater(
                _action_evidence.find("EVIDENCE: "), CheckStepIndentation.getinstance().step_indentation,
                evidence="Action evidence v/s step indentation",
            )
            self.assertgreater(
                _result_evidence.find("EVIDENCE: "), CheckStepIndentation.getinstance().step_indentation,
                evidence="Expected result evidence v/s step indentation",
            )
        if self.RESULT("'EVIDENCE:' patterns are right-aligned with 'ACTION:' and 'RESULT:' patterns."):
            self.assertequal(
                _action_evidence.find("EVIDENCE: ") + len("EVIDENCE: "), CheckActionResult.getinstance().action_text_indentation,
                evidence="Action evidence v/s action indentation",
            )
            self.assertequal(
                _result_evidence.find("EVIDENCE: ") + len("EVIDENCE: "), CheckActionResult.getinstance().result_text_indentation,
                evidence="Expected result evidence v/s expected result indentation",
            )
        if self.RESULT("'->' are indented below the action or expected result text they belong to."):
            self.assertgreater(
                _action_evidence.find("-> "), CheckActionResult.getinstance().action_text_indentation,
                evidence="Action evidence text v/s action text indentation",
            )
            self.assertgreater(
                _result_evidence.find("-> "), CheckActionResult.getinstance().result_text_indentation,
                evidence="Expected result evidence text v/s expected result text indentation",
            )
