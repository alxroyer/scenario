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

import logging
import typing

import scenario
import scenario.test

# Steps:
from steps.common import ExecScenario
from steps.common import LogVerificationStep
# Related scenarios:
from loggerscenario import LoggerScenario


class Logging300(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        scenario.test.TestCase.__init__(
            self,
            title="Log colors",
            objective=(
                "Check log lines are colored by default regarding their log level in the console, "
                "that class logger message colors can be parameterized, "
                "and that log colors can be disabled."
            ),
            features=[scenario.test.features.LOGGING],
        )

        self.section("Log colors enabled by default")
        self.addstep(ExecScenario(
            scenario.test.paths.LOGGER_SCENARIO, debug_classes=[LoggerScenario.LOGGER_DEBUG_CLASS],
            config_values={scenario.ConfigKey.LOG_COLOR_ENABLED: None},
        ))
        self.addstep(CheckLogColors(ExecScenario.getinstance(0)))

        self.section("Log colors explicitely enabled")
        self.addstep(ExecScenario(
            scenario.test.paths.LOGGER_SCENARIO, debug_classes=[LoggerScenario.LOGGER_DEBUG_CLASS],
            config_values={scenario.ConfigKey.LOG_COLOR_ENABLED: "1"},
        ))
        self.addstep(CheckLogColors(ExecScenario.getinstance(1)))

        self.section("Log colors disabled")
        self.addstep(ExecScenario(
            scenario.test.paths.LOGGER_SCENARIO, debug_classes=[LoggerScenario.LOGGER_DEBUG_CLASS],
            config_values={scenario.ConfigKey.LOG_COLOR_ENABLED: "0"},
        ))
        self.addstep(CheckLogColors(ExecScenario.getinstance(2)))


class CheckLogColors(LogVerificationStep):

    def step(self):  # type: (...) -> None
        if self.getexecstep(ExecScenario).getboolconfigvalue(scenario.ConfigKey.LOG_COLOR_ENABLED, default=True):
            self.STEP("Log colors")
        else:
            self.STEP("No log colors")

        # Main logger lines.
        self._checkline(None, logging.ERROR, "Main logger error line")
        self._checkline(None, logging.WARNING, "Main logger warning line")
        self._checkline(None, logging.INFO, "Main logger info line")
        self._checkline(None, logging.DEBUG, "Main logger debug line")

        # 'sample-log' logger lines.
        self._checkline("sample-log", logging.ERROR, "'sample-log' logger error line")
        self._checkline("sample-log", logging.WARNING, "'sample-log' logger warning line")
        self._checkline("sample-log", logging.INFO, "'sample-log' logger info line")
        self._checkline("sample-log", logging.DEBUG, "'sample-log' logger debug line")

    def _checkline(
            self,
            log_class,  # type: typing.Optional[str]
            log_level,  # type: int
            search,  # type: str
    ):  # type: (...) -> None
        _level_dict = {
            logging.ERROR: ("ERROR", "red", scenario.Console.Color.RED91),
            logging.WARNING: ("WARNING", "yellow", scenario.Console.Color.YELLOW33),
            logging.INFO: ("INFO", "white", scenario.Console.Color.WHITE01),
            logging.DEBUG: ("DEBUG", "grey", scenario.Console.Color.DARKGREY02),
        }  # type: typing.Dict[int, typing.Tuple[str, str, scenario.Console.Color]]
        assert log_level in _level_dict
        _log_level_name = _level_dict[log_level][0]  # type: str
        _log_level_color_name = _level_dict[log_level][1]  # type: str
        _log_level_color = _level_dict[log_level][2]  # type: scenario.Console.Color

        if self.getexecstep(ExecScenario).getboolconfigvalue(scenario.ConfigKey.LOG_COLOR_ENABLED, default=True):
            if log_class is None:
                if self.RESULT(f"The {search!r} line is {_log_level_color_name}-colored."):
                    _line = self.assertline(search)  # type: str
                    self.assertcolor(_line, _log_level_name, _log_level_color, evidence=True)
                    self.assertcolor(_line, search, _log_level_color, evidence=True)
            else:
                if self.RESULT(f"The {search!r} line log level is {_log_level_color_name}-colored, the message is blue-colored."):
                    _line = self.assertline(search)  # type already defined above
                    self.assertcolor(_line, _log_level_name, _log_level_color, evidence=True)
                    self.assertcolor(_line, f"[{log_class}] {search}", scenario.Console.Color.LIGHTBLUE36, evidence=True)
        else:
            if self.RESULT(f"The {search!r} line is not colored."):
                _line = self.assertline(search)  # type already defined above
                self.assertnocolor(_line, evidence=True)
