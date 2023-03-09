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


class MultipleScenarios001(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        from multiplescenarios.steps.expectations import CheckFinalResultsLogExpectations
        from multiplescenarios.steps.mainlog import CheckMultipleScenariosMainLog
        from multiplescenarios.steps.parser import ParseFinalResultsLog
        from steps.common import ExecScenario

        scenario.test.TestCase.__init__(
            self,
            title="Multiple scenarios execution",
            objective=(
                "Check that several scenarios can be executed with a single scenario launcher invocation, "
                "and that error display makes it easy to investigate on errors."
            ),
            features=[scenario.test.features.MULTIPLE_SCENARIO_EXECUTION, scenario.test.features.ERROR_HANDLING],
        )

        self.addstep(ExecScenario(
            [scenario.test.paths.FAILING_SCENARIO, scenario.test.paths.SUPERSCENARIO_SCENARIO],
            expected_return_code=scenario.ErrorCode.TEST_ERROR,
        ))
        self.addstep(CheckMultipleScenariosMainLog(ExecScenario.getinstance()))
        self.addstep(ParseFinalResultsLog(ExecScenario.getinstance()))
        self.addstep(CheckFinalResultsLogExpectations(ParseFinalResultsLog.getinstance(), scenario_expectations=[
            scenario.test.data.scenarioexpectations(scenario.test.paths.FAILING_SCENARIO, error_details=True),
            scenario.test.data.scenarioexpectations(scenario.test.paths.SUPERSCENARIO_SCENARIO),
        ]))
