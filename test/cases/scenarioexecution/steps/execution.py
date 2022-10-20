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

import enum
import typing

import scenario
import scenario.test

# Related steps:
from steps.commonargs import ExecCommonArgs
# Related scenarios:
from superscenario import SuperScenario


class ExecScenario(ExecCommonArgs):

    def __init__(
            self,
            scenario_paths,  # type: typing.Union[scenario.Path, typing.List[scenario.Path]]
            description=None,  # type: str
            subscenario=None,  # type: scenario.Path
            config_values=None,  # type: typing.Dict[typing.Union[enum.Enum, str], typing.Optional[str]]
            config_files=None,  # type: typing.List[scenario.Path]
            debug_classes=None,  # type: typing.Optional[typing.List[str]]
            log_outfile=None,  # type: bool
            generate_report=None,  # type: bool
            doc_only=None,  # type: bool
            expected_return_code=None,  # type: scenario.ErrorCode
    ):  # type: (...) -> None
        ExecCommonArgs.__init__(
            self,
            config_values=config_values, config_files=config_files,
            debug_classes=debug_classes,
            log_outfile=log_outfile,
            doc_only=doc_only,
        )

        if isinstance(scenario_paths, scenario.Path):
            self.scenario_paths = [scenario_paths]  # type: typing.List[scenario.Path]
        else:
            self.scenario_paths = scenario_paths
        assert self.scenario_paths, "No scenario to execute"
        self.subscenario_path = subscenario  # type: typing.Optional[scenario.Path]
        self.generate_report = generate_report  # type: typing.Optional[bool]
        self.expected_return_code = expected_return_code  # type: typing.Optional[scenario.ErrorCode]

        # Eventually propose a default step description.
        self.description = description
        if not self.description:
            self.description = self._strscenarios() + " execution"

    def step(self):  # type: (...) -> None
        # Description already set programmatically.
        # self.STEP()

        # Prepare the scenario subprocess.
        _action_description = "Execute " + self._strscenarios()  # type: str
        if self.doexecute():
            self.subprocess = scenario.test.ScenarioSubProcess(*self.scenario_paths)

        # Sub-scenario.
        if self.subscenario_path:
            _action_description += ", with '%s' for sub-scenario" % self.subscenario_path

            if self.doexecute():
                self.subprocess.setconfigvalue(SuperScenario.ConfigKey.SUBSCENARIO_PATH, self.subscenario_path)

        _action_description1, _action_description2 = self._preparecommonargs()  # type: str, str
        _action_description += _action_description1

        # Log output.
        _action_description += ". Catch the output"
        _action_description += _action_description2

        # JSON report generation.
        if self.generate_report is False:
            _action_description += ", do not generate the JSON report"
        if self.generate_report is True:
            _action_description += ", generate the JSON report"

            if self.doexecute():
                self.subprocess.generatereport()

        # Display the action description, and execute the scenario.
        _action_description += "."
        if self.ACTION(_action_description):
            if (self.expected_return_code is not None) and (self.expected_return_code is not scenario.ErrorCode.SUCCESS):
                self.subprocess.expectsuccess(False)
            self.subprocess.setlogger(self).run()

        # Return code.
        if self.expected_return_code is not None:
            _result_description = "The scenario launcher returned "  # type: str
            _result_description += "the %d (%s) error code." % (self.expected_return_code.value, self.expected_return_code.name)
            if self.RESULT(_result_description):
                self.assertequal(
                    self.subprocess.returncode, self.expected_return_code,
                    evidence="Return code",
                )

    def _strscenarios(self):  # type: (...) -> str
        """
        :return: "'%s', '%s', (...) and '%s'"-like string computed from :attr:`scenario_paths`.
        """
        _str = ", ".join(["'%s'" % _scenario_path for _scenario_path in self.scenario_paths[:-1]])  # type: str
        if _str:
            _str += " and "
        _str += "'%s'" % self.scenario_paths[-1]
        return _str
