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

import scenario.test

if True:
    from logutils.steps.logoutfile import LogOutfileVerificationStep as _LogOutfileVerificationStepImpl  # `LogOutfileVerificationStep` for inheritance.


class Logging510(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        from logutils.logging500 import CheckNoConsoleLogging
        from steps.common import ExecScenario

        scenario.test.TestCase.__init__(
            self,
            title="File logging",
            description="Check that logging can be saved into a file, even though console logging is turned off.",
            features=[scenario.test.features.LOGGING],
        )

        self.section("File logging activation (console logging enabled by default)")
        self.addstep(ExecScenario(
            scenario.test.paths.LOGGER_SCENARIO,
            log_outfile=True,
            config_values={
                scenario.ConfigKey.LOG_CONSOLE: None,
                # Disable log colors, so that `CheckSameOutputs` can compare the console output and the log outfile.
                scenario.ConfigKey.LOG_COLOR_ENABLED: False,
            },
        ))
        self.addstep(CheckFileLogging(ExecScenario.getinstance(0)))
        self.addstep(CheckSameOutputs(ExecScenario.getinstance(0)))

        self.section("File logging activation while console logging is disabled")
        self.addstep(ExecScenario(
            scenario.test.paths.LOGGER_SCENARIO,
            log_outfile=True,
            config_values={
                scenario.ConfigKey.LOG_CONSOLE: False,
                # Enable log colors, so that `CheckFileLogging` can check no colors are set in the log outfile.
                scenario.ConfigKey.LOG_COLOR_ENABLED: True,
            },
        ))
        self.addstep(CheckNoConsoleLogging(ExecScenario.getinstance(1)))
        self.addstep(CheckFileLogging(ExecScenario.getinstance(1)))


class CheckFileLogging(_LogOutfileVerificationStepImpl):

    def step(self):  # type: (...) -> None
        self.STEP("File logging")

        if self.RESULT("The log outfile exists."):
            self.assertisfile(
                self.log_path,
                evidence="Log outfile",
            )
        _file_content = b''  # type: bytes
        if self.RESULT("The log outfile is not empty."):
            _file_content = self.log_path.read_bytes()
            self.assertisnotempty(
                _file_content,
                evidence="Log outfile content",
            )
        if self.RESULT("The log outfile is not colorized."):
            for _pattern in (
                b'Main logger error line',
                b'Main logger warning line',
                b'Main logger info line',
                b'Main logger debug line',
            ):  # type: bytes
                self.assertnocolor(
                    self.assertline(_pattern, output=_file_content),
                    evidence="No color",
                )


class CheckSameOutputs(_LogOutfileVerificationStepImpl):

    def step(self):  # type: (...) -> None
        self.STEP("File v/s console output comparison")

        if self.RESULT("The log outfile content is the same as the console content."):
            self.assertequal(
                self.log_path.read_bytes(),
                self.subprocess.stdout,
                evidence="Outfile v/s console",
            )
