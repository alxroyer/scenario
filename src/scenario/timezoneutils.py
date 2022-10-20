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
Timezone handling.
"""

import datetime
import re
import sys
import typing


__doc__ += """
.. py:attribute:: UTC

    UTC timezone constant.
"""
# Inspired from https://stackoverflow.com/questions/2720319/python-figure-out-local-timezone#39079819
if sys.version_info >= (3, 6):
    UTC = datetime.timezone.utc  # type: datetime.tzinfo
else:
    UTC = datetime.timezone(datetime.timedelta(0))


def local(
        ref_timestamp,  # type: float
):  # type: (...) -> datetime.tzinfo
    """
    Returns the local timezone for the given timestamp.

    :param ref_timestamp: Reference timestamp to compute the local timezone for.
    :return: Local timezone (fixed time offset, non DST-aware).

    .. warning::
        The timezone returned is a fixed time offset,
        i.e. it does not handle DST (Daylight Saving Time) shifts.

        That's the reason why the ``ref_timestamp`` must be set appropriately
        in order to avoid errors between summer and winter times.
    """
    # Inspired from https://stackoverflow.com/questions/2720319/python-figure-out-local-timezone#39079819
    _dt = datetime.datetime.fromtimestamp(ref_timestamp).astimezone()  # type: datetime.datetime
    assert _dt.tzinfo is not None
    return _dt.tzinfo


def fromstr(
        tz_desc,  # type: typing.Optional[str]
):  # type: (...) -> typing.Optional[datetime.tzinfo]
    """
    Computes a timezone information from an optional string.

    :param tz_desc: Optional timezone description.
    :return: Timezone information when ``tz_desc`` is set, ``None`` otherwise.
    """
    # When the timezone description is `None`, consider the local timezone by default.
    if tz_desc is None:
        # Because the current date's tzinfo is a fixed time offset that does not handle DST (Daylight Saving Time) shifts,
        # it is worse trying to return a local timezone than returning `None`.
        # return local(time.time())
        return None

    # Well-known UTC descriptions.
    if tz_desc in ("UTC", "Z"):
        return UTC

    # When the timezone is described as a '[+-]0000' or '[+-]00:00' pattern, as usually
    _match = re.match(r"(\+|-|)(\d{2})(:|)(\d{2})", tz_desc)  # type: typing.Optional[typing.Match[str]]
    if _match:
        _sign = -1 if _match.group(1) == "-" else 1  # type: int
        _hours = int(_match.group(2))  # type: int
        _minutes = int(_match.group(4))  # type: int
        return datetime.timezone(datetime.timedelta(
            hours=_sign * _hours,
            minutes=_sign * _minutes,
        ))

    # Rely on the 'pytz' module by default.
    try:
        import pytz  # type: ignore  ## Library stubs not installed for "pytz"

        return pytz.timezone(  # type: ignore  ## Returning Any from function declared to return "Optional[tzinfo]"
            tz_desc,
        )
    except ImportError as _err:
        raise ImportError(f"{_err}, cannot parse timezone {tz_desc!r}")
