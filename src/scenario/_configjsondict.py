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
JSON / YAML configuration file management.
"""

import typing

if True:
    from ._debugutils import saferepr as _saferepr  # `saferepr()` imported once for performance concerns.
    from ._fastpath import FAST_PATH as _FAST_PATH  # `FAST_PATH` imported once for performance concerns.
if typing.TYPE_CHECKING:
    from ._configtypes import KeyType as _KeyType
    from ._path import AnyPathType as _AnyPathType


class ConfigJsonDict:
    """
    JSON / YAML configuration file management.
    """

    @staticmethod
    def loadfile(
            path,  # type: _AnyPathType
            root="",  # type: _KeyType
    ):  # type: (...) -> None
        """
        Loads a JSON / YAML configuration file.

        :param path: Path of the file to load.
        :param root: Root key to load the file from.
        """
        from ._jsondictutils import JsonDict
        if typing.TYPE_CHECKING:
            from ._jsondictutils import JsonDictType

        _FAST_PATH.config_db.debug("Loading JSON / YAML file '%s'", path)

        # Read the file.
        _data = JsonDict.readfile(path)  # type: JsonDictType

        # Push the data to the configuration database.
        _FAST_PATH.config_db.set(root, _data, origin=path)

        _FAST_PATH.config_db.debug("JSON / YAML file '%s' successfully read", path)

    @staticmethod
    def savefile(
            path,  # type: _AnyPathType
            root="",  # type: _KeyType
    ):  # type: (...) -> None
        """
        Saves a JSON / YAML configuration file.

        :param path: Path of the file to save.
        :param root: Root key to save data from.
        """
        from ._jsondictutils import JsonDict

        _FAST_PATH.config_db.debug("Saving JSON / YAML file '%s'", path)

        # Save the file.
        _content = _FAST_PATH.config_db.get(root)  # type: typing.Optional[typing.Any]
        if _content is None:
            raise KeyError(f"No content for config key {root!r}, can't save file '{path}'")
        if not isinstance(_content, dict):
            raise ValueError(f"Not a dictionary {_saferepr(_content)} for config key {root!r}, can't save file '{path}'")
        JsonDict.writefile(_content, path)

        _FAST_PATH.config_db.debug("JSON / YAML file '%s' successfully saved", path)
