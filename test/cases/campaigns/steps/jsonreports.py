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

import json
import typing

import scenario
import scenario.test
if typing.TYPE_CHECKING:
    from scenario._typing import JsonDictType as _JsonDictType  # noqa  ## Access to protected module

if typing.TYPE_CHECKING:
    from campaigns.steps.execution import ExecCampaign as _ExecCampaignType


class CheckCampaignJsonReports(scenario.test.VerificationStep):

    def __init__(
            self,
            exec_step,  # type: _ExecCampaignType
            campaign_expectations,  # type: scenario.test.CampaignExpectations
    ):  # type: (...) -> None
        from campaigns.steps.outdirfiles import CampaignOutdirFilesManager
        from jsonreport.steps.expectations import CheckJsonReportExpectations
        from scenarioexecution.steps.execution import ExecScenario

        scenario.test.VerificationStep.__init__(self, exec_step)

        self.campaign_expectations = campaign_expectations  # type: scenario.test.CampaignExpectations
        self._outfiles = CampaignOutdirFilesManager(exec_step)  # type: CampaignOutdirFilesManager
        self._json_report_checker = CheckJsonReportExpectations(
            exec_step=ExecScenario(scenario.Path(), doc_only=exec_step.doc_only),  # Unused, but the *doc-only* property.
            scenario_expectations=scenario.test.ScenarioExpectations(),  # Unused.
        )  # type: CheckJsonReportExpectations

    def step(self):  # type: (...) -> None
        self.STEP("JSON reports")

        assert self.campaign_expectations.test_suite_expectations is not None
        for _test_suite_expectations in self.campaign_expectations.test_suite_expectations:  # type: scenario.test.TestSuiteExpectations
            assert _test_suite_expectations.test_case_expectations is not None
            for _test_case_expectations in _test_suite_expectations.test_case_expectations:  # type: scenario.test.ScenarioExpectations

                # Read the JSON report file.
                _json = {}  # type: _JsonDictType
                assert _test_case_expectations.script_path is not None
                if self.ACTION(f"Read the JSON report file for '{_test_case_expectations.script_path}'."):
                    _json_path = self._outfiles.getscenarioresults(_test_case_expectations.script_path).json.path  # type: typing.Optional[scenario.Path]
                    assert _json_path
                    _json = json.loads(_json_path.read_bytes())
                    self.debug("%s", scenario.debug.jsondump(_json, indent=2),
                               extra=self.longtext(max_lines=10))

                self._json_report_checker.checkjsonreport(
                    json_scenario=_json,
                    scenario_expectations=_test_case_expectations,
                )
