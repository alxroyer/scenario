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
:class:`Logger` class definition.
"""

import enum
import logging
import traceback
import typing

# `Console` used in method signatures.
from .console import Console
# `LogExtraData` used in method signatures.
from .logextradata import LogExtraData


__doc__ += """
.. py:attribute:: _main_loggers

    Number of main loggers already created.

    Constitutes a guard against the creation of several main loggers,
    i.e. loggers without a *log class*.
"""
_main_loggers = 0  # type: int


class Logger:
    """
    `scenario` logger base class for the main logger and sub-loggers.

    The :class:`Logger` class enables you to make your log lines be controlled by a *log class*.
    This will make the log lines be prefixed with the given log class,
    and give you the opportunity to activate or deactivate the corresponding debug log lines
    programmatically (see :meth:`enabledebug()`)
    or by configuration (see :meth:`.scenarioconfig.ScenarioConfig.debugclasses()`).
    """

    def __init__(
            self,
            log_class,  # type: typing.Union[str, enum.Enum]
    ):  # type: (...) -> None
        """
        :param log_class:
            Log class.

            Empty string for the main logger (for the main logger only!).

        .. seealso:: :meth:`enabledebug()` and :meth:`setlogcolor()`.
        """
        from .enumutils import enum2str
        from .logfilters import LoggerLogFilter

        #: Log class.
        self.log_class = enum2str(log_class)  # type: str

        # Build the :class:`logging.Logger` instance, and attach a filter.
        #: :class:`logging.Logger` instance as a member variable.
        self._logger = logging.Logger(name=self.log_class, level=logging.DEBUG)  # type: logging.Logger
        self._logger.addFilter(LoggerLogFilter(logger=self))
        if not self.log_class:
            # Main logger.
            global _main_loggers
            assert _main_loggers < 1, "Only one main logger"
            _main_loggers += 1
        else:
            # Child logger.
            # Set the main logger as the parent logger.
            from .loggermain import MAIN_LOGGER
            self._logger.parent = MAIN_LOGGER.logging_instance
            self._logger.propagate = True
        # :meth:`logging.Logger._log()` indirection.
        self._logger._log = self._log  # type: ignore[assignment]  ## Cannot assign to a method

        #: ``True`` to enable log debugging.
        #: ``None`` lets the configuration tells whether debug log lines should be displayed for this logger.
        self._debug_enabled = None  # type: typing.Optional[bool]

        #: Optional log color configuration.
        self._log_color = None  # type: typing.Optional[Console.Color]

        #: Logger indentation.
        self._indentation = ""  # type: str

        #: Extra flags configurations.
        self._extra_flags = {}  # type: typing.Dict[LogExtraData, bool]

    @property
    def logging_instance(self):  # type: () -> logging.Logger
        """
        Provides the reference of the :class:`logging.Logger` instance attached with this :class:`Logger` instance.
        """
        return self._logger

    def enabledebug(
            self,  # type: VarLoggerType
            enable_debug,  # type: bool
    ):  # type: (...) -> VarLoggerType
        """
        Debug log enabling / disabling.

        :param enable_debug: ``True`` for debug log enabling, ``False`` otherwise.
        :return: ``self``

        See the :ref:`main logger <logging.main-logger>` and :ref:`class loggers <logging.class-loggers>` sections
        to learn more about debugging with :class:`Logger` instances.
        """
        self._debug_enabled = enable_debug
        return self

    def isdebugenabled(self):  # type: (...) -> bool
        """
        Tells whether debug logging is currently enabled for this :class:`Logger` instance.

        :return: ``True`` when debug logging is enabled, ``False`` otherwise.
        """
        from .args import Args
        from .scenarioconfig import SCENARIO_CONFIG

        # Try to update :attr:`self._debug_enabled` if not already set.
        if (self._debug_enabled is None) and Args.getinstance().parsed:
            self._debug_enabled = (self.log_class in SCENARIO_CONFIG.debugclasses())

        return self._debug_enabled or False

    def setlogcolor(
            self,
            color,  # type: typing.Optional[Console.Color]
    ):  # type: (...) -> None
        """
        Sets or clears a log line color specialized for the logger.

        :param color: Log line color. ``None`` to reset to default.

        *Log class* colorization offers the possibilty to differenciate log lines betwwen different loggers running at the same time,
        each one having its own color.
        See the :ref:`log class colorization <logging.colors.log-class>` section for detailed information.
        """
        self._log_color = color

    def getlogcolor(self):  # type: (...) -> typing.Optional[Console.Color]
        """
        Returns the specialized log line color for this logger, if any.

        :return: Log line color. ``None`` when not set.
        """
        return self._log_color

    def pushindentation(
            self,
            indentation="    ",  # type: str
    ):  # type: (...) -> None
        """
        Adds indentation for this :class:`Logger` instance.

        :param indentation: Optional indentation pattern.

        See the dedicated sections to learn more about the differences between calling this method
        :ref:`on the main logger <logging.indentation.main-logger>` on the one hand,
        and :ref:`on a class logger <logging.indentation.class-logger>` on the other hand.
        """
        self._indentation += indentation

    def popindentation(
            self,
            indentation="    ",  # type: str
    ):  # type: (...) -> None
        """
        Removes indentation for the :class:`Logger` instance.

        :param indentation: Optional indentation pattern.
                            Must be the same as the indentation pattern passed on with the matching :meth:`pushindentation()` call
                            on a LIFO basis (Last-In First-Out).
        """
        if self._indentation.endswith(indentation):
            self._indentation = self._indentation[:-len(indentation)]
        else:
            self.warning(f"Current indentation {self._indentation!r} does not end with {indentation!r}, cannot pop indentation")

    def resetindentation(self):  # type: (...) -> None
        """
        Resets the indentation state attached with this :class:`Logger` instance.
        """
        self._indentation = ""

    def getindentation(self):  # type: (...) -> str
        """
        Returns the current indentation attached with this :class:`Logger` instance.

        :return: Current indentation.
        """
        return self._indentation

    def setextraflag(
            self,
            extra_flag,  # type: LogExtraData
            value,  # type: typing.Optional[bool]
    ):  # type: (...) -> None
        """
        Sets or unsets an extra flag configuration.

        :param extra_flag: Extra flag name.
        :param value: Extra flag configuration. ``None`` to unset the extra flag configuration.
        """
        if value is not None:
            self._extra_flags[extra_flag] = value
        elif extra_flag in self._extra_flags:
            del self._extra_flags[extra_flag]

    def getextraflag(
            self,
            extra_flag,  # type: LogExtraData
    ):  # type: (...) -> typing.Optional[bool]
        """
        Returns the extra flag configuration set (or not).

        :param extra_flag: Extra flag name.
        :return: ``True`` or ``False`` when the configuration is set, or ``None`` otherwise.
        """
        if extra_flag in self._extra_flags:
            return self._extra_flags[extra_flag]
        return None

    def error(
            self,
            msg,  # type: str
            *args,  # type: typing.Any
            **kwargs  # type: typing.Any
    ):  # type: (...) -> None
        """
        Logs an error message with this logger.
        """
        self._logger.error(msg, *args, **kwargs)

    def warning(
            self,
            msg,  # type: str
            *args,  # type: typing.Any
            **kwargs  # type: typing.Any
    ):  # type: (...) -> None
        """
        Logs a warning message with this logger.
        """
        self._logger.warning(msg, *args, **kwargs)

    def info(
            self,
            msg,  # type: str
            *args,  # type: typing.Any
            **kwargs  # type: typing.Any
    ):  # type: (...) -> None
        """
        Logs an informational message with this logger.
        """
        self._logger.info(msg, *args, **kwargs)

    def debug(
            self,
            msg,  # type: str
            *args,  # type: typing.Any
            **kwargs  # type: typing.Any
    ):  # type: (...) -> None
        """
        Logs a debug message with this logger.

        The processing of the message depends on the :attr:`_debug_enabled` configuration
        (see :meth:`enabledebug()`).
        """
        self._logger.debug(msg, *args, **kwargs)

    def log(
            self,
            level,  # type: int
            msg,  # type: str
            *args,  # type: typing.Any
            **kwargs  # type: typing.Any
    ):  # type: (...) -> None
        """
        Logs a message with a configurable severity.
        """
        self._logger.log(level, msg, *args, **kwargs)

    def _log(
            self,  # type: Logger
            level,  # type: int
            msg,  # type: str
            args,  # type: typing.Tuple[typing.Any, ...]
            **kwargs  # type: typing.Any
    ):  # type: (...) -> None
        """
        :meth:`logging.Logger._log()` method indirection.

        :param self:
            In as much as ``self`` is bound with the method,
            even though the call was made from a :class:`logging.Logger` instance,
            ``self`` remains a `scenario` :class:`Logger` when we arrive here.
        :param level: Log level.
        :param msg: Log message.
        :param args: Other positional arguments as a tuple.
        :param kwargs: Named parameter arguments.

        Handles appropriately the optional ``exc_info`` parameter.
        """
        # Check ``self`` is actually a :class:`Logger` instance, as explained in the docstring above.
        assert isinstance(self, Logger)

        # Remove the exception info from the named arguments if any.
        _exc_info = None  # type: typing.Any
        if "exc_info" in kwargs:
            _exc_info = kwargs["exc_info"]
            del kwargs["exc_info"]

        if ("extra" in kwargs) and (str(LogExtraData.LONG_TEXT_MAX_LINES) in kwargs["extra"]):
            _long_text_max_lines = kwargs["extra"][str(LogExtraData.LONG_TEXT_MAX_LINES)]  # type: typing.Any
            assert isinstance(_long_text_max_lines, (int, type(None))), (
                f"Invalid extra data '{LogExtraData.LONG_TEXT_MAX_LINES}' {_long_text_max_lines!r}, "
                f"should be an int or None"
            )
            del kwargs["extra"][str(LogExtraData.LONG_TEXT_MAX_LINES)]
            self._loglongtext(level, msg, args, _long_text_max_lines, **kwargs)
        else:
            self._torecord(level, msg, args, **kwargs)

        # Display the exception info afterwards.
        if _exc_info:
            _traceback = "".join(traceback.format_exception(*_exc_info))  # str
            if not _traceback.startswith("None"):
                for _line in _traceback.splitlines():  # type: str
                    if _line:
                        self.log(level, _line)

    def _torecord(
            self,
            level,  # type: int
            msg,  # type: str
            args,  # type: typing.Tuple[typing.Any, ...]
            **kwargs  # type: typing.Any
    ):  # type: (...) -> None
        """
        After the :meth:`_log()` indirection, eventually sends the log data to the base ``logging`` module to create a log record.

        :param level: Log level.
        :param msg: Log message.
        :param args: Other positional arguments as a tuple.
        :param kwargs: Named parameter arguments.
        """
        # Propagate the call to the :class:`logging.Logger` member instance.
        # noinspection PyProtectedMember
        logging.Logger._log(self._logger, level, msg, args, **kwargs)

    def longtext(
            self,
            max_lines,  # type: typing.Optional[int]
    ):  # type: (...) -> typing.Dict[str, int]
        """
        Builds the *long text* `extra` option in order to display the log message as several lines.

        :param max_lines: Maximum number of lines.
        :return: *long text* `extra` option.

        See the :ref:`long text logging <logging.long-text>` section for more details.
        """
        return LogExtraData.extradata({
            LogExtraData.LONG_TEXT_MAX_LINES: max_lines,
        })

    def _loglongtext(
            self,
            level,  # type: int
            msg,  # type: str
            args,  # type: typing.Tuple[typing.Any, ...]
            max_lines,  # type: typing.Optional[int]
            **kwargs  # type: typing.Any
    ):  # type: (...) -> None
        """
        Logs the beginning of a long text on multiple lines.

        :param level: Log level.
        :param msg: Log message.
        :param args: Other positional arguments as a tuple.
        :param max_lines: Maximum number of lines to display. All lines when set to ``None``.
        :param kwargs: Named parameter arguments.
        """
        _long_text = msg % args  # type: str

        _lines_displayed = 0  # type: int
        _lines = _long_text.splitlines()  # type: typing.List[str]
        for _line in _lines:  # type: str
            _lines_displayed += 1
            if (max_lines is not None) and (_lines_displayed > max_lines):
                _lines_displayed -= 1
                break
            self._torecord(level, _line, tuple([]), **kwargs)
        if _lines_displayed < len(_lines):
            self._torecord(level, "...", tuple([]), **kwargs)


if typing.TYPE_CHECKING:
    #: Variable logger type.
    VarLoggerType = typing.TypeVar("VarLoggerType", bound=Logger)
