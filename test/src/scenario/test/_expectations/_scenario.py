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

import logging
import typing

import scenario

if typing.TYPE_CHECKING:
    from ._error import ErrorExpectations as _ErrorExpectationsType
    from ._step import StepExpectations as _StepExpectationsType
    from ._testsuite import TestSuiteExpectations as _TestSuiteExpectationsType


class ScenarioExpectations:
    def __init__(
            self,
            script_path=None,  # type: scenario.Path
            class_name=None,  # type: str
            test_suite_expectations=None,  # type: _TestSuiteExpectationsType
    ):  # type: (...) -> None
        from ._stats import StatExpectations

        self.test_suite_expectations = test_suite_expectations  # type: typing.Optional[_TestSuiteExpectationsType]

        self.class_name = class_name  # type: typing.Optional[str]
        self.script_path = script_path  # type: typing.Optional[scenario.Path]
        self.attributes = None  # type: typing.Optional[typing.Dict[str, str]]
        self.step_expectations = None  # type: typing.Optional[typing.List[_StepExpectationsType]]
        self.status = None  # type: typing.Optional[scenario.ExecutionStatus]
        self.errors = None  # type: typing.Optional[typing.List[_ErrorExpectationsType]]
        self.warnings = None  # type: typing.Optional[typing.List[_ErrorExpectationsType]]
        self.step_stats = StatExpectations("steps", None, None)  # type: StatExpectations
        self.action_stats = StatExpectations("actions", None, None)  # type: StatExpectations
        self.result_stats = StatExpectations("results", None, None)  # type: StatExpectations

    @property
    def name(self):  # type: () -> typing.Optional[str]
        if self.script_path:
            return self.script_path.prettypath
        return None

    def addattribute(
            self,
            name,  # type: str
            value,  # type: str
    ):  # type: (...) -> None
        if self.attributes is None:
            self.attributes = {}
        self.attributes[name] = value

    def addstep(
            self,
            number=None,  # type: int
            name=None,  # type: str
            description=None,  # type: str
    ):  # type: (...) -> _StepExpectationsType
        from ._step import StepExpectations

        _step_expectations = StepExpectations(self)  # type: StepExpectations
        _step_expectations.number = number
        _step_expectations.name = name
        _step_expectations.description = description

        if self.step_expectations is None:
            self.step_expectations = []
        self.step_expectations.append(_step_expectations)
        return _step_expectations

    def adderror(
            self,
            error,  # type: _ErrorExpectationsType
            level=None,  # type: int
    ):  # type: (...) -> _ErrorExpectationsType
        if level is None:
            if error.cls is scenario.KnownIssue:
                level = logging.WARNING
            else:
                level = logging.ERROR
        assert level in (logging.WARNING, logging.ERROR)
        if level == logging.WARNING:
            if self.warnings is None:
                self.warnings = []
            self.warnings.append(error)
        else:
            if self.errors is None:
                self.errors = []
            self.errors.append(error)
        return error

    def noerror(self):  # type: (...) -> None
        assert self.errors is None
        self.errors = []

    def nowarning(self):  # type: (...) -> None
        assert self.warnings is None
        self.warnings = []

    def setstats(
            self,
            steps=None,  # type: typing.Union[int, typing.Tuple[int, int]]
            actions=None,  # type: typing.Union[int, typing.Tuple[int, int]]
            results=None,  # type: typing.Union[int, typing.Tuple[int, int]]
    ):  # type: (...) -> None
        from ._stats import StatExpectations

        def _setstats(
                instance,  # type: StatExpectations
                stats,  # type: typing.Union[int, typing.Tuple[int, int]]
        ):  # type: (...) -> None
            if isinstance(stats, int):
                instance.executed = None
                instance.total = stats
            else:
                instance.executed = stats[0]
                instance.total = stats[1]

        if steps is not None:
            _setstats(self.step_stats, steps)
        if actions is not None:
            _setstats(self.action_stats, actions)
        if results is not None:
            _setstats(self.result_stats, results)

    def step(
            self,
            step_spec,  # type: typing.Union[int, str]
    ):  # type: (...) -> _StepExpectationsType
        """
        Retrieves the corresponding :class:`StepExpectations` object.

        :param step_spec: Either the step number or the step name.
        :return: :class:`StepExpectations` object.
        """
        assert self.step_expectations, "No step expectations yet"
        for _step_expectation in self.step_expectations:  # type: _StepExpectationsType
            if isinstance(step_spec, int):
                if _step_expectation.number == step_spec:
                    return _step_expectation
            if isinstance(step_spec, str):
                if _step_expectation.name == step_spec:
                    return _step_expectation
        raise KeyError(f"No such step expectations {step_spec!r}")
