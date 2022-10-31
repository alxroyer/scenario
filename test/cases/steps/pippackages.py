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
import typing

import scenario.test


# This list implements a cache that memorizes uninstalled packages,
# possibly uninstalled with error notifications, but uninstalled whatever...
UNINSTALLED = []  # type: typing.List[str]


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
        if self.installed:
            self._stepinstalled()
        else:
            self._stepuninstalled()

    def _stepinstalled(self):  # type: (...) -> None
        self.STEP(f"Ensure '{self.pip_name}' package installed")

        if self.ACTION(f"Ensure the '{self.pip_name}' pip package is installed."):
            if importlib.util.find_spec(self.import_name) and (self.pip_name not in UNINSTALLED):
                self.evidence(f"The '{self.import_name}' package can be imported.")
            else:
                _install = scenario.SubProcess(sys.executable, "-m", "pip", "install", self.pip_name)  # type: scenario.SubProcess
                _install.setlogger(self).run()
                self.assertsubprocessretcode(
                    _install, 0,
                    evidence=f"Return code of {_install}",
                )

                # Remove the package name from the *uninstalled* cache.
                while self.pip_name in UNINSTALLED:
                    UNINSTALLED.remove(self.pip_name)

    def _stepuninstalled(self):  # type: (...) -> None
        self.STEP(f"Ensure '{self.pip_name}' package uninstalled")

        if self.ACTION(f"Ensure the '{self.pip_name}' pip package is not installed."):
            if (not importlib.util.find_spec(self.import_name)) or (self.pip_name in UNINSTALLED):
                self.evidence(f"The '{self.import_name}' package cannot be imported.")
            else:
                _uninstall = scenario.SubProcess(sys.executable, "-m", "pip", "uninstall", "-y", self.pip_name)  # type: scenario.SubProcess
                _uninstall.setlogger(self).run()
                try:
                    self.assertsubprocessretcode(
                        _uninstall, 0,
                        evidence=f"Return code of {_uninstall}",
                    )
                except AssertionError as _err:
                    # Due to the fact that that the package may still be in use by the current process,
                    # the $(pip uninstall) may may fail,
                    # but the package be uninstalled whatever...
                    #
                    # This may be the case especially when executing several tests with a single *run-test* launcher command.
                    self.knownissue(
                        level=scenario.test.IssueLevel.TEST,
                        message=f"{_uninstall} returned {_uninstall.returncode}, {_err}",
                    )

                # Store the package name in the *uninstalled* cache.
                if self.pip_name not in UNINSTALLED:
                    UNINSTALLED.append(self.pip_name)
