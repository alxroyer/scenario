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

if True:
    from ._logextradata import LogExtraData as _LogExtraDataImpl
if typing.TYPE_CHECKING:
    from ._consoleutils import Console as _ConsoleType
    from ._logextradata import LogExtraData as _LogExtraDataType


#: Number of main loggers already created.
#:
#: Constitutes a guard against the creation of several main loggers,
#: i.e. loggers without a *log class*.
_main_loggers = 0  # type: int


class Logger:
    """
    `scenario` logger base class for the main logger and sub-loggers.

    The :class:`Logger` class enables you to make your log lines be controlled by a *log class*.
    This will make the log lines be prefixed with the given log class,
    and give you the opportunity to activate or deactivate the corresponding debug log lines
    programmatically (see :meth:`enabledebug()`)
    or by configuration (see :meth:`._scenarioconfig.ScenarioConfig.debugclasses()`).
    """

    #: Shortcut to :class:`._logextradata.LogExtraData` ``extra`` options keys.
    #:
    #: As ``logging`` supports a ``extra`` ``{str: Any}`` optional parameter with its logging functions,
    #: may be used as ``extra`` keys with :meth:`error()`, :meth:`warning()`, :meth:`info()`, :meth:`debug()` and :meth:`log()`.
    #:
    #: Example:
    #:
    #: .. code-block:: python
    #:
    #:     _long_text = """
    #:         Very long text,
    #:         on several lines...
    #:     """
    #:     _logger.info(
    #:         _long_text
    #:         extra={
    #:             logger.Extra.LONG_TEXT: True,
    #:             logger.Extra.LONG_TEXT_MAX_LINES: 10,
    #:         },
    #:     )
    #:
    #: May also be configured for good for the logger.
    #: See :meth:`setextraflag()` and :meth:`getextraflag()`.
    Extra = _LogExtraDataImpl

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
        from ._enumutils import enum2str
        from ._logfilters import LoggerLogFilter

        #: Log class.
        self.log_class = enum2str(log_class)  # type: str

        # Build the ``logging.Logger`` instance, and attach a filter.
        #: ``logging.Logger`` instance as a member variable.
        self._logger = logging.Logger(name=self.log_class, level=logging.DEBUG)  # type: logging.Logger
        self._logger.addFilter(LoggerLogFilter(logger=self))
        if not self.log_class:
            # Main logger.
            global _main_loggers
            # Note: A second dummy main logger may be instanciated due to our `scenario.tools.sphinx` implementation with `typing.TYPE_CHECKING` enabled.
            if (_main_loggers >= 1) and (not typing.TYPE_CHECKING):
                raise RuntimeError("Only one main logger")
            _main_loggers += 1
        else:
            # Child logger.
            # Set the main logger as the parent logger.
            # Memo: Don't import the main logger before we're sure we're not building the main logger itself!
            from ._loggermain import MAIN_LOGGER

            self._logger.parent = MAIN_LOGGER.logging_instance
            self._logger.propagate = True
        # `logging.Logger._log()` indirection.
        self._logger._log = self._log  # type: ignore[assignment]  ## Cannot assign to a method

        #: ``True`` to enable log debugging.
        #: ``None`` lets the configuration tells whether debug log lines should be displayed for this logger.
        self._debug_enabled = None  # type: typing.Optional[bool]

        #: Optional log color configuration.
        self._log_color = None  # type: typing.Optional[_ConsoleType.Color]

        #: Logger indentation stack.
        self._indentations = []  # type: typing.List[str]

        #: Extra flags configurations.
        self._extra_flags = {}  # type: typing.Dict[_LogExtraDataType, bool]

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
        from ._args import Args
        from ._scenarioconfig import SCENARIO_CONFIG

        # Try to update `self._debug_enabled` if not already set.
        if (self._debug_enabled is None) and Args.getinstance().parsed:
            self._debug_enabled = (self.log_class in SCENARIO_CONFIG.debugclasses())

        return self._debug_enabled or False

    def setlogcolor(
            self,
            color,  # type: typing.Optional[_ConsoleType.Color]
    ):  # type: (...) -> None
        """
        Sets or clears a log line color specialized for the logger.

        :param color: Log line color. ``None`` to reset to default.

        *Log class* colorization offers the possibilty to differenciate log lines betwwen different loggers running at the same time,
        each one having its own color.
        See the :ref:`log class colorization <logging.colors.log-class>` section for detailed information.
        """
        self._log_color = color

    def getlogcolor(self):  # type: (...) -> typing.Optional[_ConsoleType.Color]
        """
        Returns the specialized log line color for this logger, if any.

        :return: Log line color. ``None`` when not set.
        """
        return self._log_color

    def pushindentation(
            self,
            indentation="    ",  # type: str
    ):  # type: (...) -> typing.ContextManager[None]
        """
        Adds indentation for this :class:`Logger` instance.

        :param indentation:
            Indentation pattern.
        :return:
            Context manager that automatically pops indentation,
            when :meth:`pushindentation()` is called in a ``with`` statement.

            Unused when :meth:`pushindentation()` not called in a ``with`` statement.

        See the dedicated sections to learn more about the differences between calling this method
        :ref:`on the main logger <logging.indentation.main-logger>` on the one hand,
        and :ref:`on a class logger <logging.indentation.class-logger>` on the other hand.

        .. tip::
            Call this method in a ``with`` statement,
            in order to ensure the expected counter :meth:`popindentation()` is called,
            whatever happens (``return``, ``break``, ``continue`` jumps, or exception raised).
        """
        from ._loggingcontext import LoggingContext

        self._indentations.append(indentation)

        # Return a started `LoggingContext` instance that does not push indentation again,
        # but would call `popindentation()` with the appropriate indentation:
        # - Initialize without indentation, and start.
        _ctx = LoggingContext(logger=self, indentation="")  # type: LoggingContext
        _ctx.__enter__()
        # - Fix indentation once started.
        _ctx.indentation = indentation
        return _ctx

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
        if self._indentations and (self._indentations[-1] == indentation):
            self._indentations.pop()
        else:
            self.warning(f"Current indentation stack {self._indentations!r} does not end with {indentation!r}, cannot pop indentation")

    def resetindentation(self):  # type: (...) -> None
        """
        Resets the indentation state attached with this :class:`Logger` instance.
        """
        self._indentations.clear()

    def getindentation(self):  # type: (...) -> str
        """
        Returns the current indentation attached with this :class:`Logger` instance.

        :return: Current indentation.
        """
        return "".join(self._indentations)

    def setextraflag(
            self,
            extra_flag,  # type: _LogExtraDataType
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
            extra_flag,  # type: _LogExtraDataType
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
        ``logging.Logger._log()`` method indirection.

        :param self:
            In as much as ``self`` is bound with the method,
            even though the call was made from a ``logging.Logger`` instance,
            ``self`` remains a `scenario` :class:`Logger` when we arrive here.
        :param level: Log level.
        :param msg: Log message.
        :param args: Other positional arguments as a tuple.
        :param kwargs: Named parameter arguments.

        Handles appropriately the optional ``exc_info`` parameter.
        """
        from ._args import Args
        from ._logextradata import LogExtraData

        # Check ``self`` is actually a :class:`Logger` instance, as explained in the docstring above.
        if not isinstance(self, Logger):
            raise TypeError(f"{self!r} is not of type {Logger!r}")

        # Check that the arguments have been parsed.
        if not Args.isset():
            raise RuntimeError("Avoid logging anything before arguments have been parsed")

        # Remove the exception info from the named arguments if any.
        _exc_info = None  # type: typing.Any
        if "exc_info" in kwargs:
            _exc_info = kwargs["exc_info"]
            del kwargs["exc_info"]

        # Log extra data.
        _extra = {}  # type: typing.Dict[str, typing.Any]
        if "extra" in kwargs:
            _extra = kwargs["extra"]
            if (
                (not isinstance(_extra, dict))  # type: ignore[redundant-expr]  ## Left operand of "or" is always false
                or (not all([isinstance(_key, str) for _key in _extra]))
            ):
                raise TypeError(f"Invalid `extra` parameter type {_extra!r}, should be a {{str: Any}} dictionary")

        # Long text mode.
        _long_text_mode = None  # type: typing.Any
        _long_text_max_lines = None  # type: typing.Any
        if LogExtraData.LONG_TEXT in _extra:
            _long_text_mode = _extra[LogExtraData.LONG_TEXT]
            del _extra[LogExtraData.LONG_TEXT]
            if not isinstance(_long_text_mode, bool):
                raise TypeError(f"Invalid extra data '{LogExtraData.LONG_TEXT}', {_long_text_mode!r}, should be a `bool` value")
        if LogExtraData.LONG_TEXT_MAX_LINES in _extra:
            # Automatically activates the *long text mode*.
            _long_text_mode = True
            _long_text_max_lines = _extra[LogExtraData.LONG_TEXT_MAX_LINES]
            del _extra[LogExtraData.LONG_TEXT_MAX_LINES]
            if not isinstance(_long_text_max_lines, int):
                raise TypeError(f"Invalid extra data '{LogExtraData.LONG_TEXT_MAX_LINES}' {_long_text_max_lines!r}, should be an `int` value")
        if _long_text_mode:
            self._loglongtext(level, msg, args, _long_text_max_lines, **kwargs)
        else:
            self._torecord(level, msg, args, **kwargs)

        # Display the exception info afterwards.
        if _exc_info:
            _traceback = "".join(traceback.format_exception(*_exc_info))  # str
            if not _traceback.startswith("None"):
                self._loglongtext(level, _traceback, (), None)

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
        logging.Logger._log(self._logger, level, msg, args, **kwargs)  # noqa  ## Access to a protected member

    def _loglongtext(
            self,
            level,  # type: int
            msg,  # type: str
            args,  # type: typing.Tuple[typing.Any, ...]
            max_lines,  # type: typing.Optional[int]
            **kwargs  # type: typing.Any
    ):  # type: (...) -> None
        """
        Logs a long text on multiple lines.

        :param level: Log level.
        :param msg: Log message.
        :param args: Other positional arguments as a tuple.
        :param max_lines: Maximum number of first lines to display. All lines when set to ``None``.
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

    def logexceptiontraceback(
            self,
            exception,  # type: Exception
            *,
            level=logging.ERROR,  # type: int
            indent="",  # type: str
    ):  # type: (...) -> None
        """
        Log an exception with its traceback.

        :param exception: Exception to log.
        :param level: Log level.
        :param indent: Indentation to use.
        """
        from ._testerrors import ExceptionError, TestError

        # Use a `ExceptionError` instance to display the exception (except for `TestError`s).
        if not isinstance(exception, TestError):
            exception = ExceptionError(exception)
        exception.logerror(self, level=level, indent=indent)


if typing.TYPE_CHECKING:
    #: Variable logger type.
    VarLoggerType = typing.TypeVar("VarLoggerType", bound=Logger)
