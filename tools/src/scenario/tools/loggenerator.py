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

import re
import shutil
import sys
import typing

import scenario

from .paths import MAIN_PATH
from .subprocess import SubProcess


FLOAT_DURATION_REGEX = rb'\d+.\d+'  # type: bytes
FLOAT_DURATION_SUBST = b'SSS.mmmmmm'  # type: bytes
STR_DURATION_REGEX = rb'\d{2}:\d{2}:\d{2}\.\d+'  # type: bytes
STR_DURATION_SUBST = b'HH:MM:SS.mmmmmm'  # type: bytes
ISO_8601_REGEX = rb'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{6}\+\d{2}:\d{2}'  # type: bytes
ISO_8601_SUBST = b'YYYY-MM-DDTHH:MM:SS.mmmmmm+HH:MM'  # type: bytes


class LogGenerator:
    """
    Create a log file from a script execution.
    """

    def __init__(
            self,
            outdir,  # type: scenario.Path
    ):  # type: (...) -> None
        self.outdir = outdir  # type: scenario.Path

    def execute(
            self,
            script,  # type: scenario.Path
            options=None,  # type: typing.List[typing.Union[str, scenario.AnyPathType]]
            positionals=None,  # type: typing.List[scenario.Path]
            suffix="",  # type: str
            summary=False,  # type: bool
            json_report=False,  # type: bool
            xml_report=False,  # type: bool
    ):  # type: (...) -> None
        if options is None:
            options = []
        if positionals is None:
            positionals = []

        _basename_no_ext = script.stem + suffix  # type: str
        if positionals:
            _basename_no_ext = "+".join([_positional.stem for _positional in positionals]) + suffix

        _log_out_path = self.outdir / (_basename_no_ext + ".log")  # type: scenario.Path
        _json_report_out_path = self.outdir / (_basename_no_ext + ".json")  # type: scenario.Path
        _tmp_outdir = None  # type: typing.Optional[scenario.Path]
        if positionals:
            if sum([_positional.name.endswith(".py") for _positional in positionals]) == 0:
                _tmp_outdir = MAIN_PATH / "out"
        _xml_report_out_path = self.outdir / (_basename_no_ext + ".xml")  # type: scenario.Path

        scenario.logging.info("Updating %s" % _log_out_path)
        _subprocess = SubProcess(sys.executable, script)  # type: SubProcess
        _subprocess.addargs("--config-value", "scenario.log_color", "0")
        _subprocess.addargs("--config-value", "scenario.log_date_time", "0")
        _subprocess.addargs(*options)
        for _positional in positionals:  # type: scenario.Path
            _subprocess.addargs(_positional)
        if json_report:
            _subprocess.addargs("--json-report", _json_report_out_path)
        if _tmp_outdir:
            scenario.logging.debug("Creating directory '%s'" % _tmp_outdir)
            _tmp_outdir.mkdir(parents=True, exist_ok=True)
            _subprocess.addargs("--outdir", _tmp_outdir)
        _subprocess.setcwd(MAIN_PATH)
        _subprocess.showstdout(False)
        _subprocess.run()

        # Scan each log line.
        _log_lines = []  # type: typing.List[bytes]
        _summary_total_line_index = -1  # type: int
        for _log_line in _subprocess.stdout.splitlines():  # type: bytes
            scenario.logging.debug("Log line: %s" % repr(_log_line))

            # Ensure the local 'scenario' path is not displayed in the documentation.
            _log_line = re.sub(rb'^(INFO +)Main path: \'.*\'$', b'\\1Main path: \'/path/to/scenario\'', _log_line)

            # Ensure the execution time does not fluctuate in the output log, for documentation purpose.
            _log_line = re.sub(STR_DURATION_REGEX, STR_DURATION_SUBST, _log_line)

            # Detect the summary total line.
            if re.search(rb'INFO +TOTAL +Status', _log_line):
                _summary_total_line_index = len(_log_lines)

            _log_lines.append(_log_line)

        # scenario.logging.info("Updating %s" % _log_out_path)  # Already logged above
        self._dumptext(_log_out_path, b'\n'.join(_log_lines))

        # Dump the scenario executions summary when required.
        if summary and (_summary_total_line_index > 0):
            _log_summary_out_path = self.outdir / (_basename_no_ext + ".summary.log")  # type: scenario.Path
            scenario.logging.info("Updating %s" % _log_summary_out_path)
            self._dumptext(_log_summary_out_path, b'\n'.join(_log_lines[_summary_total_line_index - 1:]))

        # Replace execution times in the JSON and XML reports with substitution patterns.
        if json_report:
            scenario.logging.info("Updating %s" % _json_report_out_path)
            _json_data = _json_report_out_path.read_bytes()  # type: bytes
            _json_data = re.sub(rb'"(start|end)": "%s"' % ISO_8601_REGEX, rb'"\1": "%s"' % ISO_8601_SUBST, _json_data)
            _json_data = re.sub(rb'"elapsed": %s' % FLOAT_DURATION_REGEX, rb'"elapsed": %s' % FLOAT_DURATION_SUBST, _json_data)
            self._dumptext(_json_report_out_path, _json_data)
        if xml_report:
            scenario.logging.info("Updating %s" % _xml_report_out_path)
            assert _tmp_outdir, "Temporary output directory should have been determined before"
            _xml_data = (_tmp_outdir / "campaign.xml").read_bytes()  # type: bytes
            _xml_data = re.sub(rb'time="%s"' % FLOAT_DURATION_REGEX, rb'time="%s"' % FLOAT_DURATION_SUBST, _xml_data)
            _xml_data = re.sub(rb'timestamp="%s"' % ISO_8601_REGEX, rb'timestamp="%s"' % ISO_8601_SUBST, _xml_data)
            _xml_data = re.sub(rb'Time: %s' % STR_DURATION_REGEX, rb'Time: %s' % STR_DURATION_SUBST, _xml_data)
            self._dumptext(_xml_report_out_path, _xml_data)

        if _tmp_outdir:
            scenario.logging.debug("Removing directory '%s'" % _tmp_outdir)
            shutil.rmtree(_tmp_outdir)

    def _dumptext(
            self,
            path,  # type: scenario.Path
            text,  # type: bytes
    ):  # type: (...) -> None
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.replace(b'\r', b''))
