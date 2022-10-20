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

import scenario
import scenario.test

# Steps:
from steps.common import ExecScenario
from steps.common import LogVerificationStep


class Logging420(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        scenario.test.TestCase.__init__(
            self,
            title="Additional user indentation",
            objective="Check that the user test can add and remove extra indentation.",
            features=[scenario.test.features.LOGGING],
        )

        self.addstep(ExecUserIndentation(scenario.test.paths.LOGGING_INDENTATION_SCENARIO))
        self.addstep(CheckUserIndentation(ExecUserIndentation.getinstance()))


class ExecUserIndentation(ExecScenario):
    """
    .. note:: Step reused in 'logging421.py'.
    """

    def __init__(
            self,
            # Subset of parameters from `ExecScenario`:
            scenario_path,  # type: scenario.Path
            subscenario=None,  # type: scenario.Path
            scenario_stack_indentation="",  # type: str
    ):  # type: (...) -> None
        ExecScenario.__init__(self, scenario_path, subscenario=subscenario, config_values={scenario.ConfigKey.LOG_COLOR_ENABLED: "0"})

        self.scenario_stack_indentation = scenario_stack_indentation  # type: str


class CheckUserIndentation(LogVerificationStep):
    """
    .. note:: Step reused in 'logging421.py'.
    """

    def __init__(
            self,
            exec_step,  # type: ExecUserIndentation
    ):  # type: (...) -> None
        LogVerificationStep.__init__(self, exec_step)

        self._action_result_margin = -1  # type: int
        self._evidence_margin = -1  # type: int
        self._logging_margin = -1  # type: int
        self._log_level_len = -1  # type: int

    def step(self):  # type: (...) -> None
        self.STEP("Additional user indentation")

        self._checkindentation("#0", main_indentation=0, class_logger_indentation=0)
        # #1: Add indentation with this scenario class logger.
        self._checkindentation("#1", main_indentation=0, class_logger_indentation=4)
        # #2: Add indentation with this scenario class logger again.
        self._checkindentation("#2", main_indentation=0, class_logger_indentation=8)
        # #3: Add indentation with the main logger.
        self._checkindentation("#3", main_indentation=4, class_logger_indentation=8)
        # #4: Add indentation with the main logger again.
        self._checkindentation("#4", main_indentation=8, class_logger_indentation=8)
        # #5: Remove indentation with this scenario class logger.
        self._checkindentation("#5", main_indentation=8, class_logger_indentation=4)
        # #6: Reset indentation with the main logger.
        self._checkindentation("#6", main_indentation=0, class_logger_indentation=4)
        # #7: Reset indentation with this scenario class logger.
        self._checkindentation("#7", main_indentation=0, class_logger_indentation=0)

    def _checkindentation(
            self,
            search_pattern,  # type: str
            main_indentation,  # type: int
            class_logger_indentation,  # type: int
    ):  # type: (...) -> None
        assert isinstance(self.exec_step, ExecUserIndentation)

        # Pre-build useful regex strings.
        _scenario_stack_indentation_rgx = self.exec_step.scenario_stack_indentation.replace("|", r"\|")  # type: str
        _main_indentation_rgx = r" {%d}" % main_indentation  # type: str
        _class_logger_indentation_rgx = r" {%d}" % class_logger_indentation  # type: str

        _result = f"{search_pattern!r} lines are displayed with "  # type: str
        if self.exec_step.scenario_stack_indentation:
            _result += f"{self.exec_step.scenario_stack_indentation!r} for scenario stack indentation, "
        _result += f"r{_main_indentation_rgx!r} for main indentation, "
        _result += f"and r{_class_logger_indentation_rgx!r} for class logger indentation."
        if self.RESULT(_result):
            for _line in self.assertlines(search_pattern + ": "):
                # Skip "STEP#%d:" lines.
                if _line.startswith(f"STEP{search_pattern}: "):
                    continue
                if _line.startswith(f"{self.exec_step.scenario_stack_indentation}STEP{search_pattern}: "):
                    continue
                # Skip actions that introduce indentation settings.
                if ("Add indentation" in _line) or ("Remove indentation" in _line) or ("Reset indentation" in _line):
                    continue
                self.evidence(f"Line: {_line!r}")

                if "ACTION: " in _line:
                    if self._action_result_margin < 0:
                        self._action_result_margin = _line.find("ACTION: ") - len(self.exec_step.scenario_stack_indentation) - main_indentation
                        self.evidence(f"Action/result margin: {self._action_result_margin}")
                    self.assertregex(
                        r"".join([
                            r"^",
                            _scenario_stack_indentation_rgx,
                            r" {%d}" % self._action_result_margin,
                            r"ACTION: ",
                            _main_indentation_rgx,
                            r"%s: [A-Z]" % search_pattern,
                        ]),
                        _line,
                        evidence="Action indentation",
                    )
                elif "EVIDENCE: " in _line:
                    if self._evidence_margin < 0:
                        self._evidence_margin = _line.find("EVIDENCE: ") - len(self.exec_step.scenario_stack_indentation) - main_indentation
                        self.evidence(f"Evidence margin: {self._evidence_margin}")
                    self.assertregex(
                        r"".join([
                            _scenario_stack_indentation_rgx,
                            r" {%d}" % self._evidence_margin,
                            r"EVIDENCE: ",
                            _main_indentation_rgx,
                            r"  -> %s: [A-Z]" % search_pattern,
                        ]),
                        _line,
                        evidence="Evidence indentation",
                    )
                elif "INFO" in _line:
                    if self._logging_margin < 0:
                        self._logging_margin = _line.find("INFO") - len(self.exec_step.scenario_stack_indentation) - main_indentation
                        self.evidence(f"Logging margin: {self._logging_margin}")
                    if self._log_level_len < 0:
                        _non_stripped = _line[
                            # Starting position computation.
                            len(self.exec_step.scenario_stack_indentation)
                            + main_indentation
                            + self._logging_margin
                            + len("INFO")
                            # Keep the end of the line from the position computed above.
                            :
                        ]  # type: str
                        self._log_level_len = len("INFO") + len(_non_stripped) - len(_non_stripped.lstrip())
                        self.evidence(f"Log level field length: {self._log_level_len}")

                    if f"[{scenario.test.paths.LOGGING_INDENTATION_SCENARIO}] " not in _line:
                        self.assertregex(
                            r"".join([
                                _scenario_stack_indentation_rgx,
                                _main_indentation_rgx,
                                r" {%d}" % self._logging_margin,
                                r".{%d}" % self._log_level_len,
                                r"%s: [A-Z]" % search_pattern,
                            ]),
                            _line,
                            evidence="Main logger indentation",
                        )
                    else:
                        self.assertregex(
                            r"".join([
                                _scenario_stack_indentation_rgx,
                                _main_indentation_rgx,
                                r" {%d}" % self._logging_margin,
                                r".{%d}" % self._log_level_len,
                                r"\[%s\] " % scenario.test.paths.LOGGING_INDENTATION_SCENARIO.prettypath,
                                _class_logger_indentation_rgx,
                                r"%s: [A-Z]" % search_pattern,
                            ]),
                            _line,
                            evidence="Class logger indentation",
                        )
                else:
                    self.fail(f"Invalid line: {_line!r}")
