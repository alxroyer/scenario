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
    from steps.common import ExecScenario as _ExecScenarioImpl  # `ExecScenario` used for inheritance.


class FailingScenario002(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        from steps.common import CheckScenarioLogExpectations, ExecScenario, ParseScenarioLog

        scenario.test.TestCase.__init__(
            self,
            title="Continue on error",
            description="Check steps following an error step continue being executed when the *continue_on_error* option is enabled.",
        )
        self.covers(
            scenario.test.reqs.ERROR_HANDLING,
        )

        self.section("Regular execution")
        self.addstep(ExecFailingScenario(continue_on_error=False))
        self.addstep(ParseScenarioLog(ExecScenario.getinstance(0)))
        self.addstep(CheckScenarioLogExpectations(ParseScenarioLog.getinstance(0), scenario.test.data.scenarioexpectations(
            scenario.test.paths.FAILING_SCENARIO,
            # Generate the expectation details about steps, actions and expected results, in order to check how the error affects them.
            steps=True, actions_results=True, continue_on_error=False,
            # Check details about error info and statistics as well.
            error_details=True, stats=True,
        )))

        self.section("*continue_on_error* execution")
        self.addstep(ExecFailingScenario(continue_on_error=True))
        self.addstep(ParseScenarioLog(ExecScenario.getinstance(1)))
        self.addstep(CheckScenarioLogExpectations(ParseScenarioLog.getinstance(1), scenario.test.data.scenarioexpectations(
            scenario.test.paths.FAILING_SCENARIO,
            # Generate the expectation details about steps, actions and expected results, in order to check how the error affects them.
            steps=True, actions_results=True, continue_on_error=True,
            # Check details about error info and statistics as well.
            error_details=True, stats=True,
        )))


class ExecFailingScenario(_ExecScenarioImpl):

    def __init__(
            self,
            continue_on_error,  # type: bool
    ):  # type: (...) -> None
        _ExecScenarioImpl.__init__(self, scenario.test.paths.FAILING_SCENARIO)

        self.continue_on_error = continue_on_error  # type: bool

    def step(self):  # type: (...) -> None
        self.STEP("*continue_on_error* execution" if self.continue_on_error
                  else "Regular execution")

        if self.ACTION(f"Execute the '{scenario.test.paths.FAILING_SCENARIO}' scenario, "
                       f"with *continue_on_error* {'enabled' if self.continue_on_error else 'disabled'}. "
                       f"Catch the output."):
            self.subprocess = scenario.test.ScenarioSubProcess(scenario.test.paths.FAILING_SCENARIO)
            self.subprocess.setconfigvalue(scenario.ConfigKey.CONTINUE_ON_ERROR, str(int(self.continue_on_error)))
            self.subprocess.expectsuccess(False)
            self.subprocess.setlogger(self).run()
