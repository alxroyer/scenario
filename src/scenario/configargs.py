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

if typing.TYPE_CHECKING:
    from .path import Path as _PathType


class CommonConfigArgs:
    """
    Base class for argument parser classes that embed common configuration program arguments.
    """

    def __init__(self):  # type: (...) -> None
        """
        Installs common configuration program arguments.
        """
        from .args import Args

        # Let typings know this class is actually a subclass of the base `Args` class.
        assert (
            isinstance(self, CommonConfigArgs)  # type: ignore[redundant-expr]  ## Left operand of "and" is always true
            and isinstance(self, Args)
        )

        #: Configuration argument group.
        self._config_group = self._arg_parser.add_argument_group("Configuration")  # Type `argparse._ArgumentGroup` not available, let default typing.

        self._config_group.add_argument(
            "--config-file", metavar="CONFIG_PATH",
            dest="config_paths", action="append", type=str, default=[],
            help="Input configuration file path. "
                 "This option may be called several times.",
        )

        self._config_group.add_argument(
            "--config-value", metavar=("KEY", "VALUE"), nargs=2,
            dest="config_values", action="append", type=str, default=[],
            help="Single configuration value. "
                 "This option may be called several times.",
        )

    @property
    def config_paths(self):  # type: () -> typing.Sequence[_PathType]
        """
        Configuration files.
        """
        from .args import Args
        from .path import Path

        # Let typings know this class is actually a subclass of the base `Args` class.
        assert (
            isinstance(self, CommonConfigArgs)  # type: ignore[redundant-expr]  ## Left operand of "and" is always true
            and isinstance(self, Args)
        )

        return [Path(_config_path) for _config_path in self._args.config_paths]

    @property
    def config_values(self):  # type: () -> typing.Mapping[str, str]
        """
        Additional configuration values.
        """
        from .args import Args

        # Let typings know this class is actually a subclass of the base `Args` class.
        assert (
            isinstance(self, CommonConfigArgs)  # type: ignore[redundant-expr]  ## Left operand of "and" is always true
            and isinstance(self, Args)
        )

        _config_values = {}  # type: typing.Dict[str, str]
        for _config_value in self._args.config_values:  # type: typing.Tuple[str, str]
            _config_values[_config_value[0]] = _config_value[1]
        return _config_values
