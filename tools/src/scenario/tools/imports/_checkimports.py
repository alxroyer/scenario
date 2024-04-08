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
    from ._import import Import as _ImportType
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

        # Check configuration data.
        self._checkconfigdata()

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

    def _checkconfigdata(self):  # type: (...) -> None
        from ._optimized import OPTIMIZED_PATHS

        # Check all files in `OPTIMIZED_MODULES` correspond to actual files.
        for _path in OPTIMIZED_PATHS:  # type: scenario.Path
            scenario.Assertions.assertisfile(_path)

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

        # Parse the module.
        _module_parser = ModuleParser(path)
        self.modules.append(_module_parser)
        try:
            _module_parser.parse()
        except Exception as _err:
            _module_parser.error(f"{_err}")
            return
        _module_parser.debug("%d module level import(s)", len(_module_parser.module_level_imports))
        _module_parser.debug("%d local import(s)", len(_module_parser.local_imports))

        # Check imports.
        self._checkimportcontext(_module_parser)
        self._checkimportsyntax(_module_parser)
        self._checkimportedsymbols(_module_parser)
        self._checkimportjustfications(_module_parser)
        self._checklocalimports(_module_parser)

    def _checkimportcontext(
            self,
            module_parser,  # type: _ModuleParserType
    ):  # type: (...) -> None
        from .. import _paths

        for _import in module_parser.module_level_imports:  # type: _ImportType
            # ---
            # RULE: Only system imports at pure module level.
            # ---
            if _import.context.ispuremodulelevel():
                if any([
                    # Pure system import.
                    _import.issystemimport(),
                    # `scenario.test` and `scenario.tools` may import `scenario`, `scenario.inners` and `scenario.text`.
                    all([
                        any([
                            _import.importer_module_path.is_relative_to(_paths.TEST_SRC_PATH),
                            _import.importer_module_path.is_relative_to(_paths.TOOLS_SRC_PATH),
                        ]),
                        any([
                            _import.imported_module_original_name == "scenario",
                            _import.imported_module_original_name == "scenario.inners",
                            _import.imported_module_original_name == "scenario.text",
                        ]),
                    ]),
                    # Test launchers, cases, data and tool scripts may import `scenario`, `scenario.test`, `scenario.inners` and `scenario.text`.
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
                            _import.imported_module_original_name == "scenario.inners",
                            _import.imported_module_original_name == "scenario.text",
                        ]),
                    ]),
                    # Tool scripts and configurations may import `scenario`, `scenario.tools` (with subpackages), `scenario.inners` and `scenario.text`.
                    all([
                        any([
                            _import.importer_module_path.match(f"{_paths.TOOLS_PATH.abspath}/*.py"),
                            _import.importer_module_path.is_relative_to(_paths.TOOLS_CONF_PATH),
                        ]),
                        any([
                            _import.imported_module_original_name == "scenario",
                            _import.imported_module_original_name == "scenario.tools",
                            _import.imported_module_original_name.startswith("scenario.tools."),
                            _import.imported_module_original_name == "scenario.inners",
                            _import.imported_module_original_name == "scenario.text",
                        ]),
                    ]),
                ]):
                    _import.debug("Pure module level system import %r", _import.stripped_src)

                    # ---
                    # RULE: Don't import symbols from system imports
                    # ---
                    if _import.imported_symbols:
                        _import.error("Don't import symbols from system imports: %r", _import.stripped_src)
                    else:
                        _import.debug("System import without symbols: %r", _import.stripped_src)
                else:
                    _import.error("Only system imports at pure module level: %r", _import.stripped_src)

            # ---
            # RULE: Avoid unqualified `if` blocks.
            # ---
            if _import.context.isunqualifiedifblock():
                _import.error("Import made from an unqualified `if` block: %r", _import.stripped_src)

            # ---
            # RULE: Avoid `try` blocks, except for reexports.
            # ---
            if _import.context.istryblock():
                if _import.isreexport():
                    _import.debug("Reexport in a `try` block: %r", _import.stripped_src)
                else:
                    _import.error("Avoid `try` blocks, except for reexports: %r", _import.stripped_src)

            # ---
            # RULE: Avoid duplicate module imports between implementation and typing imports.
            # ---
            if _import.context.isifblockimpl() and _import.ismoduleimport():
                for _typing_import in module_parser.typing_imports:  # type: _ImportType
                    if _typing_import.ismoduleimport():
                        if _typing_import.imported_module_final_path == _import.imported_module_final_path:
                            _import.error("Duplicate module import: %r", _import.stripped_src)
                            _typing_import.error("Duplicate module import: %r", _typing_import.stripped_src)
                            break
                else:
                    _import.debug("No duplicate typing import for implementation module import: %r", _import.stripped_src)

    def _checkimportsyntax(
            self,
            module_parser,  # type: _ModuleParserType
    ):  # type: (...) -> None
        from ._form import expectedform, ImportForm

        for _import in module_parser.module_level_imports:  # type: _ImportType
            # ---
            # RULE: Only one symbol per import line.
            # ---
            if len(_import.imported_symbols) == 0:
                _import.debug("Module import without symbols: %r", _import.stripped_src)
            elif len(_import.imported_symbols) == 1:
                _import.debug("Only one imported symbol: %r", _import.stripped_src)
            else:
                _import.error("Several symbols imported in a single line: %r", _import.stripped_src)

            # ---
            # RULE: Desired import form.
            # ---
            if _import.imported_module_final_path and (not _import.isreexport()):
                _expected_form = expectedform(_import.imported_module_final_path)  # type: ImportForm
                if _import.form() != _expected_form:
                    _import.error("`%s` syntax expected: %r", _expected_form, _import.stripped_src)
                else:
                    _import.debug("`%s` syntax as expected: %r", _expected_form, _import.stripped_src)

    def _checkimportedsymbols(
            self,
            module_parser,  # type: _ModuleParserType
    ):  # type: (...) -> None
        for _import in module_parser.module_level_imports:  # type: _ImportType
            if _import.context.isifblockmain():
                # Don't check imported symbols in main blocks.
                # Consider as local imports for the purpose.
                _import.debug("Main block import %r")
            else:
                for _imported_symbol in _import.imported_symbols:  # type: _ImportType.ImportedSymbol
                    if not _imported_symbol.local_name:
                        # ---
                        # RULE: Module level imports should be renamed.
                        # ---
                        _import.error("Imported symbol %r should be renamed: %r", _imported_symbol.original_name, _import.stripped_src)
                    elif _imported_symbol.local_name == _imported_symbol.original_name:
                        # Regular reexport.
                        _import.debug("Regular reexport for %r: %r", _imported_symbol.original_name, _import.stripped_src)
                    elif _import.isreexport():
                        # Renamed reexport.
                        _import.debug("Renamed reexport for %r: %r", _imported_symbol.original_name, _import.stripped_src)
                    else:
                        # ---
                        # RULE: Symbols imported at module level should renamed as private.
                        # ---
                        if _imported_symbol.local_name.startswith("_"):
                            _import.debug("Symbol %r imported as private %r: %r",
                                          _imported_symbol.original_name, _imported_symbol.local_name, _import.stripped_src)
                        else:
                            _import.error("Imported symbol %r should be prefixed with '_': %r",
                                          _imported_symbol.original_name, _import.stripped_src)

                        # ---
                        # RULE: Symbols imported at module level for execution should suffixed with 'Impl'.
                        # ---
                        if not _import.context.isifblocktype():  # Note: Not typing import, i.e. implementation import.
                            if _imported_symbol.ismodule():
                                _import.debug("%r module import does not require a suffix: %r", _imported_symbol.original_name, _import.stripped_src)
                            elif _imported_symbol.isconstant():
                                _import.debug("%r constant import does not require a suffix: %r", _imported_symbol.original_name, _import.stripped_src)
                            elif _imported_symbol.isfunction():
                                _import.debug("%r function import does not require a suffix: %r", _imported_symbol.original_name, _import.stripped_src)
                            elif _imported_symbol.local_name.endswith("Impl"):
                                _import.debug("%r suffixed with 'Impl' as expected: %r", _imported_symbol.original_name, _import.stripped_src)
                            else:
                                _import.error("%r should be suffixed with 'Impl': %r", _imported_symbol.original_name, _import.stripped_src)

                        # ---
                        # RULE: Symbols imported at module level for typings should suffixed with 'Type' (if not already named so).
                        # ---
                        if _import.context.isifblocktype():
                            if _imported_symbol.local_name.endswith("Type"):
                                _import.debug("%r suffixed with 'Type as expected: %r", _imported_symbol.original_name, _import.stripped_src)
                            else:
                                _import.error("%r should be suffixed with 'Type': %r", _imported_symbol.original_name, _import.stripped_src)

    def _checkimportjustfications(
            self,
            module_parser,  # type: _ModuleParserType
    ):  # type: (...) -> None
        for _import in module_parser.module_level_imports:  # type: _ImportType
            # ---
            # RULE: Avoid `# noqa` on module level imports
            #       (except for main blocks and for reexports).
            # ---
            if re.search(rb'# *noqa', _import.raw_src) and (not _import.context.isifblockmain()) and (not _import.isreexport()):
                _import.error("Avoid `# noqa` on module level imports: %r", _import.raw_src)

            # ---
            # RULE: Implementation imports shall be justified.
            # ---
            if _import.context.isifblockimpl() and (not _import.isreexport()):
                _match = re.match(rb"^[^#]*#(.*)$", _import.raw_src)  # type: typing.Optional[typing.Match[bytes]]
                if (not _match) or (not _match.group(1).strip()):
                    _import.error("Justification missing with implementation import")
                else:
                    # ---
                    # RULE: Implementation import shall be justified with justfification tags.
                    # ---
                    _justification = _match.group(1).strip()  # type: bytes
                    # Avoid other pragmas if any, try to focus on justification tags.
                    _match = re.search(rb'# +(@[^#]+)(#.*|)$', _justification)
                    if _match:
                        _justification = _match.group(1).strip()
                    _justification_tags = [
                        b'@after-path-management',
                        b'@inheritance', b'@metaclass',
                        b'@module-level-instantiation', b'@class-member-instantiation',
                        b'@module-level-execution',
                        b'@perf',
                    ]  # type: typing.Sequence[bytes]
                    if not all([
                        _part in _justification_tags
                        for _part in map(lambda b: b.strip(), _justification.split(b','))
                    ]):
                        _import.warning("Unclassified justification %r", _justification)

    def _checklocalimports(
            self,
            module_parser,  # type: _ModuleParserType
    ):  # type: (...) -> None
        from .. import _paths
        from ._optimized import OPTIMIZED_PATHS

        for _import in module_parser.local_imports:  # type: _ImportType
            # ---
            # RULE: Avoid local imports for optimized modules
            #       (except for imports from `scenario.ui` to `scenario` modules).
            # ---
            if _import.imported_module_path and (_import.imported_module_path in OPTIMIZED_PATHS):
                if (
                    _import.importer_module_path.is_relative_to(_paths.SRC_PATH / "scenario" / "ui")
                    and (_import.imported_module_path.parent == (_paths.SRC_PATH / "scenario"))
                ):
                    _import.debug("Local import for optimized module ignored from `scenario.ui`: %r", _import.stripped_src)
                else:
                    _import.error("Avoid local import for optimized module: %r", _import.stripped_src)
