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
Extra debugging loggers.
"""

import time
import typing

# `DelayedStr` used in method signatures.
from .debugutils import DelayedStr
# `Logger` used for instanciation.
from .logger import Logger


class ExecTimesLogger(Logger):
    """
    Issue#65 logger.
    """

    def __init__(
            self,
            context,  # type: str
    ):  # type: (...) -> None
        """
        Creates an execution times logger for the given context.

        :param context: Context, usually a function/method name.
        """
        from .debugclasses import DebugClass

        Logger.__init__(self, DebugClass.EXECUTION_TIMES)

        #: Debug logger context. Usually a function/method name.
        self.context = context  # type: str
        #: Starting time for this debug logger.
        self.t0 = time.time()  # type: float
        #: Last tick time.
        self._last_tick = self.t0  # type: float

    def tick(
            self,
            message,  # type: typing.Union[str, DelayedStr]
    ):  # type: (...) -> None
        """
        Logs intermediate time information.

        :param message: Object of this tick.
        """
        from .datetimeutils import f2strduration
        from .debugutils import CallbackStr

        _current_time = time.time()  # type: float
        self.debug(
            "%s: %s: %s (+%s)",
            self.context, message,
            CallbackStr(f2strduration, _current_time - self.t0),
            CallbackStr(f2strduration, _current_time - self._last_tick),
        )
        self._last_tick = _current_time

    def finish(self):  # type: (...) -> None
        """
        Terminates logging for the given context.
        """
        from .datetimeutils import f2strduration
        from .debugutils import CallbackStr

        _current_time = time.time()  # type: float
        self.debug(
            "%s: Total time: %s (+%s)",
            self.context,
            CallbackStr(f2strduration, _current_time - self.t0),
            CallbackStr(f2strduration, _current_time - self._last_tick),
        )
