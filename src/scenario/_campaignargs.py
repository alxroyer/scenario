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

if True:
    from ._args import Args as _ArgsImpl  # `Args` used for inheritance.
    from ._path import Path as _PathImpl  # `Path` imported once for performance concerns.
    from ._scenarioargs import CommonExecArgs as _CommonExecArgsImpl  # `CommonExecArgs` used for inheritance.
if typing.TYPE_CHECKING:
    from ._path import Path as _PathType


class CampaignArgs(_ArgsImpl, _CommonExecArgsImpl):
    """
    Campaign runner program arguments.
    """

    def __init__(
            self,
            positional_args=True,  # type: bool
            default_outdir_cwd=True,  # type: bool
    ):  # type: (...) -> None
        """
        Defines program arguments for :class:`._campaignrunner.CampaignRunner`.

        :param positional_args:
            Deprecated.

            ``False`` to disable the scenario path positional arguments definition.

            Formerly defined for user programs that wished to redefine it.
            Now use :attr:`._scenarioconfig.ScenarioConfig.Key.TEST_SUITE_FILES` configuration instead.
        :param default_outdir_cwd:
            ``False`` to disable the use of the current directory by default.
        """
        _ArgsImpl.__init__(self, class_debugging=True)

        self.setdescription("Scenario campaign execution.")

        _CommonExecArgsImpl.__init__(self)

        #: Current directory as the default output directory flag.
        self._default_outdir_cwd = default_outdir_cwd
        #: Output directory path.
        #:
        #: Inner attribute.
        #: ``None`` until actually set, either with the ``--outdir`` option, or programmatically in subclasses.
        self._outdir = None  # type: typing.Optional[_PathType]
        self.addarg("Output directory", "_outdir", _PathImpl).define(
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

        #: Test suite file paths.
        self.test_suite_paths = []  # type: typing.List[_PathType]
        if positional_args:
            self.addarg("Test suite files", "test_suite_paths", _PathImpl).define(
                metavar="TEST_SUITE_PATH", nargs="*",
                action="store", type=str, default=[],
                help="Test suite file(s) to execute. "
                     "Defaults to 'scenario.test_suite_files' configuration.",
            )
        else:
            print(f"CampaignArgs: Deprecated `positional_args` argument. Please use 'scenario.test_suite_files' configuration instead.")

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

        .. seealso:: :meth:`._args.Args._checkargs()` for parameters and return details.
        """
        from ._loggermain import MAIN_LOGGER

        if not _ArgsImpl._checkargs(self, args):
            return False
        if not _CommonExecArgsImpl._checkargs(self, args):
            return False

        if self._outdir is None:
            if self._default_outdir_cwd:
                self.debug("Using current working directory for output directory by default")
                self._outdir = _PathImpl.cwd()
            else:
                MAIN_LOGGER.error("Output directory missing")
                return False
        self._outdir.mkdir(parents=True, exist_ok=True)

        for _test_suite_path in self.test_suite_paths:  # type: _PathType
            if not _test_suite_path.is_file():
                MAIN_LOGGER.error(f"No such file '{_test_suite_path}'")
                return False

        return True
