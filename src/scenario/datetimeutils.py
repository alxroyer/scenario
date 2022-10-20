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
Date/time conversions from timestamp to ISO8601.

.. note::
    This modules intends to centralize date/time conversions from timestamp to ISO8601, which remains a pain in Python.
    Indeed, full support of timezones with their 'Zoulou' or '+/-00:00' forms is not provided by default.
"""

import datetime
import math
import re
import sys
import time
import typing


__doc__ += """
.. py:attribute:: ISO8601_REGEX

    Regular expression matching ISO8601 date/times.
"""
ISO8601_REGEX = r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{3,}[+-][0-9]{2}:[0-9]{2}"  # type: str


def toiso8601(
        timestamp,  # type: float
):  # type: (...) -> str
    """
    Formats a timestamp to a UTC ISO8601 string.

    :param timestamp: Input timestamp.
    :return: UTC ISO8601 string.
    :raise ValueError: When the operation could not be completed.
    """
    assert sys.version_info >= (3, 6)
    return (
        datetime.datetime.fromtimestamp(timestamp)
        # Let's use the .astimezone() method in order to attach a .tzinfo with the datetime object.
        .astimezone(datetime.timezone.utc)
        # .isoformat() then adds a final "+00:00" pattern for the UTC timezone specification.
        # The 'microseconds' time spec ensures microseconds are formatted even though equal to 0.
        .isoformat(timespec="microseconds")
    )


def fromiso8601(
        iso8601,  # type: str
):  # type: (...) -> float
    """
    Parses a UTC ISO8601 string in a timestamp.

    :param iso8601: Input UTC ISO8601 string.
    :return: Timestamp.
    :raise ValueError: When the operation could not be completed.
    """
    if sys.version_info >= (3, 7):
        # `datetime.datetime.fromisoformat()` exists from Python 3.7 only.

        # Since the string gives the "+00:00" timezone specification in the end,
        # the `datetime.datetime.fromisoformat()` method will handle the timezone,
        # and the timestamp() will be applied the appropriate offset.
        return (
            datetime.datetime.fromisoformat(iso8601)
            .timestamp()
        )
    else:
        # Fix the ISO8601 timezone specification from ISO8601 to `datetime` format,
        # so that we can use the '%z' format specification for `datetime.datetime.strptime()` to handle it.
        # See: https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
        if iso8601.endswith("+00:00"):
            iso8601 = iso8601[:-len("+00:00")] + "+0000"

        return (
            datetime.datetime.strptime(iso8601, "%Y-%m-%dT%H:%M:%S.%f%z")
            .timestamp()
        )


def f2strtime(
        timestamp,  # type: typing.Optional[float]
):  # type: (...) -> str
    """
    Computes a string representation for the given timestamp.

    :param timestamp: Timestamp to convert.
    :return: String representation of the timestamp.
    """
    _str_time = repr(timestamp)  # type: str
    if timestamp is not None:
        _str_time = toiso8601(timestamp)
        # Remove the timezone info.
        _str_time = _str_time[:-len("+00:00")]
        # When the timestamp is within the latest 24 hours, remove the date info.
        if timestamp > time.time() - (24.0 * 60.0 * 60.0):
            _str_time = _str_time[len("YYYY-MM-DDT"):]
    return _str_time


def f2strduration(
        duration,  # type: typing.Optional[float]
):  # type: (...) -> str
    """
    Computes a string representation for a time duration.

    :param duration: Time duration to convert.
    :return: String representation of the duration.
    """
    _duration = repr(duration)  # type: str
    if duration is not None:
        _hours = int(duration / 3600.0)  # type: int
        duration -= _hours * 3600.0
        _minutes = int(duration / 60.0)  # type: int
        duration -= _minutes * 60.0
        _seconds = int(duration / 1.0)  # type: int
        duration -= _seconds * 1.0
        _micros = int(duration * 1000000.0)  # type: int
        _duration = "%02d:%02d:%02d.%06d" % (_hours, _minutes, _seconds, _micros)
    return _duration


def str2fduration(
        duration,  # type: str
):  # type: (...) -> float
    """
    Parses a time duration from its string representation as computed by :func:`f2strduration()`.

    :param duration: String representation of the time duration as computed by :func:`f2strduration()`.
    :return: Time duration.
    """
    _match = re.match(r"^(\d+):(\d+):(\d+)\.(\d+)$", duration)  # type: typing.Optional[typing.Match[str]]
    assert _match, "'%s' invalid duration format" % duration
    return (
        int(_match.group(1)) * 3600.0
        + int(_match.group(2)) * 60.0
        + int(_match.group(3)) * 1.0
        + int(_match.group(4)) / math.pow(10, len(_match.group(4)))
    )
