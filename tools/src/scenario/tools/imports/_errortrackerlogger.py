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

import logging
import typing

import scenario


class ErrorTrackerLogger(scenario.Logger):

    #: Errors tracked.
    errors = []  # type: typing.List[str]

    def __init__(
            self,
            location,  # type: str
    ):  # type: (...) -> None
        scenario.Logger.__init__(self, location)

        self.__location = location  # type: str

    def _log(
            self,
            level,  # type: int
            msg,  # type: str
            args,  # type: typing.Tuple[typing.Any, ...]
            **kwargs  # type: typing.Any
    ):  # type: (...) -> None
        """
        Redirect logging to `scenario.logging`.
        Count error messages by the way.
        """
        _fmt = self.__location + ("" if msg.startswith(("%s:", "%d:")) else " ") + msg  # type: str
        scenario.logging.log(level, _fmt, *args, **kwargs)

        if level >= logging.ERROR:
            ErrorTrackerLogger.errors.append(_fmt % args)
