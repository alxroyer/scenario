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
YAML configuration file management.
"""

import typing

if typing.TYPE_CHECKING:
    # `KeyType` used in method signatures.
    # Type declared for type checking only.
    from .configtypes import KeyType
    # `AnyPathType` used in method signatures and type definitions.
    # Type declared for type checking only.
    from .path import AnyPathType


class ConfigYaml:
    """
    YAML configuration file management.
    """

    @staticmethod
    def loadfile(
            path,  # type: AnyPathType
            root="",  # type: KeyType
    ):  # type: (...) -> None
        """
        Loads a YAML configuration file.

        :param path: Path of the YAML file to load.
        :param root: Root key to load the YAML file from.
        """
        from .configdb import CONFIG_DB
        from .path import Path
        from .textfile import guessencoding

        CONFIG_DB.debug("Loading YAML file '%s'", path)

        # Import `yaml`.
        try:
            import yaml  # type: ignore[import]  ## `yaml` or stubs for `yaml` may not be installed. Do not try to check typings for this package.
        except ImportError as _err:
            raise EnvironmentError(_err)

        # Read the YAML file.
        with Path(path).open("r", encoding=guessencoding(path)) as _file:  # type: typing.TextIO
            _data = yaml.safe_load(_file)  # type: typing.Any
            _file.close()

        # Push the data to the configuration database.
        CONFIG_DB.set(root, _data, origin=path)

        CONFIG_DB.debug("YAML file '%s' successfully read", path)

    @staticmethod
    def savefile(
            path,  # type: AnyPathType
            root="",  # type: KeyType
    ):  # type: (...) -> None
        """
        Saves a YAML configuration file.

        :param path: Path of the YAML file to save.
        :param root: Root key to save data from.
        """
        from .configdb import CONFIG_DB
        from .path import Path

        CONFIG_DB.debug("Saving YAML file '%s'", path)

        # Import `yaml`.
        try:
            import yaml
        except ImportError as _err:
            raise EnvironmentError(_err)

        # Save the YAML file. Use UTF-8 encoding.
        with Path(path).open("w", encoding="utf-8") as _file:  # type: typing.TextIO
            # Let `yaml.safe_load()` deal with encoding.
            yaml.safe_dump(CONFIG_DB.get(root), _file)
            _file.close()

        CONFIG_DB.debug("YAML file '%s' successfully saved", path)
