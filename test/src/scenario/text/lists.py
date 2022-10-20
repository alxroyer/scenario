# -*- coding: utf-8 -*-

# Copyright 2020-2022 Alexis Royer <https://github.com/Alexis-ROYER/scenario>
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

import typing


def comalist(
        iterable,  # type: typing.Iterable[typing.Any]
        final_and=True,  # type: bool
        quotes=False,  # type: bool
        when_empty="(empty set)",  # type: str
):  # type: (...) -> str
    if not isinstance(iterable, list):
        iterable = list(iterable)
    if quotes:
        iterable = [f"'{_item}'" for _item in iterable]
    _len = len(iterable)  # type: int

    if _len < 1:
        return when_empty
    elif _len <= 1:
        return str(iterable[0])
    else:
        return "".join([
            # Join first items with ', '.
            ", ".join([f"'{_item}'" for _item in iterable[:-1]]),
            # Final 'and'.
            " and " if final_and else ", ",
            # Last term.
            str(iterable[-1]),
        ])
