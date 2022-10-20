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

"""
Logging statistics.
"""

import typing

# `StrEnum` used for inheritance.
from .enumutils import StrEnum
# `Logger` used for inheritance.
from .logger import Logger


class LogStats(Logger):
    """
    Logging statistics management.
    """

    class CallType(StrEnum):
        """
        Logging call type.
        """
        #: :meth:`.logger.Logger.isdebugenabled()` call.
        IS_DEBUG_ENABLED = "isdebugenabled"
        #: :meth:`.logger.Logger.debug()` call.
        DEBUG = "debug"

    class LogClassStats:
        """
        Log class statistics entry.
        """

        def __init__(
                self,
                log_class,  # type: str
        ):  # type: (...) -> None
            """
            Initializes an empty log class statitstics entry.

            :param log_class: Log class.
            """
            #: Log class.
            self.log_class = log_class  # type: str
            #: Number of :meth:`.logger.Logger.isdebugenabled()` calls.
            self.is_debug_enabled = 0  # type: int
            #: Number of :meth:`.logger.Logger.debug()` calls.
            self.debug = 0  # type: int

    def __init__(self):  # type: (...) -> None
        """
        Initializes the dedicated logger, and an empty registry of log class statistics entries.
        """
        from .debug import DebugClass

        Logger.__init__(self, log_class=DebugClass.LOG_STATS)

        #: Log class statistics entries.
        self._log_class_stats = {}  # type: typing.Dict[str, LogStats.LogClassStats]

    def call(
            self,
            log_class,  # type: str
            call_type,  # type: LogStats.CallType
    ):  # type: (...) -> None
        """
        Register a call for the given ``call_type``.

        :param log_class: Log class.
        :param call_type: Call type.
        """
        if log_class in self._log_class_stats:
            _log_class_stats = self._log_class_stats[log_class]  # type: LogStats.LogClassStats
        else:
            _log_class_stats = LogStats.LogClassStats(log_class)
            self._log_class_stats[log_class] = _log_class_stats

        if call_type == LogStats.CallType.IS_DEBUG_ENABLED:
            _log_class_stats.is_debug_enabled += 1
        if call_type == LogStats.CallType.DEBUG:
            _log_class_stats.debug += 1

    def debugstats(self):  # type: (...) -> None
        """
        Debug information from the log class statistics entries.
        """
        _log_classes = []  # type: typing.List[str]
        for _log_class in self._log_class_stats:  # type: str
            _log_classes.append(_log_class)
        for _log_class in _log_classes:
            _log_class_stats = self._log_class_stats[_log_class]  # type: LogStats.LogClassStats
            if _log_class:
                self._logger.debug("%s:" % _log_class)
            else:
                self._logger.debug("Main logger:")
            self._logger.debug("  is_debug_enabled: %d" % _log_class_stats.is_debug_enabled)
            self._logger.debug("  debug:            %d" % _log_class_stats.debug)


__doc__ += """
.. py:attribute:: LOG_STATS

    Main instance of :class:`LogStats`.
"""
LOG_STATS = LogStats()  # type: LogStats
