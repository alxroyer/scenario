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

import abc
import typing

import scenario.test

from steps.logprocessing import LogProcessor  # `LogProcessor` used for inheritance.


class LogParserStep(scenario.test.VerificationStep, LogProcessor, metaclass=abc.ABCMeta):
    """
    Base class for steps which purpose is to parse a :class:`scenario.test.ExecutionStep` log output.
    """

    def __init__(
            self,
            exec_step,  # type: scenario.test.AnyExecutionStepType
            encoding=None,  # type: str
    ):  # type: (...) -> None
        scenario.test.VerificationStep.__init__(self, exec_step)
        LogProcessor.__init__(self, encoding)

    def step(self):  # type: (...) -> None
        # Let the child class set the step description by setting the :attr:`scenario.scenariodefinition.ScenarioDefinition.description` attribute.
        # self.STEP()

        if self.ACTION("Parse the log output."):
            for _line in self.subprocess.stdout.splitlines():  # type: bytes
                if not _line:
                    continue
                self.debug("line: %r", _line)
                if not self._parseline(_line):
                    self.warning(f"Line not parsed: {_line!r}")

    def _parseline(
            self,
            line,  # type: bytes
    ):  # type: (...) -> bool
        """
        To be overloaded.

        :param line: Log output line to parse.
        :return: ``True`` if the line has been recognized and parsed.
        """
        return False

    def _debuglineinfo(
            self,
            data,  # type: typing.Any
            *args,  # type: typing.Any
    ):  # type: (...) -> None
        """
        Displays useful information from what has been parsed in a line.

        :param data: Data to display, or string format.
        :param args: ``data`` arguments.
        """
        if args:
            assert isinstance(data, str)
            self.debug("  => " + data, *args)
        else:
            # Display `data` in its `repr()` form.
            self.debug("  => %r", data)
