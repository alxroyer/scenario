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
    from ._typeutils import VarItemType as _VarItemType


if typing.TYPE_CHECKING:
    #: Generic type for an ordered set of unique items.
    #:
    #: .. warning:: Imperfect typing, in as much as the `unique items` aspect is not meant, but the `ordered` primes.
    OrderedSetType = typing.Sequence

    #: Variable key function.
    #:
    #: Used to sort lists of items.
    VarKeyFunctionType = typing.Callable[[_VarItemType], typing.Any]


def orderedset(
        *unordered,  # type: typing.Iterable[_VarItemType]
        key,  # type: VarKeyFunctionType[_VarItemType]
):  # type: (...) -> OrderedSetType[_VarItemType]
    """
    Sorts and ensures unique items from unordered list(s).

    :param unordered: Unordered list(s) of items, possibly with duplicates.
    :param key: Key function to use for sorting items.
    :return: Resulting ordered set.
    """
    # Sum up all `unordered` items in a single list.
    _ordered_set = []  # type: typing.List[_VarItemType]
    for _unordered in unordered:  # type: typing.Iterable[_VarItemType]
        _ordered_set.extend(_unordered)

    # Ensure unique items.
    _ordered_set = list(set(_ordered_set))

    # Sort remaining items.
    _ordered_set.sort(key=key)

    return _ordered_set
