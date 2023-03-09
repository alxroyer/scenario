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

import typing

import scenario
import scenario.test


class InternetSectionBegin(scenario.StepSectionBegin):

    def __init__(self):  # type: (...) -> None
        scenario.StepSectionBegin.__init__(self)

        self.is_internet_up = None  # type: typing.Optional[bool]

    def step(self):  # type: (...) -> None
        # Step description.
        super().step()

        _ping_subprocess = scenario.SubProcess()  # type: scenario.SubProcess
        if self.ACTION("Send a ping request to github.com."):
            _ping_subprocess = _launchpinggithubsubprocess(self)

        if self.ACTION("If github.com responded successfully, execute the next step. "
                       f"Otherwise skip the next steps up to {self.end}."):
            if _ping_subprocess.returncode == 0:
                self.is_internet_up = True

                self.evidence(f"{_ping_subprocess} returned 0")
            else:
                self.is_internet_up = False

                # Extract the last stdout line for evidence.
                _last_stdout_line = b''  # type: bytes
                _stdout_lines = _ping_subprocess.stdout.splitlines()  # type: typing.List[bytes]
                while _stdout_lines and (not _last_stdout_line):
                    _last_stdout_line = _stdout_lines.pop().strip()
                self.evidence(f"{_ping_subprocess} returned {_ping_subprocess.returncode}: {_last_stdout_line!r}")

                # Skip the step section.
                self.skipsection(
                    issue_level=scenario.test.IssueLevel.CONTEXT,
                    message="No Internet connection",
                )


def isinternetup(
        logger,  # type: scenario.Logger
):  # type: (...) -> bool
    return _launchpinggithubsubprocess(logger).returncode == 0


def _launchpinggithubsubprocess(
        logger,  # type: scenario.Logger
):  # type: (...) -> scenario.SubProcess
    # Find out the *ping count* option name depending on the platform.
    _count_opt = "-c"  # type: str
    # '-h' may be a wrong option (under Windows among others).
    # Whatever, that will make the command display its help on stderr.
    _ping_help = scenario.SubProcess("ping", "-h").run()  # type: scenario.SubProcess
    if b'-c count' in (_ping_help.stdout + _ping_help.stderr):
        _count_opt = "-c"
    elif b'-n count' in (_ping_help.stdout + _ping_help.stderr):
        _count_opt = "-n"

    # Ping github.com.
    _ping_github = scenario.SubProcess("ping", _count_opt, "1", "github.com")  # type: scenario.SubProcess
    return _ping_github.setlogger(logger).run()
