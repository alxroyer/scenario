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
Log filtering.
"""

import logging
import typing

if typing.TYPE_CHECKING:
    from ._logger import Logger as _LoggerType


class LoggerLogFilter(logging.Filter):
    """
    Log filter attached to a :class:`._logger.Logger` instance.

    Filters log records depending on the log level and the associated logger configuration.
    """

    def __init__(
            self,
            logger,  # type: _LoggerType
    ):  # type: (...) -> None
        """
        :param logger: Attached :class:`._logger.Logger` instance.
        """
        logging.Filter.__init__(self)

        #: Attached `scenario` :class:`._logger.Logger` instance.
        self._logger = logger  # type: _LoggerType

    def filter(
            self,
            record,  # type: logging.LogRecord
    ):  # type: (...) -> bool
        """
        Filtering hook implementation.

        :param record:
            Log record to check for filtering.
        :return:
            See ``logging.Filter.filter()``: "Is the specified record to be logged? Returns 0 for no, nonzero for yes."

            Nevertheless, we can see from the code that booleans are actually returned.

        Checks whether the log record should be filtered out due to the attached :class:`._logger.Logger` configuration.
        """
        from ._logextradata import LogExtraData

        # Ensure the current logger reference is set in the record as an extra data so that `LogFormatter` knows about it.
        # Ensure class loggers prevail on the main logger.
        _logger = LogExtraData.get(record, LogExtraData.CURRENT_LOGGER)  # type: typing.Optional[_LoggerType]
        if (not _logger) or (not _logger.log_class):
            LogExtraData.set(record, LogExtraData.CURRENT_LOGGER, self._logger)

        # Log level filtering.
        if record.levelno <= logging.DEBUG:
            if not self._logger.isdebugenabled():
                return False

        # Fall back to the `logging.Filter` parent implementation.
        return super().filter(record)


class HandlerLogFilter(logging.Filter):
    """
    Log filter attached to a ``logging.Handler`` instance.

    Filters log records depending on `scenario` configurations:
    :meth:`._scenarioconfig.ScenarioConfig.logconsoleenabled()` and :meth:`._scenarioconfig.ScenarioConfig.logoutpath()`.
    """

    def __init__(
            self,
            handler,  # type: typing.Optional[logging.Handler]
    ):  # type: (...) -> None
        """
        :param handler: Attached ``logging.Handler``.
        """
        logging.Filter.__init__(self)

        #: Attached ``logging.Handler``.
        self._handler = handler  # type: typing.Optional[logging.Handler]

    def filter(
            self,
            record,  # type: logging.LogRecord
    ):  # type: (...) -> bool
        """
        Filtering hook implementation.

        :param record: Log record to check for filtering.
        :return:
            See ``logging.Filter.filter()``: "Is the specified record to be logged? Returns 0 for no, nonzero for yes."

            Nevertheless, we can see from the code that booleans are actually returned.

        Checks the :meth:`._scenarioconfig.ScenarioConfig.logconsoleenabled()` or :meth:`._scenarioconfig.ScenarioConfig.logoutpath()` configurations,
        depending on the handler attached.
        """
        from ._loghandler import LogHandler
        from ._scenarioconfig import SCENARIO_CONFIG

        # Handler filtering.
        if self._handler is LogHandler.console_handler:
            if not SCENARIO_CONFIG.logconsoleenabled():
                return False
        if self._handler is LogHandler.file_handler:
            if SCENARIO_CONFIG.logoutpath() is None:
                return False

        # Fall back to the :class:`logging.Filter` parent implementation.
        return super().filter(record)
