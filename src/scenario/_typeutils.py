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
Type definitions to help type hints.
"""

import typing


if typing.TYPE_CHECKING:
    #: Comparable type.
    #:
    #: Declared as a ``typing.TypeVar`` so that every comparable parameter within the same function call is of the same type.
    VarComparableType = typing.TypeVar("VarComparableType", int, float, str)

    #: Type representing a type, or a set of types.
    TypeOrTypesType = typing.Optional[typing.Union[type, typing.Sequence[type]]]

    #: General item type.
    VarItemType = typing.TypeVar("VarItemType")