#!/usr/bin/env python
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

import os
import pathlib
import subprocess
import sys
import typing


_root_scenario_path = pathlib.Path(__file__).parents[1].resolve()  # type: pathlib.Path


class Command:
    #: Commands successfully executed.
    executed = []  # type: typing.List[Command]

    def __init__(
            self,
            *,
            title,  # type: str
            command,  # type: typing.Sequence[str]
    ):  # type: (...) -> None
        #: Command title.
        self.title = title  # type: str
        #: Command as a sequence of strings.
        self.command = command  # type: typing.Sequence[str]

    def commanddesc(
            self,
            hide_interpreter,  # type: bool
    ):  # type: (...) -> str
        """
        Command description computation.

        Ensures POSIX paths.

        :param hide_interpreter: ``True`` to completely hide the intepreter. ``False`` to keep it, but make it short (basename without suffix).
        :return: Command description string.
        """
        _command = list(self.command)  # type: typing.List[str]

        # Process interpreter.
        if (len(_command) > 1) and (_command[0] == sys.executable):
            if hide_interpreter:
                del _command[0]
            else:
                _command[0] = pathlib.Path(sys.executable).stem

        # Ensure POSIX paths.
        for _index, _arg in enumerate(_command):  # type: int, str
            if pathlib.Path(_arg).exists():
                _command[_index] = pathlib.Path(_arg).as_posix()
            elif (not pathlib.Path(_arg).is_absolute()) and (_root_scenario_path / _arg).exists():
                _command[_index] = pathlib.Path(_arg).as_posix()

        return " ".join(_command)

    def execute(self):  # type: (...) -> None
        if Command.executed:
            self._print("")

        self._print(f"=== {self.title} ===")
        self._print(f"{_root_scenario_path.as_posix()}> {self.commanddesc(hide_interpreter=False)}")
        try:
            subprocess.check_call(self.command, cwd=_root_scenario_path)
        except subprocess.CalledProcessError as _err:
            self._print(f"{_root_scenario_path.as_posix()}> {self.commanddesc(hide_interpreter=False)} (error)")
            self._print(f"    {_err!r}")
            sys.exit(_err.returncode)
        except KeyboardInterrupt:
            self._print(f"{_root_scenario_path.as_posix()}> {self.commanddesc(hide_interpreter=False)} (interrupted)")
            sys.exit(1)

        # Successful execution.
        Command.executed.append(self)

    def _print(
            self,
            msg,  # type: str
    ):  # type: (...) -> None
        """
        Ensures printing in stdout without interleaving with subprocess outputs.
        """
        print(msg)
        sys.stdout.flush()


if __name__ == '__main__':
    # Search for 'repo-checkfiles' from the `PATH` environment variable.
    for _env_path in (os.environ.get("PATH") or "").split(os.pathsep):  # type: str
        _script_path = pathlib.Path(_env_path) / "repo-checkfiles"  # type: pathlib.Path
        if _script_path.is_file():
            # If found, execute the command.
            Command(title="Check files", command=[sys.executable, str(_script_path)]).execute()
    Command(title="Check types", command=[sys.executable, "tools/check-types.py"]).execute()
    Command(title="Check imports", command=[sys.executable, "tools/check-imports.py"]).execute()
    Command(title="Update traceability", command=[sys.executable, "test/req-mgt.py"]).execute()
    Command(title="Generate documentation", command=[sys.executable, "tools/mkdoc.py"]).execute()
