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
    from ._campaign import CampaignExpectations as _CampaignExpectationsType
    from ._scenario import ScenarioExpectations as _ScenarioExpectationsType
    from ._stats import StatExpectations as _StatExpectationsType


class TestSuiteExpectations:
    def __init__(
            self,
            campaign_expectations,  # type: _CampaignExpectationsType
            test_suite_path=None,  # type: scenario.Path
    ):  # type: (...) -> None
        self.campaign_expectations = campaign_expectations  # type: _CampaignExpectationsType

        self.test_suite_path = test_suite_path  # type: typing.Optional[scenario.Path]
        self.test_case_expectations = None  # type: typing.Optional[typing.List[_ScenarioExpectationsType]]

    def addtestcase(
            self,
            script_path=None,  # type: scenario.Path
            class_name=None,  # type: str
    ):  # type: (...) -> _ScenarioExpectationsType
        from ._scenario import ScenarioExpectations

        if self.test_case_expectations is None:
            self.test_case_expectations = []
        self.test_case_expectations.append(ScenarioExpectations(test_suite_expectations=self, script_path=script_path, class_name=class_name))
        return self.test_case_expectations[-1]

    @property
    def step_stats(self):  # type: () -> _StatExpectationsType
        from ._stats import StatExpectations

        return StatExpectations.sum("steps", self.test_case_expectations)

    @property
    def action_stats(self):  # type: () -> _StatExpectationsType
        from ._stats import StatExpectations

        return StatExpectations.sum("actions", self.test_case_expectations)

    @property
    def result_stats(self):  # type: () -> _StatExpectationsType
        from ._stats import StatExpectations

        return StatExpectations.sum("results", self.test_case_expectations)
