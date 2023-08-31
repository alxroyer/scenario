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
Set utils.

Sets being lists with unique items.
"""

import abc
import typing

if typing.TYPE_CHECKING:
    from ._typingutils import VarItemType as _VarItemType


if typing.TYPE_CHECKING:
    #: Generic type for an ordered set of unique items.
    #:
    #: .. warning:: Imperfect typing, in as much as the `unique items` aspect is not meant, but the `ordered` primes.
    OrderedSetType = typing.Sequence

    #: Variable key function.
    VarKeyFunctionType = typing.Callable[[_VarItemType], typing.Any]


class OrderedSetHelper(abc.ABC):
    """
    Helper class for ordered sets.
    """

    @staticmethod
    def build(
            unordered,  # type: typing.Iterable[_VarItemType]
            *,
            key,  # type: VarKeyFunctionType[_VarItemType]
    ):  # type: (...) -> OrderedSetType[_VarItemType]
        """
        Sorts and ensures unique items from an unordered list.

        :param unordered: Unordered list of items, possibly with duplicates.
        :param key: Key function to use for sorting items.
        :return: Resulting ordered set.
        """
        _ordered_set = list(set(unordered))  # type: typing.List[_VarItemType]
        _ordered_set.sort(key=key)
        return _ordered_set

    @staticmethod
    def merge(
            *sets,  # type: typing.Iterable[_VarItemType]
            key,  # type: VarKeyFunctionType[_VarItemType]
    ):  # type: (...) -> OrderedSetType[_VarItemType]
        """
        Merges several unordered sets as a single ordered set.

        :param sets: Unordered lists of items, possibly with duplicates each.
        :param key: Key function to use for sorting items.
        :return: Resulting ordered set.
        """
        _unordered = []  # type: typing.List[_VarItemType]
        for _set in sets:  # type: typing.Iterable[_VarItemType]
            _unordered.extend(_set)
        return OrderedSetHelper.build(_unordered, key=key)
