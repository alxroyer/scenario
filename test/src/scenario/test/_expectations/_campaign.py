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

if typing.TYPE_CHECKING:
    from ._scenario import ScenarioExpectations as _ScenarioExpectationsType
    from ._stats import StatExpectations as _StatExpectationsType
    from ._testsuite import TestSuiteExpectations as _TestSuiteExpectationsType


class CampaignExpectations:
    class ReqOutfile:
        def __init__(
                self,
                campaign_expectations,  # type: CampaignExpectations
                default_basename,  # type: str
        ):  # type: (...) -> None
            self._campaign_expectations = campaign_expectations  # type: CampaignExpectations
            self.generated = None  # type: typing.Optional[bool]
            self.basename = default_basename  # type: str
            self.with_titles_and_texts = None  # type: typing.Optional[bool]
            self.content_path = None  # type: typing.Optional[scenario.Path]

        def set(
                self,
                generated,  # type: bool
                *,
                basename=None,  # type: str
                with_titles_and_texts=None,  # type: bool
                content=None,  # type: scenario.Path
        ):  # type: (...) -> None
            self.generated = generated
            if basename is not None:
                self.basename = basename
            self.with_titles_and_texts = with_titles_and_texts
            self.content_path = content

        @property
        def path(self):  # type: () -> scenario.Path
            return self._campaign_expectations.outdir_path / self.basename

    def __init__(self):  # type: (...) -> None
        self.test_suite_expectations = None  # type: typing.Optional[typing.List[_TestSuiteExpectationsType]]
        self.req_db_file = CampaignExpectations.ReqOutfile(self, "req-db.json")  # type: CampaignExpectations.ReqOutfile
        self.downstream_traceability = CampaignExpectations.ReqOutfile(self, "req-downstream-traceability.json")  # type: CampaignExpectations.ReqOutfile
        self.upstream_traceability = CampaignExpectations.ReqOutfile(self, "req-upstream-traceability.json")  # type: CampaignExpectations.ReqOutfile

        # Should be set during test execution.
        self._outdir_path = None  # type: typing.Optional[scenario.Path]

    @property
    def campaign_report_path(self):  # type: () -> scenario.Path
        return self.outdir_path / "campaign.xml"

    def addtestsuite(
            self,
            test_suite_path=None,  # type: scenario.Path
    ):  # type: (...) -> _TestSuiteExpectationsType
        from ._testsuite import TestSuiteExpectations

        if self.test_suite_expectations is None:
            self.test_suite_expectations = []
        self.test_suite_expectations.append(TestSuiteExpectations(self, test_suite_path=test_suite_path))
        return self.test_suite_expectations[-1]

    @property
    def all_test_case_expectations(self):  # type: () -> typing.Optional[typing.List[_ScenarioExpectationsType]]
        _all_test_case_expectations = []  # type: typing.List[_ScenarioExpectationsType]
        if self.test_suite_expectations is None:
            return None
        for _test_suite_expectations in self.test_suite_expectations:  # type: _TestSuiteExpectationsType
            if _test_suite_expectations.test_case_expectations is None:
                return None
            for _test_case_expectations in _test_suite_expectations.test_case_expectations:  # type: _ScenarioExpectationsType
                _all_test_case_expectations.append(_test_case_expectations)
        return _all_test_case_expectations

    @property
    def step_stats(self):  # type: () -> _StatExpectationsType
        from ._stats import StatExpectations

        return StatExpectations.sum("steps", self.test_suite_expectations)

    @property
    def action_stats(self):  # type: () -> _StatExpectationsType
        from ._stats import StatExpectations

        return StatExpectations.sum("actions", self.test_suite_expectations)

    @property
    def result_stats(self):  # type: () -> _StatExpectationsType
        from ._stats import StatExpectations

        return StatExpectations.sum("results", self.test_suite_expectations)

    @property
    def outdir_path(self):  # type: () -> scenario.Path
        if not self._outdir_path:
            raise RuntimeError("Campaign output directory missing, please set at the beginning of the current step (in execution mode)")
        return self._outdir_path

    @outdir_path.setter
    def outdir_path(self, outdir_path):  # type: (scenario.Path) -> None
        self._outdir_path = outdir_path
