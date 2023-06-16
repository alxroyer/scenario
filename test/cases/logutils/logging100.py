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
    from steps.common import LogVerificationStep as _LogVerificationStepImpl  # `LogVerificationStep` used for inheritance.


class Logging100(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        from steps.common import ExecScenario

        scenario.test.TestCase.__init__(
            self,
            title="Logging timestamps",
            objective="Check log lines are displayed with timestamps (by default), and the ability to avoid them.",
            features=[scenario.test.features.LOGGING],
        )

        self.section("Logging date/time enabled by default")
        self.addstep(ExecScenario(scenario.test.paths.SIMPLE_SCENARIO, config_values={scenario.ConfigKey.LOG_DATETIME: None}))
        self.addstep(CheckLoggingDateTime(ExecScenario.getinstance(0)))

        self.section("Logging date/time explicitly enabled")
        self.addstep(ExecScenario(scenario.test.paths.SIMPLE_SCENARIO, config_values={scenario.ConfigKey.LOG_DATETIME: True}))
        self.addstep(CheckLoggingDateTime(ExecScenario.getinstance(1)))

        self.section("Logging date/time disabled")
        self.addstep(ExecScenario(scenario.test.paths.SIMPLE_SCENARIO, config_values={scenario.ConfigKey.LOG_DATETIME: False}))
        self.addstep(CheckNoLoggingDateTime(ExecScenario.getinstance(2)))


class CheckLoggingDateTime(_LogVerificationStepImpl):

    def step(self):  # type: (...) -> None
        self.STEP("Logging date/time enabled")

        if self.RESULT("Each output line starts with a ISO8601 timestamp."):
            _lines = 0  # type: int
            for _line in self.subprocess.stdout.splitlines():  # type: bytes
                self.assertregex(rb'^%s ' % self.tobytes(scenario.datetime.ISO8601_REGEX), _line, evidence=False)
                _lines += 1
            self.assertgreater(_lines, 0, evidence=f"Number of lines starting with {scenario.datetime.ISO8601_REGEX!r}")


class CheckNoLoggingDateTime(_LogVerificationStepImpl):

    def step(self):  # type: (...) -> None
        self.STEP("Logging date/time disabled")

        if self.RESULT("No output line starts with a ISO8601 timestamp."):
            _lines = 0  # type: int
            for _line in self.subprocess.stdout.splitlines():  # type: bytes
                self.assertnotregex(rb'^%s ' % self.tobytes(scenario.datetime.ISO8601_REGEX), _line, evidence=False)
                _lines += 1
            self.assertgreater(_lines, 0, evidence=f"Number of lines not starting with {scenario.datetime.ISO8601_REGEX!r}")
