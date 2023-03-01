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
import shutil
import typing

import scenario
import scenario.test
import scenario.text

# Related steps:
from steps.commonargs import ExecCommonArgs


class ExecCampaign(ExecCommonArgs):

    def __init__(
            self,
            test_suite_paths,  # type: typing.Sequence[scenario.Path]
            description=None,  # type: str
            config_values=None,  # type: scenario.test.configvalues.ConfigValuesType
            config_files=None,  # type: typing.List[scenario.Path]
            debug_classes=None,  # type: typing.Optional[typing.List[str]]
            log_outfile=None,  # type: bool
            dt_subdir=None,  # type: bool
            doc_only=None,  # type: bool
    ):  # type: (...) -> None
        ExecCommonArgs.__init__(
            self,
            config_values=config_values,
            config_files=config_files,
            debug_classes=debug_classes,
            log_outfile=log_outfile,
            doc_only=doc_only,
        )

        self.test_suite_paths = test_suite_paths  # type: typing.Sequence[scenario.Path]
        self._cmdline_outdir_path = None  # type: typing.Optional[scenario.Path]
        self._final_outdir_path = None  # type: typing.Optional[scenario.Path]
        self.dt_subdir = dt_subdir  # type: typing.Optional[bool]

        # Eventually propose a default step description.
        self.description = description
        if not self.description:
            self.description = "Campaign execution"

    @property
    def cmdline_outdir_path(self):  # type: () -> scenario.Path
        assert self._cmdline_outdir_path is not None
        return self._cmdline_outdir_path

    @property
    def final_outdir_path(self):  # type: () -> scenario.Path
        assert self._final_outdir_path is not None
        return self._final_outdir_path

    @property
    def junit_report_path(self):  # type: () -> scenario.Path
        return self.final_outdir_path / "campaign.xml"

    def step(self):  # type: (...) -> None
        # Description already set programmatically.
        # self.STEP()

        # Prepare the campaign subprocess.
        _action_description = "Launch a campaign based on"  # type: str
        if self.doexecute():
            # Create the output directory.
            self._mkoutdir()

            assert self._cmdline_outdir_path
            self.subprocess = scenario.test.CampaignSubProcess(
                self._cmdline_outdir_path,
                *self.test_suite_paths
            )

        assert self.test_suite_paths
        if len(self.test_suite_paths) == 1:
            _action_description += f" the {self.test_case.getpathdesc(self.test_suite_paths[0])} test suite file"
        if len(self.test_suite_paths) > 1:
            _action_description += (" " + scenario.text.commalist(
                [self.test_case.getpathdesc(_test_suite_path) for _test_suite_path in self.test_suite_paths]
            ) + " test suite files")

        if self.dt_subdir is True:
            _action_description += ", with the --dt-subdir option set"
            if self.doexecute():
                self.subprocess.addargs("--dt-subdir")
        if self.dt_subdir is False:
            _action_description += ", without the --dt-subdir option set"

        _action_description1, _action_description2 = self._preparecommonargs()  # type: str, str
        _action_description += _action_description1

        _action_description += ". Catch the output"
        _action_description += _action_description2

        # Display the action description, and execute the campaign.
        _action_description += "."
        if self.ACTION(_action_description):
            self.subprocess.setlogger(self).run()

            # Ensure the final output directory reference is known.
            self._checkfinaloutdir()

    def _mkoutdir(self):  # type: (...) -> None
        assert isinstance(self.scenario, scenario.test.TestCase)
        self._cmdline_outdir_path = self.scenario.mktmppath()
        self.debug(f"Creating directory '{self._cmdline_outdir_path}'")
        self._cmdline_outdir_path.mkdir(parents=True, exist_ok=True)

        scenario.handlers.install(
            scenario.Event.AFTER_TEST, self._rmfinaloutdir, scenario=self.scenario, once=True,
            # Ensure this handler is called before the ones already installed by :class:`scenario.test.TestScenario`,
            # especially :meth:`scenario.test.TestScenario.rmtmpfiles()` that cannot remove non empty directories.
            first=True,
        )

    def _checkfinaloutdir(self):  # type: (...) -> None
        if (self._final_outdir_path is None) and (self._cmdline_outdir_path is not None):
            if self.dt_subdir:
                for _subpath in self._cmdline_outdir_path.iterdir():  # type: scenario.Path
                    if _subpath.is_dir():
                        self._final_outdir_path = _subpath
            else:
                self._final_outdir_path = self._cmdline_outdir_path

    def _rmfinaloutdir(
            self,
            event,  # type: str
            data,  # type: typing.Any
    ):  # type: (...) -> None
        if self._final_outdir_path:
            if scenario.stack.current_scenario_execution and scenario.stack.current_scenario_execution.errors:
                _errors_txt = scenario.text.Countable("error", scenario.stack.current_scenario_execution.errors)  # type: scenario.text.Countable
                self.warning(f"{len(_errors_txt)} {_errors_txt} while executing the test")
                self.warning(f"Leaving the output files in place in '{self._final_outdir_path}' for investigation purpose")
            else:
                self.debug("Removing final output directory '%s'", self._final_outdir_path)
                shutil.rmtree(self._final_outdir_path, ignore_errors=True)
