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


class ReqManagementArgs(_ArgsImpl):
    """
    Requirement management program arguments.
    """

    def __init__(self):  # type: (...) -> None
        """
        Defines program arguments for :class:`._reqmgt.ReqManagement`.
        """
        from ._path import Path

        _ArgsImpl.__init__(self, class_debugging=True)

        #: Downstream traceability option.
        self.downstream_traceability_outfile = Path()  # type: Path
        self.addarg("Downstream traceability", "downstream_traceability_outfile", Path).define(
            "--downstream-traceability", metavar="PATH",
            action="store", type=str, default=None,
            help="Generate downstream traceability, i.e. from requirements with subreferences to scenarios with related steps.",
        )

        #: Upstream traceability option.
        self.upstream_traceability_outfile = Path()  # type: Path
        self.addarg("Upstream traceability", "upstream_traceability_outfile", Path).define(
            "--upstream-traceability", metavar="PATH",
            action="store", type=str, default=None,
            help="Generate upstream traceability, i.e. from scenarios with related steps to requirements with subreferences.",
        )

        #: ``--serve`` option.
        self.serve = False  # type: bool
        self.addarg("Serve", "serve", bool).define(
            "--serve",
            action="store_true",
            help="Launch the requirement management server.",
        )

    def _checkargs(
            self,
            args,  # type: typing.Any
    ):  # type: (...) -> bool
        """
        Checks requirement management arguments once parsed.

        .. seealso:: :meth:`._args.Args._checkargs()` for parameters and return details.
        """
        from ._loggermain import MAIN_LOGGER

        if not super()._checkargs(args):
            return False

        _is_traceability_outfile = any([
            not self.downstream_traceability_outfile.is_void(),
            not self.upstream_traceability_outfile.is_void(),
        ])  # type: bool

        if not any([_is_traceability_outfile, self.serve]):
            MAIN_LOGGER.error("Please use one option at least")
            return False

        if self.serve and _is_traceability_outfile:
            MAIN_LOGGER.error("Can't use --serve with other options")
            return False

        return True
