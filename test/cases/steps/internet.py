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
                evidence="%s return code" % _subprocess,
            )

    @staticmethod
    def _launchsubprocess(
            logger,  # type: scenario.Logger
    ):  # type: (...) -> scenario.SubProcess
        _subprocess = scenario.SubProcess("ping", "-n", "1", "github.com")  # type: scenario.SubProcess
        return _subprocess.setlogger(logger).run()

    @staticmethod
    def isup(
            logger,  # type: scenario.Logger
    ):  # type: (...) -> bool
        return EnsureInternetConnection._launchsubprocess(logger).returncode == 0
