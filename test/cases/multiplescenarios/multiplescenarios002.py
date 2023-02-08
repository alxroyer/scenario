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

# Steps:
from steps.common import ExecScenario
from .steps.mainlog import CheckMultipleScenariosMainLog
from .steps.parser import ParseFinalResultsLog
from .steps.expectations import CheckFinalResultsLogExpectations


class MultipleScenarios002(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        scenario.test.TestCase.__init__(
            self,
            title="Multiple scenarios --doc-only",
            objective="Check that several scenarios can be executed with a single scenario launcher invocation with the --doc-only option set.",
            features=[scenario.test.features.MULTIPLE_SCENARIO_EXECUTION, scenario.test.features.DOC_ONLY],
        )

        self.section("Test execution")
        self.addstep(ExecScenario(
            [scenario.test.paths.FAILING_SCENARIO, scenario.test.paths.SUPERSCENARIO_SCENARIO],
            doc_only=False,
            expected_return_code=scenario.ErrorCode.TEST_ERROR,
        ))
        self.addstep(CheckMultipleScenariosMainLog(ExecScenario.getinstance(0)))
        self.addstep(ParseFinalResultsLog(ExecScenario.getinstance(0)))
        self.addstep(CheckFinalResultsLogExpectations(ParseFinalResultsLog.getinstance(0), scenario_expectations=[
            scenario.test.data.scenarioexpectations(scenario.test.paths.FAILING_SCENARIO, doc_only=False),
            scenario.test.data.scenarioexpectations(scenario.test.paths.SUPERSCENARIO_SCENARIO, doc_only=False),
        ]))

        self.section("Documentation generation")
        self.addstep(ExecScenario(
            [scenario.test.paths.FAILING_SCENARIO, scenario.test.paths.SUPERSCENARIO_SCENARIO],
            doc_only=True,
            expected_return_code=scenario.ErrorCode.SUCCESS,
        ))
        self.addstep(CheckMultipleScenariosMainLog(ExecScenario.getinstance(1)))
        self.addstep(ParseFinalResultsLog(ExecScenario.getinstance(1)))
        self.addstep(CheckFinalResultsLogExpectations(ParseFinalResultsLog.getinstance(1), scenario_expectations=[
            scenario.test.data.scenarioexpectations(scenario.test.paths.FAILING_SCENARIO, doc_only=True),
            scenario.test.data.scenarioexpectations(scenario.test.paths.SUPERSCENARIO_SCENARIO, doc_only=True),
        ]))
