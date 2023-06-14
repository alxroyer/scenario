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
import scenario.test

if True:
    from steps.common import LogVerificationStep as _LogVerificationStepImpl  # `LogVerificationStep` for inheritance.


class Logging200(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        from steps.common import ExecScenario

        scenario.test.TestCase.__init__(
            self,
            title="Log levels and classes",
            objective="Check log lines are tagged with a log level between DEBUG, INFO, WARNING and ERROR, and an optional log class.",
            features=[scenario.test.features.LOGGING],
        )

        self.addstep(ExecScenario(
            scenario.test.paths.LOGGER_SCENARIO,
            # Activate `LOGGER_DEBUG_CLASS` debugging.
            debug_classes=[scenario.test.data.scenarios.LoggerScenario.LOGGER_DEBUG_CLASS],
            # Explicitely disable log date/time for verification purposes in `CheckMainLoggerLogLevels` and `CheckClassLoggerLogLevels`.
            config_values={scenario.ConfigKey.LOG_DATETIME: False},
        ))
        self.addstep(CheckMainLoggerLogLevels(ExecScenario.getinstance()))
        self.addstep(CheckClassLoggerLogLevels(ExecScenario.getinstance()))


class CheckMainLoggerLogLevels(_LogVerificationStepImpl):

    def step(self):  # type: (...) -> None
        self.STEP("Main logger log levels")

        if self.RESULT("The 'Main logger error line' line is marked with the 'ERROR' log level."):
            _error_line = self.assertline("Main logger error line")  # type: str
            self.assertregex("^ *ERROR ", _error_line, evidence=True)

        if self.RESULT("The 'Main logger warning line' line is marked with the 'WARNING' log level."):
            _warning_line = self.assertline("Main logger warning line")  # type: str
            self.assertregex("^ *WARNING ", _warning_line, evidence=True)

        if self.RESULT("The 'Main logger info line' line is marked with the 'INFO' log level."):
            _info_line = self.assertline("Main logger info line")  # type: str
            self.assertregex("^ *INFO ", _info_line, evidence=True)

        if self.RESULT("The 'Main logger debug line' line is marked with the 'DEBUG' log level."):
            _debug_line = self.assertline("Main logger debug line")  # type: str
            self.assertregex("^ *DEBUG ", _debug_line, evidence=True)


class CheckClassLoggerLogLevels(_LogVerificationStepImpl):

    def step(self):  # type: (...) -> None
        from steps.common import ExecScenario

        self.STEP("Class logger log levels")

        _error_line = f"'{scenario.test.data.scenarios.LoggerScenario.LOGGER_DEBUG_CLASS}' logger error line"  # type: str
        if self.RESULT(f"The {_error_line!r} line is marked with the 'ERROR' log level "
                       f"and the '{scenario.test.data.scenarios.LoggerScenario.LOGGER_DEBUG_CLASS}' log class."):
            _error_line = self.assertline(_error_line)
            self.assertregex(r"^ *ERROR +\[%s\] " % scenario.test.data.scenarios.LoggerScenario.LOGGER_DEBUG_CLASS, _error_line, evidence=True)

        _warning_line = f"'{scenario.test.data.scenarios.LoggerScenario.LOGGER_DEBUG_CLASS}' logger warning line"  # type: str
        if self.RESULT(f"The {_warning_line!r} line is marked with the 'WARNING' log level "
                       f"and the '{scenario.test.data.scenarios.LoggerScenario.LOGGER_DEBUG_CLASS}' log class."):
            _warning_line = self.assertline(_warning_line)
            self.assertregex(r"^ *WARNING +\[%s\] " % scenario.test.data.scenarios.LoggerScenario.LOGGER_DEBUG_CLASS, _warning_line, evidence=True)

        _info_line = f"'{scenario.test.data.scenarios.LoggerScenario.LOGGER_DEBUG_CLASS}' logger info line"  # type: str
        if self.RESULT(f"The {_info_line!r} line is marked with the 'INFO' log level "
                       f"and the '{scenario.test.data.scenarios.LoggerScenario.LOGGER_DEBUG_CLASS}' log class."):
            _info_line = self.assertline(_info_line)
            self.assertregex(r"^ *INFO +\[%s\] " % scenario.test.data.scenarios.LoggerScenario.LOGGER_DEBUG_CLASS, _info_line, evidence=True)

        _debug_line = f"'{scenario.test.data.scenarios.LoggerScenario.LOGGER_DEBUG_CLASS}' logger debug line"
        if scenario.test.data.scenarios.LoggerScenario.LOGGER_DEBUG_CLASS in (self.getexecstep(ExecScenario).debug_classes or []):
            if self.RESULT(f"The {_debug_line!r} line is displayed, "
                           f"and marked with the 'DEBUG' log level and the '{scenario.test.data.scenarios.LoggerScenario.LOGGER_DEBUG_CLASS}' log class."):
                _debug_line = self.assertline(_debug_line)
                self.assertregex(r"^ *DEBUG +\[%s\] " % scenario.test.data.scenarios.LoggerScenario.LOGGER_DEBUG_CLASS, _debug_line, evidence=True)
        else:
            if self.RESULT(f"The {_debug_line!r} line is not displayed."):
                self.assertnoline(f"'{scenario.test.data.scenarios.LoggerScenario.LOGGER_DEBUG_CLASS}' logger debug line", evidence=True)
