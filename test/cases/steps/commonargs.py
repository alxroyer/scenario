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

import enum
import typing

import scenario
import scenario.test
import scenario.text


class ExecCommonArgs(scenario.test.ExecutionStep):
    """
    Common arguments management for `ExecScenario` and `ExecCampaign`.
    """

    def __init__(
            self,
            config_values=None,  # type: scenario.test.configvalues.ConfigValuesType
            config_files=None,  # type: typing.List[scenario.Path]
            debug_classes=None,  # type: typing.Optional[typing.List[str]]
            log_outfile=None,  # type: bool
            doc_only=None,  # type: bool
    ):  # type: (...) -> None
        scenario.test.ExecutionStep.__init__(self)

        self.config_values = config_values or {}  # type: scenario.test.configvalues.ConfigValuesType
        self.config_file_paths = config_files or []  # type: typing.List[scenario.Path]
        self.debug_classes = debug_classes  # type: typing.Optional[typing.List[str]]
        self.log_outfile = log_outfile  # type: typing.Optional[bool]
        self.doc_only = doc_only  # type: typing.Optional[bool]

    def _preparecommonargs(self):  # type: (...) -> typing.Tuple[str, str]
        """
        Prepares the step with common arguments.

        Contributes in building the action description,
        and sets arguments to the subprocess.

        :return: Action description parts.
        """
        # === Action secription part 1 ===
        _action_description1 = ""  # type: str

        # Configuration values.
        for _config_key in self.config_values:  # type: typing.Union[enum.Enum, str]
            _config_value = self.config_values[_config_key]  # type: typing.Optional[scenario.test.configvalues.AnyConfigValueType]
            if _config_key == scenario.ConfigKey.LOG_DATETIME:
                if _config_value is None:
                    _action_description1 += ", with date/time logging by default"
                elif self.getboolconfigvalue(scenario.ConfigKey.LOG_DATETIME):
                    _action_description1 += ", with date/time logging enabled"
                else:
                    _action_description1 += ", with date/time logging disabled"
            elif _config_key == scenario.ConfigKey.LOG_CONSOLE:
                if _config_value is None:
                    _action_description1 += ", with console logging by default"
                elif self.getboolconfigvalue(scenario.ConfigKey.LOG_CONSOLE):
                    _action_description1 += ", with console logging enabled"
                else:
                    _action_description1 += ", with console logging disabled"
            elif _config_key == scenario.ConfigKey.LOG_COLOR_ENABLED:
                if _config_value is None:
                    _action_description1 += ", with log colorization by default"
                elif self.getboolconfigvalue(scenario.ConfigKey.LOG_COLOR_ENABLED):
                    _action_description1 += ", with log colorization enabled"
                else:
                    _action_description1 += ", with log colorization disabled"
            else:
                _action_description1 += f", with {scenario.enumutils.enum2str(_config_key)}={_config_value!r}"

            if self.doexecute():
                self.subprocess.unsetconfigvalue(_config_key)
                if _config_value is not None:
                    self.subprocess.setconfigvalue(_config_key, scenario.test.configvalues.tostr(_config_value))

        # Configuration files.
        _config_files_mentionned = 0  # type: int
        for _config_file_path in self.config_file_paths:  # type: scenario.Path
            if _config_files_mentionned == 0:
                _action_description1 += f", with configuration file '{_config_file_path}'"
            else:
                _action_description1 += f", then '{_config_file_path}'"
            _config_files_mentionned += 1

            if self.doexecute():
                self.subprocess.addargs("--config-file", _config_file_path)

        # Debug classes.
        if self.debug_classes is not None:
            if self.debug_classes:
                _action_description1 += f", with {scenario.text.commalist(self.debug_classes, quotes=True)} "
                _action_description1 += f"{scenario.text.pluralize('debug class', len(self.debug_classes))} enabled"

                if self.doexecute():
                    for _debug_class in self.debug_classes:  # type: str
                        self.subprocess.addargs("--debug-class", _debug_class)
            else:
                _action_description1 += ", with no debug class enabled"

        # Documentation generation.
        if self.doc_only is True:
            _action_description1 += ", with the --doc-only option set"

            if self.doexecute():
                self.subprocess.addargs("--doc-only")

        if self.doc_only is False:
            _action_description1 += ", without the --doc-only option set"

        # === Action secription part 2 ===
        _action_description2 = ""  # type: str

        # File logging.
        if self.log_outfile is False:
            _action_description2 += ", do not save log output to a file"
        if self.log_outfile is True:
            _action_description2 += ", save log output to a file"

            if self.doexecute():
                self.subprocess.logoutfile()

        return _action_description1, _action_description2

    def getboolconfigvalue(
            self,
            key,  # type: enum.Enum
            default=None,  # type: bool
    ):  # type: (...) -> bool
        # This method only deals with configuration values passed on with the `config_values` parameter.
        assert key in self.config_values, f"Unknown configuration key {key!r}"

        # When the value was set to `None` (i.e. default behaviour),
        # expect the caller has provided the default value for the given configuration key.
        if self.config_values[key] is None:
            assert default is not None, f"Value is None for key {key!r}, please provide default value"
            return default

        # Use the `scenario.ConfigNode` class to interprete the string as a boolean value.
        _config_node = scenario.ConfigNode(parent=None, key="foo")  # type: scenario.ConfigNode
        _config_node.set(self.config_values[key])
        return _config_node.cast(bool)

    def listpaths(self):  # type: (...) -> str
        """
        Formats the list of scenario paths or unit test files of the related :class:`scenario.test.lib.subprocess.ScenarioSubProcess`.

        :return: Coma-separated list of paths.
        """
        _paths = []
        assert isinstance(self.subprocess, (scenario.test.ScenarioSubProcess, scenario.test.CampaignSubProcess))
        if isinstance(self.subprocess, scenario.test.ScenarioSubProcess):
            _paths = self.subprocess.scenario_paths
        if isinstance(self.subprocess, scenario.test.CampaignSubProcess):
            _paths = self.subprocess.unit_paths

        return scenario.text.commalist([self.test_case.getpathdesc(_path) for _path in _paths])
