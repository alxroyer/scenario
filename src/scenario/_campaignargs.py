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
    from . import _enumutils as _enumutils  # @inheritance
    from ._args import Args as _ArgsImpl  # @inheritance
    from ._fastpath import FAST_PATH as _FAST_PATH  # @perf
    from ._path import Path as _PathImpl  # @perf
    from ._scenarioargs import CommonExecArgs as _CommonExecArgsImpl  # @inheritance
if typing.TYPE_CHECKING:
    from ._path import Path as _PathType


class CampaignArgs(_ArgsImpl, _CommonExecArgsImpl):
    """
    Campaign runner program arguments.
    """

    class SubdirMode(_enumutils.StrEnum):
        """
        Campaign subdirectory mode.
        """
        #: No subdirectory.
        NONE = "none"
        #: Date/time subdirectory.
        DATE_TIME = "date/time"

    def __init__(self):  # type: (...) -> None
        """
        Defines program arguments for :class:`._campaignrunner.CampaignRunner`.
        """
        _ArgsImpl.__init__(self, class_debugging=True)
        self.setdescription("Scenario campaign execution.")

        _CommonExecArgsImpl.__init__(self)

        #: Output directory path.
        #:
        #: Inner attribute.
        #: ``None`` until actually set, either with the ``--outdir`` option, or programmatically in subclasses.
        self.outdir = _PathImpl()  # type: _PathType
        self.addarg("Output directory", "outdir", _PathImpl).define(
            "--outdir", metavar="OUTDIR_PATH",
            action="store", type=str,
            help="Output directory to store test results into. "
                 f"Defaults to {str(_FAST_PATH.scenario_config.Key.CAMPAIGN_OUTDIR)!r} configuration, "
                 "or current working directory.",
        )

        #: ``True`` when an output subdirectory in :attr:`CampaignArgs.outdir` named with the campaign execution date and time should be created.
        self.subdir_mode = None  # type: typing.Optional[CampaignArgs.SubdirMode]
        self.addarg("Subdirectory mode", "subdir_mode", CampaignArgs.SubdirMode).define(
            "--subdir", metavar="SUBDIR_MODE",
            action="store",
            help="Choose the subdirectory mode in OUTDIR_PATH (or configured path) to store test results into. "
                 f"'{CampaignArgs.SubdirMode.DATE_TIME}' (default behaviour): to create a subdirectory named with current date and time "
                 f"('YYYY-MM-DD_HH-MM-SS' pattern). "
                 f"'{CampaignArgs.SubdirMode.NONE}': to store test results directly in OUTDIR_PATH.",
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
        self.addarg("Test suite files", "test_suite_paths", _PathImpl).define(
            metavar="TEST_SUITE_PATH", nargs="*",
            action="store", type=str, default=[],
            help="Test suite file(s) to execute. "
                 f"Defaults to {str(_FAST_PATH.scenario_config.Key.TEST_SUITE_FILES)!r} configuration.",
        )

    def _checkargs(
            self,
            args,  # type: typing.Any
    ):  # type: (...) -> bool
        """
        Check campaign arguments once parsed.

        .. seealso:: :meth:`._args.Args._checkargs()` for parameters and return details.
        """
        if not _ArgsImpl._checkargs(self, args):
            return False
        if not _CommonExecArgsImpl._checkargs(self, args):
            return False

        # Check TEST_SUITE_PATH (from program arguments or configuration).
        if not _FAST_PATH.scenario_config.testsuitepaths():
            _FAST_PATH.main_logger.error("TEST_SUITE_PATH missing")
            return False
        for _test_suite_path in _FAST_PATH.scenario_config.testsuitepaths():  # type: _PathType
            if not _test_suite_path.is_file():
                _FAST_PATH.main_logger.error(f"No such file '{_test_suite_path}'")
                return False

        # Ensure OUTDIR_PATH exists.
        _FAST_PATH.scenario_config.campaignoutdir().mkdir(parents=True, exist_ok=True)

        return True
