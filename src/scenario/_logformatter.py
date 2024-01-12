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
Log record formatting.
"""

import logging
import re
import typing

if True:
    from ._fastpath import FAST_PATH as _FAST_PATH  # `FAST_PATH` imported once for performance concerns.
    from ._logextradata import LogExtraData as _LogExtraDataImpl  # `LogExtraData` imported once for performance concerns.
    from ._logextradata import LogExtraDataHelper as _LogExtraDataHelperImpl  # `LogExtraDataHelper` imported once for performance concerns.
    from ._logger import Logger as _LoggerImpl  # `Logger` imported once for performance concerns.
if typing.TYPE_CHECKING:
    from ._consoleutils import Console as _ConsoleType
    from ._logextradata import LogExtraData as _LogExtraDataType
    from ._logger import Logger as _LoggerType


class LogFormatter(logging.Formatter):
    """
    Formats log records.

    Log record formatting includes the following aspects:

    :Date/time display:
        See :ref:`log date/time <logging.date-time>` documentation.

        Displayed by default, unless it is disabled through
        the :meth:`._scenarioconfig.ScenarioConfig.logdatetimeenabled()` configuration,
        or the :attr:`._logextradata.LogExtraData.DATE_TIME` extra flag.
    :Log level display:
        See :ref:`log levels <logging.log-levels>` documentation.

        Log level is always displayed,
        unless it is disabled through the :attr:`._logextradata.LogExtraData.LOG_LEVEL` extra flag.
    :Date/time display:
        See :ref:`log date/time <logging.date-time>` documentation.

        Displayed by default, unless it is disabled through
        the :meth:`._scenarioconfig.ScenarioConfig.logdatetimeenabled()` configuration,
        or the :attr:`._logextradata.LogExtraData.DATE_TIME` extra flag.
    :Log level display:
        See :ref:`log levels <logging.log-levels>` documentation.

        Log level is always displayed,
        unless it is disabled through the :attr:`._logextradata.LogExtraData.LOG_LEVEL` extra flag.
    :Log class display:
        See :ref:`class loggers <logging.class-loggers>` documentation.
    :Indentation:
        See :ref:`log indentation <logging.indentation>` documentation.
    :Colorization:
        See :ref:`log colors <logging.colors>` documentation.

        Console log colorization may be disabled through
        the :meth:`._scenarioconfig.ScenarioConfig.logconsoleenabled()` configuration,
        or the :attr:`._logextradata.LogExtraData.COLOR` extra flag.
    """

    def __init__(
            self,
            handler,  # type: logging.Handler
    ):  # type: (...) -> None
        """
        :param handler: Attached ``logging.Handler``.
        """
        logging.Formatter.__init__(self)

        #: Attached ``logging.Handler``.
        self._handler = handler  # type: logging.Handler

    def format(
            self,
            record,  # type: logging.LogRecord
    ):  # type: (...) -> str
        """
        ``logging`` method overload that implements most of the `scenario` log formatting expectations.

        :param record: Log record to format for printing.
        :return: Log string representation.
        """
        from ._consoleutils import Console
        from ._datetimeutils import toiso8601
        from ._loggermain import MAIN_LOGGER
        from ._scenariologging import ScenarioLogging
        from ._scenariostack import SCENARIO_STACK

        # Retrieve the logger reference from the record.
        # Memo: Logger reference as extra data set by :class:`logfilters.LoggerLogFilter`.
        _logger = _LogExtraDataHelperImpl.get(record, _LogExtraDataImpl.CURRENT_LOGGER)  # type: typing.Optional[_LoggerType]

        # Build the log line.
        _log_line = ""  # type: str

        # Date / time.
        if self._with(record, _LogExtraDataImpl.DATE_TIME, default=True):
            # Compute an ISO8601 time representation.
            _log_line += toiso8601(record.created)
            _log_line += " - "

        # Head indentation.
        _log_line += (_LogExtraDataHelperImpl.get(record, _LogExtraDataImpl.HEAD_INDENTATION) or "")

        # Scenario stack indentation.
        if self._with(record, _LogExtraDataImpl.SCENARIO_STACK_INDENTATION, default=True):
            _log_line += ScenarioLogging.SCENARIO_STACK_INDENTATION_PATTERN * (SCENARIO_STACK.size - 1)

        # Action / result margin.
        if self._with(record, _LogExtraDataImpl.ACTION_RESULT_MARGIN, default=True):
            _log_line += ((" " * ScenarioLogging.ACTION_RESULT_MARGIN) + "  ")

        # Log level, with color, when applicable.
        _level_color = None  # type: typing.Optional[Console.Color]
        if self._with(record, _LogExtraDataImpl.COLOR, default=True):
            _level_color = self._levelcolor(record.levelno)
        if self._with(record, _LogExtraDataImpl.LOG_LEVEL, default=True):
            if _level_color:
                _log_line += f"\033[{_level_color}m"
            _log_line += record.levelname
            if _level_color:
                _log_line += f"\033[{Console.Color.RESET}m"
            _max_level_len = max(len(logging.getLevelName(x)) for x in range(0, logging.CRITICAL + 1))  # type: int
            _log_line += f"{' ':>{_max_level_len - len(record.levelname)}}"
            _log_line += " "

        # Main logger indentation.
        if self._with(record, _LogExtraDataImpl.MAIN_LOGGER_INDENTATION, default=True):
            _log_line += MAIN_LOGGER.getindentation()

        # Log message color (begin).
        _message_color = None  # type: typing.Optional[Console.Color]
        if self._with(record, _LogExtraDataImpl.COLOR, default=True):
            if isinstance(_logger, _LoggerImpl):
                _message_color = _logger.getlogcolor()
            if _message_color is None:
                _message_color = _level_color
        if _message_color is not None:
            _log_line += f"\033[{_message_color}m"

        # Log class, with indentation.
        if isinstance(_logger, _LoggerImpl) and _logger.log_class:
            _log_line += f"[{_logger.log_class}] "
            # Note: Don't duplicate main logger indentation. That's the reason why `_logger.log_class` is checked above.
            if self._with(record, _LogExtraDataImpl.CLASS_LOGGER_INDENTATION, default=_logger.isdebugenabled()):
                _log_line += _logger.getindentation()

        # Log message.
        _log_line += record.getMessage()

        # Log message color (end).
        if _message_color:
            _log_line += f"\033[{Console.Color.RESET}m"

        # Exception.
        _exception = ""  # type: str
        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            _exception += record.exc_text
        if _exception and _logger:
            for _exception_line in _exception.splitlines():  # type: str
                _logger.log(record.levelno, _exception_line)

        # Remove trailing white spaces.
        return _log_line.rstrip()

    def _with(
            self,
            record,  # type: logging.LogRecord
            extra_flag,  # type: _LogExtraDataType
            *,
            default,  # type: bool
    ):  # type: (...) -> bool
        """
        Tells whether the logging aspect described by ``extra_flag`` is on or off for the given record.

        :param extra_flag: Extra flag / logging aspect to check.
        :param default:
            Default return value.
            May be set to ``False`` when required.
        :return:
            ``True`` if the logging aspect described by ``extra_flag`` in on for the current record,
            ``False`` otherwise.

        Depends on :

        1. The extra flags set in the log record,
        2. The scenario configuration,
        3. The current execution state.
        """
        from ._loghandler import LogHandler
        from ._scenariostack import SCENARIO_STACK

        # 1. Check whether the record or the attached logger has the given flag set.
        _value = _LogExtraDataHelperImpl.get(record, extra_flag)  # type: typing.Any
        if isinstance(_value, bool):
            return _value

        # 2. Check whether a scenario configuration or execution state gives an answer for the given flag.
        if extra_flag == _LogExtraDataImpl.DATE_TIME:
            return _FAST_PATH.scenario_config.logdatetimeenabled()
        if extra_flag == _LogExtraDataImpl.COLOR:
            # Use colors in the console handler only.
            if (self._handler is LogHandler.console_handler) and _FAST_PATH.scenario_config.logcolorenabled():
                return True
            else:
                return False
        if extra_flag == _LogExtraDataImpl.ACTION_RESULT_MARGIN:
            # Action/result margin only when there is a current action or expected result.
            return SCENARIO_STACK.current_action_result_execution is not None

        # 3. Otherwise, return the default value.
        return default

    @staticmethod
    def _levelcolor(
            level,  # type: int
    ):  # type: (...) -> _ConsoleType.Color
        """
        Determines log color out from log level.

        :param level: Log level which respective color to find out.
        :return: Log color corresponding to the given log level.
        """
        from ._consoleutils import Console

        if level < logging.INFO:
            return _FAST_PATH.scenario_config.logcolor(logging.getLevelName(logging.DEBUG), Console.Color.DARKGREY02)
        elif level < logging.WARNING:
            return _FAST_PATH.scenario_config.logcolor(logging.getLevelName(logging.INFO), Console.Color.WHITE01)
        elif level < logging.ERROR:
            return _FAST_PATH.scenario_config.logcolor(logging.getLevelName(logging.WARNING), Console.Color.YELLOW33)
        else:
            return _FAST_PATH.scenario_config.logcolor(logging.getLevelName(logging.ERROR), Console.Color.RED91)

    @staticmethod
    def nocolor(
            string,  # type: str
    ):  # type: (...) -> str
        """
        Removes color control characters from a string.

        :param string: String to remove color control characters from.
        :return: String without color control characters.
        """
        # See https://docs.python.org/3/library/re.html#re.sub.
        return re.sub(
            pattern="\033" + r"\[\d+(;\d+)*m",
            repl="",
            string=string,
            count=0,  # "If omitted or zero, all occurrences will be replaced."
        )
