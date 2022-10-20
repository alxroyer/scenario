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
JSON configuration file management.
"""

import json
import typing

if typing.TYPE_CHECKING:
    # `AnyPathType` used in method signatures and type definitions.
    # Type declared for type checking only.
    from .path import AnyPathType


class ConfigJson:
    """
    JSON configuration file management.
    """

    @staticmethod
    def loadfile(
            path,  # type: AnyPathType
    ):  # type: (...) -> None
        """
        Loads a JSON configuration file.

        :param path: Path of the JSON file to load.
        """
        from .configdb import CONFIG_DB
        from .path import Path

        CONFIG_DB.debug("Loading JSON file '%s'" % path)

        # Read the JSON file.
        _data = json.load(Path(path).open("rb"))  # type: typing.Any

        # Push the data to the configuration database.
        CONFIG_DB.set("", _data, origin=path)

        CONFIG_DB.debug("JSON file '%s' successfully read" % path)
