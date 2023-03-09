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
Campaign runner program arguments.
"""

import typing

from .args import Args  # `Args` used for inheritance.
from .scenarioargs import CommonExecArgs  # `CommonExecArgs` used for inheritance.

if typing.TYPE_CHECKING:
    from .path import Path as _PathType


class CampaignArgs(Args, CommonExecArgs):
    """
    Campaign runner program arguments.
    """

    def __init__(
            self,
            positional_args=True,  # type: bool
            default_outdir_cwd=True,  # type: bool
    ):  # type: (...) -> None
        """
        Defines program arguments for :class:`.campaignrunner.CampaignRunner`.

        :param positional_args: ``False`` to disable the scenario path positional arguments definition.
                                Useful for user programs that wish to redefine it.
        :param default_outdir_cwd: ``False`` to disable the use of the current directory by default.
        """
        from .path import Path

        Args.__init__(self, class_debugging=True)

        self.setdescription("Scenario campaign execution.")

        CommonExecArgs.__init__(self)

        #: Current directory as the default output directory flag.
        self._default_outdir_cwd = default_outdir_cwd
        #: Output directory path.
        #:
        #: Inner attribute.
        #: ``None`` until actually set, either with the --outdir option, or programmatically in sub-classes.
        self._outdir = None  # type: typing.Optional[Path]
        self.addarg("Output directory", "_outdir", Path).define(
            "--outdir", metavar="OUTDIR_PATH",
            action="store", type=str,
            help=f"Output directory to store test results into.{' Defaults to the current directory.' if self._default_outdir_cwd else ''}",
        )

        #: ``True`` when an output subdirectory in :attr:`CampaignArgs.outdir` named with the campaign execution date and time should be created.
        self.create_dt_subdir = True  # type: bool
        self.addarg("Create date-time subdirectory", "create_dt_subdir", bool).define(
            "--dt-subdir",
            action="store_true", default=False,
            help="Do not store the test results directly in OUTDIR_PATH, "
                 "but within a subdirectory named with the current date and time.",
        )

        #: Attribute names to display for extra info.
        #: Applicable when executing several tests.
        self.extra_info = []  # type: typing.List[str]
        self.addarg("Results extra info", "extra_info", str).define(
            "--extra-info", metavar="ATTRIBUTE_NAME",
            action="append", type=str, default=[],
            help="Scenario attribute to display for extra info when displaying results. "
                 "This option may be called several times to display more info.",
        )

        #: Campaign file path.
        self.test_suite_paths = []  # type: typing.List[Path]
        if positional_args:
            self.addarg("Test suite files", "test_suite_paths", Path).define(
                metavar="TEST_SUITE_PATH", nargs="+",
                action="store", type=str, default=[],
                help="Test suite file(s) to execute.",
            )

    @property
    def outdir(self):  # type: () -> _PathType
        """
        Output directory path as a public property.
        """
        if not self._outdir:
            raise ValueError("Output directory not set")
        return self._outdir

    def _checkargs(
            self,
            args,  # type: typing.Any
    ):  # type: (...) -> bool
        """
        Check campaign arguments once parsed.

        :return: True for success, False otherwise.
        """
        from .loggermain import MAIN_LOGGER
        from .path import Path

        if not Args._checkargs(self, args):
            return False
        if not CommonExecArgs._checkargs(self, args):
            return False

        if self._outdir is None:
            if self._default_outdir_cwd:
                self.debug("Using current working directory for output directory by default")
                self._outdir = Path.cwd()
            else:
                MAIN_LOGGER.error("Output directory missing")
                return False
        self._outdir.mkdir(parents=True, exist_ok=True)

        for _test_suite_path in self.test_suite_paths:  # type: Path
            if not _test_suite_path.is_file():
                MAIN_LOGGER.error(f"No such file '{_test_suite_path}'")
                return False

        return True
