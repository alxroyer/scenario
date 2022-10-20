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

import math
import re
import time
import typing

import scenario
import scenario.test

# Related steps:
from .execution import ExecCampaign


class CheckCampaignNoDtOutdir(scenario.test.VerificationStep):

    def step(self):  # type: (...) -> None
        self.STEP("No date/time output directory")

        _outdir_content = []  # type: typing.List[scenario.Path]
        if self.ACTION("Read the directory pointed by the campaign command line."):
            self.evidence(f"Reading '{self.getexecstep(ExecCampaign).cmdline_outdir_path}'")
            _outdir_content = list(self.getexecstep(ExecCampaign).cmdline_outdir_path.iterdir())

        if self.RESULT("The directory contains no subdirectories."):
            self.assertisnotempty(
                _outdir_content,
                evidence="Output directory content",
            )
            for _subpath in _outdir_content:  # type: scenario.Path
                self.assertisfile(
                    _subpath,
                    evidence="Not a directory",
                )


class CheckCampaignDtOutdir(scenario.test.VerificationStep):

    def step(self):  # type: (...) -> None
        self.STEP("Date/time output directory")

        _outdir_content = []  # type: typing.List[scenario.Path]
        if self.ACTION("Read the directory pointed by the campaign command line."):
            self.evidence(f"Reading '{self.getexecstep(ExecCampaign).cmdline_outdir_path}'")
            _outdir_content = list(self.getexecstep(ExecCampaign).cmdline_outdir_path.iterdir())

        _timestamp = 0.0  # type: float
        if self.RESULT("The directory contains 1 directory named with an ISO8601 date."):
            self.assertlen(
                _outdir_content, 1,
                evidence="Output directory content",
            )
            _final_outdir_path = _outdir_content[0]  # type: scenario.Path
            self.assertisdir(
                _final_outdir_path,
                evidence="Date/time directory",
            )
            _local_timezone = scenario.datetime.toiso8601(time.time())[-len("+00:00"):]  # type: str
            _iso8601 = re.sub(
                r"^(\d{4})-(\d{2})-(\d{2})_(\d{2})-(\d{2})-(\d{2})$",
                r"\1-\2-\3T\4:\5:\6.000000" + _local_timezone,
                _final_outdir_path.name,
            )  # type: str
            _timestamp = scenario.datetime.fromiso8601(_iso8601)
            self.evidence(f"ISO8601 date/time: {_iso8601} = {_timestamp}")

        if self.RESULT(f"The ISO8601 date corresponds to step {self.exec_step!r}."):
            # Due to the fact that the output directory lacks the milliseconds / microseconds in its name,
            # the `asserttimeinstep()` may fail.
            # self.asserttimeinstep(
            #     _timestamp, step_name,
            #     evidence="Timestamp",
            # )
            _step_execution = scenario.assertionhelpers.getstepexecution(self.exec_step)  # type: scenario.StepExecution
            _start = math.floor(_step_execution.getstarttime())  # type: float
            _end = math.ceil(_step_execution.getendtime(expect=True))  # type: float
            self.assertbetweenorequal(
                _timestamp, _start, _end,
                err=scenario.debug.FmtAndArgs(
                    "Output directory date/time %s does not take place in step %r execution %s",
                    scenario.debug.callback(scenario.datetime.f2strtime, _timestamp), self.exec_step, _step_execution.time,
                ),
                evidence="Timestamp",
            )
