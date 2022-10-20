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
Logging service.
"""

import logging
import typing


class LoggingService:
    """
    Logging service management class.
    """

    def start(self):  # type: (...) -> None
        """
        Starts logging features.
        """
        from .logfilters import HandlerLogFilter
        from .logformatter import LogFormatter
        from .loggermain import MAIN_LOGGER
        from .loghandler import LogHandler
        from .path import Path
        from .scenarioconfig import SCENARIO_CONFIG

        # Start file logging if required.
        _log_outpath = SCENARIO_CONFIG.logoutpath()  # type: typing.Optional[Path]
        if _log_outpath is not None:
            LogHandler.file_handler = logging.FileHandler(_log_outpath, mode="w", encoding="utf-8")
            LogHandler.file_handler.addFilter(HandlerLogFilter(handler=LogHandler.file_handler))
            LogHandler.file_handler.setFormatter(LogFormatter(LogHandler.file_handler))
            MAIN_LOGGER.logging_instance.addHandler(LogHandler.file_handler)

    def stop(self):  # type: (...) -> None
        """
        Stops logging features.
        """
        from .loggermain import MAIN_LOGGER
        from .loghandler import LogHandler
        from .logstats import LOG_STATS

        LOG_STATS.debugstats()

        if LogHandler.file_handler:
            if LogHandler.file_handler in MAIN_LOGGER.logging_instance.handlers:
                MAIN_LOGGER.logging_instance.removeHandler(LogHandler.file_handler)
            LogHandler.file_handler.close()
            LogHandler.file_handler = None


__doc__ += """
.. py:attribute:: LOGGING_SERVICE

    Main instance of :class:`LoggingService`.
"""
LOGGING_SERVICE = LoggingService()  # type: LoggingService
