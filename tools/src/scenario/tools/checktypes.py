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
                check_types,  # type: CheckTypes
        ):  # type: (...) -> None
            scenario.Args.__init__(self, class_debugging=False)

            self.setdescription("Typehints checker.")

            self.all = False  # type: bool
            self.addarg("All", "all", bool).define(
                "--all",
                action="store_true", default=False,
                help=f"Show all errors. Only the {check_types.max_errors} first errors otherwise.",
            )

    def __init__(
            self,
            main_path,  # type: scenario.AnyPathType
            mypy_conf_path,  # type: scenario.AnyPathType
            mypy_args=None,  # type: typing.Optional[typing.Sequence[str]]
            max_errors=50,  # type: int
    ):  # type: (...) -> None

        self.main_path = scenario.Path(main_path)  # type: scenario.Path
        self.mypy_conf_path = scenario.Path(mypy_conf_path)  # type: scenario.Path
        self.mypy_args = mypy_args or []  # type: typing.Sequence[str]
        self.max_errors = max_errors  # type: int

    def run(self):  # type: (...) -> scenario.ErrorCode
        from ._subprocess import SubProcess
        from .tracking import tracktoolversion

        # Command line arguments.
        if not scenario.Args.isset():
            scenario.Args.setinstance(CheckTypes.Args(self))
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
                if CheckTypes.Args.getinstance().all or (_errors < self.max_errors):
                    scenario.logging.error(_line.decode("utf-8"))
                elif (not CheckTypes.Args.getinstance().all) and (_errors == self.max_errors):
                    scenario.logging.error("...")
                _errors += 1
            else:
                scenario.logging.info(_line.decode("utf-8"))
        for _line in _subprocess.stderr.splitlines():
            scenario.logging.error(_line.decode("utf-8"))
            _errors += 1
        if _errors > 0:
            return scenario.ErrorCode.TEST_ERROR
        return scenario.ErrorCode.SUCCESS
