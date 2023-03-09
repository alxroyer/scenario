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
            def_test_suite_paths_arg=True,  # type: bool
            default_outdir_cwd=True,  # type: bool
    ):  # type: (...) -> None
        """
        Defines program arguments for :class:`.campaignrunner.CampaignRunner`.

        :param def_test_suite_paths_arg:
            ``False`` to disable the test suite paths positional arguments definition.
            Useful for user programs that wish to redefine it.
            Use :meth:`_deftestsuitepathsarg()` in that case.
        :param default_outdir_cwd:
            ``False`` to disable the use of the current working directory by default.
        """
        Args.__init__(self, class_debugging=True)

        self.setdescription("Scenario campaign execution.")

        CommonExecArgs.__init__(self)

        #: Current directory as the default output directory flag.
        self._default_outdir_cwd = default_outdir_cwd

        #: Campaign argument group.
        self._campaign_group = self._arg_parser.add_argument_group("Campaign execution")  # Type `argparse._ArgumentGroup` not available, let default typing.

        self._campaign_group.add_argument(
            "--outdir", metavar="OUTDIR_PATH",
            dest="outdir", action="store", type=str, default=None,
            help=(
                "Output directory to store test results into."
                f"{' Defaults to the current directory.' if self._default_outdir_cwd else ''}"
            ),
        )

        self._campaign_group.add_argument(
            "--dt-subdir",
            dest="create_dt_subdir", action="store_true", default=False,
            help=(
                "Do not store the test results directly in OUTDIR_PATH, "
                "but within a subdirectory named with the current date and time."
            ),
        )

        self._campaign_group.add_argument(
            "--extra-info", metavar="ATTRIBUTE_NAME",
            dest="extra_info", action="append", type=str, default=[],
            help=(
                "Scenario attribute to display for extra info when displaying results. "
                "This option may be called several times to display more info."
            ),
        )

        if def_test_suite_paths_arg:
            self._deftestsuitepathsarg()

    def _deftestsuitepathsarg(
            self,
            nargs=None,  # type: str
            help=None,  # type: str  # noqa  ## Shadows built-in name 'help'.
    ):  # type: (...) -> None
        """
        Defines test suite paths positional arguments.

        :param nargs:
            ``argparse`` ``add_argument()`` ``nargs`` parameter.
            ``"+"`` if not set.
        :param help:
            ``argparse`` ``add_argument()`` ``help`` parameter.
            Default help message if not set.
        """
        self._campaign_group.add_argument(
            metavar="TEST_SUITE_PATH", nargs=nargs or "+",
            dest="test_suite_paths", action="store", type=str, default=[],
            help=help or "Test suite file(s) to execute.",
        )

    def _checkargs(self):  # type: (...) -> bool
        """
        Check campaign arguments once parsed.

        :return: True for success, False otherwise.
        """
        from .loggermain import MAIN_LOGGER
        from .path import Path

        if not Args._checkargs(self):
            return False
        if not CommonExecArgs._checkargs(self):
            return False

        # Output directory.
        if self._args.outdir is None:
            if self._default_outdir_cwd:
                self.debug("Using current working directory for output directory by default")
                self._args.outdir = Path.cwd()
            else:
                MAIN_LOGGER.error("Output directory missing")
                return False
        # Ensure a `Path` instance for `self._args.outdir`, more robust to current working directory changes.
        if not isinstance(self._args.outdir, Path):
            self._args.outdir = Path(self._args.outdir)
        # Create the directory if needed.
        self.outdir.mkdir(parents=True, exist_ok=True)

        # Test suite paths.
        for _test_suite_path in self.test_suite_paths:  # type: Path
            if not _test_suite_path.is_file():
                MAIN_LOGGER.error(f"No such file '{_test_suite_path}'")
                return False

        return True

    @property
    def outdir(self):  # type: () -> _PathType
        """
        Output directory path.

        Expected to be set:

        - either with the --outdir option
        - or programmatically in subclasses through the :meth:`outdir()` setter.

        :raise ValueError: If the output directory has not been defined.
        """
        from .path import Path

        if not self._args.outdir:
            raise ValueError("Output directory not set")
        # `self._args.outdir` should normally be a `Path` instance already, whatever.
        if not isinstance(self._args.outdir, Path):
            self._args.outdir = Path(self._args.outdir)
        assert isinstance(self._args.outdir, Path)  # Help type checking.
        return self._args.outdir

    @outdir.setter
    def outdir(self, outdir):  # type: (_PathType) -> None
        """
        Output directory programmatic setter.
        """
        self._args.outdir = outdir

    @property
    def create_dt_subdir(self):  # type: () -> bool
        """
        ``True`` when an output subdirectory in :attr:`CampaignArgs.outdir` named with the campaign execution date and time should be created.
        """
        return bool(self._args.create_dt_subdir)

    @property
    def extra_info(self):  # type: () -> typing.Sequence[str]
        """
        Attribute names to display for extra info.
        Applicable when executing several tests.
        """
        return list(self._args.extra_info)

    @property
    def test_suite_paths(self):  # type: () -> typing.Sequence[_PathType]
        """
        Campaign file path.
        """
        from .path import Path

        return [Path(_test_suite_path) for _test_suite_path in self._args.test_suite_paths]
