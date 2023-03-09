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
    from scenarioexecution.steps.execution import ExecScenario as _ExecScenarioType


class CheckFullScenarioLogOutput(scenario.test.VerificationStep):

    def __init__(
            self,
            exec_step,  # type: _ExecScenarioType
    ):  # type: (...) -> None
        scenario.test.VerificationStep.__init__(self, exec_step)

        # Read the reference log file.
        assert len(exec_step.scenario_paths) == 1
        self._stdout_path_ref = scenario.test.paths.datapath(
            exec_step.scenario_paths[0].name.replace(
                ".py",
                ".doc-only.log" if exec_step.doc_only else ".executed.log",
            ),
        )  # type: scenario.Path
        self.assertisfile(self._stdout_path_ref)
        self._stdout_log_ref = self._stdout_path_ref.read_bytes()  # type: bytes

    def step(self):  # type: (...) -> None
        self.STEP("Full scenario log output")

        scenario.logging.resetindentation()

        _lines = []  # type: typing.List[bytes]
        if self.ACTION(f"Check the log output v/s the expected output '{self._stdout_path_ref}'."):
            _lines = self.subprocess.stdout.splitlines()
            # Remove last empty lines.
            while _lines and (not _lines[-1]):
                _lines = _lines[:-1]

        _lines_ref = self._stdout_log_ref.splitlines()  # type: typing.List[bytes]
        # Remove last empty lines.
        while _lines_ref and (not _lines_ref[-1]):
            _lines_ref = _lines_ref[:-1]

        for _line_index in range(len(_lines_ref)):  # type: int
            _line_ref = _lines_ref[_line_index]  # type: bytes
            if _line_ref.endswith(b'Time: 0.0 s'):
                if self.RESULT(f"Line {_line_index + 1} matches pattern 'Time: HH:MM:SS.uuuuuu'."):
                    self.assertgreater(len(_lines), _line_index, f"No such line {_line_index + 1}: {_line_ref!r}")
                    self.assertregex(
                        rb'^ *Time: \d{2}:\d{2}:\d{2}\.\d+$', _lines[_line_index],
                        evidence=f"Line {_line_index + 1}",
                    )
            else:
                if self.RESULT(f"Line {_line_index + 1} is {_line_ref!r}."):
                    self.assertgreater(len(_lines), _line_index, f"No such line {_line_index + 1}: {_line_ref!r}")
                    self.assertequal(
                        _lines[_line_index], _line_ref,
                        evidence=f"Line {_line_index + 1}",
                    )
