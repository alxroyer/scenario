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
Command line error codes.

Error codes returned by the :class:`._scenariorunner.ScenarioRunner` or :class:`._campaignrunner.CampaignRunner` programs.
"""

import enum
import typing


class ErrorCode(enum.IntEnum):
    """
    Error codes enum.

    .. note:: Codes inspired from HTTP status codes, but with error codes less than 256.

       - 20-29: Normal errors.
       - 40-49: Input related errors.
       - 50-59: Processing and output related errors.
    """

    #: Success.
    SUCCESS = 0
    #: When one or several tests failed.
    TEST_ERROR = 21

    #: Errors due to the environnement.
    ENVIRONMENT_ERROR = 40
    #: Errors due to invalid arguments.
    ARGUMENTS_ERROR = 41

    #: Errors due to missing inputs.
    INPUT_MISSING_ERROR = 42
    #: Errors due to invalid input format.
    INPUT_FORMAT_ERROR = 43

    #: Internal error.
    INTERNAL_ERROR = 50

    @staticmethod
    def fromexception(
            exception,  # type: Exception
    ):  # type: (...) -> ErrorCode
        """
        Computes a :class:`ErrorCode` value from an exception.

        :param exception: Exception to compute a :class:`ErrorCode` value for.
        :return: Error code computed.
        """
        from ._testerrors import TestError

        if isinstance(exception, ErrorCodeError):
            return exception.error_code
        if isinstance(exception, TestError):
            return ErrorCode.TEST_ERROR
        if isinstance(exception, EnvironmentError):
            return ErrorCode.ENVIRONMENT_ERROR

        # Default to internal error.
        return ErrorCode.INTERNAL_ERROR

    @staticmethod
    def worst(
            error_codes,  # type: typing.List[ErrorCode]
    ):  # type: (...) -> ErrorCode
        """
        Returns the worst error code from the list.

        The higher the error value, the worse.

        :param error_codes: List to find the worst error code from. May be empty.
        :return: Worst error code. :const:`ErrorCode.SUCCESS` by default.
        """
        _res = ErrorCode.SUCCESS  # type: ErrorCode
        for _error in error_codes:  # type: ErrorCode
            if int(_error) > int(_res):
                _res = _error
        return _res


class ErrorCodeError(Exception):
    """
    Exception that holds a :class:`ErrorCode` value.
    """

    @staticmethod
    def fromexception(
            exception,  # type: Exception
    ):  # type: (...) -> ErrorCodeError
        """
        Builds a :class:`ErrorCodeError` from a cause exception.

        :param exception: Exception to create a :class:`ErrorCodeError` from.
        :return: :class:`ErrorCodeError` exception created.
        """
        return ErrorCodeError(
            error_code=ErrorCode.fromexception(exception),
            message=str(exception),
            exception=exception,
        )

    def __init__(
            self,
            error_code,  # type: ErrorCode
            message,  # type: str
            *,
            exception=None,  # type: Exception
    ):  # type: (...) -> None
        """
        Initializes error code and message, with optional exception.

        :param error_code: Error code to save with this :class:`ErrorCodeError`.
        :param message: Descriptive message.
        :param exception: Optional related exception.
        """
        Exception.__init__(self, f"{error_code.name}({error_code.value}): {message}")

        #: Error code held by the exception.
        self.error_code = error_code  # type: ErrorCode
        #: Optional related exception.
        self.exception = exception  # type: typing.Optional[Exception]
