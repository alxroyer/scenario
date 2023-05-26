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
import sys
import typing

import scenario


class CheckModuleDeps:

    def run(self):  # type: (...) -> scenario.ErrorCode
        from .._paths import MAIN_PATH

        # Command line arguments.
        scenario.Args.setinstance(scenario.Args(class_debugging=False))
        scenario.Args.getinstance().setdescription("Module dependency checker.")
        if not scenario.Args.getinstance().parse(sys.argv[1:]):
            return scenario.Args.getinstance().error_code

        # Set main path after arguments have been parsed.
        scenario.Path.setmainpath(MAIN_PATH, log_level=logging.DEBUG)

        self._parseimports()
        self._computedeps()
        self._sortdeps()

        return scenario.ErrorCode.SUCCESS

    def _parseimports(self):  # type: (...) -> None
        from .._paths import SRC_PATH
        from ._moduledeps import ModuleDeps

        scenario.logging.debug("Walking through '%s'", SRC_PATH / "scenario")
        for _src_path in (SRC_PATH / "scenario").iterdir():  # type: scenario.Path
            if _src_path.is_file() and _src_path.name.endswith(".py"):
                _current_module = ModuleDeps.get(_src_path)  # type: ModuleDeps
                _current_module.parser.parse()
            elif _src_path.is_dir() and (_src_path.name == "__pycache__"):
                pass
            else:
                raise FileExistsError(f"Unexpected file or directory '{_src_path}'")

    def _computedeps(self):  # type: (...) -> None
        from ._moduledeps import ModuleDeps

        scenario.logging.debug("Computing deps")
        for _module in ModuleDeps.all.values():  # type: ModuleDeps
            scenario.logging.debug("%s: %d", _module.basename, _module.getscore())

    def _sortdeps(self):  # type: (...) -> None
        from ._moduledeps import ModuleDeps

        scenario.logging.debug("Sorting deps")
        _deps = list(ModuleDeps.all.values())  # type: typing.List[ModuleDeps]
        _deps = sorted(
            _deps,
            # Use a combination of score + basename, so that items are ordered by scores, then by basenames.
            # Artificially reverse the scores so that the higher scores get sorted first.
            key=lambda deps: f"{1000000 - deps.getscore():06d}-{deps.basename}",
        )

        scenario.logging.debug("Displaying deps")
        _max_basename_len = max(len(_dep.basename) for _dep in _deps)  # type: int
        for _dep in _deps:  # type: ModuleDeps
            # Build the full line.
            # Note: The '>' format specifier makes the basenames right-aligned.
            _left = f"<{_dep.getscore():02d}> {_dep.basename:>{_max_basename_len}} => ["  # type: str
            _line = f"{_left}{', '.join(sorted(_dep2.basename for _dep2 in _dep.deps))}]"  # type: str

            # Display it on several lines if it is more than 120 characters long.
            while _line:
                _line_length = len(_line)  # type: int
                if _line_length > 120:
                    _line_length = _line[:120].rfind(" ")
                scenario.logging.info(_line[:_line_length])
                _line = _line[_line_length:].lstrip()
                if _line:
                    _line = f"{' ' * len(_left)}{_line}"
