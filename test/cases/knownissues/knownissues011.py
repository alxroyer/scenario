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


class KnownIssues011(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        from steps.common import CheckScenarioLogExpectations, ExecScenario, ParseScenarioLog

        scenario.test.TestCase.__init__(
            self,
            title="Known issues --doc-only",
            objective="Check that known issues when declared at the definition level still generate warnings in --doc-only.",
            features=[scenario.test.features.KNOWN_ISSUES, scenario.test.features.DOC_ONLY],
        )

        self.section("Regular execution")
        self.addstep(ExecScenario(scenario.test.paths.KNOWN_ISSUES_SCENARIO, doc_only=False))
        self.addstep(ParseScenarioLog(ExecScenario.getinstance(0)))
        self.addstep(CheckScenarioLogExpectations(ParseScenarioLog.getinstance(0), scenario.test.data.scenarioexpectations(
            scenario.test.paths.KNOWN_ISSUES_SCENARIO, doc_only=False,
            # Check all steps are executed.
            steps=True, stats=True,
            # Error details makes the step check the warnings, i.e. known issues.
            error_details=True,
        )))

        self.section("Documentation generation")
        self.addstep(ExecScenario(scenario.test.paths.KNOWN_ISSUES_SCENARIO, doc_only=True))
        self.addstep(ParseScenarioLog(ExecScenario.getinstance(1)))
        self.addstep(CheckScenarioLogExpectations(ParseScenarioLog.getinstance(1), scenario.test.data.scenarioexpectations(
            scenario.test.paths.KNOWN_ISSUES_SCENARIO, doc_only=True,
            # Check all steps are defined.
            steps=True, stats=True,
            # Error details makes the step check the warnings, i.e. known issues.
            error_details=True,
        )))
