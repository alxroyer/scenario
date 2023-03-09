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
    from steps.common import ParseFinalResultsLog as _ParseFinalResultsLogType


class KnownIssueLevelUtils:
    """
    Base class for knownissues180 and knownissues190 tests.

    Defines common test data and useful methods.
    """

    # Use thresholds with different number of digits in order not to rely on alphabetical order.
    ISSUE_LEVEL_ERROR = 200  # type: int
    ISSUE_LEVEL_IGNORED = 10  # type: int

    ISSUE_LEVELS = [
        # Let's puzzle issue levels in order to see how the final results reorder them ascendingly.
        ISSUE_LEVEL_ERROR,                              # FAIL (200)
        ISSUE_LEVEL_ERROR - 1,                              # WARNINGS (199)
        ISSUE_LEVEL_ERROR + 2,                          # FAIL (202)
        ISSUE_LEVEL_IGNORED - 1,                                # SUCCESS (9)
        ISSUE_LEVEL_IGNORED + 1,                            # WARNINGS (11)
        (ISSUE_LEVEL_ERROR + ISSUE_LEVEL_IGNORED) // 2,     # WARNINGS (95)
        ISSUE_LEVEL_ERROR + 1,                          # FAIL (201)
        ISSUE_LEVEL_IGNORED,                                    # SUCCESS (10)
        ISSUE_LEVEL_IGNORED - 2,                                # SUCCESS (8)
    ]  # type: typing.Sequence[int]

    def _mktmppaths(self):  # type: (...) -> typing.Sequence[scenario.Path]
        """
        Call from an execution step.
        """
        assert (
            isinstance(self, KnownIssueLevelUtils)  # type: ignore[redundant-expr]  ## Left operand of "and" is always true
            and isinstance(self, scenario.test.Step)
        )

        # Prepare a tmp script path for each issue level.
        return [
            self.test_case.mktmppath(
                prefix=f"{scenario.test.paths.KNOWN_ISSUE_DETAILS_SCENARIO.stem}-{int(_issue_level):03d}-",
                suffix=".py",
            )
            for _issue_level in self.ISSUE_LEVELS
        ]

    def _createscenariofilesactions(
            self,
            scenario_paths,  # type: typing.Sequence[scenario.Path]
    ):  # type: (...) -> None
        """
        Call from an execution step.
        """
        assert (
            isinstance(self, KnownIssueLevelUtils)  # type: ignore[redundant-expr]  ## Left operand of "and" is always true
            and isinstance(self, scenario.test.Step)
        )
        self.assertequal(len(scenario_paths), len(self.ISSUE_LEVELS))

        for _index in range(len(self.ISSUE_LEVELS)):  # type: int
            if self.ACTION(f"Copy {scenario.test.paths.KNOWN_ISSUE_DETAILS_SCENARIO} "
                           f"into a {self.test_case.getpathdesc(scenario_paths[_index])} temporary file, "
                           f"and make it register a known issue with level {self.ISSUE_LEVELS[_index]}."):
                _content = scenario.test.paths.KNOWN_ISSUE_DETAILS_SCENARIO.read_bytes()  # type: bytes
                # Note:
                # `KnownIssueDetailsScenario.ConfigKey.LEVEL` is not set.
                # By the way, the `scenario.IssueLevel.parse()` returns a `None` value which we override with the `or` operator.
                _content = _content.replace(
                    b')  # type: typing.Optional[scenario.AnyIssueLevelType]',
                    b') or %d  # type: typing.Optional[scenario.AnyIssueLevelType],' % self.ISSUE_LEVELS[_index],
                )
                scenario_paths[_index].write_bytes(_content)
                self.evidence(f"File {self.test_case.getpathdesc(scenario_paths[_index])} '{scenario_paths[_index]}' created "
                              f"with issue level {self.ISSUE_LEVELS[_index]}")

    def _buildscenarioexpectations(
            self,
            scenario_paths,  # type: typing.Sequence[scenario.Path]
            config_values,  # type: scenario.test.configvalues.ConfigValuesType
    ):  # type: (...) -> typing.Sequence[scenario.test.ScenarioExpectations]
        """
        Call from a scenario.
        """
        assert (
            isinstance(self, KnownIssueLevelUtils)  # type: ignore[redundant-expr]  ## Left operand of "and" is always true
            and isinstance(self, scenario.test.TestCase)
        )
        self.assertequal(len(scenario_paths), len(self.ISSUE_LEVELS))

        _scenario_expectation_list = []  # type: typing.List[scenario.test.ScenarioExpectations]
        for _index in range(len(self.ISSUE_LEVELS)):  # type: int
            _scenario_expectations = scenario.test.data.scenarioexpectations(
                scenario.test.paths.KNOWN_ISSUE_DETAILS_SCENARIO,
                config_values={
                    **config_values,
                    scenario.test.data.scenarios.KnownIssueDetailsScenario.ConfigKey.LEVEL: self.ISSUE_LEVELS[_index],
                },
                error_details=True,
            )  # type: scenario.test.ScenarioExpectations

            # Fix the script path (otherwise the expectations will be confused).
            _scenario_expectations.script_path = scenario_paths[_index]

            # Fix the known issue level (if any).
            if _scenario_expectations.status != scenario.ExecutionStatus.SUCCESS:
                self.assertequal(len(_scenario_expectations.errors or []) + len(_scenario_expectations.warnings or []), 1)
                (_scenario_expectations.errors or _scenario_expectations.warnings or [])[-1].level = self.ISSUE_LEVELS[_index]

            self.debug(f"Scenario #{_index + 1} expected status: {_scenario_expectations.status}")
            _scenario_expectation_list.append(_scenario_expectations)

        return _scenario_expectation_list


class CheckFinalResultsAscendingIssueLevelOrder(scenario.test.VerificationStep, KnownIssueLevelUtils):

    def __init__(
            self,
            exec_step,  # type: _ParseFinalResultsLogType
    ):  # type: (...) -> None
        scenario.test.VerificationStep.__init__(self, exec_step)

    def step(self):  # type: (...) -> None
        from steps.common import ParseFinalResultsLog

        assert isinstance(self.exec_step, ParseFinalResultsLog)

        _sorted_issue_levels = sorted(self.ISSUE_LEVELS)  # type: typing.List[int]

        if self.RESULT(f"Tests that ended with the {scenario.ExecutionStatus.WARNINGS} status are ordered in asceneding issue levels."):
            self.evidence(f"Ignored issue level: {self.ISSUE_LEVEL_IGNORED}")
            for _index in range(len(_sorted_issue_levels)):  # type: int
                if self.exec_step.json_scenario_stats[_index]["status"] == str(scenario.ExecutionStatus.WARNINGS):
                    self.assertjson(
                        self.exec_step.json_scenario_stats[_index], "warnings[0].level", value=_sorted_issue_levels[_index],
                        evidence=True,
                    )

        if self.RESULT(f"Tests that ended with the {scenario.ExecutionStatus.FAIL} status are ordered in ascending issue levels."):
            self.evidence(f"Error issue level: {self.ISSUE_LEVEL_ERROR}")
            for _index in range(len(_sorted_issue_levels)):  # Type already declared above
                if self.exec_step.json_scenario_stats[_index]["status"] == str(scenario.ExecutionStatus.FAIL):
                    self.assertjson(
                        self.exec_step.json_scenario_stats[_index], "errors[0].level", value=_sorted_issue_levels[_index],
                        evidence=True,
                    )
