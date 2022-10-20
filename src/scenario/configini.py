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
    # `KeyType` used in method signatures.
    # Type declared for type checking only.
    from .configtypes import KeyType
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
            root="",  # type: KeyType
    ):  # type: (...) -> None
        """
        Loads a INI configuration file.

        :param path: Path of the INI file to load.
        :param root: Root key to load the INI file from.
        """
        from .configdb import CONFIG_DB
        from .textfile import guessencoding

        CONFIG_DB.debug("Loading INI file '%s'", path)

        _config_parser = configparser.ConfigParser()  # type: configparser.ConfigParser
        # Override the optionxform member in ordre to make the ConfigParser case sensitive.
        # See https://stackoverflow.com/questions/1611799/preserve-case-in-configparser#1611877/964122
        _config_parser.optionxform = lambda optionstr: optionstr  # type: ignore  ## Cannot assign to a method

        _res = _config_parser.read(path, encoding=guessencoding(path))  # type: typing.List[str]
        if os.fspath(path) not in _res:
            raise IOError(f"Could not read '{path}'")

        # Build a dictionary from the INI file content.
        _data = {}  # type: typing.Dict[str, typing.Any]
        for _section in _config_parser.sections():  # type: str
            CONFIG_DB.debug(f"  Section '{_section}'")
            _data[_section] = {}
            for _option in _config_parser.options(_section):  # Type already declared above.
                _data[_section][_option] = _config_parser.get(_section, _option)
                CONFIG_DB.debug(f"    Option '{_option}' = {_data[_section][_option]!r}")

        # Push the dictionary to the configuration database.
        CONFIG_DB.set(root, _data, origin=path)

        CONFIG_DB.debug("INI file '%s' successfully read", path)

    @staticmethod
    def savefile(
            path,  # type: AnyPathType
            root="",  # type: KeyType
    ):  # type: (...) -> None
        """
        Saves a INI configuration file.

        :param path: Path of the INI file to save.
        :param root: Root key to save data from.

        .. warning:: Works only for `Dict[str, Dict[str, Union[str, int, bool, float]]]` dictionaries (i.e. *[section]/key = value* structures).
        """
        from .configdb import CONFIG_DB
        from .configkey import ConfigKey
        from .debugutils import saferepr

        CONFIG_DB.debug("Saving INI file '%s'", path)

        _config_parser = configparser.ConfigParser()  # type: configparser.ConfigParser
        # Override the optionxform member in ordre to make the ConfigParser case sensitive.
        # See https://stackoverflow.com/questions/1611799/preserve-case-in-configparser#1611877/964122
        _config_parser.optionxform = lambda optionstr: optionstr  # type: ignore  ## Cannot assign to a method

        # Populate the `ConfigParser` with the dictionary from the root key.
        def _feedini(
                parent_node_key,  # type: str
                current_node_subkey,  # type: str
                current_node,  # type: typing.Any
        ):  # type: (...) -> None
            if isinstance(current_node, dict):
                for _subkey in current_node:
                    _feedini(
                        parent_node_key=ConfigKey.join(parent_node_key, current_node_subkey),
                        current_node_subkey=_subkey,
                        current_node=current_node[_subkey],
                    )
            elif isinstance(current_node, list):
                for _index in range(len(current_node)):
                    _feedini(
                        parent_node_key=ConfigKey.join(parent_node_key, current_node_subkey),
                        current_node_subkey=f"[{_index}]",
                        current_node=current_node[_index],
                    )
            else:
                _ini_section = parent_node_key.replace("[", ".").replace("]", "")  # type: str
                if _ini_section not in _config_parser.sections():
                    _config_parser.add_section(_ini_section)
                CONFIG_DB.debug(f"Feeding INI with [{_ini_section}]/{current_node_subkey} = '{current_node}'")
                _config_parser.set(_ini_section, current_node_subkey, f"{current_node}")
        _dict = CONFIG_DB.get(root)  # type: typing.Any
        assert isinstance(_dict, dict), f"Configuration at '{root}' is not a dictionary ({saferepr(_dict)})"
        _feedini("", "", _dict)

        # Save the file. Use UTF-8 encoding.
        with open(path, "w", encoding="utf-8") as _file:
            _config_parser.write(_file)
            _file.close()

        CONFIG_DB.debug("INI file '%s' successfully saved", path)
