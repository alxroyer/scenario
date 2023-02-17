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
# `Path` used in method signatures.
from .path import Path
# `SubProcess` used in method signatures.
from .subprocess import SubProcess
if typing.TYPE_CHECKING:
    # `AnyIssueLevelType` used in method signatures.
    from .issuelevels import AnyIssueLevelType


class CommonExecArgs:
    """
    Base class for argument parser classes that embed common test execution program arguments.
    """

    def __init__(self):  # type: (...) -> None
        """
        Installs common test execution program arguments.
        """
        from .issuelevels import IssueLevel

        # Let typings know this class is actually a subclass of the base `Args` class.
        assert isinstance(self, CommonExecArgs) and isinstance(self, Args)

        #: Test execution argument group.
        self._test_exec_group = self._arg_parser.add_argument_group("Test execution")  # Type `argparse._ArgumentGroup` not available, let default typing.

        self._test_exec_group.add_argument(
            "--doc-only",
            dest="doc_only", action="store_true", default=False,
            help="Generate documentation without executing the test(s).",
        )

        self._test_exec_group.add_argument(
            "--issue-level-error", metavar="ISSUE_LEVEL",
            dest="issue_level_error", action="store", default=None,
            help=(
                "Define the issue level from and above which known issues should be considered as errors. "
                "None by default, i.e. all known issues are considered as warnings."
                f"{f' Named levels: {IssueLevel.getnameddesc()}.' if IssueLevel.getnamed() else ''}"
            ),
        )

        self._test_exec_group.add_argument(
            "--issue-level-ignored", metavar="ISSUE_LEVEL",
            dest="issue_level_ignored", action="store", default=None,
            help=(
                "Define the issue level from and under which known issues should be ignored. "
                "None by default, i.e. no known issue ignored by default."
                f"{f' Named levels: {IssueLevel.getnameddesc()}.' if IssueLevel.getnamed() else ''}"
            ),
        )

    def _checkargs(self):  # type: (...) -> bool
        """
        Check common test execution program arguments once parsed.

        :return: True for success, False otherwise.
        """
        from .scenarioconfig import SCENARIO_CONFIG

        # Just ensure issue names from configuration files are loaded.
        SCENARIO_CONFIG.loadissuelevelnames()

        return True

    @property
    def doc_only(self):  # type: () -> bool
        """
        ``True`` when the test(s) is(are) executed for documentation generation only,
        i.e. the test script(s) for actions and verifications should not be executed.
        """
        # Let typings know this class is actually a subclass of the base `Args` class.
        assert isinstance(self, CommonExecArgs) and isinstance(self, Args)

        return bool(self._args.doc_only)

    @property
    def issue_level_error(self):  # type: () -> typing.Optional[AnyIssueLevelType]
        """
        Error issue level.
        """
        from .issuelevels import IssueLevel

        # Let typings know this class is actually a subclass of the base `Args` class.
        assert isinstance(self, CommonExecArgs) and isinstance(self, Args)

        return IssueLevel.parse(self._args.issue_level_error)

    @property
    def issue_level_ignored(self):  # type: () -> typing.Optional[AnyIssueLevelType]
        """
        Ignored issue level.
        """
        from .issuelevels import IssueLevel

        # Let typings know this class is actually a subclass of the base `Args` class.
        assert isinstance(self, CommonExecArgs) and isinstance(self, Args)

        return IssueLevel.parse(self._args.issue_level_ignored)

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
            def_scenario_paths_arg=True,  # type: bool
    ):  # type: (...) -> None
        """
        Declares the scenario runner program arguments,
        and binds them to the member fields.

        :param def_scenario_paths_arg:
            ``False`` to disable the scenario paths positional arguments definition.
            Useful for user programs that wish to redefine it.
            Use :meth:`_defscenariopathsarg()` in that case.
        """
        Args.__init__(self, class_debugging=True)

        self.setdescription("Scenario test execution.")

        CommonExecArgs.__init__(self)

        self._test_exec_group.add_argument(
            "--json-report", metavar="JSON_REPORT_PATH",
            dest="json_report", action="store", type=str, default=None,
            help=(
                "Save the report in the given JSON output file path. "
                "Single scenario only."
            ),
        )

        self._test_exec_group.add_argument(
            "--extra-info", metavar="ATTRIBUTE_NAME",
            dest="extra_info", action="append", type=str, default=[],
            help=(
                "Scenario attribute to display for extra info when displaying results. "
                "Applicable when executing several tests. "
                "This option may be called several times to display more info."
            ),
        )

        if def_scenario_paths_arg:
            self._defscenariopathsarg()

    def _defscenariopathsarg(
            self,
            nargs=None,  # type: str
            help=None,  # type: str  # noqa  ## Shadows built-in name 'help'.
    ):  # type: (...) -> None
        """
        Defines scenario paths positional arguments.

        :param nargs:
            ``argparse`` ``add_argument()`` ``nargs`` parameter.
            ``"+"`` if not set.
        :param help:
            ``argparse`` ``add_argument()`` ``help`` parameter.
            Default help message if not set.
        """
        self._test_exec_group.add_argument(
            metavar="SCENARIO_PATH", nargs=nargs or "+",
            dest="scenario_paths", action="store", type=str, default=[],
            help=help or "Scenario script(s) to execute.",
        )

    def _checkargs(self):  # type: (...) -> bool
        """
        Checks scenario runner arguments once parsed.

        :return: ``True`` for success, ``False`` otherwise.
        """
        from .loggermain import MAIN_LOGGER

        if not Args._checkargs(self):
            return False
        if not CommonExecArgs._checkargs(self):
            return False

        # Scenario paths.
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

    @property
    def json_report(self):  # type: () -> typing.Optional[Path]
        """
        JSON report output file path.
        No JSON report when ``None``.
        """
        if self._args.json_report:
            return Path(self._args.json_report)
        return None

    @property
    def extra_info(self):  # type: () -> typing.Sequence[str]
        """
        Attribute names to display for extra info.
        Applicable when executing several tests.
        """
        return list(self._args.extra_info)

    @property
    def scenario_paths(self):  # type: () -> typing.Sequence[Path]
        """
        Path of the scenario Python script(s) to execute.
        """
        return [Path(_scenario_path) for _scenario_path in self._args.scenario_paths]
