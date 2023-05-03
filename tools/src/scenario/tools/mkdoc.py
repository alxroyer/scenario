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
import shutil
import sys
import typing

import scenario

from . import _paths  # `_paths` used for class member instanciation.


class MkDoc:

    PLANTUML_PATH = _paths.TOOLS_LIB_PATH / "plantuml.1.2020.15.jar"  # type: scenario.Path

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
        from .sphinx import sphinxbuild

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
            # sphinxapidoc()
            sphinxbuild()

    def checktools(self):  # type: (...) -> None
        from .sphinx import PY_SPHINX_APIDOC_CMD, PY_SPHINX_BUILD_CMD
        from .tracking import tracktoolversion

        tracktoolversion("python", [sys.executable, "--version"])
        tracktoolversion("sphinx-apidoc", [*PY_SPHINX_APIDOC_CMD, "--version"])
        tracktoolversion("sphinx-build", [*PY_SPHINX_BUILD_CMD, "--version"])
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
