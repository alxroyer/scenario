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


class Issue45(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        scenario.test.TestCase.__init__(
            self,
            title="Issue #45! Test scripts in packages",
            objective="Check that test scripts are loaded respecting their package belonging.",
            features=[],
        )

        self.addstep(ExecScenario(scenario.test.paths.PACKAGE_SCENARIO))
        self.addstep(CheckModuleName(ExecScenario.getinstance()))
        self.addstep(CheckLocalImport(ExecScenario.getinstance()))


class CheckModuleName(LogVerificationStep):

    def step(self):  # type: (...) -> None
        self.STEP("Module name")

        if self.RESULT("The `__package__` variable equals 'xyz'"):
            self.assertline(
                "__package__ = 'xyz'",
                evidence="`__package__` value",
            )


class CheckLocalImport(LogVerificationStep):

    def step(self):  # type: (...) -> None
        self.STEP("Local import")

        if self.RESULT(f"The scenario returned {scenario.ErrorCode.SUCCESS} (SUCCESS)."):
            self.assertequal(
                self.subprocess.returncode, scenario.ErrorCode.SUCCESS,
                evidence="Return code",
            )

        if self.RESULT("The test displayed the DATA value."):
            self.assertline(
                "DATA = ",
                evidence="`DATA` value",
            )
