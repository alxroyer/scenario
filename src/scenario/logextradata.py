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
Logging extra data handling.
"""

import logging
import typing

# `StrEnum` used for inheritance.
from .enumutils import StrEnum


class LogExtraData(StrEnum):
    """
    Keys to can be used in the dictionary passed on in the ``extra`` parameter of the standard :mod:`logging` functions.
    """
    #: Current logger reference.
    #:
    #: Stores a class:`.logger.Logger` instance reference.
    #:
    #: Automatically set by :class:`.logfilters.LoggerLogFilter`
    #: so that :class:`.logformatter.LogFormatter`
    #: knows about the current :class:`.logger.Logger` instance
    #: when processing the log event.
    CURRENT_LOGGER = "_logger_"

    #: Long text mode option.
    #:
    #: When set, activates the *long text mode*.
    #:
    #: ``int`` that gives the maximum number of lines to display.
    LONG_TEXT_MAX_LINES = "_long_text_max_lines_"

    # === Extra flags ===

    #: Extra flag: Should date/time be displayed?
    #:
    #: ``True`` by default.
    #:
    #: Still depends on usual :mod:`logging` configurations.
    DATE_TIME = "_date_time_"

    #: Extra flag: May color be used? (console only)
    #:
    #: ``True`` by default.
    #:
    #: Still depends on usual :mod:`logging` configurations.
    COLOR = "_color_"

    #: Extra flag: Should the log level be displayed?
    #:
    #: ``True`` by default.
    LOG_LEVEL = "_log_level_"

    #: Extra flag: Should the scenario stack indentation be displayed?
    #:
    #: ``True`` by default.
    SCENARIO_STACK_INDENTATION = "_scenario_stack_indentation_"

    #: Extra flag: Should the main logger indentation be displayed?
    #:
    #: ``True`` by default.
    MAIN_LOGGER_INDENTATION = "_main_logger_indentation_"

    #: Extra flag: Should the main logger indentation be displayed?
    #:
    #: ``True`` by default.
    CLASS_LOGGER_INDENTATION = "_class_logger_indentation_"

    #: Extra flag: Should the log be applied a margin that makes it indented within the action/result block it belongs to?
    #:
    #: ``True`` by default.
    ACTION_RESULT_MARGIN = "_action_result_margin_"

    @staticmethod
    def extradata(
            extra,  # type: typing.Dict[LogExtraData, typing.Any]
    ):  # type: (...) -> typing.Dict[str, typing.Any]
        """
        Translates a {ExtraFlag: Any} dictionary into a :mod:`logging` compatible dictionary.

        The resulting dictionary basically deserves the ``extra`` parameter of :mod:`logging` functions.

        :param extra: Enumerate dictionary to translate.
        :return: :mod:`logging` compatible dictionary.
        """
        _dict = {}  # type: typing.Dict[str, typing.Any]
        for _enum in extra:  # type: LogExtraData
            _dict[str(_enum)] = extra[_enum]
        return _dict

    @staticmethod
    def get(
            record,  # type: logging.LogRecord
            key,  # type: LogExtraData
    ):  # type: (...) -> typing.Optional[typing.Any]
        """
        Retrieves extra data from a record.

        :param record: Record to look for extra data in.
        :param key: Extra data name to look for.
        :return: Extra data value if set, or ``None`` otherwise.
        """
        if hasattr(record, str(key)):
            return getattr(record, str(key))
        return None

    @staticmethod
    def set(
            record,  # type: logging.LogRecord
            key,  # type: LogExtraData
            value,  # type: typing.Any
    ):  # type: (...) -> typing.Any
        """
        Sets extra data with a record.

        :param record: Record to store extra data in.
        :param key: Extra data name to set.
        :param value: Extra data value.
        """
        setattr(record, str(key), value)
