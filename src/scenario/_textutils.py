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

import re
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

    :param any_text: Single string, or multiline string.
    :return: Simple string.
    """
    from ._assertions import Assertions

    # Convert `any_text` as a modifiable list of lines.
    if isinstance(any_text, str):
        any_text = any_text.splitlines()
    any_text = list(any_text)

    # Remove empty heading and tailing lines.
    while any_text and (not any_text[0].strip()):
        any_text.pop(0)
    while any_text and (not any_text[-1].strip()):
        any_text.pop()

    # Determine the left blank indentation to remove from non-empty lines.
    _left_blank_indentation = min([
        # Compute the number of leading spaces or tabs.
        len(Assertions.assertisnotnone(re.search(r"^([ \t]*)", _line)).group(1))
        # Iterate over `any_text` lines...
        for _line in filter(
            # ...except empty lines.
            lambda line: True if line.strip() else False,
            any_text,
        )
    ])  # type: int

    # Eventually (re)join the lines with '\n' characters...
    return "\n".join(map(
        # ...by removing the left blank indentation computed just before.
        lambda line: line[_left_blank_indentation:],
        any_text,
    ))
