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
Test errors.
"""

import logging
import traceback
import typing

if typing.TYPE_CHECKING:
    from ._locations import CodeLocation as _CodeLocationType
    from ._logger import Logger as _LoggerType
    from ._typing import JsonDictType


class TestError(Exception):
    """
    Base test error object.

    Stores information about an error that occurred during the test.

    Declared as an exception so that it can be propagated as is.
    """

    def __init__(
            self,
            message,  # type: str
            location=None,  # type: typing.Optional[_CodeLocationType]
    ):  # type: (...) -> None
        """
        :param message: Error message.
        :param location: Error location.
        """
        Exception.__init__(self)

        #: Error message.
        self.message = message  # type: str

        #: Error location.
        self.location = location  # type: typing.Optional[_CodeLocationType]

    def __str__(self):  # type: () -> str
        """
        Short representation of the error.
        """
        return self.message

    def __repr__(self):  # type: () -> str
        """
        Programmatic representation of the error.
        """
        _severity = (
            "ERROR" if self.iserror() else
            "WARNING" if self.iswarning() else
            "IGNORED"
        )  # type: str
        return f"<{type(self).__name__} {_severity!r} {str(self)!r}>"

    def iserror(self):  # type: (...) -> bool
        """
        Tells whether this error object is actually an error.

        :return:
            ``True`` for a real error,
            ``False`` for a simple warning (see :meth:`iswarning()`) or when the error should be ignored (see :meth:`isignored()`).
        """
        return True

    def iswarning(self):  # type: (...) -> bool
        """
        Tells whether this error object is just a warning.

        :return:
            ``True`` for a simple warning,
            ``False`` for a real error (see :meth:`iserror()`) or when the error should be ignored (see :meth:`isignored()`).
        """
        return False

    def isignored(self):  # type: (...) -> bool
        """
        Tells whether this error object should be ignored.

        :return:
            ``True`` when the error should be ignored,
            ``False`` for a real error (see :meth:`iserror()`) or a warning (see :meth:`iswarning()`).
        """
        return False

    def logerror(
            self,
            logger,  # type: _LoggerType
            level=logging.ERROR,  # type: int
            indent="",  # type: str
    ):  # type: (...) -> None
        """
        Logs the error info.

        :param logger: Logger to use for logging.
        :param level: Log level.
        :param indent: Indentation to use.
        """
        if self.location:
            logger.log(level, "%s%s (%s)", indent, str(self), self.location.tolongstring())
        else:
            logger.log(level, "%s%s", indent, str(self))

    def tojson(self):  # type: (...) -> JsonDictType
        """
        Converts the :class:`TestError` instance into a JSON dictionary.

        :return: JSON dictionary.
        """
        _json = {
            "message": self.message,
        }  # type: JsonDictType
        if self.location:
            _json["location"] = self.location.tolongstring()
        return _json

    @staticmethod
    def fromjson(
            json_data,  # type: JsonDictType
    ):  # type: (...) -> TestError
        """
        Builds a :class:`TestError` instance from its JSON representation.

        :param json_data: JSON dictionary.
        :return: New :class:`TestError` instance.
        """
        from ._knownissues import KnownIssue
        from ._locations import CodeLocation

        if "type" in json_data:
            if json_data["type"] == "known-issue":
                return KnownIssue.fromjson(json_data)
            else:
                return ExceptionError.fromjson(json_data)

        _location = None  # type: typing.Optional[CodeLocation]
        if "location" in json_data:
            _location = CodeLocation.fromlongstring(json_data["location"])
        return TestError(message=json_data["message"], location=_location)


class ExceptionError(TestError):
    """
    Test error related to an exception.
    """

    def __init__(
            self,
            exception=None,  # type: typing.Optional[typing.Union[BaseException, traceback.TracebackException]]
    ):  # type: (...) -> None
        """
        :param exception: Root cause exception, if available.
        """
        from ._locations import CodeLocation, EXECUTION_LOCATIONS
        from ._path import Path

        # Check input parameters.
        if isinstance(exception, BaseException):
            exception = traceback.TracebackException.from_exception(exception)

        # Call the `TestError` initializer.
        if exception:
            # Caution: in case of internal error, `fromexception()` may return an empty list.
            _location = CodeLocation(Path(), 0, "")
            if EXECUTION_LOCATIONS.fromexception(exception, limit=1):
                _location = EXECUTION_LOCATIONS.fromexception(exception, limit=1, fqn=True)[-1]
            TestError.__init__(
                self,
                message=str(exception),
                location=_location,
            )
        else:
            TestError.__init__(self, message="", location=None)

        #: The root cause exception, if any.
        self.exception = exception  # type: typing.Optional[traceback.TracebackException]

        #: Type of the exception, if any.
        self.exception_type = ""  # type: str
        if exception:
            self.exception_type = exception.exc_type.__name__

        # Redefine the type of :attr:`TestError.location` in order to explicitize it cannot be ``None`` for :class:`ExceptionError` instances.
        self.location = self.location  # type: _CodeLocationType

    def __str__(self):  # type: () -> str
        """
        Short representation of the exception error.

        Exception type + message.
        """
        return f"{self.exception_type}: {self.message}"

    def logerror(
            self,
            logger,  # type: _LoggerType
            level=logging.ERROR,  # type: int
            indent="",  # type: str
    ):  # type: (...) -> None
        """
        :meth:`TestError.logerror()` override in order to log the exception traceback, if an exception is stored.

        Defaults to :meth:`TestError.logerror()` if no exception.
        """
        if self.exception:
            _traceback = "".join(self.exception.format())  # str
            for _line in _traceback.splitlines():  # type: str
                if _line:
                    logger.log(level, "%s  %s", indent, _line)
        else:
            super().logerror(logger, level=level, indent=indent)

    def tojson(self):  # type: (...) -> JsonDictType
        _json = {
            "type": self.exception_type,
            "message": self.message,
            "location": self.location.tolongstring(),
        }  # type: JsonDictType
        return _json

    @staticmethod
    def fromjson(
            json_data,  # type: JsonDictType
    ):  # type: (...) -> ExceptionError
        """
        Builds a :class:`ExceptionError` instance from its JSON representation.

        :param json_data: JSON dictionary.
        :return: New :class:`ExceptionError` instance.
        """
        from ._locations import CodeLocation

        _error = ExceptionError(exception=None)  # type: ExceptionError
        _error.exception_type = json_data["type"]
        _error.message = json_data["message"]
        _error.location = CodeLocation.fromlongstring(json_data["location"])
        return _error
