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

import enum
import typing

import scenario

if typing.TYPE_CHECKING:
    # `NotSetType` used in method signatures.
    # Type declared for type checking only.
    from .notset import NotSetType


class ErrorExpectations:
    def __init__(
            self,
            message,  # type: str
            cls=None,  # type: typing.Optional[typing.Union[typing.Type[scenario.ExceptionError], typing.Type[scenario.KnownIssue]]]
            exception_type=None,  # type: typing.Optional[str]
            level=None,  # type: typing.Optional[typing.Union[scenario.AnyIssueLevelType, NotSetType]]
            id=None,  # type: typing.Optional[typing.Union[str, NotSetType]]  # noqa  ## Shadows built-in name 'id'
            url=None,  # type: typing.Optional[typing.Union[str, NotSetType]]
            location=None,  # type: typing.Optional[str]
    ):  # type: (...) -> None
        assert (exception_type is None) or (cls is scenario.ExceptionError)
        assert (id is None) or (cls is scenario.KnownIssue)

        self.cls = cls  # type: typing.Optional[typing.Union[typing.Type[scenario.ExceptionError], typing.Type[scenario.KnownIssue]]]
        self.error_type = exception_type  # type: typing.Optional[str]
        if (self.error_type is None) and (self.cls is scenario.KnownIssue):
            self.error_type = "known-issue"
        self.level = level  # type: typing.Optional[typing.Union[scenario.AnyIssueLevelType, NotSetType]]
        self.id = id  # type: typing.Optional[typing.Union[str, NotSetType]]
        self.url = url  # type: typing.Optional[typing.Union[str, NotSetType]]
        self.message = message  # type: str
        self.location = location  # type: typing.Optional[str]

    def __repr__(self):  # type: (...) -> str
        return f"<ErrorExpectations {self.error_type!r} {self.message!r}>"

    def loggingtext(self):  # type: (...) -> str
        """
        Returns a logging line for the error as :meth:`scenario.TestError.__str__()` and subclasses would.
        """
        _text = ""  # type: str
        if self.cls is not scenario.KnownIssue:
            _text += f"{self.error_type}: {self.message}"
        else:
            _text += "Issue"
            assert self.level is not None, f"Please provide issue level or NOT_SET for {self!r}"
            if isinstance(self.level, (int, enum.IntEnum)):
                _text += f"({scenario.IssueLevel.getdesc(self.level)})"
            assert self.id is not None, f"Please provide issue id or NOT_SET for {self!r}"
            if isinstance(self.id, str):
                _text += f" {self.id}"
            _text += f"! {self.message}"
        if self.location is not None:
            _text += f" ({self.location})"
        return _text
