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
JSON configuration file management.
"""

import json
import typing

if typing.TYPE_CHECKING:
    from .configtypes import KeyType
    from .path import AnyPathType


class ConfigJson:
    """
    JSON configuration file management.
    """

    @staticmethod
    def loadfile(
            path,  # type: AnyPathType
            root="",  # type: KeyType
    ):  # type: (...) -> None
        """
        Loads a JSON configuration file.

        :param path: Path of the JSON file to load.
        :param root: Root key to load the JSON file from.
        """
        from .configdb import CONFIG_DB
        from .path import Path
        from .textfile import guessencoding

        CONFIG_DB.debug("Loading JSON file '%s'", path)

        # Read the JSON file.
        with Path(path).open("r", encoding=guessencoding(path)) as _file:  # type: typing.TextIO
            _data = json.load(_file)  # type: typing.Any
            _file.close()

        # Push the data to the configuration database.
        CONFIG_DB.set(root, _data, origin=path)

        CONFIG_DB.debug("JSON file '%s' successfully read", path)

    @staticmethod
    def savefile(
            path,  # type: AnyPathType
            root="",  # type: KeyType
    ):  # type: (...) -> None
        """
        Saves a JSON configuration file.

        :param path: Path of the JSON file to save.
        :param root: Root key to save data from.
        """
        from .configdb import CONFIG_DB
        from .path import Path

        CONFIG_DB.debug("Saving JSON file '%s'", path)

        # Save the JSON file. Use UTF-8 encoding.
        with Path(path).open("w", encoding="utf-8") as _file:  # type: typing.TextIO
            json.dump(CONFIG_DB.get(root), _file)
            _file.close()

        CONFIG_DB.debug("JSON file '%s' successfully saved", path)
