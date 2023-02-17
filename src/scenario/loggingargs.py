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
        from .args import Args

        # Let typings know this class is actually a subclass of the base `Args` class.
        assert isinstance(self, CommonLoggingArgs) and isinstance(self, Args)

        #: Logging argument group.
        self._logging_group = self._arg_parser.add_argument_group("Logging")  # Type `argparse._ArgumentGroup` not available, let default typing.

        if not class_debugging:
            self._logging_group.add_argument(
                "--debug",
                dest="debug_main", action="store_true", default=False,
                help="Enable debugging.",
            )

        if class_debugging:
            self._logging_group.add_argument(
                "--debug-class", metavar="DEBUG_CLASS",
                dest="debug_classes", action="append", type=str, default=[],
                help="Activate debugging for the given class.",
            )

    @property
    def debug_main(self):  # type: () -> bool
        """
        Main logger debugging.
        """
        from .args import Args

        # Let typings know this class is actually a subclass of the base `Args` class.
        assert isinstance(self, CommonLoggingArgs) and isinstance(self, Args)

        if hasattr(self._args, "debug_main"):
            return bool(self._args.debug_main)
        else:
            # When the `--debug` option was not defined,
            # i.e. class-debugging is enabled,
            # main debugging is automatically enabled.
            return True

    @property
    def debug_classes(self):  # type: () -> typing.Sequence[str]
        """
        Debug classes.
        """
        from .args import Args

        # Let typings know this class is actually a subclass of the base `Args` class.
        assert isinstance(self, CommonLoggingArgs) and isinstance(self, Args)

        if hasattr(self._args, "debug_classes"):
            return list(self._args.debug_classes)
        return []
