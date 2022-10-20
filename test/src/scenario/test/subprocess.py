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
import os
import sys
import typing

import scenario

from .paths import CAMPAIGN_LAUNCHER, TEST_LAUNCHER
from .testcase import TestCase


class SubProcess(scenario.SubProcess):

    def __init__(
            self,
            launcher=None,  # type: scenario.Path
    ):  # type: (...) -> None
        """
        :param launcher: Launcher script path. May be ``None`` in order to create a *void* instance.
        """
        if launcher:
            scenario.SubProcess.__init__(self, sys.executable, "-u", launcher)

            self.setconfigvalue(scenario.ConfigKey.LOG_COLOR_ENABLED, "0")
            self.setconfigvalue(scenario.ConfigKey.LOG_DATETIME, "0")
            self._expect_success = True  # type: typing.Optional[bool]
        else:
            # *Void* instance.
            scenario.SubProcess.__init__(self)

        self.launcher_path = scenario.Path(launcher)  # type: scenario.Path
        self.log_path = None  # type: typing.Optional[scenario.Path]
        self.report_path = None  # type: typing.Optional[scenario.Path]

    def setconfigvalue(
            self,  # type: scenario.VarSubProcessType
            config_key,  # type: typing.Union[enum.Enum, str]
            value,  # type: typing.Union[str, os.PathLike[str]]
    ):  # type: (...) -> scenario.VarSubProcessType
        """
        Set a configuration in the command line.

        :param config_key: Configuration key to set.
        :param value: Configuration value.
        :return: ``self``
        """
        assert isinstance(self, SubProcess)

        config_key = scenario.enum.enum2str(config_key)

        self.unsetconfigvalue(config_key)
        self.addargs("--config-value", config_key, value)
        return self  # type: ignore  ## Incompatible return value type (got "ScriptExecution", expected "SubProcessType")

    def unsetconfigvalue(
            self,  # type: scenario.VarSubProcessType
            config_key,  # type: typing.Union[enum.Enum, str]
    ):  # type: (...) -> scenario.VarSubProcessType
        """
        Unset a configuration from the command line.

        :param config_key: Configuration key to remove.
        :return: ``self``
        """
        config_key = scenario.enum.enum2str(config_key)

        _arg_index = 0  # type: int
        while _arg_index < len(self._cmd_line):
            if (
                (_arg_index < len(self._cmd_line) - 2)
                and (self._cmd_line[_arg_index + 0] == "--config-value")
                and (self._cmd_line[_arg_index + 1] == config_key)
            ):
                # Remove the 3 next words in the command line.
                del self._cmd_line[_arg_index]
                del self._cmd_line[_arg_index]
                del self._cmd_line[_arg_index]
            else:
                _arg_index += 1
        return self

    def logoutfile(
            self,  # type: scenario.VarSubProcessType
            log_outfile_path=None,  # type: scenario.Path
    ):  # type: (...) -> scenario.VarSubProcessType
        """
        Makes logging being output in a file.

        :param log_outfile_path: Path of the output file used.
        :return: ``self``
        """
        assert isinstance(self, SubProcess)

        if log_outfile_path is None:
            log_outfile_path = TestCase.getinstance().mktmppath(prefix=self.launcher_path.name, suffix=".log")
        self.log_path = log_outfile_path

        self.setconfigvalue(scenario.ConfigKey.LOG_FILE, self.log_path)
        return self  # type: ignore  ## Incompatible return value type (got "ScriptExecution", expected "SubProcessType")

    def generatereport(
            self,  # type: scenario.VarSubProcessType
            report_path=None,  # type: scenario.Path
    ):  # type: (...) -> scenario.VarSubProcessType
        """
        Activates report generation.

        :param report_path: Path of the output file used for report generation.
        :return: ``self``
        """
        assert isinstance(self, SubProcess)

        if report_path is None:
            report_path = TestCase.getinstance().mktmppath(prefix=self.launcher_path.name, suffix=".json")
        self.report_path = report_path

        if self.launcher_path.samefile(TEST_LAUNCHER):
            assert not self.hasargs("--json-report")
            self.addargs("--json-report", report_path)
        elif self.launcher_path.samefile(CAMPAIGN_LAUNCHER):
            scenario.Assertions.fail("Campaign reports not handled yet")
        else:
            scenario.Assertions.fail("Unknown launcher '%s'" % self.launcher_path)
        return self  # type: ignore  ## Incompatible return value type (got "ScriptExecution", expected "SubProcessType")

    def expectsuccess(
            self,  # type: scenario.VarSubProcessType
            expect_success,  # type: bool
    ):  # type: (...) -> scenario.VarSubProcessType
        """
        Sets whether a success is expected or not.

        :param expect_success: :const:`True` if success is expected for this scenario (default),
                               :const:`False` if failure is expected,
                               :const:`None` if nothing should be checked.
        :return: ``self``
        """
        assert isinstance(self, SubProcess)
        self._expect_success = expect_success
        return self  # type: ignore  ## Incompatible return value type (got "ScriptExecution", expected "SubProcessType")

    def run(
            self,
            timeout=None,  # type: float
    ):  # type: (...) -> SubProcess
        """
        Overrides the base :meth:`scenario.tools.SubProcess.run()` method in order to avoid ``sys.exit()`` calls,
        and generate assertion errors when appropriate.

        :return: See :meth:`SubProcess.run()`
        """
        self.exitonerror(False)
        super().run(timeout=timeout)
        if self._expect_success:
            scenario.Assertions.assertequal(self.returncode, 0, "%s failed" % repr(self._cmd_line))
        else:
            scenario.Assertions.assertnotequal(self.returncode, 0, "%s succeeded unexpectedly" % repr(self._cmd_line))
        return self


class ScenarioSubProcess(SubProcess):

    def __init__(
            self,
            *scenario_paths  # type: scenario.Path
    ):  # type: (...) -> None
        """
        Prepares a scenario execution as a :class:`scenario.tools.SubProcess` object.

        :param scenario_paths: Target scenarios, as given to the 'run-test' script.
        :return: :class:`ScriptExecution` ready for execution.
        """
        SubProcess.__init__(self, TEST_LAUNCHER)

        self.scenario_paths = list(scenario_paths)  # type: typing.List[scenario.Path]

        for _scenario_path in scenario_paths:  # type: scenario.Path
            self.addargs(_scenario_path)
        self.setenv(PYTHONPATH=os.pathsep.join(sys.path))


class CampaignSubProcess(SubProcess):

    def __init__(
            self,
            output_directory,  # type: scenario.Path
            *unit_paths  # type: scenario.Path
    ):  # type: (...) -> None
        """
        Prepares a campaign execution as a :class:`scenario.tools.SubProcess` object.

        :param output_directory: Campaign results output directory.
        :param unit_paths: Test unit definition files, as given to the 'run-campaign' script.
        :return: :class:`ScriptExecution` ready for execution.
        """
        SubProcess.__init__(self, CAMPAIGN_LAUNCHER)

        self.unit_paths = list(unit_paths)  # type: typing.List[scenario.Path]

        self.addargs("--outdir", output_directory)
        for _unit_path in unit_paths:  # type: scenario.Path
            self.addargs(_unit_path)
        self.setenv(PYTHONPATH=os.pathsep.join(sys.path))

        # Ensure the tests are executed from the main path currently configured,
        # otherwise the pretty paths will differ between the campaign output and this script execution.
        _main_path = scenario.Path.getmainpath()  # type: typing.Optional[scenario.Path]
        assert _main_path
        self.setcwd(_main_path)
