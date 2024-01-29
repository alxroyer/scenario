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

if True:
    from ._enumutils import StrEnum as _StrEnumImpl  # `StrEnum` used for inheritance.
    from ._logger import Logger as _LoggerImpl  # `Logger` used for inheritance.
    from ._path import Path as _PathImpl  # `Path` imported once for performance concerns.
if typing.TYPE_CHECKING:
    from ._confignode import ConfigNode as _ConfigNodeType
    from ._configtypes import KeyType as _KeyType
    from ._configtypes import OriginType as _OriginType
    from ._configtypes import VarDataType as _VarDataType
    from ._path import AnyPathType as _AnyPathType


class ConfigDatabase(_LoggerImpl):
    """
    Configuration management.

    Instantiated once with the :data:`CONFIG_DB` singleton.

    This class loads a list of configuration files,
    and aggregates all configuration read in a single configuration tree.

    See the :ref:`configuration database <config-db>` documentation.
    """

    class FileFormat(_StrEnumImpl):
        """
        Configuration file formats.
        """
        #: INI configuration file format.
        INI = "INI"
        #: JSON-like configuration file format.
        JSON_DICT = "JSON / YAML"

    def __init__(self):  # type: (...) -> None
        """
        Initializes instance attributes and configures logging for the :class:`ConfigDatabase` class.
        """
        from ._confignode import ConfigNode
        from ._debugclasses import DebugClass

        _LoggerImpl.__init__(self, log_class=DebugClass.CONFIG_DATABASE)

        #: Configuration tree.
        self._root = ConfigNode(parent=None, key="")  # type: ConfigNode

    def loadfile(
            self,
            path,  # type: _AnyPathType
            format=None,  # type: ConfigDatabase.FileFormat  # noqa  ## Shadows built-in name 'format'
            root="",  # type: _KeyType
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
        from ._configini import ConfigIni
        from ._configjsondict import ConfigJsonDict
        from ._jsondictutils import JsonDict

        if format is None:
            if _PathImpl(path).suffix.lower() == ".ini":
                format = ConfigDatabase.FileFormat.INI  # noqa  ## Shadows built-in name 'format'
            elif JsonDict.isknwonsuffix(path):
                format = ConfigDatabase.FileFormat.JSON_DICT  # noqa  ## Shadows built-in name 'format'
            else:
                raise ValueError(f"{path}: Unknown configuration file suffix")

        if format == ConfigDatabase.FileFormat.INI:
            ConfigIni.loadfile(path, root=root)
        elif format == ConfigDatabase.FileFormat.JSON_DICT:
            ConfigJsonDict.loadfile(path, root=root)
        else:
            raise NotImplementedError(f"Unknown file format {format}")

    def savefile(
            self,
            path,  # type: _AnyPathType
            format=None,  # type: ConfigDatabase.FileFormat  # noqa  ## Shadows built-in name 'format'
            root="",  # type: _KeyType
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
        from ._configini import ConfigIni
        from ._configjsondict import ConfigJsonDict
        from ._jsondictutils import JsonDict

        if format is None:
            if _PathImpl(path).suffix.lower() == ".ini":
                format = ConfigDatabase.FileFormat.INI  # noqa  ## Shadows built-in name 'format'
            elif JsonDict.isknwonsuffix(path):
                format = ConfigDatabase.FileFormat.JSON_DICT  # noqa  ## Shadows built-in name 'format'
            else:
                raise ValueError("%s: Unknown configuration file suffix" % path)

        if format == ConfigDatabase.FileFormat.INI:
            ConfigIni.savefile(path, root=root)
        elif format == ConfigDatabase.FileFormat.JSON_DICT:
            ConfigJsonDict.savefile(path, root=root)
        else:
            raise NotImplementedError(f"Unknown file format {format}")

    def set(
            self,
            key,  # type: _KeyType
            data,  # type: typing.Any
            origin=None,  # type: _OriginType
    ):  # type: (...) -> None
        """
        Sets a configuration value of any type.

        :param key:
            Configuration key.
        :param data:
            Configuration data.

            Can be a single value, a dictionary or a list.

            When ``os.PathLike`` are given, values are automatically converted in their string form with ``os.fspath()``.

            When ``None`` is given, it is equivalent to calling :meth:`remove()` for the given ``key``.
        :param origin:
            Origin of the configuration data: either a simple string, or the path of the configuration file it was defined in.

            Defaults to code location when not set.
        """
        self.debug("ConfigDatabase.set(key=%r, data=%r, origin=%r)", key, data, origin)

        self._root.set(subkey=key, data=data, origin=origin)

        self.show(logging.DEBUG)

    def remove(
            self,
            key,  # type: _KeyType
    ):  # type: (...) -> None
        """
        Removes a configuration key (if exists).

        :param key: Configuration key to remove.
        """
        self.debug("ConfigDatabase.remove(key=%r)", key)

        # Search for the configuration node from the key, and call `remove()` on it when found.
        _node = self._root.get(subkey=key)  # type: typing.Optional[_ConfigNodeType]
        if _node is not None:
            _node.remove()

        self.show(logging.DEBUG)

    def show(
            self,
            log_level,  # type: int
    ):  # type: (...) -> None
        """
        Displays the configuration database with the given log level.

        :param log_level: ``logging`` log level.
        """
        self._root.show(log_level)

    def getkeys(
            self,
    ):  # type: (...) -> typing.List[str]
        """
        Returns the list of keys.

        :return: Configuration keys.
        """
        return self._root.getkeys()

    def getnode(
            self,
            key,  # type: _KeyType
    ):  # type: (...) -> typing.Optional[_ConfigNodeType]
        """
        Retrieves the configuration node for the given key.

        :param key: Searched configuration key.
        :return: Configuration node when the configuration could be found, or ``None`` otherwise.
        """
        return self._root.get(key)

    @typing.overload
    def get(self, key):  # type: (_KeyType) -> typing.Optional[typing.Any]
        ...

    @typing.overload
    def get(self, key, type):  # type: (_KeyType, typing.Type[_VarDataType]) -> typing.Optional[_VarDataType]  # noqa  ## Shadows built-in name 'type'
        ...

    @typing.overload
    def get(self, key, type, default):  # type: (_KeyType, typing.Type[_VarDataType], None) -> typing.Optional[_VarDataType]  # noqa  ## Shadows built-in name 'type'
        ...

    @typing.overload
    def get(self, key, type, default):  # type: (_KeyType, typing.Type[_VarDataType], typing.Union[str, os.PathLike[str], bool, int, float]) -> _VarDataType  # noqa  ## Shadows built-in name 'type'
        ...

    def get(
            self,
            key,  # type: _KeyType
            type=None,  # type: type  # noqa  ## Shadows built-in name 'type'
            default=None,  # type: typing.Any
    ):  # type: (...) -> typing.Optional[typing.Any]
        """
        Returns a configuration value of any type.

        :param key:
            Configuration key.
        :param type:
            Expected value type.
        :param default:
            Default value.

            Not saved in the database.

            if ``os.PathLike``, converted to ``str`` with ``os.fspath()`` called on it.
        :return:
            Configuration value if set, or default value if set, or ``None`` otherwise.
        """
        from ._confignode import ConfigNode

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


#: Main instance of :class:`ConfigDatabase`.
#:
#: Also available as :attr:`._fastpath.FastPath.config_db`.
#: Please prefer the latter instead of using local imports of this module.
CONFIG_DB = ConfigDatabase()  # type: ConfigDatabase
