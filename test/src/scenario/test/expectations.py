# -*- coding: utf-8 -*-

# Copyright 2020-2022 Alexis Royer <https://github.com/Alexis-ROYER/scenario>
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


class CampaignExpectations:
    def __init__(self):  # type: (...) -> None
        self.test_suite_expectations = None  # type: typing.Optional[typing.List[TestSuiteExpectations]]

    def addtestsuite(
            self,
            test_suite_path=None,  # type: scenario.Path
    ):  # type: (...) -> TestSuiteExpectations
        if self.test_suite_expectations is None:
            self.test_suite_expectations = []
        self.test_suite_expectations.append(TestSuiteExpectations(self, test_suite_path=test_suite_path))
        return self.test_suite_expectations[-1]

    @property
    def all_test_case_expectations(self):  # type: (...) -> typing.Optional[typing.List[ScenarioExpectations]]
        _all_test_case_expectations = []  # type: typing.List[ScenarioExpectations]
        if self.test_suite_expectations is None:
            return None
        for _test_suite_expectations in self.test_suite_expectations:  # type: TestSuiteExpectations
            if _test_suite_expectations.test_case_expectations is None:
                return None
            for _test_case_expectations in _test_suite_expectations.test_case_expectations:  # type: ScenarioExpectations
                _all_test_case_expectations.append(_test_case_expectations)
        return _all_test_case_expectations

    @property
    def step_stats(self):  # type: (...) -> StatExpectations
        return StatExpectations.sum("steps", self.test_suite_expectations)

    @property
    def action_stats(self):  # type: (...) -> StatExpectations
        return StatExpectations.sum("actions", self.test_suite_expectations)

    @property
    def result_stats(self):  # type: (...) -> StatExpectations
        return StatExpectations.sum("results", self.test_suite_expectations)


class TestSuiteExpectations:
    def __init__(
            self,
            campaign_expectations,  # type: CampaignExpectations
            test_suite_path=None,  # type: scenario.Path
    ):  # type: (...) -> None
        self.campaign_expectations = campaign_expectations  # type: CampaignExpectations

        self.test_suite_path = test_suite_path  # type: typing.Optional[scenario.Path]
        self.test_case_expectations = None  # type: typing.Optional[typing.List[ScenarioExpectations]]

    def addtestcase(
            self,
            script_path=None,  # type: scenario.Path
            class_name=None,  # type: str
    ):  # type: (...) -> ScenarioExpectations
        if self.test_case_expectations is None:
            self.test_case_expectations = []
        self.test_case_expectations.append(ScenarioExpectations(test_suite_expectations=self, script_path=script_path, class_name=class_name))
        return self.test_case_expectations[-1]

    @property
    def step_stats(self):  # type: (...) -> StatExpectations
        return StatExpectations.sum("steps", self.test_case_expectations)

    @property
    def action_stats(self):  # type: (...) -> StatExpectations
        return StatExpectations.sum("actions", self.test_case_expectations)

    @property
    def result_stats(self):  # type: (...) -> StatExpectations
        return StatExpectations.sum("results", self.test_case_expectations)


class ScenarioExpectations:
    def __init__(
            self,
            script_path=None,  # type: scenario.Path
            class_name=None,  # type: str
            test_suite_expectations=None,  # type: TestSuiteExpectations
    ):  # type: (...) -> None
        self.test_suite_expectations = test_suite_expectations  # type: typing.Optional[TestSuiteExpectations]

        self.class_name = class_name  # type: typing.Optional[str]
        self.script_path = script_path  # type: typing.Optional[scenario.Path]
        self.attributes = None  # type: typing.Optional[typing.Dict[str, str]]
        self.step_expectations = None  # type: typing.Optional[typing.List[StepExpectations]]
        self.status = None  # type: typing.Optional[scenario.ExecutionStatus]
        self.errors = None  # type: typing.Optional[typing.List[ErrorExpectations]]
        self.warnings = None  # type: typing.Optional[typing.List[ErrorExpectations]]
        self.step_stats = StatExpectations("steps", None, None)  # type: StatExpectations
        self.action_stats = StatExpectations("actions", None, None)  # type: StatExpectations
        self.result_stats = StatExpectations("results", None, None)  # type: StatExpectations

    @property
    def name(self):  # type: (...) -> typing.Optional[str]
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
    ):  # type: (...) -> StepExpectations
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
            error,  # type: ErrorExpectations
            level=None,  # type: int
    ):  # type: (...) -> ErrorExpectations
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
    ):  # type: (...) -> StepExpectations
        """
        Retrieves the corresponding :class:`StepExpectations` object.

        :param step_spec: Either the step number or the step name.
        :return: :class:`StepExpectations` object.
        """
        assert self.step_expectations, "No step expectations yet"
        for _step_expectation in self.step_expectations:  # type: StepExpectations
            if isinstance(step_spec, int):
                if _step_expectation.number == step_spec:
                    return _step_expectation
            if isinstance(step_spec, str):
                if _step_expectation.name == step_spec:
                    return _step_expectation
        raise KeyError(f"No such step expectations {step_spec!r}")


class StepExpectations:
    def __init__(
            self,
            scenario_expectations,  # type: ScenarioExpectations
    ):  # type: (...) -> None
        self.scenario_expectations = scenario_expectations  # type: ScenarioExpectations

        self.number = None  # type: typing.Optional[int]
        self.name = None  # type: typing.Optional[str]
        self.description = None  # type: typing.Optional[str]
        self.action_result_expectations = None  # type: typing.Optional[typing.List[ActionResultExpectations]]

    def __str__(self):  # type: (...) -> str
        if self.number is not None:
            return f"step#{self.number}"
        if self.name is not None:
            return f"step<name={self.name!r}>"
        if self.description is not None:
            return f"step<description={self.description!r}>"
        return "step<?>"

    def addaction(
            self,
            action,  # type: str
    ):  # type: (...) -> ActionResultExpectations
        _action = ActionResultExpectations(self)  # type: ActionResultExpectations
        _action.type = scenario.ActionResult.Type.ACTION
        _action.description = action
        if self.action_result_expectations is None:
            self.action_result_expectations = []
        self.action_result_expectations.append(_action)
        return _action

    def addresult(
            self,
            result,  # type: str
    ):  # type: (...) -> ActionResultExpectations
        _result = ActionResultExpectations(self)  # type: ActionResultExpectations
        _result.type = scenario.ActionResult.Type.RESULT
        _result.description = result
        if self.action_result_expectations is None:
            self.action_result_expectations = []
        self.action_result_expectations.append(_result)
        return _result

    def action(
            self,
            action_result_index,  # type: int
    ):  # type: (...) -> ActionResultExpectations
        """
        Retrieves the corresponding :class:`ActionResultExpectations` object.

        :param action_result_index: Action/result index, starting from 0.
        :return: :class:`ActionResultExpectations` object.
        """
        assert self.action_result_expectations, "No action/result expectations yet"
        if self.action_result_expectations[action_result_index].type != scenario.ActionResult.Type.ACTION:
            raise KeyError(f"Action/result#{action_result_index}: Not an action")
        return self.action_result_expectations[action_result_index]

    def result(
            self,
            action_result_index,  # type: int
    ):  # type: (...) -> ActionResultExpectations
        """
        Retrieves the corresponding :class:`ActionResultExpectations` object.

        :param action_result_index: Action/result index, starting from 0.
        :return: :class:`ActionResultExpectations` object.
        """
        assert self.action_result_expectations, "No action/result expectations yet"
        if self.action_result_expectations[action_result_index].type != scenario.ActionResult.Type.RESULT:
            raise KeyError(f"Action/result#{action_result_index}: Not an expected result")
        return self.action_result_expectations[action_result_index]


class ActionResultExpectations:
    def __init__(
            self,
            step_expectations,  # type: StepExpectations
    ):  # type: (...) -> None
        self.step_expectations = step_expectations  # type: StepExpectations

        self.type = scenario.ActionResult.Type.ACTION  # type: scenario.ActionResult.Type
        self.description = None  # type: typing.Optional[str]
        self.subscenario_expectations = None  # type: typing.Optional[typing.List[ScenarioExpectations]]

    def addsubscenario(
            self,
            subscenario_expectations,  # type: ScenarioExpectations
    ):  # type: (...) -> ScenarioExpectations
        if self.subscenario_expectations is None:
            self.subscenario_expectations = []
        self.subscenario_expectations.append(subscenario_expectations)
        return subscenario_expectations

    def nosubscenarios(self):  # type: (...) -> None
        assert self.subscenario_expectations is None
        self.subscenario_expectations = []


class ErrorExpectations:
    def __init__(
            self,
            message,  # type: str
            cls=None,  # type: typing.Optional[typing.Union[typing.Type[scenario.ExceptionError], typing.Type[scenario.KnownIssue]]]
            exception_type=None,  # type: typing.Optional[str]
            issue_id=None,  # type: typing.Optional[str]
            location=None,  # type: typing.Optional[str]
    ):  # type: (...) -> None
        assert (exception_type is None) or (cls is scenario.ExceptionError)
        assert (issue_id is None) or (cls is scenario.KnownIssue)

        self.cls = cls  # type: typing.Optional[typing.Union[typing.Type[scenario.ExceptionError], typing.Type[scenario.KnownIssue]]]
        self.error_type = exception_type  # type: typing.Optional[str]
        if (self.error_type is None) and (self.cls is scenario.KnownIssue):
            self.error_type = "known-issue"
        self.issue_id = issue_id  # type: typing.Optional[str]
        self.message = message  # type: str
        self.location = location  # type: typing.Optional[str]


class StatExpectations:
    def __init__(
            self,
            item_type,  # type: str
            executed_count,  # type: typing.Optional[int]
            total_count,  # type: typing.Optional[int]
    ):  # type: (...) -> None
        self.item_type = item_type  # type: str
        self.executed = executed_count  # type: typing.Optional[int]
        self.total = total_count  # type: typing.Optional[int]

    @staticmethod
    def sum(
            stat_type,  # type: str
            subs,  # type: typing.Optional[typing.List[typing.Any]]
    ):  # type: (...) -> StatExpectations
        assert stat_type in ("steps", "actions", "results")
        if subs is None:
            return StatExpectations(stat_type, None, None)

        _sum = StatExpectations(stat_type, 0, 0)  # type: StatExpectations
        _attr_name = stat_type[:-1] + "_stats"  # type: str
        for _sub in subs:  # type: typing.Any
            _sub_stats = getattr(_sub, _attr_name)  # type: StatExpectations
            if _sub_stats.total is None:
                return StatExpectations(stat_type, None, None)
            else:
                assert _sum.total is not None
                _sum.total += _sub_stats.total

            if _sub_stats.executed is None:
                _sum.executed = None
            elif _sum.executed is not None:
                _sum.executed += _sub_stats.executed
        return _sum
