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
Requirement management arguments.
"""

import typing

if True:
    from ._args import Args as _ArgsImpl  # `Args` used for inheritance.
    from ._fastpath import FAST_PATH as _FAST_PATH  # `FAST_PATH` imported once for performance concerns.
    from ._path import Path as _PathImpl  # `Path` imported once for performance concerns.
if typing.TYPE_CHECKING:
    from ._path import Path as _PathType


class ReqManagementArgs(_ArgsImpl):
    """
    Requirement management program arguments.
    """

    def __init__(self):  # type: (...) -> None
        """
        Defines program arguments for :class:`._reqmgt.ReqManagement`.
        """
        _ArgsImpl.__init__(self, class_debugging=True)

        #: Input requirement database files.
        self.req_db_paths = []  # type: typing.List[_PathType]
        self.addarg("Req-db files", "req_db_paths", _PathImpl).define(
            "--req-db", metavar="PATH",
            action="append", type=str, default=[],
            help="Requirement database file to load. "
                 "May be called several times. "
                 "Defaults to 'scenario.req_db_files' configuration if not set.",
        )

        #: Test suite files to load scenarios from.
        self.test_suite_paths = []  # type: typing.List[_PathType]
        self.addarg("Test suite files", "test_suite_paths", _PathImpl).define(
            "--test-suite", metavar="PATH",
            action="append", type=str, default=[],
            help="Test suite file to load scenarios from. "
                 "May be called several times. "
                 "Defaults to 'scenario.test_suite_files' configuration if not set.",
        )

        #: Campaign results to load data from.
        self.campaign_results_path = None  # type: typing.Optional[_PathType]
        self.addarg("Campaign results path", "campaign_results_path", _PathImpl).define(
            "--campaign", metavar="PATH",
            action="store", type=str,
            help="Campaign directory or JUnit report file to load data from. "
                 "Incompatible with --req-db and --test-suite options.",
        )

        #: Downstream traceability option.
        self.downstream_traceability_outfile = None  # type: typing.Optional[_PathType]
        self.addarg("Downstream traceability", "downstream_traceability_outfile", _PathImpl).define(
            "--downstream-traceability", metavar="PATH",
            action="store", type=str, default=None,
            help="Generate downstream traceability, i.e. from requirements to scenarios.",
        )

        #: Upstream traceability option.
        self.upstream_traceability_outfile = None  # type: typing.Optional[_PathType]
        self.addarg("Upstream traceability", "upstream_traceability_outfile", _PathImpl).define(
            "--upstream-traceability", metavar="PATH",
            action="store", type=str, default=None,
            help="Generate upstream traceability, i.e. from scenarios to requirements.",
        )

        #: Allow test results in traceability reports option.
        self.allow_results = True  # type: bool
        self.addarg("No results", "allow_results", bool).define(
            "--no-results",
            action="store_false", default=True,
            help="Prevent test results in traceability reports.",
        )

    def _checkargs(
            self,
            args,  # type: typing.Any
    ):  # type: (...) -> bool
        """
        Checks requirement management arguments once parsed.

        .. seealso:: :meth:`._args.Args._checkargs()` for parameters and return details.
        """
        if not super()._checkargs(args):
            return False

        # Input options.
        if self.campaign_results_path:
            if self.req_db_paths:
                _FAST_PATH.main_logger.error("Can't use --req-db with --campaign")
            if self.test_suite_paths:
                _FAST_PATH.main_logger.error("Can't use --test-suite with --campaign")
            if self.req_db_paths or self.test_suite_paths:
                return False

        # Output options.
        if not any([self.downstream_traceability_outfile, self.upstream_traceability_outfile]):
            _FAST_PATH.main_logger.error("Please use one option of --downstream-traceability or --upstream-traceability at least")
            return False

        return True
