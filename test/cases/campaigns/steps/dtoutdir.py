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
            self.evidence("Reading '%s'" % self.getexecstep(ExecCampaign).cmdline_outdir_path)
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
            self.evidence("Reading '%s'" % self.getexecstep(ExecCampaign).cmdline_outdir_path)
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
            _iso8601 = "%sT%s.000000+00:00" % (
                _final_outdir_path.name[:len("XXXX-XX-XX")],
                _final_outdir_path.name[len("XXXX-XX-XXT"):].replace("-", ":"),
            )  # type: str
            _timestamp = scenario.datetime.fromiso8601(_iso8601)
            self.evidence("ISO8601 date/time: %s = %f" % (_iso8601, _timestamp))

        if self.RESULT("The ISO8601 date corresponds to step %s." % repr(self.exec_step)):
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
                err="Output directory date/time %s does not take place in step %s execution %s"
                    % (scenario.datetime.f2strtime(_timestamp), repr(self.exec_step), str(_step_execution.time)),
                evidence="Timestamp",
            )
