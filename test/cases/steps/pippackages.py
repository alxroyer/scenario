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

import importlib.util
import sys

import scenario.test


class EnsurePipPackage(scenario.test.Step):

    def __init__(
            self,
            pip_name,  # type: str
            import_name,  # type: str
            installed,  # type: bool
    ):  # type: (...) -> None
        scenario.test.Step.__init__(self)

        self.pip_name = pip_name  # type: str
        self.import_name = import_name  # type: str
        self.installed = installed  # type: bool

    def step(self):  # type: (...) -> None
        self.STEP("Ensure '%s' package %s" % (self.pip_name, "installed" if self.installed else "uninstalled"))

        if self.installed:
            if self.ACTION("Ensure the '%s' pip package is installed." % self.pip_name):
                if importlib.util.find_spec(self.import_name):
                    self.evidence("The '%s' package can be imported." % self.import_name)
                else:
                    _install = scenario.SubProcess(sys.executable, "-m", "pip", "install", self.pip_name)  # type: scenario.SubProcess
                    _install.setlogger(self).run()
                    self.assertsubprocessretcode(
                        _install, 0,
                        evidence="Return code of %s" % _install,
                    )
        else:
            if self.ACTION("Ensure the '%s' pip package is not installed." % self.pip_name):
                if not importlib.util.find_spec(self.import_name):
                    self.evidence("The '%s' package cannot be imported." % self.import_name)
                else:
                    _uninstall = scenario.SubProcess(sys.executable, "-m", "pip", "uninstall", "-y", self.pip_name)  # type: scenario.SubProcess
                    _uninstall.setlogger(self).run()
                    self.assertsubprocessretcode(
                        _uninstall, 0,
                        evidence="Return code of %s" % _uninstall,
                    )
