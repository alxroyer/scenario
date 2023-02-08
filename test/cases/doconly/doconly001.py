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

# Steps:
from steps.common import ExecScenario
from steps.common import ParseScenarioLog, CheckScenarioLogExpectations


class DocOnly001(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        scenario.test.TestCase.__init__(
            self,
            title="--doc-only execution",
            objective="Check the --doc-only execution succeeds even for a failing scenario.",
            features=[scenario.test.features.DOC_ONLY],
        )

        self.section("Test execution in failure")
        self.addstep(ExecScenario(scenario.test.paths.FAILING_SCENARIO, doc_only=False, expected_return_code=scenario.ErrorCode.TEST_ERROR))
        self.addstep(ParseScenarioLog(ExecScenario.getinstance(0)))
        self.addstep(CheckScenarioLogExpectations(ParseScenarioLog.getinstance(0), scenario.test.data.scenarioexpectations(
            scenario.test.paths.FAILING_SCENARIO,
            steps=True, stats=True, doc_only=False,
        )))

        self.section("Documentation generation")
        self.addstep(ExecScenario(scenario.test.paths.FAILING_SCENARIO, doc_only=True, expected_return_code=scenario.ErrorCode.SUCCESS))
        self.addstep(ParseScenarioLog(ExecScenario.getinstance(1)))
        self.addstep(CheckScenarioLogExpectations(ParseScenarioLog.getinstance(1), scenario.test.data.scenarioexpectations(
            scenario.test.paths.FAILING_SCENARIO,
            steps=True, stats=True, doc_only=True,
        )))
