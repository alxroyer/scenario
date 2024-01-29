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
Common configuration program arguments.
"""

import typing

if True:
    from ._path import Path as _PathImpl  # `Path` imported once for performance concerns.
if typing.TYPE_CHECKING:
    from ._path import Path as _PathType


class CommonConfigArgs:
    """
    Base class for argument parser classes that embed common configuration program arguments.
    """

    def __init__(self):  # type: (...) -> None
        """
        Installs common configuration program arguments.
        """
        if typing.TYPE_CHECKING:
            from ._args import Args  # check-imports: ignore  ## Non-executable local import, in type-checking mode only, to avoid cyclic module dependency.
            assert isinstance(self, Args)

        #: Configuration files.
        self.config_paths = []  # type: typing.List[_PathType]
        self.addarg("Configuration files", "config_paths", _PathImpl).define(
            "--config-file", metavar="CONFIG_PATH",
            action="append", type=str, default=[],
            help="Input configuration file path. "
                 "This option may be called several times.",
        )

        #: Additional configuration values.
        self.config_values = {}  # type: typing.Dict[str, str]
        self.addarg("Configuration values", "config_values", (str, str)).define(
            "--config-value", metavar=("KEY", "VALUE"), nargs=2,
            action="append", type=str, default=[],
            help="Single configuration value. "
                 "This option may be called several times.",
        )
