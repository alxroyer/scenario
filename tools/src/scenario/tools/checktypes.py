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

import configparser
import os
import re
import sys
import tempfile
import typing

import scenario
import scenario.inners


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

        #: {temporary name: initial name} dictionary.
        self._tmp_renames = {}  # type: typing.Dict[scenario.Path, scenario.Path]

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

        try:
            # Mypy version verification.
            tracktoolversion("python", [sys.executable, "--version"])
            tracktoolversion("mypy", [*CheckTypes.PY_MYPY, "--version"])

            # Work around duplicate name scripts.
            self._avoidduplicatenames()

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
                # Check for starting path.
                _match = re.match(rb'^(.*)(:\d+: .*)$', _line)  # type: typing.Optional[typing.Match[bytes]]
                if _match:
                    _path = self.main_path / _match.group(1).decode("utf-8")  # type: scenario.Path
                    if _path.is_file():
                        _path = self._tmp_renames.get(_path, _path)
                        _line = _path.prettypath.encode("utf-8") + _match.group(2)

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

        except Exception as _err:
            scenario.logging.logexceptiontraceback(_err)
            return scenario.ErrorCode.fromexception(_err)

        finally:
            # Ensure file name restorations at the end.
            self._restoreduplicatenames()

    def _avoidduplicatenames(self):  # type: (...) -> None
        # Read `mypy_path` and `files` configuration.
        _config_parser = configparser.ConfigParser()  # type: configparser.ConfigParser
        # Override the optionxform member in ordre to make the ConfigParser case sensitive.
        # See https://stackoverflow.com/questions/1611799/preserve-case-in-configparser#1611877/964122
        _config_parser.optionxform = lambda optionstr: optionstr  # type: ignore[assignment]  ## Cannot assign to a method
        _res = _config_parser.read(self.mypy_conf_path, encoding=scenario.inners.textfileutils.guessencoding(self.mypy_conf_path))  # type: typing.List[str]
        if os.fspath(self.mypy_conf_path) not in _res:
            raise IOError(f"Could not read '{self.mypy_conf_path}'")

        # Ensure `mypy_path` configuration is set in `sys.path`.
        _mypy_path = []  # type: typing.List[scenario.Path]
        for _part in _config_parser.get("mypy", "mypy_path", fallback="").split(":"):  # type: str
            if _part.strip():
                _mypy_path.append(self.main_path / _part.strip())
        scenario.logging.debug("`mypy_path` configuration read from '%s' (%d paths):", self.mypy_conf_path, len(_mypy_path))
        for _index, _path in enumerate(_mypy_path):  # type: int, scenario.Path
            scenario.logging.debug("- '%s'", _path)
        sys.path.extend([os.fspath(_path) for _path in _mypy_path])

        # Resolve `files` configuration with related module names.
        _files = []  # type: typing.List[scenario.Path]
        for _part in _config_parser.get("mypy", "files", fallback="").split(","):  # Type already declared above.
            if _part.strip():
                _files.extend(self.main_path.glob(_part.strip()))
        _module_names = [scenario.inners.reflection.modulenamefrompath(_) for _ in _files]  # type: typing.List[str]
        scenario.logging.debug("`files` configuration read from '%s' (%d files):", self.mypy_conf_path, len(_files))
        for _index, _path in enumerate(_files):  # Types already declared above.
            scenario.logging.debug("- '%s' (module name: %r)", _path, _module_names[_index])

        # Dequeue `_files` and `_module_names` lists, and check for duplicate names.
        self._tmp_renames.clear()
        while _files and _module_names:
            _script_path = _files.pop(0)  # type: scenario.Path
            _module_name = _module_names.pop(0)  # type: str

            try:
                while True:
                    # Search for `_module_name` in the remaining `_module_names` list.
                    # Raises a `ValueError` if the module name can't be found.
                    _index = _module_names.index(_module_name)  # Type already declared above.

                    def _mktmppath(path):  # type: (scenario.Path) -> None
                        _tmp_path = path  # type: scenario.Path
                        while scenario.inners.reflection.modulenamefrompath(_tmp_path) in _module_names:
                            _tmp_path = scenario.Path(tempfile.mktemp(dir=path.parent, prefix=path.stem + ".", suffix=".py"))
                        scenario.logging.debug("Renaming duplicate '%s' into '%s'", path, _tmp_path)
                        self._tmp_renames[_tmp_path] = path
                        path.rename(_tmp_path)

                    # Rename `_script_path` (if not already renamed).
                    if _script_path not in self._tmp_renames:
                        _mktmppath(_script_path)

                    # Rename `_files[_index]`.
                    _mktmppath(_files[_index])

                    # Remove processed file and module name,
                    # and search for another occurrence of `_module_name` in `_module_names`.
                    del _files[_index]
                    del _module_names[_index]
            except ValueError:
                # No such `_module_name` (anymore) in the remaining `_module_names` list.
                pass

    def _restoreduplicatenames(self):  # type: (...) -> None
        for _renamed_path, _initial_path in self._tmp_renames.items():  # type: scenario.Path, scenario.Path
            scenario.logging.debug("Restoring '%s' into '%s'", _renamed_path, _initial_path)
            _renamed_path.rename(_initial_path)
