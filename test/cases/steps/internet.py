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

import scenario
import scenario.test


class EnsureInternetConnection(scenario.test.Step):

    def step(self):  # type: (...) -> None
        self.STEP("Ensure Internet connection")

        _subprocess = scenario.SubProcess()  # type: scenario.SubProcess
        if self.ACTION("Send a ping request to github.com."):
            _subprocess = self._launchsubprocess(self)
        if self.RESULT("github.com responded successfully."):
            self.assertsubprocessretcode(
                _subprocess, 0,
                evidence=f"{_subprocess} return code",
            )

    @staticmethod
    def _launchsubprocess(
            logger,  # type: scenario.Logger
    ):  # type: (...) -> scenario.SubProcess
        # Find out the *ping count* option name depending on the platform.
        _count_opt = "-c"  # type: str
        # '-h' may be a wrong option (under Windows among others).
        # Whatever, that will make the command display its help on stderr.
        _ping_help = scenario.SubProcess("ping", "-h").run()  # type: scenario.SubProcess
        if b'-c count' in _ping_help.stdout + _ping_help.stderr:
            _count_opt = "-c"
        elif b'-n count' in _ping_help.stdout + _ping_help.stderr:
            _count_opt = "-n"

        # Ping github.com.
        _ping_github = scenario.SubProcess("ping", _count_opt, "1", "github.com")  # type: scenario.SubProcess
        return _ping_github.setlogger(logger).run()

    @staticmethod
    def isup(
            logger,  # type: scenario.Logger
    ):  # type: (...) -> bool
        return EnsureInternetConnection._launchsubprocess(logger).returncode == 0
