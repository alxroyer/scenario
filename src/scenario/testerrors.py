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
Test errors.
"""

import logging
import traceback
import typing

# `CodeLocation` used in method signatures.
from .locations import CodeLocation
# `Logger` used in method signatures.
from .logger import Logger

if typing.TYPE_CHECKING:
    # `JSONDict` used in method signatures.
    # Type declared for type checking only.
    from .typing import JSONDict


class TestError(Exception):
    """
    Base test error object.

    Stores information about an error that occurred during the test.

    Declared as an exception so that it can be propagated as is.
    """

    def __init__(
            self,
            message,  # type: str
            location=None,  # type: typing.Optional[CodeLocation]
    ):  # type: (...) -> None
        """
        :param message: Error message.
        :param location: Error location.
        """
        Exception.__init__(self)

        #: Error message.
        self.message = message  # type: str

        #: Error location.
        self.location = location  # type: typing.Optional[CodeLocation]

    def __str__(self):  # type: (...) -> str
        """
        Short representation of the error.
        """
        return self.message

    def __repr__(self):  # type: (...) -> str
        """
        Programmatic representation of the error.
        """
        return "<%s '%s'>" % (type(self).__name__, str(self))

    def __eq__(
            self,
            other,  # type: typing.Any
    ):  # type: (...) -> bool
        """
        Test error equality operator.

        :param other: Candidate object.
        :return: ``True`` when code locations and short representations match, ``False`` otherwise.
        """
        if isinstance(other, TestError):
            if (self.location == other.location) and (str(self) == str(other)):
                return True
        return False

    def iswarning(self):  # type: (...) -> bool
        """
        Tells whether the error a just a warning.

        :return: ``True`` for a simple warning, ``False`` for a real error.
        """
        return False

    def logerror(
            self,
            logger,  # type: Logger
            level=logging.ERROR,  # type: int
    ):  # type: (...) -> None
        """
        Logs the error info.

        :param logger: Logger to use for logging.
        :param level: Log level.
        """
        if self.location:
            logger.log(level, "%s: %s" % (self.location.tolongstring(), str(self)))
        else:
            logger.log(level, str(self))

    def tojson(self):  # type: (...) -> JSONDict
        """
        Converts the :class:`TestError` instance into a JSON dictionary.

        :return: JSON dictionary.
        """
        _json = {
            "message": self.message,
        }  # type: JSONDict
        if self.location:
            _json["location"] = self.location.tolongstring()
        return _json

    @staticmethod
    def fromjson(
            json_data,  # type: JSONDict
    ):  # type: (...) -> TestError
        """
        Builds a :class:`TestError` instance from its JSON representation.

        :param json_data: JSON dictionary.
        :return: New :class:`TestError` instance.
        """
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
        from .locations import EXECUTION_LOCATIONS
        from .path import Path

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
        self.location = self.location  # type: CodeLocation

    def __str__(self):  # type: (...) -> str
        """
        Short representation of the exception error.

        Exception type + message.
        """
        return "%s: %s" % (self.exception_type, self.message)

    def logerror(
            self,
            logger,  # type: Logger
            level=logging.ERROR,  # type: int
    ):  # type: (...) -> None
        """
        Logs the exception traceback, if an exception is stored,
        or the available error info otherwise.

        :param logger: Logger to use for logging.
        :param level: Log level.
        """
        if self.exception:
            _traceback = "".join(self.exception.format())  # str
            for _line in _traceback.splitlines():  # type: str
                if _line:
                    logger.log(level, "  " + _line)
        else:
            TestError.logerror(self, logger, level=level)

    def tojson(self):  # type: (...) -> JSONDict
        _json = {
            "type": self.exception_type,
            "message": self.message,
            "location": self.location.tolongstring(),
        }  # type: JSONDict
        return _json

    @staticmethod
    def fromjson(
            json_data,  # type: JSONDict
    ):  # type: (...) -> ExceptionError
        """
        Builds a :class:`ExceptionError` instance from its JSON representation.

        :param json_data: JSON dictionary.
        :return: New :class:`ExceptionError` instance.
        """
        _error = ExceptionError(exception=None)  # type: ExceptionError
        _error.exception_type = json_data["type"]
        _error.message = json_data["message"]
        _error.location = CodeLocation.fromlongstring(json_data["location"])
        return _error


class KnownIssue(TestError):
    """
    Known issue object.
    """

    def __init__(
            self,
            issue_id,  # type: str
            message,  # type: str
    ):  # type: (...) -> None
        """
        Creates a known issue instance from the info given and the current execution stack.

        :param issue_id: Issue identifier.
        :param message: Error or warning message to display with.
        """
        from .locations import EXECUTION_LOCATIONS

        TestError.__init__(
            self,
            message=message,
            location=EXECUTION_LOCATIONS.fromcurrentstack(limit=1, fqn=True)[-1],
        )

        #: Issue identifier.
        self.issue_id = issue_id  # type: str

        #: Marker for known issues defined during initializers only.
        self.init_only = False

        # Redefine the type of :attr:`TestError.location` in order to explicitize it cannot be ``None`` for :class:`KnownIssue` instances.
        self.location = self.location  # type: CodeLocation

    def __str__(self):  # type: (...) -> str
        """
        Short representation of the known issue.

        Issue id + message.
        """
        return "Issue %s! %s" % (self.issue_id, self.message)

    def iswarning(self):  # type: (...) -> bool
        return True

    def tojson(self):  # type: (...) -> JSONDict
        """
        Converts the :class:`TestError` instance into a JSON dictionary.

        :return: JSON dictionary.
        """
        _json = {
            "type": "known-issue",
            "id": self.issue_id,
            "message": self.message,
            "location": self.location.tolongstring(),
        }  # type: JSONDict
        return _json

    @staticmethod
    def fromjson(
            json_data,  # type: JSONDict
    ):  # type: (...) -> TestError
        """
        Builds a :class:`KnownIssue` instance from its JSON representation.

        :param json_data: JSON dictionary.
        :return: New :class:`KnownIssue` instance.
        """
        from .locations import CodeLocation

        _known_issue = KnownIssue(
            issue_id=json_data["id"],
            message=json_data["message"],
        )  # type: KnownIssue
        _known_issue.location = CodeLocation.fromlongstring(json_data["location"])
        return _known_issue
