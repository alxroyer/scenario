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
Configuration database management.
"""

import builtins
import logging
import os
import typing

# `Logger` used for inheritance.
from .logger import Logger
# `ConfigNode` used in method signatures.
from .confignode import ConfigNode
# `StrEnum` used for inheritance.
from .enumutils import StrEnum

if typing.TYPE_CHECKING:
    # `KeyType`, `OriginType` and `T` used in method signatures.
    # Type declared for type checking only.
    from .configtypes import KeyType, OriginType, T
    # `AnyPathType` used in method signatures and type definitions.
    # Type declared for type checking only.
    from .path import AnyPathType


class ConfigDatabase(Logger):
    """
    Configuration management.

    This class loads a list of configuration files,
    and aggregates all configuration read in a single configuration tree.

    See the :ref:`configuration database <config-db>` documentation.
    """

    class FileFormat(StrEnum):
        """
        Configuration file formats.
        """
        #: INI configuration file format.
        INI = "INI"
        #: JSON configuration file format.
        JSON = "JSON"
        #: YAML configuration file format.
        YAML = "YAML"

    def __init__(
            self,  # type: ConfigDatabase
    ):  # type: (...) -> None
        """
        Initializes instance attributes and configures logging for the :class:`ConfigDatabase` class.
        """
        from .debugclasses import DebugClass

        Logger.__init__(self, log_class=DebugClass.CONFIG_DATABASE)

        #: Configuration tree.
        self._root = ConfigNode(parent=None, key="")  # type: ConfigNode

    def loadfile(
            self,  # type: ConfigDatabase
            path,  # type: AnyPathType
            format=None,  # type: ConfigDatabase.FileFormat  # noqa  ## Shadows built-in name 'format'
            root="",  # type: KeyType
    ):  # type: (...) -> None
        """
        Loads a configuration file.

        :param path:
            Path of the configuration file to load.
        :param format:
            File format.

            Determined automatically from the file extension when not specified.
        :param root:
            Root key to load the file from.
        """
        from .configini import ConfigIni
        from .configjson import ConfigJson
        from .configyaml import ConfigYaml
        from .path import Path

        if format is None:
            _suffix = Path(path).suffix.lower()  # type: str
            if _suffix in (".ini", ):
                format = ConfigDatabase.FileFormat.INI  # noqa  ## Shadows built-in name 'format'
            elif _suffix in (".json", ):
                format = ConfigDatabase.FileFormat.JSON  # noqa  ## Shadows built-in name 'format'
            elif _suffix in (".yml", ".yaml", ):
                format = ConfigDatabase.FileFormat.YAML  # noqa  ## Shadows built-in name 'format'
            else:
                raise ValueError(f"{path}: Unknown configuration file suffix")

        if format == ConfigDatabase.FileFormat.INI:
            ConfigIni.loadfile(path, root=root)
        elif format == ConfigDatabase.FileFormat.JSON:
            ConfigJson.loadfile(path, root=root)
        elif format == ConfigDatabase.FileFormat.YAML:
            ConfigYaml.loadfile(path, root=root)
        else:
            raise NotImplementedError(f"Unknown file format {format}")

    def savefile(
            self,  # type: ConfigDatabase
            path,  # type: AnyPathType
            format=None,  # type: ConfigDatabase.FileFormat  # noqa  ## Shadows built-in name 'format'
            root="",  # type: KeyType
    ):  # type: (...) -> None
        """
        Saves a configuration file.

        :param path:
            Path of the configuration file to save.
        :param format:
            File format.

            Determined automatically from the file extension when not specified.
        :param root:
            Root key to save the file from.
        """
        from .configini import ConfigIni
        from .configjson import ConfigJson
        from .configyaml import ConfigYaml
        from .path import Path

        if format is None:
            _suffix = Path(path).suffix.lower()  # type: str
            if _suffix in (".ini", ):
                format = ConfigDatabase.FileFormat.INI  # noqa  ## Shadows built-in name 'format'
            elif _suffix in (".json", ):
                format = ConfigDatabase.FileFormat.JSON  # noqa  ## Shadows built-in name 'format'
            elif _suffix in (".yml", ".yaml", ):
                format = ConfigDatabase.FileFormat.YAML  # noqa  ## Shadows built-in name 'format'
            else:
                raise ValueError("%s: Unknown configuration file suffix" % path)

        if format == ConfigDatabase.FileFormat.INI:
            ConfigIni.savefile(path, root=root)
        elif format == ConfigDatabase.FileFormat.JSON:
            ConfigJson.savefile(path, root=root)
        elif format == ConfigDatabase.FileFormat.YAML:
            ConfigYaml.savefile(path, root=root)
        else:
            raise NotImplementedError(f"Unknown file format {format}")

    def set(
            self,  # type: ConfigDatabase
            key,  # type: KeyType
            data,  # type: typing.Any
            origin=None,  # type: OriginType
    ):  # type: (...) -> None
        """
        Sets a configuration value of any type.

        :param key:
            Configuration key.
        :param data:
            Configuration data.

            Can be a single value, a dictionary or a list.

            When a :class:`os.PathLike` is given, it is automatically converted in its string form with :func:`os.fspath()`.

            When ``None`` is given, it is equivalent to calling :meth:`remove()` for the given ``key``.
        :param origin:
            Origin of the configuration data: either a simple string, or the path of the configuration file it was defined in.

            Defaults to code location when not set.
        """
        self.debug("ConfigDatabase.set(key=%r, data=%r, origin=%r)", key, data, origin)

        self._root.set(subkey=key, data=data, origin=origin)

        self.show(logging.DEBUG)

    def remove(
            self,  # type: ConfigDatabase
            key,  # type: KeyType
    ):  # type: (...) -> None
        """
        Removes a configuration key (if exists).

        :param key: Configuration key to remove.
        """
        self.debug("ConfigDatabase.remove(key=%r)", key)

        # Search for the configuration node from the key, and call `remove()` on it when found.
        _node = self._root.get(subkey=key)  # type: typing.Optional[ConfigNode]
        if _node is not None:
            _node.remove()

        self.show(logging.DEBUG)

    def show(
            self,  # type: ConfigDatabase
            log_level,  # type: int
    ):  # type: (...) -> None
        """
        Displays the configuration database with the given log level.

        :param log_level: ``logging`` log level.
        """
        self._root.show(log_level)

    def getkeys(
            self,  # type: ConfigDatabase
    ):  # type: (...) -> typing.List[str]
        """
        Returns the list of keys.

        :return: Configuration keys.
        """
        return self._root.getkeys()

    def getnode(
            self,  # type: ConfigDatabase
            key,  # type: KeyType
    ):  # type: (...) -> typing.Optional[ConfigNode]
        """
        Retrieves the configuration node for the given key.

        :param key: Searched configuration key.
        :return: Configuration node when the configuration could be found, or ``None`` otherwise.
        """
        return self._root.get(key)

    @typing.overload
    def get(self, key):  # type: (KeyType) -> typing.Optional[typing.Any]
        ...

    @typing.overload
    def get(self, key, type):  # type: (KeyType, typing.Type[T]) -> typing.Optional[T]  # noqa  ## Shadows built-in name 'type'
        ...

    @typing.overload
    def get(self, key, type, default):  # type: (KeyType, typing.Type[T], None) -> typing.Optional[T]  # noqa  ## Shadows built-in name 'type'
        ...

    @typing.overload
    def get(self, key, type, default):  # type: (KeyType, typing.Type[T], typing.Union[str, os.PathLike[str], bool, int, float]) -> T  # noqa  ## Shadows built-in name 'type'
        ...

    def get(
            self,  # type: ConfigDatabase
            key,  # type: KeyType
            type=None,  # type: type  # noqa  ## Shadows built-in name 'type'
            default=None,  # type: typing.Any
    ):  # type: (...) -> typing.Any
        """
        Returns a configuration value of any type.

        :param key: Configuration key.
        :param type: Expected value type.
        :param default: Default value.
        :return: Configuration value if set, or default value if set, or ``None`` otherwise.
        """
        # Check input parameters:
        # - Convert default value from path-like to string.
        if isinstance(default, os.PathLike):
            default = os.fspath(default)
        # - Guess the expected type from the default value when applicable.
        if (type is None) and (default is not None):
            type = builtins.type(default)  # noqa  ## Shadows built-in name 'type'

        # Search for the configuration node from the key, and return its data when found.
        _node = self._root.get(key)  # type: typing.Optional[ConfigNode]
        if _node is not None:
            if (type is not None) and (_node.data is not None):
                return _node.cast(type=type)
            return _node.data

        # Return the default value when set.
        if default is not None:
            return default

        # Default to `None` otherwise.
        return None


__doc__ += """
.. py:attribute:: CONFIG_DB

    Main instance of :class:`ConfigDatabase`.
"""
CONFIG_DB = ConfigDatabase()  # type: ConfigDatabase
