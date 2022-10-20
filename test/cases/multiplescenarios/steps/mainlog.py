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

import scenario.test

# Related steps:
from steps.logverifications import LogVerificationStep


class CheckMultipleScenariosMainLog(LogVerificationStep):

    def __init__(
            self,
            exec_step,  # type: scenario.test.AnyExecutionStepType
    ):  # type: (...) -> None
        LogVerificationStep.__init__(self, exec_step)

    def step(self):  # type: (...) -> None
        self.STEP("Multiple scenario log output")

        if self.RESULT("The '%s' scenario has been executed." % scenario.test.paths.FAILING_SCENARIO):
            self.assertline("SCENARIO '%s'" % scenario.test.paths.FAILING_SCENARIO, evidence=True)
            self.assertline("END OF '%s'" % scenario.test.paths.FAILING_SCENARIO, evidence=True)

        if self.RESULT("The '%s' scenario has been executed." % scenario.test.paths.SUPERSCENARIO_SCENARIO):
            self.assertline("SCENARIO '%s'" % scenario.test.paths.SUPERSCENARIO_SCENARIO, evidence=True)
            self.assertline("END OF '%s'" % scenario.test.paths.SUPERSCENARIO_SCENARIO, evidence=True)

        if self.RESULT("The '%s' scenario has been executed before the '%s' one."
                       % (scenario.test.paths.FAILING_SCENARIO, scenario.test.paths.SUPERSCENARIO_SCENARIO)):
            self.assertless(
                self._scenarioendpos(scenario.test.paths.FAILING_SCENARIO), self._scenariostartpos(scenario.test.paths.SUPERSCENARIO_SCENARIO),
                evidence="'%s' (end) v/s '%s' (start) positions" % (scenario.test.paths.FAILING_SCENARIO, scenario.test.paths.SUPERSCENARIO_SCENARIO),
            )

    def _scenariostartpos(
            self,
            path,  # type: scenario.Path
    ):  # type: (...) -> int
        return self.subprocess.stdout.find(self.tobytes("SCENARIO '%s'" % path))

    def _scenarioendpos(
            self,
            path,  # type: scenario.Path
    ):  # type: (...) -> int
        return self.subprocess.stdout.find(self.tobytes("END OF '%s'" % path))
