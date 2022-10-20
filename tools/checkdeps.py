#!/usr/bin/env python
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
import pathlib
import sys
import typing

# Path management.
MAIN_PATH = pathlib.Path(__file__).parents[1]  # type: pathlib.Path
sys.path.append(str(MAIN_PATH / "src"))
sys.path.append(str(MAIN_PATH / "tools" / "src"))

# :mod:`scenario` imports.
import scenario  # noqa: E402  ## Module level import not at top of file
import scenario.tools  # noqa: E402  ## Module level import not at top of file


class CheckDeps:

    def run(self):  # type: (...) -> None
        # Command line arguments.
        scenario.Args.setinstance(scenario.Args(class_debugging=False))
        scenario.Args.getinstance().setdescription("Module dependency checker.")
        if not scenario.Args.getinstance().parse(sys.argv[1:]):
            sys.exit(int(scenario.Args.getinstance().error_code))

        # Set main path after arguments have been parsed.
        scenario.Path.setmainpath(scenario.tools.paths.MAIN_PATH, log_level=logging.DEBUG)

        self.lsdeps()
        self.computedeps()
        self.sortdeps()

    def lsdeps(self):  # type: (...) -> None
        scenario.logging.debug("Walking through '%s'", scenario.tools.paths.SRC_PATH / "scenario")
        for _src_path in (scenario.tools.paths.SRC_PATH / "scenario").iterdir():  # type: scenario.Path
            if _src_path.is_file() and _src_path.name.endswith(".py"):
                _current_module = ModuleDeps.get(_src_path.name)  # type: ModuleDeps
                scenario.logging.debug("  Reading %s:", _src_path)
                for _line in _src_path.read_bytes().splitlines():  # type: bytes
                    if not _line.startswith(b'from .'):
                        continue
                    _words = _line.split()  # type: typing.List[bytes]
                    assert len(_words) >= 4
                    assert _words[0] == b'from'
                    assert _words[2] == b'import'
                    if _words[1] != b'.':
                        # Regular ``from <module> import ...`` pattern.
                        # The 2nd word is the module name.
                        _module_name = _words[1][1:]  # type: bytes

                        scenario.logging.debug("    %s => %s", _src_path.name, _module_name.decode("utf-8") + ".py")
                        _current_module.adddep(ModuleDeps.get(_module_name.decode("utf-8") + ".py"))
                    else:
                        # ``from . import <module>`` pattern (usually in '__init__.py' files).
                        # The module name(s) is(are) after the ``import`` keyword.
                        _line = _line[_line.find(b'import') + len(b'import'):]
                        # Get rid of the trailing comment if any.
                        if b'#' in _line:
                            _line = _line[:_line.find(b'#')]
                        # Consider that several modules may be imported in a row:
                        # `from . import <module1>, <module2>, ...`
                        for _module_name in _line.split(b','):  # Type already declared above.
                            # Modules may be aliases with the ``as`` keyword:
                            # ``from . import <module> as <alias>``
                            _module_name = _module_name.split()[0]

                            scenario.logging.debug("    %s => %s", _src_path.name, _module_name.decode("utf-8") + ".py")
                            _current_module.adddep(ModuleDeps.get(_module_name.decode("utf-8") + ".py"))

    def computedeps(self):  # type: (...) -> None
        scenario.logging.debug("Computing deps")
        for _basename in ModuleDeps.all:  # type: str
            _module = ModuleDeps.get(_basename)  # type: ModuleDeps
            scenario.logging.debug("%s: %d", _module.basename, _module.getscore())

    def sortdeps(self):  # type: (...) -> None
        scenario.logging.debug("Sorting deps")
        _deps = []  # type: typing.List[ModuleDeps]
        for _basename in ModuleDeps.all:  # type: str
            _deps.append(ModuleDeps.get(_basename))
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
            _line = f"<{_dep.getscore():02d}> "  # type: str
            _line += f"{_dep.basename:>{_max_basename_len}} "  # Note: Use of the '>' format specifier on the basenames to have them right-aligned.
            _line += f"=> [{', '.join(sorted(x.basename for x in _dep.deps))}]"

            # Display it on several lines if it is more than 120 characters long.
            while _line:
                _line_length = len(_line)  # type: int
                if _line_length > 120:
                    _line_length = _line[:120].rfind(" ")
                scenario.logging.info(_line[:_line_length])
                _line = _line[_line_length:].lstrip()
                if _line:
                    # Note: The use of the '>' format specifier ensures expected amount of space characters.
                    _line = " " * len(f"<{0:02d}> {'':>{_max_basename_len}} => [") + _line


class ModuleDeps:
    class ComputationStatus(scenario.enum.StrEnum):
        NOT_STARTED = "not-started"
        COMPUTING = "computing"
        DONE = "done"

    all = {}  # type: typing.Dict[str, ModuleDeps]
    #: TODO: Use :mod:`scenario` logging indentation facilities instead?
    indent_count = 0  # type: int

    @staticmethod
    def get(
            basename,  # type: str
    ):  # type: (...) -> ModuleDeps
        if basename not in ModuleDeps.all:
            ModuleDeps.all[basename] = ModuleDeps(basename)
        return ModuleDeps.all[basename]

    def __init__(
            self,
            basename,  # type: str
    ):  # type: (...) -> None
        self.basename = basename  # type: str
        self.status = ModuleDeps.ComputationStatus.NOT_STARTED  # type: ModuleDeps.ComputationStatus
        self.deps = []  # type: typing.List[ModuleDeps]
        self.score = 0  # type: int

    def adddep(
            self,
            dep,  # type: ModuleDeps
    ):  # type: (...) -> None
        if dep not in self.deps:
            self.deps.append(dep)

    def getscore(self):  # type: (...) -> int
        if self.status == ModuleDeps.ComputationStatus.DONE:
            return self.score

        assert self.status != ModuleDeps.ComputationStatus.COMPUTING, "Cyclic module dependency"
        scenario.logging.debug("%s%s: Computing score...", "  " * ModuleDeps.indent_count, self.basename)
        ModuleDeps.indent_count += 1
        self.status = ModuleDeps.ComputationStatus.COMPUTING
        _max = 0  # type: int
        for _dep in self.deps:  # type: ModuleDeps
            if _dep.getscore() > _max:
                _max = _dep.getscore()
        self.score = _max + 1
        self.status = ModuleDeps.ComputationStatus.DONE
        ModuleDeps.indent_count -= 1
        scenario.logging.debug("%s%s: score=%d...", "  " * ModuleDeps.indent_count, self.basename, self.score)
        return self.score


if __name__ == "__main__":
    CheckDeps().run()
