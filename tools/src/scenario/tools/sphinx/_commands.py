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
import shutil
import sys
import typing

import scenario


PY_SPHINX_APIDOC_CMD = (sys.executable, "-m", "sphinx.ext.apidoc")  # type: typing.Sequence[str]
PY_SPHINX_BUILD_CMD = (sys.executable, "-m", "sphinx.cmd.build")  # type: typing.Sequence[str]


def sphinxapidoc():  # type: (...) -> None
    """
    Sphinx-apidoc execution: build .rst source files from the python sources.

    See [SPHINX_APIDOC_HELP]: `sphinx-apidoc --help`
    """
    from .._paths import DOC_SRC_PATH, MAIN_PATH, SRC_PATH
    from .._subprocess import SubProcess

    # First remove the previous 'doc/src/py/' directory with its .rst generated files.
    # Useful in case source modules have been renamed.
    _doc_src_py_path = DOC_SRC_PATH / "py"  # type: scenario.Path
    if _doc_src_py_path.is_dir():
        scenario.logging.info(f"Removing {_doc_src_py_path}")
        shutil.rmtree(_doc_src_py_path)

    # Execute sphinx-apidoc.
    scenario.logging.info("Executing sphinx-apidoc...")

    _subprocess = SubProcess(*PY_SPHINX_APIDOC_CMD)  # type: SubProcess
    # [SPHINX_APIDOC_HELP]:
    #     -o DESTDIR, --output-dir DESTDIR = "directory to place all output"
    _subprocess.addargs("--output-dir", _doc_src_py_path)
    # [SPHINX_APIDOC_HELP]:
    #     -f, --force = "overwrite existing files"
    #
    # Apparently, does not ensure an update of the output file timestamps,
    # That's the reason why the `shutil.rmtree()` call above still needs to be done.
    _subprocess.addargs("--force")
    # [SPHINX_APIDOC_HELP]:
    #     -M, --module-first = "put module documentation before submodule documentation"
    _subprocess.addargs("--module-first")
    # [SPHINX_APIDOC_HELP]:
    #     -P, --private = "include '_private' modules"
    #
    # We choose to leave the documentation for exported symbols in separate private module pages for the following reasons:
    # - Lots of cross references are missing otherwise.
    # - It keeps the main `scenario` page short and well organized (huge, hard to navigate into otherwise).
    _subprocess.addargs("--private")
    # [SPHINX_APIDOC_HELP]:
    #     -e, --separate = "put documentation for each module on its own page"
    _subprocess.addargs("--separate")
    _subprocess.addargs(SRC_PATH / "scenario")

    _subprocess.setcwd(MAIN_PATH)
    _subprocess.run()

    # Fix 'scenario.rst'.
    _scenario_rst_path = _doc_src_py_path / "scenario.rst"  # type: scenario.Path
    scenario.logging.info(f"Fixing {_scenario_rst_path}")
    _scenario_rst_lines = _scenario_rst_path.read_bytes().splitlines()  # type: typing.List[bytes]
    _line_index = 0  # type: int
    while _line_index < len(_scenario_rst_lines):
        _line = _scenario_rst_lines[_line_index]  # type: bytes
        _match = re.search(rb'(:.*members:)', _line)  # type: typing.Optional[typing.Match[bytes]]
        if _match:
            # Avoid documenting module members for 'scenario/__init__.py',
            # otherwise Sphinx repeats documentation for each exported symbol at the end of the module.
            # This causes "more than one target found for cross-reference" errors,
            # and is moreover contradictory with the `--private` and `--separate` *apidoc* options used above.
            scenario.logging.debug("Removing automodule `%s` option for 'scenario'", _match.group(1).decode("utf-8"))
            del _scenario_rst_lines[_line_index]
            continue
        if b':maxdepth:' in _line:
            # Limit private module TOC depth to 1,
            # otherwise all symbols contained in each are displayed with this TOC,
            # which is heavy and useless.
            scenario.logging.debug("Fixing submodule toc depth to 1")
            _scenario_rst_lines[_line_index] = _line = re.sub(rb'^(.*:maxdepth:) *(\d+)$', rb'\1 1', _line)
        _line_index += 1
    _scenario_rst_path.write_bytes(b'\n'.join(_scenario_rst_lines))


def sphinxbuild():  # type: (...) -> None
    """
    Sphinx-build execution: build the sphinx documentation.

    See [SPHINX_BUILD_HELP]: `sphinx-build --help`
    """
    from .._paths import DOC_OUT_PATH, DOC_SRC_PATH, MAIN_PATH, TOOLS_CONF_PATH
    from .._subprocess import SubProcess

    scenario.logging.info("Executing sphinx-build...")

    # Update timestamps.
    scenario.logging.debug("Ensuring every .rst file timestamp has been updated")
    for _path in DOC_SRC_PATH.iterdir():  # type: scenario.Path
        if _path.is_file() and _path.name.endswith(".rst"):
            scenario.logging.debug("%r.touch()", _path)
            _path.touch()

    # Prepare the $(sphinx-build) process.
    _subprocess = SubProcess(*PY_SPHINX_BUILD_CMD)  # type: SubProcess

    # Debug & display:
    # [SPHINX_BUILD_HELP]:
    #     -q = no output on stdout, just warnings on stderr
    # _subprocess.addargs("-q")
    # [SPHINX_BUILD_HELP]:
    #     -v = increase verbosity (can be repeated)
    if scenario.Args.getinstance().debug_main:
        _subprocess.addargs("-vv")
    # [SPHINX_BUILD_HELP]:
    #     -T = show full traceback on exception
    # if scenario.Args.getinstance().debug_main:
    #     _subprocess.addargs("-T")
    # [SPHINX_BUILD_HELP]:
    #     --color = do emit colored output (default: auto-detect)
    _subprocess.addargs("--color")

    # Builder:
    # [SPHINX_BUILD_HELP]:
    #     -b buildername = The most important option: it selects a builder.
    _subprocess.addargs("-b", "html")

    # Write all files:
    # [SPHINX_BUILD_HELP]:
    #     -a = write all files (default: only write new and changed files)
    _subprocess.addargs("-a")

    # Configuration file:
    # [SPHINX_BUILD_HELP]:
    #     -c PATH = path where configuration file (conf.py) is located
    #               (default: same as SOURCEDIR)
    _subprocess.addargs("-c", TOOLS_CONF_PATH / "sphinx")

    # Errors:
    # [SPHINX_BUILD_HELP]:
    #     -W = turn warnings into errors
    # _subprocess.addargs("-W")
    # [SPHINX_BUILD_HELP]:
    #     -n = nit-picky mode, warn about all missing references
    #
    # Generates tons of false errors, due to typings that sphinx does not handle correctly. Do not use.
    # _subprocess.addargs("-n")

    # Source directory:
    # [SPHINX_BUILD_HELP]:
    #     path to documentation source files
    _subprocess.addargs(DOC_SRC_PATH)

    # Output directory:
    # [SPHINX_BUILD_HELP]:
    #     path to output directory
    _subprocess.addargs(DOC_OUT_PATH)

    # $(sphinx-build) execution.
    def _onstderrline(line):  # type: (bytes) -> None
        _level = logging.ERROR  # type: int
        if b'TODO entry found:' in line:
            # Just warn on todos.
            _level = logging.WARNING
        scenario.logging.log(_level, line.decode("utf-8"))

    _subprocess.onstderrline(_onstderrline)
    _subprocess.setcwd(MAIN_PATH)
    _subprocess.run()
