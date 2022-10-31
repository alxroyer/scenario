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

# Steps:
from steps.internet import EnsureInternetConnection
from steps.pippackages import EnsurePipPackage
from steps.common import ExecScenario


class ConfigDb320(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        scenario.test.TestCase.__init__(
            self,
            title="'pyyaml' environment error",
            objective="Check that an environment error is raised when 'pyyaml' is not installed.",
            features=[scenario.test.features.CONFIG_DB],
        )

        self.section("'pyyaml' not installed")
        if not EnsureInternetConnection.isup(self):
            # Avoid going through 'pyyaml' uninstallation when Internet is not available,
            # otherwise we may not be able to reinstall it afterwards.
            self.knownissue(
                level=scenario.test.IssueLevel.CONTEXT,
                message="No internet connection: behaviour when 'pyyaml' missing not checked",
            )
        else:
            self.addstep(EnsurePipPackage("pyyaml", "yaml", False))
            self.addstep(ExecScenario(
                scenario.test.paths.CONFIG_DB_SCENARIO,
                config_files=[scenario.test.paths.datapath("conf.yml")],
                expected_return_code=scenario.ErrorCode.ENVIRONMENT_ERROR,
            ))

        self.section("'pyyaml' installed")
        self.addstep(EnsurePipPackage("pyyaml", "yaml", True))
        self.addstep(ExecScenario(
            scenario.test.paths.CONFIG_DB_SCENARIO,
            config_files=[scenario.test.paths.datapath("conf.yml")],
            expected_return_code=scenario.ErrorCode.SUCCESS,
        ))
