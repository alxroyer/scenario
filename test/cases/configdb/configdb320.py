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


class ConfigDb320(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        from steps.common import ExecScenario
        from steps.pythonpackages import PythonPackageBegin

        scenario.test.TestCase.__init__(
            self,
            title="'pyyaml' environment error",
            description="Check that an environment error is raised when 'pyyaml' is not installed.",
        )
        self.covers(
            scenario.test.reqs.CONFIG_DB,
        )

        self.section("'pyyaml' not installed")
        _no_pyyaml_section = self.addstep(PythonPackageBegin("pyyaml", "yaml", False))  # type: scenario.StepSectionBegin
        self.addstep(ExecScenario(
            scenario.test.paths.CONFIG_DB_SCENARIO,
            config_files=[scenario.test.paths.datapath("conf.yml")],
            expected_return_code=scenario.ErrorCode.ENVIRONMENT_ERROR,
        ))
        self.addstep(_no_pyyaml_section.end)

        self.section("'pyyaml' installed")
        _pyyaml_section = self.addstep(PythonPackageBegin("pyyaml", "yaml", True))  # type: scenario.StepSectionBegin
        self.addstep(ExecScenario(
            scenario.test.paths.CONFIG_DB_SCENARIO,
            config_files=[scenario.test.paths.datapath("conf.yml")],
            expected_return_code=scenario.ErrorCode.SUCCESS,
        ))
        self.addstep(_pyyaml_section.end)
