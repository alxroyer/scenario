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
        self.raw_src = src  # type: bytes
        self.stripped_src = ModuleParser.stripsrc(src)  # type: bytes
        self._imported_module_original_name = ""  # type: str
        self._imported_module_local_name = None  # type: typing.Optional[str]
        self._imported_module_path = None  # type: typing.Optional[scenario.Path]
        self._imported_module_final_path = None  # type: typing.Optional[scenario.Path]
        self._imported_symbols = []  # type: typing.List[Import.ImportedSymbol]

        self._parsed = False  # type: bool
        self._resolved = False  # type: bool

    def __repr__(self):  # type: () -> str
        return "".join([
            f"<Import",
            f" context={self.context!r}",
            f" {self.importer_module_path}:{self.importer_module_line}:",
            f" {self.stripped_src!r}",
            f" => {self._imported_module_path}" if self._imported_module_path else "",
            f">",
        ])

    def isfromsyntax(self):  # type: (...) -> bool
        return self.stripped_src.startswith(b'from ')

    @property
    def imported_module_original_name(self):  # type: () -> str
        self._ensureparsed()
        return self._imported_module_original_name

    @property
    def imported_module_local_name(self):  # type: () -> typing.Optional[str]
        self._ensureparsed()
        return self._imported_module_local_name

    @property
    def imported_module_path(self):  # type: () -> typing.Optional[scenario.Path]
        self._ensureresolved()
        return self._imported_module_path

    @property
    def imported_module_final_path(self):  # type: () -> typing.Optional[scenario.Path]
        """
        May differ from :attr:`imported_module_path`:

        1. when the imported symbol is a module (single imported symbol only),
        2. if not option 1 above, when the imported module is a package.
        """
        self._ensureresolved()
        return self._imported_module_final_path

    def issystemimport(self):  # type: (...) -> bool
        return self.imported_module_path is None

    def isscenarioimport(self):  # type: (...) -> bool
        return self.imported_module_path is not None

    @property
    def imported_symbols(self):  # type: () -> typing.Sequence[Import.ImportedSymbol]
        self._ensureparsed()
        return self._imported_symbols

    def isreexport(self):  # type: (...) -> bool
        from .. import _paths

        if not any([
            self.importer_module_path.name == "__init__.py",
            self.importer_module_path in [
                _paths.SRC_PATH / "scenario" / "_typeexports.py",
                _paths.TEST_CASES_PATH / "steps" / "common.py",
                _paths.TEST_SRC_PATH / "scenario" / "test" / "_datascenarios.py",
            ],
        ]):
            return False
        if self.imported_symbols:
            return all([_symbol.isreexport() for _symbol in self.imported_symbols])
        return False

    def _ensureparsed(
            self,
    ):  # type: (...) -> None
        # Parse once.
        if self._parsed:
            return
        self._parsed = True

        _match = None  # type: typing.Optional[typing.Match[bytes]]

        _match = re.match(rb'^import +([^ ,]+)( +as +([^ ,]*))?$', self.stripped_src)
        if _match:
            self._imported_module_original_name = _match.group(1).decode("utf-8")
            if _match.group(3):
                self._imported_module_local_name = _match.group(3).decode("utf-8")

        _match = re.match(rb'^from +([^ ,]+) +import +([^ ,].*)$', self.stripped_src)
        if _match:
            self._imported_module_original_name = _match.group(1).decode("utf-8")
            if _match.group(2):
                for _part in _match.group(2).split(b','):  # type: bytes
                    _part = _part.strip()
                    self._imported_symbols.append(Import.ImportedSymbol(_part))
                    _match = re.match(rb'^([^ ,]+)( +as +([^ ,]+))?$', _part)
                    if not _match:
                        self.raiseerror(SyntaxError, f"Invalid import part {_part!r}")
                    self._imported_symbols[-1].original_name = _match.group(1).decode("utf-8")
                    if _match.group(3):
                        self._imported_symbols[-1].local_name = _match.group(3).decode("utf-8")

        if not self._imported_module_original_name:
            self.raiseerror(SyntaxError, f"Failed to parse {self.stripped_src!r}")

    def _ensureresolved(self):  # type: (...) -> None
        from .. import _paths

        # Resolve once.
        if self._resolved:
            return
        self._resolved = True

        # Ensure the import is parsed before resolving it.
        self._ensureparsed()

        # Starting point.
        _module_name = self._imported_module_original_name  # type: str
        _path = None  # type: typing.Optional[scenario.Path]
        if _module_name.startswith("."):
            # Relative import.
            _path = self.importer_module_path
            while _module_name.startswith("."):
                _path = _path.parent
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
                    (self._imported_module_original_name == _scenario_root_name)
                    or self._imported_module_original_name.startswith(f"{_scenario_root_name}.")
                ):
                    _path = _scenario_root_path
                    # Remove the root name, with the following '.' character if any.
                    _module_name = self._imported_module_original_name[len(f"{_scenario_root_name}."):]
                    break

        def _resolvesubmodulepath(
                directory_path,  # type: scenario.Path
                submodule_name,  # type: str
        ):  # type: (...) -> scenario.Path
            if not directory_path.is_dir():
                self.raiseerror(ImportError, f"Can't resolve {submodule_name!r} from '{directory_path}', '{directory_path}' not a directory")
            if (directory_path / submodule_name).is_dir():
                return directory_path / submodule_name
            if (directory_path / f"{submodule_name}.py").is_file():
                return directory_path / f"{submodule_name}.py"
            self.raiseerror(ImportError, f"Can't resolve {submodule_name!r} from '{directory_path}'")

        # Follow remaining import names.
        if _path and _module_name:
            for _part in _module_name.split("."):  # type: str
                _path = _resolvesubmodulepath(_path, _part)

        # No error: save resolved path (if any).
        self._imported_module_path = _path

        # Finish with computing the final path.
        if _path and _path.is_dir() and (len(self._imported_symbols) == 1) and self._imported_symbols[0].ismodule():
            _path = _resolvesubmodulepath(_path, self._imported_symbols[0].original_name)
        if _path and _path.is_dir():
            _path = _path / "__init__.py"

        # No error: save resolved final path (if any).
        self._imported_module_final_path = _path

    def error(
            self,
            msg,  # type: str
            *args,  # type: typing.Any
            **kwargs  # type: typing.Any
    ):  # type: (...) -> None
        """
        :class:`scenario._logger.Logger.error()` override, for ``'# check-imports: ignore'`` pattern management.

        Automatically redirected to :class:`scenario._logger.Logger.debug()` when ignored.
        """
        if b'# check-imports: ignore' not in self.raw_src:
            # Error not ignored.
            super().error(msg, *args, **kwargs)
        else:
            # Error ignored.
            _args = list(args)  # type: typing.List[typing.Any]
            while self.stripped_src in _args:
                _args[_args.index(self.stripped_src)] = self.raw_src
            self.debug("(Ignored) " + msg, *_args, **kwargs)
