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
Common logging program arguments.
"""

import typing


class CommonLoggingArgs:
    """
    Base class for argument parser classes that embed common logging program arguments.
    """

    def __init__(
            self,
            class_debugging,  # type: bool
    ):  # type: (...) -> None
        """
        Installs common logging program arguments.

        :param class_debugging: ``True`` to enable per-class debugging, ``False`` for unclassed debugging only.

        When per-class debugging is enabled, the main logger debugging is enabled by default.
        """
        from ._args import Args

        assert isinstance(self, Args)

        #: Main logger debugging.
        self.debug_main = False  # type: bool
        if class_debugging:
            self.debug_main = True
        else:
            self.addarg("Debug main", "debug_main", bool).define(
                "--debug",
                action="store_true", default=False,
                help="Enable debugging.",
            )

        #: Debug classes.
        self.debug_classes = []  # type: typing.List[str]
        if class_debugging:
            self.addarg("Debug classes", "debug_classes", str).define(
                "--debug-class", metavar="DEBUG_CLASS",
                action="append", type=str, default=[],
                help="Activate debugging for the given class.",
            )
