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


class CampaignScenarioResultsReader:
    """
    Base class for reading scenario log and reports in campaign results.

    Shall be inherited by a :class:`scenario.test._steps.VerificationStep` relating to a :class:`campaigns.steps.execution.ExecCampaign` step.
    """

    def __init__(self):  # type: (...) -> None
        #: {*Pretty path*: :class:`CampaignOutdirFilesManager.ScenarioResults`} dictionary.
        self.__scenario_results = {}  # type: typing.Dict[str, CampaignScenarioResultsReader.ScenarioResults]

    @property
    def __exec_step(self):  # type: () -> _ExecCampaignType
        from campaigns.steps.execution import ExecCampaign

        assert isinstance(self, scenario.test.VerificationStep)
        return self.getexecstep(ExecCampaign)

    def getscenarioresults(
            self,
            script_path,  # type: scenario.Path
    ):  # type: (...) -> CampaignScenarioResultsReader.ScenarioResults
        if script_path.prettypath not in self.__scenario_results:
            self.__scenario_results[script_path.prettypath] = CampaignScenarioResultsReader.ScenarioResults(self.__exec_step, script_path)
        return self.__scenario_results[script_path.prettypath]

    class ScenarioResults:
        def __init__(
                self,
                exec_step,  # type: _ExecCampaignType
                scenario_path,  # type: scenario.Path
        ):  # type: (...) -> None
            from scenario._campaignexecution import LogFileReader, ReportFileReader  # noqa  ## Access to protected module

            self.scenario_path = scenario_path  # type: scenario.Path
            self.log = LogFileReader(exec_step.campaign_req_baseline)  # type: LogFileReader
            self.log.path = exec_step.final_outdir_path / scenario_path.name.replace(".py", ".log")
            self.report = ReportFileReader(exec_step.campaign_req_baseline)  # type: ReportFileReader
            self.report.path = exec_step.final_outdir_path / scenario_path.name.replace(".py", ".json")


class CheckCampaignOutdirFiles(scenario.test.VerificationStep, CampaignScenarioResultsReader):

    def __init__(
            self,
            exec_step,  # type: _ExecCampaignType
            campaign_expectations,  # type: scenario.test.CampaignExpectations
    ):  # type: (...) -> None
        scenario.test.VerificationStep.__init__(self, exec_step)
        CampaignScenarioResultsReader.__init__(self)

        self.campaign_expectations = campaign_expectations  # type: scenario.test.CampaignExpectations
        self._outdir_content = []  # type: typing.List[scenario.Path]

    def step(self):  # type: (...) -> None
        from campaigns.steps.execution import ExecCampaign

        self.STEP("Output directory content")

        # Ensure the `CampaignExpectations` object knows the campaign output directory path.
        if self.doexecute():
            self.campaign_expectations.outdir_path = self.getexecstep(ExecCampaign).final_outdir_path

        _outfiles_expectation = {}  # type: typing.Dict[str, bool]

        if self.ACTION("Read the directory containing the campaign results."):
            self.evidence(f"Reading '{self.campaign_expectations.outdir_path}'")
            self._outdir_content = list(self.campaign_expectations.outdir_path.iterdir())

        # Scenario reports.
        _outfiles_expectation["scenario reports"] = self.campaign_expectations.test_suite_expectations is not None
        if self.campaign_expectations.test_suite_expectations is not None:
            if self.RESULT("This directory contains 1 '.log' and 1 '.json' file for each scenario executed."):
                for _test_suite_expectations in self.campaign_expectations.test_suite_expectations:  # type: scenario.test.TestSuiteExpectations
                    assert _test_suite_expectations.test_case_expectations is not None
                    for _test_case_expectations in _test_suite_expectations.test_case_expectations:  # type: scenario.test.ScenarioExpectations
                        assert _test_case_expectations.script_path is not None
                        self._assertoutfile(
                            self.getscenarioresults(_test_case_expectations.script_path).log.path,
                            evidence=f"'{_test_case_expectations.script_path}' '.log' file",
                        )
                        self._assertoutfile(
                            self.getscenarioresults(_test_case_expectations.script_path).report.path,
                            evidence=f"'{_test_case_expectations.script_path}' '.json' file",
                        )

        # Campaign report.
        if self.RESULT("The directory contains a campaign report file."):
            self._assertoutfile(
                self.campaign_expectations.campaign_report_path,
                evidence="Campaign report",
            )

        # Requirement file and traceability reports.
        _outfiles_expectation["requirement database file"] = self.campaign_expectations.req_db_file.generated is not None
        if self.campaign_expectations.req_db_file.generated is True:
            if self.RESULT("The directory contains a requirement file."):
                self._assertoutfile(
                    self.campaign_expectations.req_db_file.path,
                    evidence="Requirement file",
                )
        elif self.campaign_expectations.req_db_file.generated is False:
            if self.RESULT("The directory contains no requirement file."):
                self.assertnotexists(
                    self.campaign_expectations.req_db_file.path,
                    evidence="Requirement file",
                )
        _outfiles_expectation["downstream traceability"] = self.campaign_expectations.downstream_traceability.generated is not None
        if self.campaign_expectations.downstream_traceability.generated is True:
            if self.RESULT("The directory contains a downstream traceability report."):
                self._assertoutfile(
                    self.campaign_expectations.downstream_traceability.path,
                    evidence="Downstream traceability report",
                )
        elif self.campaign_expectations.downstream_traceability.generated is False:
            if self.RESULT("The directory contains no downstream traceability report."):
                self.assertnotexists(
                    self.campaign_expectations.downstream_traceability.path,
                    evidence="Downstream traceability report",
                )
        _outfiles_expectation["upstream traceability"] = self.campaign_expectations.upstream_traceability.generated is not None
        if self.campaign_expectations.upstream_traceability.generated is True:
            if self.RESULT("The directory contains an upstream traceability report."):
                self._assertoutfile(
                    self.campaign_expectations.upstream_traceability.path,
                    evidence="Upstream traceability report",
                )
        elif self.campaign_expectations.upstream_traceability.generated is False:
            if self.RESULT("The directory contains no upstream traceability report."):
                self.assertnotexists(
                    self.campaign_expectations.upstream_traceability.path,
                    evidence="Upstream traceability report",
                )

        # No other file.
        if all(_outfiles_expectation.values()):
            if self.RESULT("The directory contains no other file."):
                self.assertisempty(
                    self._outdir_content,
                    evidence="Remaining files",
                )
        elif not any(_outfiles_expectation.values()):
            raise ValueError("".join([
                "Please specify either all or none of the following outfile expectations: ",
                ", ".join(_outfiles_expectation.keys()),
                " (only %s given)" % ", ".join(map(
                    lambda item: item[0],
                    filter(lambda item: item[1], _outfiles_expectation.items()),
                )),
            ]))

    def _assertoutfile(
            self,
            expected_path,  # type: typing.Optional[scenario.Path]
            evidence,  # type: str
    ):  # type: (...) -> None
        # Check the expected file exists.
        self.assertisfile(expected_path, evidence=evidence)

        # Remove it from the `self._outdir_content` member list.
        def not_expected_path(remaining_path):  # type: (scenario.Path) -> bool
            assert expected_path  # `expected_path` can't be `None` at this point.
            return not remaining_path.samefile(expected_path)
        self._outdir_content = list(filter(not_expected_path, self._outdir_content))
