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

import typing

import scenario
import scenario.test

if typing.TYPE_CHECKING:
    from campaigns.steps.execution import ExecCampaign as _ExecCampaignType


class CheckCampaignScenarioReports(scenario.test.VerificationStep):

    def __init__(
            self,
            exec_step,  # type: _ExecCampaignType
            campaign_expectations,  # type: scenario.test.CampaignExpectations
    ):  # type: (...) -> None
        from scenarioexecution.steps.execution import ExecScenario
        from scenarioreport.steps.expectations import CheckScenarioReportExpectations

        scenario.test.VerificationStep.__init__(self, exec_step)

        self.campaign_expectations = campaign_expectations  # type: scenario.test.CampaignExpectations
        self._scenario_report_checker = CheckScenarioReportExpectations(
            exec_step=ExecScenario(scenario.Path(), doc_only=exec_step.doc_only),  # Unused, but the *doc-only* property.
            scenario_expectations=scenario.test.ScenarioExpectations(),  # Unused.
        )  # type: CheckScenarioReportExpectations

    def step(self):  # type: (...) -> None
        from campaigns.steps.execution import ExecCampaign
        from campaigns.steps.outdirfiles import CampaignScenarioResultsReader
        from scenario._jsondictutils import JsonDict  # noqa  ## Access to protected module

        self.STEP("Scenario reports")

        assert self.campaign_expectations.test_suite_expectations is not None
        for _test_suite_expectations in self.campaign_expectations.test_suite_expectations:  # type: scenario.test.TestSuiteExpectations
            assert _test_suite_expectations.test_case_expectations is not None
            for _test_case_expectations in _test_suite_expectations.test_case_expectations:  # type: scenario.test.ScenarioExpectations

                # Read the scenario report file.
                _json = {}  # type: scenario.types.JsonDict
                assert _test_case_expectations.script_path is not None
                if self.ACTION(f"Read the scenario report file for '{_test_case_expectations.script_path}'."):
                    _scenario_results = CampaignScenarioResultsReader(self.getexecstep(ExecCampaign).final_outdir_path)  # type: CampaignScenarioResultsReader
                    _report_path = _scenario_results.get(_test_case_expectations.script_path).report.path  # type: typing.Optional[scenario.Path]
                    assert _report_path is not None, f"Report path missing for '{_test_case_expectations.script_path}'"
                    _json = JsonDict.readfile(_report_path)
                    self.debug("%s", scenario.debug.jsondump(_json, indent=2),
                               extra={self.Extra.LONG_TEXT_MAX_LINES: 10})

                self._scenario_report_checker.checkscenarioreport(
                    json_scenario=_json,
                    scenario_expectations=_test_case_expectations,
                )
