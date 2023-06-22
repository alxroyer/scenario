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
Types and functions for text maagement.
"""

import typing


if typing.TYPE_CHECKING:
    #: Single string, or multiline string as a sequence of lines.
    AnyLongTextType = typing.Union[
        # Single string.
        str,
        # Sequence of lines.
        typing.Sequence[str],
    ]


def anylongtext2str(
        any_text,  # type: AnyLongTextType
):  # type: (...) -> str
    """
    Converts (if need) a :obj:`AnyLongTextType` to ``str``.

    :param any_text:  Single string, or multiline string
    :return: Simple string.
    """
    if isinstance(any_text, str):
        return any_text
    else:
        return "\n".join(any_text)
