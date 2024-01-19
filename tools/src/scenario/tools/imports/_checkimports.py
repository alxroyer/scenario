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
import re
import sys
import typing

import scenario
import scenario.text

if typing.TYPE_CHECKING:
    from ._moduleparser import ModuleParser as _ModuleParserType


class CheckImports:

    class Args(scenario.Args):
        def __init__(self):  # type: (...) -> None
            scenario.Args.__init__(self, class_debugging=False)

            self.setdescription("Import checker.")

            self.paths = []  # type: typing.List[scenario.Path]
            self.addarg("Path(s)", "paths", scenario.Path).define(
                metavar="PATH", nargs="*",
                action="store", type=str, default=[],
                help="Path(s) to check.",
            )

    def __init__(self):  # type: (...) -> None
        self.modules = []  # type: typing.List[_ModuleParserType]

    def run(self):  # type: (...) -> scenario.ErrorCode
        from .. import _paths
        from ._errortrackerlogger import ErrorTrackerLogger

        # Command line arguments.
        scenario.Args.setinstance(CheckImports.Args())
        if not scenario.Args.getinstance().parse(sys.argv[1:]):
            sys.exit(int(scenario.Args.getinstance().error_code))

        # Set main path after arguments have been parsed.
        scenario.Path.setmainpath(_paths.ROOT_SCENARIO_PATH, log_level=logging.INFO)

        # Process paths.
        for _start_path in (CheckImports.Args.getinstance().paths or (
            _paths.BIN_PATH,
            # _paths.DEMO_PATH,  # Don't process 'demo/' scripts.
            _paths.SRC_PATH,
            _paths.TEST_PATH,
            _paths.TOOLS_PATH,
        )):  # type: scenario.Path
            self._walkpath(_start_path)

        # Final result.
        _modules = scenario.text.Countable("module", self.modules)  # type: scenario.text.Countable
        _errors = scenario.text.Countable("import error", ErrorTrackerLogger.errors)  # type: scenario.text.Countable
        if not ErrorTrackerLogger.errors:
            scenario.logging.info(f"Success: no {_errors} in {len(_modules)} {_modules}")
            return scenario.ErrorCode.SUCCESS
        else:
            scenario.logging.info(f"{len(_errors)} {_errors} in {len(_modules)} {_modules}")
            return scenario.ErrorCode.TEST_ERROR

    def _walkpath(
            self,
            path,  # type: scenario.Path
    ):  # type: (...) -> None
        if path.is_dir():
            scenario.logging.debug("%s: Walking through directory", path)
            for _subpath in path.iterdir():  # type: scenario.Path
                self._walkpath(_subpath)
        elif path.suffix == ".py":
            scenario.logging.debug("%s: Analyzing module", path)
            self._checkmodule(path)
        else:
            scenario.logging.debug("%s: Skipping file", path)

    def _checkmodule(
            self,
            path,  # type: scenario.Path
    ):  # type: (...) -> None
        from ._moduleparser import ModuleParser

        _module_parser = ModuleParser(path)
        self.modules.append(_module_parser)
        try:
            _module_parser.parse()
        except Exception as _err:
            _module_parser.error(f"{_err}")
            return

        self._checkmodulelevelimports(_module_parser)
        self._checklocalimports(_module_parser)

    def _checkmodulelevelimports(
            self,
            module_parser,  # type: _ModuleParserType
    ):  # type: (...) -> None
        from .. import _paths
        from ._import import Import

        # Check module level imports.
        module_parser.debug("%d module level import(s)", len(module_parser.module_level_imports))
        for _import in module_parser.module_level_imports:  # type: Import

            # === Import context ===

            # ---
            # RULE: Only system imports at pure module level.
            # ---
            if _import.context.ispuremodulelevel():
                if any([
                    # Pure system import.
                    _import.issystemimport(),
                    # `scenario.test` and `scenario.tools` may import `scenario` and `scenario.text`.
                    all([
                        any([
                            _import.importer_module_path.is_relative_to(_paths.TEST_SRC_PATH),
                            _import.importer_module_path.is_relative_to(_paths.TOOLS_SRC_PATH),
                        ]),
                        any([
                            _import.imported_module_original_name == "scenario",
                            _import.imported_module_original_name == "scenario.text",
                        ]),
                    ]),
                    # Test launchers, cases, data and tool scripts may import `scenario`, `scenario.test` and `scenario.text`.
                    all([
                        any([
                            _import.importer_module_path.match(f"{_paths.TEST_PATH.abspath}/*.py"),
                            _import.importer_module_path.is_relative_to(_paths.TEST_CASES_PATH),
                            _import.importer_module_path.is_relative_to(_paths.TEST_DATA_PATH),
                            _import.importer_module_path.is_relative_to(_paths.TEST_TOOLS_PATH),
                        ]),
                        any([
                            _import.imported_module_original_name == "scenario",
                            _import.imported_module_original_name == "scenario.test",
                            _import.imported_module_original_name == "scenario.text",
                        ]),
                    ]),
                    # Tool scripts and configurations may import `scenario`, `scenario.tools` (with subpackages) and `scenario.text`.
                    all([
                        any([
                            _import.importer_module_path.match(f"{_paths.TOOLS_PATH.abspath}/*.py"),
                            _import.importer_module_path.is_relative_to(_paths.TOOLS_CONF_PATH),
                        ]),
                        any([
                            _import.imported_module_original_name == "scenario",
                            _import.imported_module_original_name == "scenario.tools",
                            _import.imported_module_original_name.startswith("scenario.tools."),
                            _import.imported_module_original_name == "scenario.text",
                        ]),
                    ]),
                ]):
                    _import.debug("Pure module level system import %r", _import.src)

                    # ---
                    # RULE: Don't import symbols from system imports
                    # ---
                    if _import.imported_symbols:
                        _import.error("Don't import symbols from system imports: %r", _import.src)
                    else:
                        _import.debug("System import without symbols: %r", _import.src)
                else:
                    _import.error("Only system imports at pure module level: %r", _import.src)

            # ---
            # RULE: Avoid `# noqa` on module level imports.
            # ---
            if re.search(rb'# *noqa', _import.src):
                _import.error("Avoid `# noqa` on module level imports: %r", _import.src)

            # ---
            # RULE: Avoid unqualified `if` blocks.
            # ---
            if _import.context.isunqualifiedifblock():
                _import.error("Import made from an unqualified `if` block: %r", _import.src)

            # ---
            # RULE: Avoid `try` blocks, except for reexports.
            # ---
            if _import.context.istryblock():
                if _import.isreexport():
                    _import.debug("Reexport in a `try` block: %r", _import.src)
                else:
                    _import.error("Avoid `try` blocks, except for reexports: %r", _import.src)

            # === Import syntax ===

            # ---
            # RULE: Only one symbol per import line.
            # ---
            if len(_import.imported_symbols) == 0:
                _import.debug("Module import without symbols: %r", _import.src)
            elif len(_import.imported_symbols) == 1:
                _import.debug("Only one imported symbol: %r", _import.src)
            else:
                _import.error("Several symbols imported in a single line: %r", _import.src)

            # === Imported symbols ===

            if _import.context.isifblockmain():
                # Don't check renames, privates or reexports in main blocks.
                _import.debug("Main block import %r")
            else:
                for _imported_symbol in _import.imported_symbols:  # type: Import.ImportedSymbol
                    if not _imported_symbol.local_name:
                        # ---
                        # RULE: Module level imports should be renamed.
                        # ---
                        _import.error("Imported symbol %r should be renamed: %r", _imported_symbol.original_name, _import.src)
                    elif _imported_symbol.local_name == _imported_symbol.original_name:
                        # Regular reexport.
                        _import.debug("Regular reexport for %r: %r", _imported_symbol.original_name, _import.src)
                    elif any([
                        _import.importer_module_path.name == "__init__.py",
                        _import.importer_module_path in [
                            _paths.SRC_PATH / "scenario" / "_typeexports.py",
                        ],
                    ]):
                        # Renamed reexport.
                        _import.debug("Renamed reexport for %r: %r", _imported_symbol.original_name, _import.src)
                    else:
                        # ---
                        # RULE: Symbols imported at module level should renamed as private.
                        # ---
                        if _imported_symbol.local_name.startswith("_"):
                            _import.debug("Symbol %r imported as private %r: %r", _imported_symbol.original_name, _imported_symbol.local_name, _import.src)
                        else:
                            _import.error("Imported symbol %r should be prefixed with '_': %r", _imported_symbol.original_name, _import.src)

                        # ---
                        # RULE: Symbols imported at module level for execution should suffixed with 'Impl'.
                        # ---
                        if not _import.context.isifblocktype():
                            if _imported_symbol.ismodule():
                                _import.debug("%r module import does not require a suffix: %r", _imported_symbol.original_name, _import.src)
                            elif _imported_symbol.isconstant():
                                _import.debug("%r constant import does not require a suffix: %r", _imported_symbol.original_name, _import.src)
                            elif _imported_symbol.local_name.endswith("Impl"):
                                _import.debug("%r suffixed with 'Impl' as expected: %r", _imported_symbol.original_name, _import.src)
                            else:
                                _import.error("%r should be suffixed with 'Impl': %r", _imported_symbol.original_name, _import.src)

                        # ---
                        # RULE: Symbols imported at module level for typings should suffixed with 'Type' (if not already named so).
                        # ---
                        if _import.context.isifblocktype():
                            if _imported_symbol.local_name.endswith("Type"):
                                _import.debug("%r suffixed with 'Type as expected: %r", _imported_symbol.original_name, _import.src)
                            else:
                                _import.error("%r should be suffixed with 'Type': %r", _imported_symbol.original_name, _import.src)

    def _checklocalimports(
            self,
            module_parser,  # type: _ModuleParserType
    ):  # type: (...) -> None
        from .. import _paths
        from ._import import Import
        from ._optimized import OPTIMIZED_PATHS

        # Check all files in `OPTIMIZED_MODULES` correspond to actual files.
        for _path in OPTIMIZED_PATHS:  # type: scenario.Path
            scenario.Assertions.assertisfile(_path)

        # Check local imports.
        module_parser.debug("%d local import(s)", len(module_parser.local_imports))
        for _import in module_parser.local_imports:  # type: Import
            # ---
            # RULE: Avoid local imports for optimized modules in main `scenario` modules
            #       (except for imports from `scenario.ui` to `scenario` modules).
            # ---
            if _import.importer_module_path.is_relative_to(_paths.SRC_PATH) and (_import.imported_module_path in OPTIMIZED_PATHS):
                if (
                    _import.importer_module_path.is_relative_to(_paths.SRC_PATH / "scenario" / "ui")
                    and _import.imported_module_path and (_import.imported_module_path.parent == (_paths.SRC_PATH / "scenario"))
                ):
                    _import.debug("Ignored local import for optimized %r from `scenario.ui`", _import.imported_module_original_name)
                else:
                    _import.error("Avoid local import for optimized %r", _import.imported_module_original_name)
