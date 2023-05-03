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
    #: When a test failed.
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
    def worst(
            error_codes,  # type: typing.List[ErrorCode]
    ):  # type: (...) -> ErrorCode
        """
        Returns the worst error code from the list.

        The higher the error value, the worse.

        :param error_codes: List to find the worst error code from.
        :return: Worst error code.
        """
        _res = ErrorCode.SUCCESS  # type: ErrorCode
        for _error in error_codes:  # type: ErrorCode
            if int(_error) > int(_res):
                _res = _error
        return _res
