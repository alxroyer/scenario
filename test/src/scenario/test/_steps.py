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
    from ._subprocess import SubProcess as _SubProcessType
    from ._testcase import TestCase as _TestCaseType


if typing.TYPE_CHECKING:
    VarDataType = typing.TypeVar("VarDataType")


class Step(scenario.Step):
    """
    :mod:`scenario.test` augmentation for step definitions.
    """

    def __init__(self):  # type: (...) -> None
        scenario.Step.__init__(self)

    @property
    def test_case(self):  # type: () -> _TestCaseType
        from ._testcase import TestCase

        _scenario = scenario.stack.building.scenario_definition  # type: typing.Optional[scenario.Scenario]
        # Avoid failing when the owner scenario is not set yet.
        if hasattr(self, "_scenario") and (self._scenario is not None):
            _scenario = self._scenario
        assert isinstance(_scenario, TestCase), f"{_scenario!r} not a {TestCase!r}"
        return _scenario

    def testdatafromlist(
            self,
            items,  # type: typing.List[VarDataType]
            index,  # type: int
            default,  # type: VarDataType
    ):  # type: (...) -> VarDataType
        """
        Helps walking through test data as a list.

        :param items: List to walk through. Possibly no valid data while the test is not actually being executed.
        :param index: Index of item required.
        :param default: Default value to return when the test is not being executed.
        :return: Test data, or default value when the test is not being executed.
        """
        if not self.doexecute():
            return default
        else:
            return items[index]

    def testdatafromjson(
            self,
            json_data,  # type: typing.Optional[scenario.types.JsonDict]
            jsonpath,  # type: typing.Optional[str]
            type=None,  # type: type  # noqa  ## Shadows built-in name 'type'
    ):  # type: (...) -> typing.Any
        """
        Helps walking through JSON test data.

        :param json_data: JSON test data to walk through. Possibly no valid data while the test is not actually being executed.
        :param jsonpath: JSONPath required.
        :param type: Expected type.
        :return: Test data, or empty dictionary when the test is not being executed.
        """
        if not self.doexecute():
            return {}
        else:
            return self.assertjson(json_data, jsonpath, type=type)

    def assertsubprocessretcode(
            self,
            subprocess,  # type: scenario.SubProcess
            retcode,  # type: int
            evidence,  # type: scenario.assertionhelpers.EvidenceParamType
    ):  # type: (...) -> None
        """
        Asserts a sub-process has returned the code expected.

        :param subprocess: Sub-process which return code to check.
        :param retcode: Expected return code.
        :param evidence: Evidence activation (see :ref:`dedicated note <assertions.evidence-param>`).
        """
        self.assertequal(
            subprocess.returncode, retcode,
            f"{subprocess} returned {subprocess.returncode!r}",
            evidence=evidence,
        )


if typing.TYPE_CHECKING:
    VarStepType = typing.TypeVar("VarStepType", bound=Step)


class ExecutionStep(Step):
    """
    Step that owns a :class:`SubProcess` instance.
    """

    def __init__(self):  # type: (...) -> None
        from ._subprocess import SubProcess

        Step.__init__(self)

        #: :class:`SubProcess` instance owned.
        #:
        #: Initialized as a *void* instance.
        #: To be set with actual instances in subclasses.
        self.subprocess = SubProcess()  # type: SubProcess


class VerificationStep(Step):
    """
    Step that makes verifications based on the results of an execution step.
    """

    def __init__(
            self,
            exec_step,  # type: AnyExecutionStepType
    ):  # type: (...) -> None
        Step.__init__(self)

        self.exec_step = exec_step  # type: AnyExecutionStepType

    def getexecstep(
            self,
            cls,  # type: typing.Type[VarStepType]
    ):  # type: (...) -> VarStepType
        """
        Recursively retrieves the :attr:`exec_step` which type matches with ``cls``.

        :param cls: Type of step expected.
        :return: The step of the right type.
        """
        if isinstance(self.exec_step, cls):
            return self.exec_step
        assert isinstance(self.exec_step, VerificationStep)
        return self.exec_step.getexecstep(cls)

    @property
    def subprocess(self):  # type: () -> _SubProcessType
        return self.exec_step.subprocess


if typing.TYPE_CHECKING:
    AnyExecutionStepType = typing.Union[ExecutionStep, VerificationStep]
