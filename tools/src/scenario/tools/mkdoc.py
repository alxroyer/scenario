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

from . import _paths  # `_paths` used for class member instanciation.


class MkDoc:

    PLANTUML_PATH = _paths.TOOLS_LIB_PATH / "plantuml.1.2020.15.jar"  # type: scenario.Path
    PY_SPHINX_APIDOC = (sys.executable, "-m", "sphinx.ext.apidoc")  # type: typing.Sequence[str]
    PY_SPHINX_BUILD = (sys.executable, "-m", "sphinx.cmd.build")  # type: typing.Sequence[str]

    class Args(scenario.Args):
        def __init__(self):  # type: (...) -> None
            scenario.Args.__init__(self, class_debugging=False)

            self.setdescription("Documentation builder.")

            self.logs = False  # type: bool
            self.addarg("Log generation", "logs", bool).define(
                "--logs",
                action="store_true", default=False,
                help=f"Update log files only.",
            )

            self.uml = False  # type: bool
            self.addarg("UML diagram generation", "uml", bool).define(
                "--uml",
                action="store_true", default=False,
                help=f"Update UML diagrams only.",
            )

        @property
        def all(self):  # type: () -> bool
            if self.logs:
                return False
            if self.uml:
                return False
            return True

    def run(self):  # type: (...) -> None

        # Command line arguments.
        scenario.Args.setinstance(MkDoc.Args())
        scenario.Args.getinstance().setdescription("Documentation generation.")
        if not scenario.Args.getinstance().parse(sys.argv[1:]):
            sys.exit(int(scenario.Args.getinstance().error_code))

        # Execution.
        scenario.Path.setmainpath(_paths.MAIN_PATH)
        self.checktools()
        if MkDoc.Args.getinstance().all or MkDoc.Args.getinstance().logs:
            self.buildlogs()
        if MkDoc.Args.getinstance().all or MkDoc.Args.getinstance().uml:
            self.builddiagrams()
        if MkDoc.Args.getinstance().all:
            # `sphinxapidoc()` directly called from Sphinx handlers,
            # so that documentation generation from https://readthedocs.org/ generate the 'doc/src/py/' files automatically.
            # self.sphinxapidoc()
            self.sphinxbuild()

    def checktools(self):  # type: (...) -> None
        from .tracking import tracktoolversion

        tracktoolversion("python", [sys.executable, "--version"])
        tracktoolversion("sphinx-apidoc", [*MkDoc.PY_SPHINX_APIDOC, "--version"])
        tracktoolversion("sphinx-build", [*MkDoc.PY_SPHINX_BUILD, "--version"])
        # tracktoolversion("dot", ["dot", "-V"])  ## PlantUML does not need dot to be installed for regular sequence diagrams.
        tracktoolversion("java", ["java", "-version"])
        tracktoolversion("PlantUML", ["java", "-jar", self.PLANTUML_PATH, "-version"], cwd=_paths.MAIN_PATH)

    def buildlogs(self):  # type: (...) -> None
        """
        Updates the documentation log data files.

        Ensures the sample execution times do not fluctuate in the output documentation from build to build.
        """
        from ._subprocess import SubProcess

        _float_duration_regex = rb'\d+.\d+'  # type: bytes
        _float_duration_subst = b'SSS.mmmmmm'  # type: bytes
        _str_duration_regex = rb'\d{2}:\d{2}:\d{2}\.\d+'  # type: bytes
        _str_duration_subst = b'HH:MM:SS.mmmmmm'  # type: bytes
        _iso_8601_regex = rb'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{6}\+\d{2}:\d{2}'  # type: bytes
        _iso_8601_subst = b'YYYY-MM-DDTHH:MM:SS.mmmmmm+HH:MM'  # type: bytes

        def _generatelog(
                script,  # type: scenario.Path
                options=None,  # type: typing.List[typing.Union[str, scenario.AnyPathType]]
                positionals=None,  # type: typing.List[scenario.Path]
                suffix="",  # type: str
                summary=False,  # type: bool
                json_report=False,  # type: bool
                xml_report=False,  # type: bool
        ):  # type: (...) -> None
            """
            Create a log file from a script execution.
            """
            options = options or []
            positionals = positionals or []

            _basename_no_ext = script.stem + suffix  # type: str
            if positionals:
                _basename_no_ext = "+".join([_positional.stem for _positional in positionals]) + suffix

            _log_out_path = _paths.DOC_DATA_PATH / (_basename_no_ext + ".log")  # type: scenario.Path
            _json_report_out_path = _paths.DOC_DATA_PATH / (_basename_no_ext + ".json")  # type: scenario.Path
            _tmp_outdir = None  # type: typing.Optional[scenario.Path]
            if positionals:
                if sum([_positional.name.endswith(".py") for _positional in positionals]) == 0:
                    _tmp_outdir = _paths.MAIN_PATH / "out"
            _xml_report_out_path = _paths.DOC_DATA_PATH / (_basename_no_ext + ".xml")  # type: scenario.Path

            scenario.logging.info(f"Updating {_log_out_path}")
            _subprocess = SubProcess(sys.executable, script)  # type: SubProcess
            _subprocess.addargs("--config-value", "scenario.log_color", "0")
            _subprocess.addargs("--config-value", "scenario.log_date_time", "0")
            _subprocess.addargs(*options)
            for _positional in positionals:  # type: scenario.Path
                _subprocess.addargs(_positional)
            if json_report:
                _subprocess.addargs("--json-report", _json_report_out_path)
            if _tmp_outdir:
                scenario.logging.debug("Creating directory '%s'", _tmp_outdir)
                _tmp_outdir.mkdir(parents=True, exist_ok=True)
                _subprocess.addargs("--outdir", _tmp_outdir)
            _subprocess.setcwd(_paths.MAIN_PATH)
            _subprocess.showstdout(False)
            _subprocess.run()

            # Scan each log line.
            _log_lines = []  # type: typing.List[bytes]
            _summary_total_line_index = -1  # type: int
            for _log_line in _subprocess.stdout.splitlines():  # type: bytes
                scenario.logging.debug("Log line: %r", _log_line)

                # Ensure the local 'scenario' path is not displayed in the documentation.
                _log_line = re.sub(rb'^(INFO +)Main path: \'.*\'$', b'\\1Main path: \'/path/to/scenario\'', _log_line)

                # Ensure the execution time does not fluctuate in the output log, for documentation purpose.
                _log_line = re.sub(_str_duration_regex, _str_duration_subst, _log_line)

                # Detect the summary total line.
                if re.search(rb'INFO +TOTAL +Status', _log_line):
                    _summary_total_line_index = len(_log_lines)

                _log_lines.append(_log_line)

            # scenario.logging.info(f"Updating {_log_out_path}")  # Already logged above
            _dumptext(_log_out_path, b'\n'.join(_log_lines))

            # Dump the scenario executions summary when required.
            if summary and (_summary_total_line_index > 0):
                _log_summary_out_path = _paths.DOC_DATA_PATH / (_basename_no_ext + ".summary.log")  # type: scenario.Path
                scenario.logging.info(f"Updating {_log_summary_out_path}")
                _dumptext(_log_summary_out_path, b'\n'.join(_log_lines[_summary_total_line_index - 1:]))

            # Replace execution times in the JSON and XML reports with substitution patterns.
            if json_report:
                scenario.logging.info(f"Updating {_json_report_out_path}")
                _json_data = _json_report_out_path.read_bytes()  # type: bytes
                _json_data = re.sub(rb'"(start|end)": "%s"' % _iso_8601_regex, rb'"\1": "%s"' % _iso_8601_subst, _json_data)
                _json_data = re.sub(rb'"elapsed": %s' % _float_duration_regex, rb'"elapsed": %s' % _float_duration_subst, _json_data)
                _dumptext(_json_report_out_path, _json_data)
            if xml_report:
                scenario.logging.info(f"Updating {_xml_report_out_path}")
                assert _tmp_outdir, "Temporary output directory should have been determined before"
                _xml_data = (_tmp_outdir / "campaign.xml").read_bytes()  # type: bytes
                _xml_data = re.sub(rb'time="%s"' % _float_duration_regex, rb'time="%s"' % _float_duration_subst, _xml_data)
                _xml_data = re.sub(rb'timestamp="%s"' % _iso_8601_regex, rb'timestamp="%s"' % _iso_8601_subst, _xml_data)
                _xml_data = re.sub(rb'Time: %s' % _str_duration_regex, rb'Time: %s' % _str_duration_subst, _xml_data)
                _dumptext(_xml_report_out_path, _xml_data)

            if _tmp_outdir:
                scenario.logging.debug("Removing directory '%s'", _tmp_outdir)
                shutil.rmtree(_tmp_outdir)

        def _dumptext(
                path,  # type: scenario.Path
                text,  # type: bytes
        ):  # type: (...) -> None
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(text.replace(b'\r', b''))

        # Help logs.
        _generatelog(
            _paths.BIN_PATH / "run-test.py", options=["--help"],
            suffix=".help",
        )
        _generatelog(
            _paths.BIN_PATH / "run-campaign.py", options=["--help"],
            suffix=".help",
        )
        _generatelog(
            _paths.DEMO_PATH / "run-demo.py", options=["--help"],
            suffix=".help",
        )

        # Scenario executions.
        _generatelog(
            _paths.BIN_PATH / "run-test.py",
            positionals=[_paths.DEMO_PATH / "commutativeaddition.py"],
            json_report=True,
        )
        _generatelog(
            _paths.BIN_PATH / "run-test.py",
            positionals=[_paths.DEMO_PATH / "commutativeadditions.py"],
            json_report=True,
        )
        _generatelog(
            _paths.BIN_PATH / "run-test.py",
            positionals=[_paths.DEMO_PATH / "loggingdemo.py"],
            json_report=True,
        )
        _generatelog(
            _paths.BIN_PATH / "run-test.py",
            positionals=[_paths.DEMO_PATH / "commutativeaddition.py", _paths.DEMO_PATH / "loggingdemo.py"],
            summary=True,
        )
        _generatelog(
            _paths.DEMO_PATH / "run-demo.py", options=[
                "--config-file", _paths.DEMO_PATH / "conf.json",
                "--config-value", "x.y[0].z", "0",
                "--show-configs",
                _paths.DEMO_PATH / "htmllogin.py",
            ],
            suffix=".show-configs",
        )
        if (_paths.DEMO_PATH / "htmllogin.log").exists():
            (_paths.DEMO_PATH / "htmllogin.log").unlink()

        # Campaign executions.
        _generatelog(
            _paths.BIN_PATH / "run-campaign.py", positionals=[_paths.DEMO_PATH / "demo.suite"],
            suffix=".campaign", summary=True, xml_report=True,
        )

        # Import dependencies.
        _generatelog(_paths.MAIN_PATH / "tools" / "checkdeps.py")

    def builddiagrams(self):  # type: (...) -> None
        """
        Builds the documentation diagrams.
        """
        from ._subprocess import SubProcess
        from .deps import shouldupdate

        _cfg_path = _paths.TOOLS_CONF_PATH / "umlconf.uml"  # type: scenario.Path
        for _path in (_paths.DOC_SRC_PATH / "uml").iterdir():  # type: scenario.Path
            if _path.is_file() and _path.name.endswith(".uml") and (not _path.samefile(_cfg_path)):
                _png_outpath = _path.parent / _path.name.replace(".uml", ".png")  # type: scenario.Path
                if shouldupdate(_png_outpath, [_path, _cfg_path]):
                    scenario.logging.info(f"Generating {_png_outpath} from {_path}")
                    _subprocess = SubProcess("java", "-jar", self.PLANTUML_PATH)  # type: SubProcess
                    _subprocess.addargs("-config", _cfg_path)
                    _subprocess.addargs(_path)
                    _subprocess.setcwd(_paths.MAIN_PATH)
                    _subprocess.run()
                else:
                    scenario.logging.info(f"No need to update {_png_outpath} from {_path}")

    def sphinxapidoc(self):  # type: (...) -> None
        """
        Sphinx-apidoc execution: build .rst source files from the python sources.
        """
        from ._subprocess import SubProcess

        # First remove the previous 'doc/src/py/' directory with its .rst generated files.
        # Useful in case source modules have been renamed.
        if (_paths.DOC_SRC_PATH / "py").is_dir():
            scenario.logging.info(f"Removing {_paths.DOC_SRC_PATH / 'py'}")
            shutil.rmtree(_paths.DOC_SRC_PATH / "py")

        # Execute sphinx-apidoc.
        #
        # [SPHINX_APIDOC_HELP]:
        #     `sphinx-apidoc --help`
        scenario.logging.info("Executing sphinx-apidoc...")

        _subprocess = SubProcess(*MkDoc.PY_SPHINX_APIDOC)  # type: SubProcess
        # [SPHINX_APIDOC_HELP]:
        #     -o DESTDIR, --output-dir DESTDIR = "directory to place all output"
        _subprocess.addargs("--output-dir", _paths.DOC_SRC_PATH / "py")
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
        _subprocess.addargs(_paths.SRC_PATH / "scenario")

        _subprocess.setcwd(_paths.MAIN_PATH)
        _subprocess.run()

        # Fix 'scenario.rst'.
        _scenario_rst_path = _paths.DOC_SRC_PATH / "py" / "scenario.rst"  # type: scenario.Path
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

    def sphinxbuild(self):  # type: (...) -> None
        """
        Sphinx-build execution: build the sphinx documentation.

        Useful options:
          -b buildername = The most important option: it selects a builder.
          -a = write all files (default: only write new and changed files)
          -n = nit-picky mode, warn about all missing references
               => Generates tons of false errors, due to typings that sphinx does not handle correctly. Do not use.
          -W = turn warnings into errors
          --color = do emit colored output (default: auto-detect)
          -q = no output on stdout, just warnings on stderr
          -v = increase verbosity (can be repeated)
          -T = show full traceback on exception
        """
        from ._subprocess import SubProcess

        scenario.logging.info("Executing sphinx-build...")

        scenario.logging.debug("Ensuring every .rst file timestamp has been updated")
        for _path in scenario.tools.paths.DOC_SRC_PATH.iterdir():  # type: scenario.Path
            if _path.is_file() and _path.name.endswith(".rst"):
                scenario.logging.debug("%r.touch()", _path)
                _path.touch()

        # Prepare the $(sphinx-build) process.
        _subprocess = SubProcess(*MkDoc.PY_SPHINX_BUILD)  # type: SubProcess
        # Debug & display:
        if scenario.Args.getinstance().debug_main:
            _subprocess.addargs("-vv")
        _subprocess.addargs("--color")
        # Builder:
        _subprocess.addargs("-b", "html")
        # Write all files:
        _subprocess.addargs("-a")
        # Configuration file:
        _subprocess.addargs("-c", _paths.TOOLS_CONF_PATH / "sphinx")
        # Source directory:
        _subprocess.addargs(_paths.DOC_SRC_PATH)
        # Output directory:
        _subprocess.addargs(_paths.DOC_OUT_PATH)

        # $(sphinx-build) execution.
        def _onstderrline(line):  # type: (bytes) -> None
            _level = logging.ERROR  # type: int
            if b'TODO entry found:' in line:
                # Just warn on todos.
                _level = logging.WARNING
            elif b'WARNING: duplicate object description' in line:
                # Just debug dublicate object warnings.
                _level = logging.DEBUG
            scenario.logging.log(_level, line.decode("utf-8"))
        _subprocess.onstderrline(_onstderrline)
        _subprocess.setcwd(_paths.MAIN_PATH)
        _subprocess.run()
