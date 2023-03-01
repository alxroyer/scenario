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

import scenario
from scenario.scenariologging import ScenarioLogging
import scenario.test

# Steps:
from steps.common import ExecScenario
from steps.common import LogVerificationStep


class Logging410(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        scenario.test.TestCase.__init__(
            self,
            title="Scenario stack indentation",
            objective="Check that indentation is shifted for each subscenario being executed.",
            features=[scenario.test.features.LOGGING],
        )

        self.addstep(ExecScenario(
            scenario.test.paths.SUPERSCENARIO_SCENARIO, subscenario=scenario.test.paths.SCENARIO_LOGGING_SCENARIO,
            config_values={scenario.ConfigKey.LOG_COLOR_ENABLED: False},
        ))
        self.addstep(CheckMainScenario(ExecScenario.getinstance()))
        self.addstep(CheckSubScenario(CheckMainScenario.getinstance()))


class CheckMainScenario(LogVerificationStep):

    def __init__(
            self,
            exec_step,  # type: ExecScenario
    ):  # type: (...) -> None
        LogVerificationStep.__init__(self, exec_step)

        self.action_indentation = 0  # type: int
        self.result_indentation = 0  # type: int

    def step(self):  # type: (...) -> None
        self.STEP("Main scenario indentation")

        if self.RESULT("The beginning of the main scenario is displayed without indentation."):
            _main_beginning_line = self.assertline(f"SCENARIO '{scenario.test.paths.SUPERSCENARIO_SCENARIO}'")  # type: str
            self.assertregex("^SCENARIO ", _main_beginning_line, evidence=True)
        if self.RESULT("The steps of the main scenario are displayed without indentation."):
            for _main_step_text in (
                "STEP#1: Subscenario execution",
            ):  # type: str
                for _main_step_line in self.assertlines(_main_step_text):  # type: str
                    self.assertregex(
                        r"^STEP#", _main_step_line,
                        evidence=True,
                    )
        if self.RESULT("The 'ACTION: ' patterns of the main scenario actions of are right-aligned "
                       f"with {ScenarioLogging.ACTION_RESULT_MARGIN} characters."):
            for _main_action_text in (
                f"Execute the '{scenario.test.paths.SCENARIO_LOGGING_SCENARIO}' scenario.",
            ):  # type: str
                for _main_action_line in self.assertlines(_main_action_text):  # type: str
                    self.assertregex(
                        r"".join([
                            r"^",
                            r" " * (ScenarioLogging.ACTION_RESULT_MARGIN - len("ACTION: ")),
                            r"ACTION: ",
                        ]),
                        _main_action_line,
                        evidence=True,
                    )
                    self.action_indentation = _main_action_line.find("ACTION: ")
        if self.RESULT("The 'RESULT: ' patterns of the main scenario expected results are right-aligned "
                       f"with {ScenarioLogging.ACTION_RESULT_MARGIN} characters."):
            for _main_result_text in (
                "No exception is thrown.",
            ):  # type: str
                for _main_result_line in self.assertlines(_main_result_text):  # type: str
                    self.assertregex(
                        r"".join([
                            r"^",
                            r" " * (ScenarioLogging.ACTION_RESULT_MARGIN - len("RESULT: ")),
                            r"RESULT: ",
                        ]),
                        _main_result_line,
                        evidence=True,
                    )
                    self.result_indentation = _main_result_line.find("RESULT: ")
        if self.RESULT("The 'EVIDENCE: ' patterns the the main scenario evidence are right-aligned "
                       f"with {ScenarioLogging.ACTION_RESULT_MARGIN} characters."):
            for _main_evidence_text in (
                "Subscenario executed successfully",
            ):  # type: str
                for _main_evidence_line in self.assertlines(_main_evidence_text):  # type: str
                    self.assertregex(
                        r"".join([
                            r"^",
                            r" " * (ScenarioLogging.ACTION_RESULT_MARGIN - len("EVIDENCE: ")),
                            r"EVIDENCE: ",
                        ]),
                        _main_evidence_line,
                        evidence=True,
                    )


class CheckSubScenario(LogVerificationStep):

    def step(self):  # type: (...) -> None
        self.STEP("Subscenario indentation")

        assert isinstance(self.exec_step, CheckMainScenario)

        _subscenario_regex_start = r"^" + ScenarioLogging.SCENARIO_STACK_INDENTATION_PATTERN.replace("|", r"\|")  # type: str
        if self.RESULT(f"The '{ScenarioLogging.SCENARIO_STACK_INDENTATION_PATTERN}' indentation pattern "
                       "makes the '|' characters be indented constantly, and below the 'ACTION: ' and 'RESULT: ' patterns."):
            self.evidence(f"Main action indentation: {self.exec_step.action_indentation}")
            self.assertgreater(self.exec_step.action_indentation, 0)
            self.evidence(f"Main expected result indentation: {self.exec_step.result_indentation}")
            self.assertgreater(self.exec_step.result_indentation, 0)
            _main_action_result_indentation = max(
                self.exec_step.action_indentation,
                self.exec_step.result_indentation,
            )  # type: int
            _subscenario_line_indentation = -1  # type: int
            for _subscenario_line in self.assertlines(ScenarioLogging.SCENARIO_STACK_INDENTATION_PATTERN):  # type: str
                self.evidence(f"Subscenario line: {_subscenario_line!r}")
                if _subscenario_line_indentation < 0:
                    _subscenario_line_indentation = _subscenario_line.find("|")
                    self.assertgreater(
                        _subscenario_line_indentation, _main_action_result_indentation,
                        evidence="'|' character position",
                    )
                else:
                    self.assertequal(
                        _subscenario_line.find("|"), _subscenario_line_indentation,
                        evidence="'|' character position",
                    )
            # Check we have actually processed subscenario lines.
            self.assertgreater(_subscenario_line_indentation, 0)
        if self.RESULT("The beginning of the subscenario is displayed "
                       f"with the {ScenarioLogging.SCENARIO_STACK_INDENTATION_PATTERN!r} indentation pattern."):
            for _subscenario_beginning_line in self.assertlines(f"SCENARIO '{scenario.test.paths.SCENARIO_LOGGING_SCENARIO}'"):  # type: str
                self.assertregex(
                    _subscenario_regex_start + r"SCENARIO ", _subscenario_beginning_line,
                    evidence=True,
                )
        if self.RESULT("The steps of the subscenario are displayed "
                       f"with the {ScenarioLogging.SCENARIO_STACK_INDENTATION_PATTERN!r} indentation pattern."):
            for _subscenario_step_text in (
                "STEP#1: Scenario logging",
            ):  # type: str
                for _subscenario_step_line in self.assertlines(_subscenario_step_text):  # type: str
                    self.assertregex(
                        _subscenario_regex_start + r"STEP#[0-9]+", _subscenario_step_line,
                        evidence=True,
                    )
        if self.RESULT("The 'ACTION: ' patterns of the subscenario actions are prefixed "
                       f"with the {ScenarioLogging.SCENARIO_STACK_INDENTATION_PATTERN!r} indentation pattern, "
                       f"then right-aligned with {ScenarioLogging.ACTION_RESULT_MARGIN} characters."):
            for _subscenario_action_text in (
                "This is a sample action.",
            ):  # type: str
                for _subscenario_action_line in self.assertlines(_subscenario_action_text):  # type: str
                    self.assertregex(
                        r"".join([
                            _subscenario_regex_start,
                            r" " * (ScenarioLogging.ACTION_RESULT_MARGIN - len("ACTION: ")),
                            r"ACTION: ",
                        ]),
                        _subscenario_action_line,
                        evidence=True,
                    )
        if self.RESULT("The 'RESULT: ' patterns of the of the subscenario expected results are prefixed "
                       f"with the {ScenarioLogging.SCENARIO_STACK_INDENTATION_PATTERN!r} indentation pattern, "
                       f"then right-aligned with {ScenarioLogging.ACTION_RESULT_MARGIN} characters."):
            for _subscenario_result_text in (
                "This is a sample expected result.",
            ):  # type: str
                for _subscenario_result_line in self.assertlines(_subscenario_result_text):  # type: str
                    self.assertregex(
                        r"".join([
                            _subscenario_regex_start,
                            r" " * (ScenarioLogging.ACTION_RESULT_MARGIN - len("RESULT: ")),
                            r"RESULT: ",
                        ]),
                        _subscenario_result_line,
                        evidence=True,
                    )
        if self.RESULT("The 'EVIDENCE: ' patterns of of the subscenario evidence are prefixed "
                       f"with the {ScenarioLogging.SCENARIO_STACK_INDENTATION_PATTERN!r} indentation pattern, "
                       f"then right-aligned with {ScenarioLogging.ACTION_RESULT_MARGIN} characters."):
            for _subscenario_evidence_text in (
                "Action evidence.",
                "Expected result evidence.",
            ):  # type: str
                for _subscenario_evidence_line in self.assertlines(_subscenario_evidence_text):  # type: str
                    self.assertregex(
                        r"".join([
                            _subscenario_regex_start,
                            r" " * (ScenarioLogging.ACTION_RESULT_MARGIN - len("EVIDENCE: ")),
                            r"EVIDENCE: ",
                        ]),
                        _subscenario_evidence_line,
                        evidence=True,
                    )
