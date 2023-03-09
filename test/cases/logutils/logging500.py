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


class Logging500(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        from steps.common import ExecScenario

        scenario.test.TestCase.__init__(
            self,
            title="Console logging",
            objective="Check that logging is displayed by default in the console, and that it can be disabled.",
            features=[scenario.test.features.LOGGING],
        )

        self.section("Console output enabled by default")
        self.addstep(ExecScenario(scenario.test.paths.SIMPLE_SCENARIO, config_values={scenario.ConfigKey.LOG_CONSOLE: None}))
        self.addstep(CheckConsoleLogging(ExecScenario.getinstance(0)))

        self.section("Console output explicitely enabled")
        self.addstep(ExecScenario(scenario.test.paths.SIMPLE_SCENARIO, config_values={scenario.ConfigKey.LOG_CONSOLE: True}))
        self.addstep(CheckConsoleLogging(ExecScenario.getinstance(1)))

        self.section("Console output disabled")
        self.addstep(ExecScenario(scenario.test.paths.SIMPLE_SCENARIO, config_values={scenario.ConfigKey.LOG_CONSOLE: False}))
        self.addstep(CheckNoConsoleLogging(ExecScenario.getinstance(2)))


class CheckConsoleLogging(scenario.test.VerificationStep):

    def step(self):  # type: (...) -> None
        self.STEP("Console logging")

        if self.RESULT("The standard output is not empty."):
            self.assertisnotempty(
                self.subprocess.stdout,
                evidence="Standard output",
            )
        if self.RESULT("The standard error is empty."):
            self.assertisempty(
                self.subprocess.stderr,
                evidence="Standard error",
            )


class CheckNoConsoleLogging(scenario.test.VerificationStep):

    def step(self):  # type: (...) -> None
        self.STEP("No console logging")

        if self.RESULT("The standard output is empty."):
            self.assertisempty(
                self.subprocess.stdout,
                evidence="Standard output",
            )
        if self.RESULT("The standard error is empty."):
            self.assertisempty(
                self.subprocess.stderr,
                evidence="Standard error",
            )
        if self.RESULT(f"In spite nothing has been displayed in the console, the scenario returned {scenario.ErrorCode.SUCCESS} (SUCCESS)."):
            self.assertequal(
                self.subprocess.returncode, scenario.ErrorCode.SUCCESS,
                evidence="Return code",
            )
