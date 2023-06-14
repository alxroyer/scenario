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
import scenario.text

if True:
    from steps.commonargs import ExecCommonArgs as _ExecCommonArgsImpl  # `ExecCommonArgs` used for inheritance.


class ExecScenario(_ExecCommonArgsImpl):

    def __init__(
            self,
            scenario_paths,  # type: typing.Union[scenario.Path, typing.Sequence[scenario.Path]]
            description=None,  # type: str
            subscenario=None,  # type: scenario.Path
            config_values=None,  # type: scenario.test.configvalues.ConfigValuesType
            config_files=None,  # type: typing.List[scenario.Path]
            debug_classes=None,  # type: typing.Optional[typing.List[str]]
            log_outfile=None,  # type: bool
            generate_report=None,  # type: bool
            doc_only=None,  # type: bool
            expected_return_code=None,  # type: scenario.ErrorCode
    ):  # type: (...) -> None
        _ExecCommonArgsImpl.__init__(
            self,
            config_values=config_values, config_files=config_files,
            debug_classes=debug_classes,
            log_outfile=log_outfile,
            doc_only=doc_only,
        )

        if isinstance(scenario_paths, scenario.Path):
            self.scenario_paths = [scenario_paths]  # type: typing.Sequence[scenario.Path]
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

        # Subscenario.
        if self.subscenario_path:
            _action_description += f", with '{self.subscenario_path}' for subscenario"

            if self.doexecute():
                self.subprocess.setconfigvalue(scenario.test.data.scenarios.SuperScenario.ConfigKey.SUBSCENARIO_PATH, self.subscenario_path)

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
            if self.RESULT(f"The scenario launcher returned the {self.expected_return_code.value} ({self.expected_return_code.name}) error code."):
                self.assertequal(
                    self.subprocess.returncode, self.expected_return_code,
                    evidence="Return code",
                )

    def _strscenarios(self):  # type: (...) -> str
        """
        :return: "'%s', '%s', (...) and '%s'"-like string computed from :attr:`scenario_paths`.
        """
        _scenario_paths = []  # type: typing.List[typing.Union[scenario.Path, str]]
        for _path in self.scenario_paths:  # type: scenario.Path
            _scenario_paths.append(self.test_case.getpathdesc(_path))
        return scenario.text.commalist(_scenario_paths)
