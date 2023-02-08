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


class SubProcess(scenario.SubProcess):
    """
    Sub-process default configuration for the :mod:`scenario.tools` package.
    """

    def __init__(
            self,
            *args  # type: typing.Union[str, scenario.AnyPathType]
    ):  # type: (...) -> None
        """
        Initializes the :class:`scenario.subprocess.SubProcess` instance
        with a simple default configuration for sub-proces executions in the :mod:`scenario.tools` package:

        - Loggings with the main logger,
        - Exit on error by default.
        """
        scenario.SubProcess.__init__(self, *args)

        self._show_stdout = True  # type: bool
        self._show_stderr = True  # type: bool

        # Log stdout and stderr with the main logger.
        self.onstdoutline(self._onstdoutline)
        self.onstderrline(self._onstderrline)
        # Use the main logger for logging.
        self.setlogger(scenario.logging)
        # Exit on error by default.
        self.exitonerror(True)

    def showstdout(
            self,  # type: scenario.VarSubProcessType
            show_stdout,  # type: bool
    ):  # type: (...) -> scenario.VarSubProcessType
        assert isinstance(self, SubProcess)
        self._show_stdout = show_stdout
        return self  # type: ignore  ## Incompatible return value type (got "SubProcess", expected "scenario.VarSubProcessType")

    def showstderr(
            self,  # type: scenario.VarSubProcessType
            show_stderr,  # type: bool
    ):  # type: (...) -> scenario.VarSubProcessType
        assert isinstance(self, SubProcess)
        self._show_stderr = show_stderr
        return self  # type: ignore  ## Incompatible return value type (got "SubProcess", expected "scenario.VarSubProcessType")

    def _onstdoutline(
            self,
            line,  # type: bytes
    ):  # type: (...) -> None
        from scenario.logformatter import LogFormatter
        from scenario.scenarioconfig import SCENARIO_CONFIG

        if self._show_stdout:
            _line = line.decode("utf-8")  # type: str
            if not SCENARIO_CONFIG.logcolorenabled():
                _line = LogFormatter.nocolor(_line)
            scenario.logging.info(_line)

    def _onstderrline(
            self,
            line,  # type: bytes
    ):  # type: (...) -> None
        from scenario.logformatter import LogFormatter
        from scenario.scenarioconfig import SCENARIO_CONFIG

        if self._show_stderr:
            _line = line.decode("utf-8")  # type: str
            if not SCENARIO_CONFIG.logcolorenabled():
                _line = LogFormatter.nocolor(_line)
            scenario.logging.error(_line)
