# -*- coding: utf-8 -*-

# Copyright 2020-2022 Alexis Royer <https://github.com/Alexis-ROYER/scenario>
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
INI configuration file management.
"""

import configparser
import os
import typing

if typing.TYPE_CHECKING:
    # `AnyPathType` used in method signatures and type definitions.
    # Type declared for type checking only.
    from .path import AnyPathType


class ConfigIni:
    """
    INI configuration file management.
    """

    @staticmethod
    def loadfile(
            path,  # type: AnyPathType
    ):  # type: (...) -> None
        """
        Loads a INI configuration file.

        :param path: Path of the INI file to load.
        """
        from .configdb import CONFIG_DB

        CONFIG_DB.debug("Loading INI file '%s'" % path)

        _config_parser = configparser.ConfigParser()  # type: configparser.ConfigParser
        _res = _config_parser.read(path)  # type: typing.List[str]
        if os.fspath(path) not in _res:
            raise IOError("Could not read '%s'" % path)

        # Build a dictionary from the INI file content.
        _data = {}  # type: typing.Dict[str, typing.Any]
        for _section in _config_parser.sections():  # type: str
            _data[_section] = {}
            for _option in _config_parser.options(_section):  # Type already declared above.
                _data[_section][_option] = _config_parser.get(_section, _option)

        # Push the dictionary to the configuration database.
        CONFIG_DB.set("", _data, origin=path)

        CONFIG_DB.debug("INI file '%s' successfully read" % path)
