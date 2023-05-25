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

import re
import typing

import scenario

if True:
    from ._errortrackerlogger import ErrorTrackerLogger as _ErrorTrackerLoggerImpl  # `TrackerLogger` used for inheritance.
if typing.TYPE_CHECKING:
    from ._modulelevelcontext import ModuleLevelContext as _ModuleLevelContextType


class Import(_ErrorTrackerLoggerImpl):

    class ImportedSymbol:
        def __init__(
                self,
                src,  # type: bytes
        ):  # type: (...) -> None
            self.src = src  # type: bytes
            self.original_name = ""  # type: str
            self.local_name = ""  # type: str

        def ismodule(self):  # type: (...) -> bool
            return re.match(r"^[_a-z]+$", self.original_name) is not None

        def isconstant(self):  # type: (...) -> bool
            return re.match(r"^[_A-Z]+$", self.original_name) is not None

        def isreexport(self):  # type: (...) -> bool
            return all([
                self.local_name,
                not self.local_name.startswith("_"),
            ])

    def __init__(
            self,
            importer_module_path,  # type: scenario.Path
            importer_module_line,  # type: int
            context,  # type: _ModuleLevelContextType
            src,  # type: bytes
    ):  # type: (...) -> None
        from ._moduleparser import ModuleParser

        _ErrorTrackerLoggerImpl.__init__(self, f"{importer_module_path}:{importer_module_line}:")

        self.importer_module_path = importer_module_path  # type: scenario.Path
        self.importer_module_line = importer_module_line  # type: int
        self.context = context  # type: _ModuleLevelContextType
        self.src = ModuleParser.stripsrc(src)  # type: bytes
        self.imported_module_original_name = ""  # type: str
        self.imported_module_local_name = ""  # type: str
        self.imported_module_path = None  # type: typing.Optional[scenario.Path]
        self.imported_symbols = []  # type: typing.List[Import.ImportedSymbol]

    def __repr__(self):  # type: () -> str
        return "".join([
            f"<Import",
            f" context={self.context!r}",
            f" {self.importer_module_path}:{self.importer_module_line}:",
            f" {self.src!r}",
            f" => {self.imported_module_path}" if self.imported_module_path else "",
            f">",
        ])

    def parse(
            self,
            resolve=False,  # type: bool
    ):  # type: (...) -> None
        _match = None  # type: typing.Optional[typing.Match[bytes]]

        _match = re.match(rb'^import +([^ ,]+)( +as +([^ ,]*))?$', self.src)
        if _match:
            self.imported_module_original_name = _match.group(1).decode("utf-8")
            if _match.group(3):
                self.imported_module_local_name = _match.group(3).decode("utf-8")

        _match = re.match(rb'^from +([^ ,]+) +import +([^ ,].*)$', self.src)
        if _match:
            self.imported_module_original_name = _match.group(1).decode("utf-8")
            if _match.group(2):
                for _part in _match.group(2).split(b','):  # type: bytes
                    _part = _part.strip()
                    self.imported_symbols.append(Import.ImportedSymbol(_part))
                    _match = re.match(rb'^([^ ,]+)( +as +([^ ,]+))?$', _part)
                    if not _match:
                        raise SyntaxError(f"Invalid import part {_part!r}")
                    self.imported_symbols[-1].original_name = _match.group(1).decode("utf-8")
                    if _match.group(3):
                        self.imported_symbols[-1].local_name = _match.group(3).decode("utf-8")

        if not self.imported_module_original_name:
            raise SyntaxError(f"No module name found from {self.src!r}")

        if resolve:
            self.resolvemodulepath()

    def resolvemodulepath(self):  # type: (...) -> None
        from .. import _paths

        if not self.imported_module_original_name:
            raise ValueError("Import should be parsed before resolving module path")

        # Starting point.
        _module_name = self.imported_module_original_name  # type: str
        if self.imported_module_original_name.startswith("."):
            # Relative import.
            self.imported_module_path = self.importer_module_path
            while _module_name.startswith("."):
                self.imported_module_path = self.imported_module_path.parent
                _module_name = _module_name[1:]
        else:
            # `scenario` source root directories.
            for _scenario_root_name, _scenario_root_path in (
                # The first match will break the loop.
                ("scenario.test", _paths.TEST_SRC_PATH / "scenario" / "test"),
                ("scenario.tools", _paths.TOOLS_SRC_PATH / "scenario" / "tools"),
                ("scenario.text", _paths.UTILS_SRC_PATH / "scenario" / "text"),
                # Finish with `scenario`.
                ("scenario", _paths.SRC_PATH / "scenario"),
            ):  # type: str, scenario.Path
                if (
                    (self.imported_module_original_name == _scenario_root_name)
                    or self.imported_module_original_name.startswith(f"{_scenario_root_name}.")
                ):
                    self.imported_module_path = _scenario_root_path
                    # Remove the root name, with the following '.' character if any.
                    _module_name = self.imported_module_original_name[len(f"{_scenario_root_name}."):]
                    break

        # Follow remaining import names.
        if self.imported_module_path and _module_name:
            for _part in _module_name.split("."):  # type: str
                if (self.imported_module_path / _part).is_dir():
                    self.imported_module_path = self.imported_module_path / _part
                elif (self.imported_module_path / f"{_part}.py").is_file():
                    self.imported_module_path = self.imported_module_path / f"{_part}.py"
                else:
                    raise ImportError(f"Can't resolve {_part!r} from '{self.imported_module_path}'")

    def isfromsyntax(self):  # type: (...) -> bool
        return self.src.startswith(b'from ')

    def issystemimport(self):  # type: (...) -> bool
        return self.imported_module_path is None

    def isscenarioimport(self):  # type: (...) -> bool
        return self.imported_module_path is not None

    def isreexport(self):  # type: (...) -> bool
        return all([
            self.imported_symbols,
            all([_symbol.isreexport() for _symbol in self.imported_symbols]),
        ])
