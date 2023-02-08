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

"""
Scenario runner program arguments.
"""

import typing

# `Args` used for inheritance.
from .args import Args
# `SubProcess` used in method signatures.
from .subprocess import SubProcess


class CommonExecArgs:
    """
    Base class for argument parser classes that embed common test execution program arguments.
    """

    def __init__(self):  # type: (...) -> None
        """
        Installs common test execution program arguments.
        """
        from .issuelevels import IssueLevel
        if typing.TYPE_CHECKING:
            from .issuelevels import AnyIssueLevelType

        assert isinstance(self, Args)

        #: ``True`` when the test(s) is(are) executed for documentation generation only,
        #: i.e. the test script(s) for actions and verifications should not be executed.
        self.doc_only = False  # type: bool
        self.addarg("Doc only", "doc_only", bool).define(
            "--doc-only",
            action="store_true", default=False,
            help="Generate documentation without executing the test(s).",
        )

        # Memo: Handler conversion inspired from:
        # - https://stackoverflow.com/questions/42279063/python-typehints-for-argparse-namespace-objects#57524956
        # - https://github.com/swansonk14/typed-argument-parser#union

        #: Error issue level.
        self.issue_level_error = None  # type: typing.Optional[AnyIssueLevelType]
        self.addarg("Error issue level", "issue_level_error", IssueLevel.parse).define(
            "--issue-level-error", metavar="ISSUE_LEVEL",
            action="store", default=None,
            help="Define the issue level from and above which known issues should be considered as errors. "
                 "None by default, i.e. all known issues are considered as warnings."
                 f"{f' Named levels: {IssueLevel.getnameddesc()}.' if IssueLevel.getnamed() else ''}",
        )

        #: Ignored issue level.
        self.issue_level_ignored = None  # type: typing.Optional[AnyIssueLevelType]
        self.addarg("Ignored issue level", "issue_level_ignored", IssueLevel.parse).define(
            "--issue-level-ignored", metavar="ISSUE_LEVEL",
            action="store", default=None,
            help="Define the issue level from and under which known issues should be ignored. "
                 "None by default, i.e. no known issue ignored by default."
                 f"{f' Named levels: {IssueLevel.getnameddesc()}.' if IssueLevel.getnamed() else ''}",
        )

    def _checkargs(
            self,
            args,  # type: typing.Any
    ):  # type: (...) -> bool
        """
        Check common test execution program arguments once parsed.

        :return: True for success, False otherwise.
        """
        from .scenarioconfig import SCENARIO_CONFIG

        # Just ensure issue names from configuration files are loaded.
        SCENARIO_CONFIG.loadissuelevelnames()

        return True

    @staticmethod
    def reportexecargs(
            args,  # type: CommonExecArgs
            subprocess,  # type: SubProcess
    ):  # type: (...) -> None
        """
        Report execution program arguments from an argument parser instance to the arguments of a sub-process being built.

        :param args: Argument parser instance to report program arguments from to.
        :param subprocess: Sub-process being built to report program arguments to.
        """
        if args.doc_only:
            subprocess.addargs("--doc-only")
        if args.issue_level_error is not None:
            subprocess.addargs("--issue-level-error", str(int(args.issue_level_error)))
        if args.issue_level_ignored is not None:
            subprocess.addargs("--issue-level-ignored", str(int(args.issue_level_ignored)))


class ScenarioArgs(Args, CommonExecArgs):
    """
    Scenario runner program argument management.

    Provides arguments for the :class:`.scenariorunner.ScenarioRunner` execution.

    Arguments given through the command line prevail on the configurations in the configuration files
    (see :class:`.scenarioconfig.ScenarioConfig`).
    """

    def __init__(
            self,
            positional_args=True,  # type: bool
    ):  # type: (...) -> None
        """
        Declares the scenario runner program arguments,
        and binds them to the member fields.

        :param positional_args:
            ``False`` to disable the scenario path positional arguments definition.
            Useful for user programs that wish to redefine it.
        """
        from .path import Path

        Args.__init__(self, class_debugging=True)

        self.setdescription("Scenario test execution.")

        CommonExecArgs.__init__(self)

        #: JSON report output file path.
        #: No JSON report when ``None``.
        self.json_report = None  # type: typing.Optional[Path]
        self.addarg("JSON output file", "json_report", Path).define(
            "--json-report", metavar="JSON_REPORT_PATH",
            action="store", type=str, default=None,
            help="Save the report in the given JSON output file path. "
                 "Single scenario only.",
        )

        #: Attribute names to display for extra info.
        #: Applicable when executing several tests.
        self.extra_info = []  # type: typing.List[str]
        self.addarg("Results extra info", "extra_info", str).define(
            "--extra-info", metavar="ATTRIBUTE_NAME",
            action="append", type=str, default=[],
            help="Scenario attribute to display for extra info when displaying results. "
                 "Applicable when executing several tests. "
                 "This option may be called several times to display more info.",
        )

        #: Path of the scenario Python script to execute.
        self.scenario_paths = []  # type: typing.List[Path]
        if positional_args:
            self.addarg("Scenario path(s)", "scenario_paths", Path).define(
                metavar="SCENARIO_PATH", nargs="+",
                action="store", type=str, default=[],
                help="Scenario script(s) to execute.",
            )

    def _checkargs(
            self,
            args,  # type: typing.Any
    ):  # type: (...) -> bool
        """
        Checks scenario runner arguments once parsed.

        :return: ``True`` for success, ``False`` otherwise.
        """
        from .loggermain import MAIN_LOGGER
        from .path import Path

        if not Args._checkargs(self, args):
            return False
        if not CommonExecArgs._checkargs(self, args):
            return False

        for _scenario_path in self.scenario_paths:  # type: Path
            if not _scenario_path.is_file():
                MAIN_LOGGER.error(f"No such file '{_scenario_path}'")
                return False

        # Multiple scenarios.
        if len(self.scenario_paths) > 1:
            if self.json_report:
                MAIN_LOGGER.error("Cannot use the --json-report option with multiple scenario files")
                return False

        return True
