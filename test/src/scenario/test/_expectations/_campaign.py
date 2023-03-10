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
    def __init__(self):  # type: (...) -> None
        self.test_suite_expectations = None  # type: typing.Optional[typing.List[_TestSuiteExpectationsType]]

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
