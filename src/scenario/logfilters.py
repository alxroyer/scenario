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
Log filtering.
"""

import logging
import typing

# `Logger` used in method signatures.
from .logger import Logger


class LoggerLogFilter(logging.Filter):
    """
    Log filter attached to a :class:`.logger.Logger` instance.

    Filters log records depending on the log level and the associated logger configuration.
    """

    def __init__(
            self,
            logger,  # type: Logger
    ):  # type: (...) -> None
        """
        :param logger: Attached :class:`.logger.Logger` instance.
        """
        logging.Filter.__init__(self)

        #: Attached :mod:`scenario` :class:`.logger.Logger` instance.
        self._logger = logger  # type: Logger

    def filter(
            self,
            record,  # type: logging.LogRecord
    ):  # type: (...) -> bool
        """
        Filtering hook implementation.

        :param record: Log record to check for filtering.
        :return:
            See :meth:`logging.Filter.filter()`: "Is the specified record to be logged? Returns 0 for no, nonzero for yes."

            Nevertheless, we can see from the code that booleans are actually returned.

        Checks whether the log record should be filtered out due to the attached :class:`Logger` configuration.
        """
        from .logextradata import LogExtraData

        # Ensure the current logger reference is set in the record as an extra data so that :class:`.logformatter.LogFormatter` knows about it.
        # Ensure class loggers prevail on the main logger.
        _logger = LogExtraData.get(record, LogExtraData.CURRENT_LOGGER)  # type: typing.Optional[Logger]
        if (not _logger) or (not _logger.log_class):
            LogExtraData.set(record, LogExtraData.CURRENT_LOGGER, self._logger)

        # Log level filtering.
        if record.levelno <= logging.DEBUG:
            if not self._logger.isdebugenabled():
                return False

        # Fall back to the :class:`logging.Filter` parent implementation.
        return super().filter(record)


class HandlerLogFilter(logging.Filter):
    """
    Log filter attached to a :class:`logging.Handler` instance.

    Filters log records depending on :mod:`scenario` configurations:
    :attr:`.scenarioconfig.ScenarioConfig.Key.LOG_CONSOLE` and :attr:`.scenarioconfig.ScenarioConfig.Key.LOG_FILE`.
    """

    def __init__(
            self,
            handler,  # type: typing.Optional[logging.Handler]
    ):  # type: (...) -> None
        """
        :param handler: Attached :class:`logging.Handler`.
        """
        logging.Filter.__init__(self)

        #: Attached :class:`logging.Handler`.
        self._handler = handler  # type: typing.Optional[logging.Handler]

    def filter(
            self,
            record,  # type: logging.LogRecord
    ):  # type: (...) -> bool
        """
        Filtering hook implementation.

        :param record: Log record to check for filtering.
        :return:
            See :meth:`logging.Filter.filter()`: "Is the specified record to be logged? Returns 0 for no, nonzero for yes."

            Nevertheless, we can see from the code that booleans are actually returned.

        Checks the :attr:`.scenarioconfig.ScenarioConfig.Key.LOG_CONSOLE` or :attr:`.scenarioconfig.ScenarioConfig.Key.LOG_FILE` configurations,
        depending on the handler attached.
        """
        from .loghandler import LogHandler
        from .scenarioconfig import SCENARIO_CONFIG

        # Handler filtering.
        if self._handler is LogHandler.console_handler:
            if not SCENARIO_CONFIG.logconsoleenabled():
                return False
        if self._handler is LogHandler.file_handler:
            if SCENARIO_CONFIG.logoutpath() is None:
                return False

        # Fall back to the :class:`logging.Filter` parent implementation.
        return super().filter(record)
