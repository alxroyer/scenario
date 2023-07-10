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

import sys
import typing

import scenario


class CheckTypes:

    PY_MYPY = (sys.executable, "-m", "mypy")  # type: typing.Sequence[str]

    class Args(scenario.Args):
        def __init__(
                self,
                default_max_errors=None,  # type: int
        ):  # type: (...) -> None
            scenario.Args.__init__(self, class_debugging=False)

            self.setdescription("Python code type checker.")

            self.max_errors = default_max_errors or 50  # type: int
            self.addarg("Max errors", "max_errors", int).define(
                "--max-errors", metavar="MAX_ERRORS",
                action="store", default=self.max_errors,
                help=f"Set the maximum number of errors to display. {self.max_errors} by default.",
            )

            self.all_errors = False  # type: bool
            self.addarg("All errors", "all_errors", bool).define(
                "--all-errors",
                action="store_true", default=False,
                help="Show all errors. Only MAX_ERRORS first errors otherwise.",
            )

    def __init__(
            self,
            main_path,  # type: scenario.AnyPathType
            mypy_conf_path,  # type: scenario.AnyPathType
            mypy_args=None,  # type: typing.Optional[typing.Sequence[str]]
            max_errors=None,  # type: int
    ):  # type: (...) -> None

        self.main_path = scenario.Path(main_path)  # type: scenario.Path
        self.mypy_conf_path = scenario.Path(mypy_conf_path)  # type: scenario.Path
        self.mypy_args = mypy_args or []  # type: typing.Sequence[str]
        self._default_max_errors = max_errors  # type: typing.Optional[int]

    def run(self):  # type: (...) -> scenario.ErrorCode
        from ._subprocess import SubProcess
        from .tracking import tracktoolversion

        # Command line arguments.
        if not scenario.Args.isset():
            scenario.Args.setinstance(CheckTypes.Args(default_max_errors=self._default_max_errors))
            if not CheckTypes.Args.getinstance().parse(sys.argv[1:]):
                sys.exit(int(CheckTypes.Args.getinstance().error_code))

        # Set main path after arguments have been parsed.
        scenario.Path.setmainpath(self.main_path)

        # Mypy version verification.
        tracktoolversion("python", [sys.executable, "--version"])
        tracktoolversion("mypy", [*CheckTypes.PY_MYPY, "--version"])

        # Mypy execution.
        scenario.logging.info(f"Executing mypy with '{self.mypy_conf_path}'...")
        _subprocess = SubProcess(*CheckTypes.PY_MYPY)  # type: SubProcess
        _subprocess.addargs("--config-file", self.mypy_conf_path, *self.mypy_args)
        _subprocess.setcwd(self.main_path)
        _subprocess.showstdout(False).showstderr(False)
        _subprocess.exitonerror(False).run()

        # Display results.
        _errors = 0  # type: int
        for _line in _subprocess.stdout.splitlines():  # type: bytes
            if b'error:' in _line:
                if CheckTypes.Args.getinstance().all_errors or (_errors < CheckTypes.Args.getinstance().max_errors):
                    scenario.logging.error(_line.decode("utf-8"))
                else:
                    scenario.logging.debug("Error line skipped: %r", _line)
                    if _errors == CheckTypes.Args.getinstance().max_errors:
                        scenario.logging.error("...")
                _errors += 1
            elif (b'note: ' in _line) and (_line.endswith(b' defined here')):
                scenario.logging.debug(_line.decode("utf-8"))
            else:
                scenario.logging.info(_line.decode("utf-8"))
        for _line in _subprocess.stderr.splitlines():
            scenario.logging.error(_line.decode("utf-8"))
            _errors += 1
        if _errors > 0:
            return scenario.ErrorCode.TEST_ERROR
        return scenario.ErrorCode.SUCCESS
