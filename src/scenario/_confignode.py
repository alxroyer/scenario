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
Configuration node management.
"""

import enum
import os
import re
import typing

if True:
    from ._debugutils import saferepr as _saferepr  # `saferepr()` imported once for performance concerns.
    from ._enumutils import enum2str as _enum2str  # `enum2str()` imported once for performance concerns.
    from ._fastpath import FAST_PATH as _FAST_PATH  # `FAST_PATH` imported once for performance concerns.
    from ._path import Path as _PathImpl  # `Path` imported once for performance concerns.
if typing.TYPE_CHECKING:
    from ._configtypes import KeyType as _KeyType
    from ._configtypes import OriginType as _OriginType
    from ._configtypes import VarDataType as _VarDataType
    from ._path import Path as _PathType


class ConfigNode:
    """
    Considering that configurations are organized in a tree structure,
    this class represents a node of the tree,
    with either:

    - a final item,
    - a dictionary of :class:`ConfigNode`,
    - or a list of :class:`ConfigNode`.
    """

    def __init__(
            self,
            parent,  # type: typing.Optional[ConfigNode]
            key,  # type: str
    ):  # (...) -> None
        """
        :param parent: Parent node. ``None`` for the root node.
        :param key: Key of the configuration node.
        """
        #: Parent node.
        #:
        #: ``None`` for the root node, as well as for removed nodes.
        self.parent = parent

        #: Configuration key.
        self.key = key  # type: str

        #: Configuration data.
        #:
        #: Either:
        #:
        #: - a final item,
        #: - a dictionary of :class:`ConfigNode`,
        #: - or a list of :class:`ConfigNode`.
        self._data = None  # type: typing.Any

        #: Origins of the configuration value: either a string or the path of the configuration file it was defined in.
        self.origins = []  # type: typing.List[_OriginType]

    def __repr__(self):  # type: () -> str
        """
        Canonical string representation.

        Gives the configuration key and type of data.
        """
        from ._reflection import qualname

        _repr = f"<{qualname(type(self))}"  # type: str
        _repr += f" key='{self.key}'"
        if isinstance(self._data, dict):
            _repr += " data={...}"
        elif isinstance(self._data, list):
            _repr += " data=[...]"
        elif self._data is not None:
            _repr += f" data={self._data!r}"
        _repr += ">"
        return _repr

    def set(
            self,
            data,  # type: typing.Any
            subkey=None,  # type: _KeyType
            origin=None,  # type: _OriginType
    ):  # type: (...) -> None
        """
        Sets configuration data.

        :param data:
            Configuration data: dictionary, list or single value.

            When ``None`` is given and no ``subkey`` is provided, it is equivalent to calling :meth:`remove()` on the current node.
        :param subkey:
            Relative key from this node to store the data in.
        :param origin:
            Origin of the configuration data: either a simple string, or the path of the configuration file it was defined in.
            Defaults to code location when not set.
        """
        # Redirect to `remove()` when `None` is set.
        if (not subkey) and (data is None):
            return self.remove()

        with _FAST_PATH.config_db.pushindentation():
            _FAST_PATH.config_db.debug("%r: set(subkey=%r, data=%r, origin=%r)", self, subkey, data, origin)

            # Default ``origin`` to code location.
            if origin is None:
                origin = _FAST_PATH.execution_locations.fromcurrentstack(limit=1, fqn=True)[0].tolongstring()

            # When a sub-key is given, set the data on the sub-node described by the sub-key.
            if subkey:
                # Retrieve or create the target sub-node.
                _target_node = self._getsubnode(subkey, create_missing=True, origin=origin)  # type: typing.Optional[ConfigNode]
                _FAST_PATH.config_db.debug("%r: _target_node = %r", self, _target_node)
                assert _target_node, "Sub-node should have been created"
                # Set the data on it.
                _target_node.set(data=data, origin=origin)

            # Store the data directly in this node otherwise.
            else:
                # Dictionary data.
                if isinstance(data, dict):
                    # Instanciate / check this node manages a dictionary of sub-nodes.
                    if self._data is None:
                        self._setdata({})
                    if not isinstance(self._data, dict):
                        raise ValueError(self.errmsg(f"Bad dict data {_saferepr(data)} for a non-dict configuration node", origin=origin))
                    # Use recursive calls with the ``subkey`` parameter set for each field of the input dictionary.
                    for _field_name in data:  # type: str
                        self.set(subkey=_field_name, data=data[_field_name], origin=origin)

                # List data (or enum definitions).
                elif isinstance(data, (list, enum.EnumMeta)):
                    # Instanciate / check this node manages a list of sub-nodes.
                    if self._data is None:
                        self._setdata([])
                    if not isinstance(self._data, list):
                        raise ValueError(self.errmsg(f"Bad list data {_saferepr(data)} for a non-list configuration node", origin=origin))
                    # Add sub-nodes for each item of the input list.
                    for _index in range(len(data)):  # type: int
                        self._data.append(ConfigNode(parent=self, key=f"{self.key}[{len(self._data)}]"))
                        # Apply `list()` on `data` so that enum definitions can be indexed.
                        self._data[-1].set(list(data)[_index], origin=origin)

                # Final value.
                else:
                    # Check this node does not already handle sub-nodes.
                    if isinstance(self._data, dict):
                        raise ValueError(self.errmsg(f"Bad final data {data!r} for a dictionary node", origin=origin))
                    if isinstance(self._data, list):
                        raise ValueError(self.errmsg(f"Bad final data {data!r} for a list node", origin=origin))
                    # Store the data.
                    self._setdata(data)

                # Ensure origin is set.
                if origin and (origin not in self.origins):
                    self.origins.append(origin)

    def _setdata(
            self,
            data,  # type: typing.Any
    ):  # type: (...) -> None
        """
        Sets the node's data,
        applying conversions when applicable,
        and displays debug info on the data stored.

        :param data: Node's data being set.
        """
        # Apply automatic conversions:
        # - path-likes to strings,
        if isinstance(data, os.PathLike):
            self._data = os.fspath(data)
        # - `IntEnum` to integers,
        elif isinstance(data, enum.IntEnum):
            self._data = data.value
        # - other enums to strings,
        elif isinstance(data, enum.Enum):
            self._data = str(data.value)
        # - store the data as is otherwise.
        else:
            self._data = data

        # Debug the new data being stored.
        _FAST_PATH.config_db.debug("%r: data = %r", self, data)

        # When the `scenario` TIMEZONE configuration is modified, invalidate the related cache value.
        if self.key == _FAST_PATH.scenario_config.Key.TIMEZONE:
            _FAST_PATH.scenario_config.invalidatetimezonecache()

    def remove(self):  # type: (...) -> None
        """
        Removes the node from its parent.

        Note: Does nothing on the root node (no parent for the root node, by definition).
        """
        if self.parent:
            # Remove the node from its parent.
            _parent_data = getattr(self.parent, "_data")  # type: typing.Any
            if isinstance(_parent_data, dict):
                for _field_name in list(_parent_data.keys()):  # type: str
                    if _parent_data[_field_name] == self:
                        del _parent_data[_field_name]
            if isinstance(_parent_data, list):
                _parent_data.remove(self)

            # Debug the configuration key removal.
            _FAST_PATH.config_db.debug("%r: removed", self)

            # Check whether the parent node should be removed as a consequence.
            if _parent_data in ([], {}):
                self.parent.remove()

            # Eventuelly clear the parent node reference.
            self.parent = None

    def show(
            self,
            log_level,  # type: int
    ):  # type: (...) -> None
        """
        Displays the configuration database with the given log level.

        :param log_level: ``logging`` log level.
        """
        if isinstance(self._data, dict):
            if self.key:
                _FAST_PATH.config_db.log(
                    log_level, f"{self.key}:",
                    extra={_FAST_PATH.config_db.Extra.CLASS_LOGGER_INDENTATION: True},
                )
            for _direct_subkey in sorted(self._data.keys()):  # type: str
                with _FAST_PATH.config_db.pushindentation("  "):
                    # Recursive call.
                    self._data[_direct_subkey].show(log_level)
        elif isinstance(self._data, list):
            for _index in range(len(self._data)):  # type: int
                # Recursive call.
                self._data[_index].show(log_level)
        else:
            _FAST_PATH.config_db.log(
                log_level, f"{self.key}: {self._data!r}  # from {', '.join(str(_origin) for _origin in self.origins)}",
                extra={_FAST_PATH.config_db.Extra.CLASS_LOGGER_INDENTATION: True},
            )

    def getkeys(self):  # type: (...) -> typing.List[str]
        """
        Retrieves the list of full keys from this node.

        :return: List of full keys.
        """
        from ._configkey import ConfigKey

        return [ConfigKey.join(self.key, _subkey) for _subkey in self.getsubkeys()]

    def getsubkeys(self):  # type: (...) -> typing.List[str]
        """
        Retrieves the list of sub-keys from this node.

        :return: List of sub-keys.
        """
        from ._configkey import ConfigKey

        _subkeys = []  # type: typing.List[str]
        if isinstance(self._data, dict):
            for _direct_subkey in self._data:  # type: str
                _subnode = self._data[_direct_subkey]  # type: ConfigNode
                for _subsubkey in _subnode.getsubkeys():  # type: str
                    _subkeys.append(ConfigKey.join(_direct_subkey, _subsubkey))
        elif isinstance(self._data, list):
            for _index in range(len(self._data)):  # type: int
                _subnode = self._data[_index]  # Type already declared above.
                for _subsubkey in _subnode.getsubkeys():  # Type already declared above.
                    _subkeys.append(ConfigKey.join(f"[{_index}]", _subsubkey))
        else:
            _subkeys.append("")
        return _subkeys

    def get(
            self,
            subkey,  # type: _KeyType
    ):  # type: (...) -> typing.Optional[ConfigNode]
        """
        Finds a sub-node from this node.

        :param subkey: Sub-key from this node.
        :return: Sub-node if found, ``None`` otherwise.
        """
        return self._getsubnode(subkey, create_missing=False)

    def _getsubnode(
            self,
            subkey,  # type: _KeyType
            create_missing=False,  # type: bool
            origin=None,  # type: _OriginType
    ):  # type: (...) -> typing.Optional[ConfigNode]
        """
        Finds or creates a sub-node from this node.

        :param subkey: Sub-key from this node.
        :param create_missing: ``True`` to create missing sub-nodes.
        :param origin: Origin info to set for each sub-node walked through or created, starting from this one.
        :return: Sub-node if found, ``None`` otherwise.
        """
        from ._configkey import ConfigKey

        if create_missing:
            _FAST_PATH.config_db.debug("%r: _getsubnode(subkey=%r, create_missing=%r, origin=%r)", self, subkey, create_missing, origin)

        # Set origin info on the current node.
        if origin and (origin not in self.origins):
            self.origins.append(origin)

        # When the sub-key is empty, it means we have reached the sub-node we are looking for.
        subkey = _enum2str(subkey)
        if not subkey:
            return self

        # Parse the sub-key.
        _sep_index = min(filter(
            # Filter-out -1 and 0 values.
            lambda index: index > 0,
            [
                # Search for a '.' or '[' character from the second character of `subkey`.
                subkey.find(".", 1),
                subkey.find("[", 1),
                # Default to the length of `subkey`.
                # Memo:
                #  `len(sub-key) > 0` since `subkey` is not empty at this point.
                #  So we will always have the `len(sub-key)` value left at least for the `min()` function to work on.
                len(subkey),
            ],
        ))  # type: int
        _first = subkey[:_sep_index]  # type: str
        _sep = subkey[_sep_index:_sep_index+1]  # type: str
        _remaining = subkey[_sep_index:] if (_sep == "[") else subkey[_sep_index+1:]  # type: str

        # Depending on the sub-key, let's search for a sub-node.
        _subnode = None  # type: typing.Optional[ConfigNode]
        _errmsg_start = self.errmsg(f"Bad sub-key {subkey!r}: ", origin)  # type: str

        # List index selector.
        _match = re.match(r"^\[?(-?[0-9]+)]?$", _first)  # type: typing.Optional[typing.Match[str]]
        if _match:
            if self._data is None:
                self._setdata([])
            if not isinstance(self._data, list):
                raise IndexError(_errmsg_start + f"Cannot index a non-list node with {_first!r}")
            _index = int(_match.group(1))  # type: int
            if create_missing and (_index == len(self._data)):
                self._data.append(ConfigNode(parent=self, key=ConfigKey.join(self.key, f"[{_index}]")))
                _FAST_PATH.config_db.debug("  New %r", self._data[-1])
            try:
                _subnode = self._data[_index]
            except IndexError:
                if create_missing:
                    raise IndexError(_errmsg_start + f"Cannot create list item from index {_first!r}")

        # Dictionary field name selector.
        else:
            # Create the member dictionary data when applicable.
            if (self._data is None) and create_missing:
                self._setdata({})
            if self._data is not None:
                # Find the direct sub-node in the member dictionary.
                if not isinstance(self._data, dict):
                    raise IndexError(
                        _errmsg_start + f"Cannot index a non-dictionary node with {_first!r}, data is {_saferepr(self._data)} (origin: {self.origin})"
                    )
                if _first in self._data:
                    _subnode = self._data[_first]
                # Create it when missing and applicable.
                elif create_missing:
                    _subnode = self._data[_first] = ConfigNode(parent=self, key=ConfigKey.join(self.key, _first))
                    _FAST_PATH.config_db.debug("  New %r", _subnode)

        # Walk through the sub-node.
        if _subnode:
            with _FAST_PATH.config_db.pushindentation():
                return _subnode._getsubnode(
                    subkey=_remaining,
                    create_missing=create_missing,
                    origin=origin,
                )
        return None

    @property
    def data(self):  # type: () -> typing.Any
        """
        Retrieves the node data as a JSON-like structure, or value as given.

        :return: JSON-like structure or value.
        """
        # JSON dictionary.
        if isinstance(self._data, dict):
            _dict = {}  # type: typing.Dict[str, typing.Any]
            for _direct_subkey in self._data:  # type: str
                _dict[_direct_subkey] = self._data[_direct_subkey].data
            return _dict

        # JSON list.
        if isinstance(self._data, list):
            _list = []  # type: typing.List[typing.Any]
            for _index in range(len(self._data)):  # type: int
                _list.append(self._data[_index].data)
            return _list

        # Final value.
        return self._data

    def cast(
            self,
            type,  # type: typing.Type[_VarDataType]  # noqa  ## Shadows built-in name 'type'
    ):  # type: (...) -> _VarDataType
        """
        Ensures the retrieval of the node data with the expected type.

        :param type: Expected type.
        :return: JSON-like structure or value of the expected type.

        When the configuration data is not of the expected type, a ``ValueError`` is raised.
        """
        from ._reflection import qualname

        def _castreturntype(value):  # type: (typing.Any) -> _VarDataType
            """
            Avoids using ``# type: ignore`` pragmas every time this :meth:`ConfigNode.cast()` method returns a value.
            """
            _value = value  # type: _VarDataType
            return _value

        # Dictionary.
        if type is dict:
            if not isinstance(self._data, dict):
                raise ValueError(self.errmsg(f"{self._data!r} not a valid dictionary"))
            # Call the property above that will build a JSON dictionary.
            return _castreturntype(self.data)

        # Dictionary.
        if type is list:
            if not isinstance(self._data, list):
                raise ValueError(self.errmsg(f"{self._data!r} not a valid list"))
            # Call the property above that will build a JSON list.
            return _castreturntype(self.data)

        # Boolean type expected.
        if type is bool:
            if isinstance(self._data, bool):
                # Direct bool value.
                return _castreturntype(self._data)
            if isinstance(self._data, (int, float)):
                # Number to bool.
                return _castreturntype(bool(self._data))
            if isinstance(self._data, str):
                # String to bool.
                if self._data.strip().lower() in ["true", "yes", "y", "1"]:
                    return _castreturntype(True)
                if self._data.strip().lower() in ["false", "no", "n", "0"]:
                    return _castreturntype(False)
                # Default: string to int to bool.
                try:
                    return _castreturntype(bool(int(self._data)))
                except ValueError:
                    pass
            raise ValueError(self.errmsg(f"{self._data!r} not a valid boolean value"))

        # Other expected type.
        try:
            # Convert the configuration value in the ``type`` type.
            return _castreturntype(typing.cast(typing.Any, type)(self._data))
        except ValueError:
            raise ValueError(self.errmsg(f"{self._data!r} not a valid {qualname(type)} value"))

    @property
    def origin(self):  # type: () -> _OriginType
        """
        Representative origin for the current node.
        """
        if self.origins:
            return self.origins[-1]
        return ""

    @property
    def source_file(self):  # type: () -> typing.Optional[_PathType]
        """
        Source configuration file for the current node.

        ``None`` when the origin of the configuration node is not a file.

        .. seealso:: :attr:`origin`.
        """
        try:
            _path = _PathImpl(self.origin)  # type: _PathType
            if _path.is_file():
                return _path
        except:  # noqa  ## Too broad exception clause.
            pass
        return None

    def errmsg(
            self,
            msg,  # type: str
            origin=None,  # type: _OriginType
    ):  # type: (...) -> str
        """
        Builds an error message giving the context of the current node.

        :param msg: Detailed message.
        :param origin: Specific origin info. Use of :attr:`origins` by default.
        :return: Error message.
        """
        _err_msg = ""  # type: str
        if (origin is None) and self.origins:
            origin = self.origins[-1]
        if origin:
            _err_msg += f"{origin}:"
        _err_msg += f"'{self.key}': "
        _err_msg += msg
        return _err_msg
