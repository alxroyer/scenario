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
``enum`` augmentations.
"""

import enum
import typing


class StrEnum(str, enum.Enum):
    """
    String enum.
    """

    def __str__(self):  # type: () -> str
        """
        Returns the enum value (as ``enum.IntEnum.__int__()`` does) instead of a qualified enum name.

        :return: Enum value.
        """
        assert isinstance(self.value, str)
        return self.value


def enum2str(
        value,  # type: typing.Union[enum.Enum, str]
):  # type: (...) -> str
    """
    Ensures a string value from a string/enum union.

    :param value: String already, or string enum.
    :return: String.

    .. note::
        ``value`` if given as an enum is basically expected to be a string enum.
        Whether this is not the case, the value is converted as a string anyways.
    """
    if isinstance(value, enum.Enum):
        return str(value.value)
    return value


def isin(
        value,  # type: typing.Any
        enum_type,  # type: typing.Type[enum.Enum]
):  # type: (...) -> bool
    """
    Determines whether ``value`` is part of ``enum_type``.

    :param value: Enum or enum value to check in ``enum_type``.
    :param enum_type: Enum definition to check ``value`` in.
    :return: ``True`` if ``value`` in ``enum_type``, ``False`` otherwise.
    """
    for _enum in enum_type:  # type: enum.Enum
        if (value == _enum) or (value == _enum.value):
            return True
    return False
