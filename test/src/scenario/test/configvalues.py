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
Configuration value management.

Eases the way to prepare configuration values to pass on to scenario and campaign executions,
and to manipulate them.
"""

import enum
import typing

import scenario


if typing.TYPE_CHECKING:
    AnyConfigKeyType = typing.Union[
        enum.Enum,
        str,
    ]

    AnyConfigValueType = typing.Union[
        bool,
        enum.IntEnum,
        int,
        scenario.enum.StrEnum,
        scenario.Path,
        str,
    ]

    ConfigValuesType = typing.Dict[
        AnyConfigKeyType,
        typing.Optional[AnyConfigValueType],
    ]


def tostr(
        config_value,  # type: AnyConfigValueType
):  # type: (...) -> str
    # Ensure config value is of type `str`.
    if isinstance(config_value, bool):
        config_value = "1" if config_value else "0"
    if isinstance(config_value, scenario.Path):
        config_value = config_value.abspath
    if isinstance(config_value, enum.IntEnum):
        config_value = int(config_value)
    if not isinstance(config_value, str):
        config_value = str(config_value)
    return config_value


def getbool(
        configs,  # type: typing.Optional[ConfigValuesType]
        key,  # type: AnyConfigKeyType
        default,  # type: bool
):  # type: (...) -> bool
    if configs and (key in configs):
        # Use `scenario.ConfigNode`'s boolean conversion ability.
        _config_node = scenario.ConfigNode(parent=None, key="foo")  # type: scenario.ConfigNode
        _config_node.set(configs[key])
        return _config_node.cast(bool)
    return default


def getint(
        configs,  # type: typing.Optional[ConfigValuesType]
        key,  # type: AnyConfigKeyType
        default,  # type: int
):  # type: (...) -> int
    if configs and (key in configs):
        _value = configs[key]  # type: typing.Optional[AnyConfigValueType]
        assert not isinstance(_value, scenario.Path), f"Cannot convert {_value!r} to an integer value"
        if _value is not None:
            return int(_value)
    return default


def getstr(
        configs,  # type: typing.Optional[ConfigValuesType]
        key,  # type: AnyConfigKeyType
        default,  # type: str
):  # type: (...) -> str
    if configs and (key in configs):
        _value = configs[key]  # type: typing.Optional[AnyConfigValueType]
        if _value is not None:
            return tostr(_value)
    return default


def getpath(
        configs,  # type: typing.Optional[ConfigValuesType]
        key,  # type: AnyConfigKeyType
        default,  # type: scenario.Path
):  # type: (...) -> scenario.Path
    if configs and (key in configs):
        _value = configs[key]  # type: typing.Optional[AnyConfigValueType]
        if _value is not None:
            return scenario.Path(tostr(_value))
    return default
