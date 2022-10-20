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


class LogProcessor:

    def __init__(
            self,
            encoding=None,  # type: str
    ):  # type: (...) -> None
        self.encoding = encoding or "utf-8"  # type: str

    def tobytes(
            self,
            string,  # type: typing.Union[str, bytes]
            encoding=None,  # type: str
    ):  # type: (...) -> bytes
        if isinstance(string, bytes):
            return string
        else:
            return string.encode(encoding or self.encoding)

    def tostr(
            self,
            string,  # type: typing.Union[str, bytes]
            encoding=None,  # type: str
    ):  # type: (...) -> str
        if isinstance(string, str):
            return string
        else:
            return string.decode(encoding or self.encoding)

    def toanystr(
            self,
            string,  # type: typing.Union[str, bytes]
            string_type,  # type: typing.Type[typing.AnyStr]
    ):  # type: (...) -> typing.AnyStr
        # Note: `mypy` (as of 0.910) seems not to compute all typing constraints with the `AnyStr` variable type.
        #       Let's use `typing.cast(Any)` to work around it.
        _anystr = string_type()  # type: typing.AnyStr
        if string_type is str:
            # mypy: "Incompatible types in assignment (expression has type "str", variable has type "bytes")"
            # However, in as much as `string_type` is `str`, `_anystr`, of type `AnyStr`, should be understood to be of type `str` only, not `bytes`.
            _anystr = typing.cast(typing.Any, self.tostr(string))
        elif string_type is bytes:
            # mypy: "Incompatible types in assignment (expression has type "bytes", variable has type "str")"
            # However, in as much as `string_type` is `bytes`, `_anystr`, of type `AnyStr`, should be understood to be of type `bytes` only, not `str`.
            _anystr = typing.cast(typing.Any, self.tobytes(string))
        else:
            raise ValueError(f"Invalid type {string_type!r}")
        return _anystr
