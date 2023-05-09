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
    from .execution import ExecCampaign as _ExecCampaignType


class CampaignOutdirFilesManager:
    """
    Base class for objects (and step objects among others) that need to manipulate campaign results.
    """

    class ScenarioResults:
        def __init__(
                self,
                campaign_execution,  # type: _ExecCampaignType
                scenario_path,  # type: scenario.Path
        ):  # type: (...) -> None
            from scenario._campaignexecution import JsonReportReader, LogFileReader  # noqa  ## Access to protected module

            self.scenario_path = scenario_path  # type: scenario.Path
            self.log = LogFileReader()  # type: LogFileReader
            self.log.path = campaign_execution.final_outdir_path / scenario_path.name.replace(".py", ".log")
            self.json = JsonReportReader()  # type: JsonReportReader
            self.json.path = campaign_execution.final_outdir_path / scenario_path.name.replace(".py", ".json")

        @property
        def scenario_report(self):  # type: () -> typing.Optional[scenario.ScenarioExecution]
            if self.json.content:
                return self.json.content.execution
            return None

    def __init__(
            self,
            campaign_execution,  # type: _ExecCampaignType
    ):  # type: (...) -> None
        self._campaign_execution = campaign_execution  # type: _ExecCampaignType
        #: *Pretty path* => :class:`CampaignOutdirFilesManager.ScenarioResults` dictionary.
        self._scenario_results = {}  # type: typing.Dict[str, CampaignOutdirFilesManager.ScenarioResults]

    def getscenarioresults(
            self,
            script_path,  # type: scenario.Path
    ):  # type: (...) -> CampaignOutdirFilesManager.ScenarioResults
        if script_path.prettypath not in self._scenario_results:
            self._scenario_results[script_path.prettypath] = CampaignOutdirFilesManager.ScenarioResults(self._campaign_execution, script_path)
        return self._scenario_results[script_path.prettypath]

    @property
    def junit_report_path(self):  # type: () -> scenario.Path
        return self._campaign_execution.junit_report_path


class CheckCampaignOutdirFiles(scenario.test.VerificationStep):

    def __init__(
            self,
            exec_step,  # type: _ExecCampaignType
            campaign_expectations,  # type: scenario.test.CampaignExpectations
    ):  # type: (...) -> None
        scenario.test.VerificationStep.__init__(self, exec_step)

        self.campaign_expectations = campaign_expectations  # type: scenario.test.CampaignExpectations
        self._outfiles = CampaignOutdirFilesManager(exec_step)  # type: CampaignOutdirFilesManager
        self._outdir_content = []  # type: typing.List[scenario.Path]

    def step(self):  # type: (...) -> None
        from campaigns.steps.execution import ExecCampaign

        self.STEP("Output directory content")

        if self.ACTION("Read the directory containing the campaign results."):
            self.evidence(f"Reading '{self.getexecstep(ExecCampaign).final_outdir_path}'")
            self._outdir_content = list(self.getexecstep(ExecCampaign).final_outdir_path.iterdir())
        if self.RESULT("This directory contains 1 '.log' and 1 '.json' file for each scenario executed."):
            assert self.campaign_expectations.test_suite_expectations is not None
            for _test_suite_expectations in self.campaign_expectations.test_suite_expectations:  # type: scenario.test.TestSuiteExpectations
                assert _test_suite_expectations.test_case_expectations is not None
                for _test_case_expectations in _test_suite_expectations.test_case_expectations:  # type: scenario.test.ScenarioExpectations
                    assert _test_case_expectations.script_path is not None
                    self.assertisfile(
                        self._outfiles.getscenarioresults(_test_case_expectations.script_path).log.path,
                        evidence=f"'{_test_case_expectations.script_path}' '.log' file",
                    )
                    self._expectedfilefound(self._outfiles.getscenarioresults(_test_case_expectations.script_path).log.path)
                    self.assertisfile(
                        self._outfiles.getscenarioresults(_test_case_expectations.script_path).json.path,
                        evidence=f"'{_test_case_expectations.script_path}' '.json' file",
                    )
                    self._expectedfilefound(self._outfiles.getscenarioresults(_test_case_expectations.script_path).json.path)
        if self.RESULT("The directory also contains a '.xml' campaign report file."):
            self.assertisfile(
                self._outfiles.junit_report_path,
                evidence="Campaign report",
            )
            self._expectedfilefound(self._outfiles.junit_report_path)
        if self.RESULT("The directory contains no other file."):
            self.assertisempty(
                self._outdir_content,
                evidence="Remaining files",
            )

    def _expectedfilefound(
            self,
            path,  # type: typing.Optional[scenario.Path]
    ):  # type: (...) -> None
        if path:
            _index = 0  # type: int
            while _index < len(self._outdir_content):
                if self._outdir_content[_index].samefile(path):
                    del self._outdir_content[_index]
                else:
                    _index += 1
