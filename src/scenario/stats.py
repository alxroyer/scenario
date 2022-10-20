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
Common statistics.
"""

import time
import typing

if typing.TYPE_CHECKING:
    # `JSONDict` used in method signatures.
    # Type declared for type checking only.
    from .typing import JSONDict


class TimeStats:
    """
    Common time statistics.
    """

    def __init__(self):  # type: (...) -> None
        """
        Initializes the time statistics with :const:`None` values.
        """
        #: Start time.
        self.start = None  # type: typing.Optional[float]
        #: End time.
        self.end = None  # type: typing.Optional[float]
        #: Elapsed time.
        self.elapsed = None  # type: typing.Optional[float]

    def __str__(self):  # type: (...) -> str
        """
        Computes a string representation of the time interval in the '[%s - %s]' form.

        :return: String representation of the time interval.
        """
        from .datetimeutils import f2strtime

        return "[%s - %s]" % (f2strtime(self.start), f2strtime(self.end))

    def setstarttime(self):  # type: (...) -> None
        """
        Starts the time statistics.
        """
        self.start = time.time()
        self.end = None
        self.elapsed = None

    def setendtime(self):  # type: (...) -> None
        """
        Ends the time statistics.
        """
        self.end = time.time()
        if self.start is not None:
            self.elapsed = self.end - self.start

    def tojson(self):  # type: (...) -> JSONDict
        """
        Converts the :class:`TimeStats` instance into a JSON dictionary.

        :return: JSON dictionary, with optional 'start', 'end' and 'elapsed' ``float`` fields, when the values are set.
        """
        from .datetimeutils import toiso8601

        _json = {"start": None, "end": None, "elapsed": None}  # type: JSONDict
        if self.start is not None:
            _json["start"] = toiso8601(self.start)
        if self.end is not None:
            _json["end"] = toiso8601(self.end)
        if (self.start is not None) and (self.end is not None):
            _json["elapsed"] = self.end - self.start
        return _json

    @staticmethod
    def fromjson(
            json_data,  # type: JSONDict
    ):  # type: (...) -> TimeStats
        """
        Builds a :class:`TimeStats` instance from its JSON representation.

        :param json_data: JSON dictionary, with optional 'start', 'end' and 'elapsed' ``float`` fields.
        :return: New :class:`TimeStats` instance.
        """
        from .datetimeutils import fromiso8601
        from .loggermain import MAIN_LOGGER

        _stat = TimeStats()  # type: TimeStats
        if ("start" in json_data) and isinstance(json_data["start"], str):
            try:
                _stat.start = fromiso8601(json_data["start"])
            except Exception as _err:
                MAIN_LOGGER.warning(str(_err))
        if ("end" in json_data) and isinstance(json_data["end"], str):
            try:
                _stat.end = fromiso8601(json_data["end"])
            except Exception as _err:
                MAIN_LOGGER.warning(str(_err))
        # Do not rely on the input 'elapsed' field if given.
        # Recompute from 'start' and 'end' values.
        if (_stat.start is not None) and (_stat.end is not None):
            _stat.elapsed = _stat.end - _stat.start
        return _stat


class ExecTotalStats:
    """
    Executable item statistics: number of executed items over a total count.
    """

    def __init__(self):  # type: (...) -> None
        """
        Initializes the count statistics with :const:`0`.
        """
        #: Total count of executable items.
        self.total = 0  # type: int
        #: Count of items executed.
        self.executed = 0  # type: int

    def __str__(self):  # type: (...) -> str
        """
        Computes a '%d' or '%d/%d' string representation of the statistics,
        depending on the :attr:`.args.Args.doc_only` parameter.

        :return: String representation of the statistics.
        """
        from .scenarioargs import ScenarioArgs
        from .campaignargs import CampaignArgs

        if ScenarioArgs.isset() and ScenarioArgs.getinstance().doc_only:
            return "%d" % self.total
        elif CampaignArgs.isset() and CampaignArgs.getinstance().doc_only:
            return "%d" % self.total
        else:
            return "%d/%d" % (self.executed, self.total)

    def add(
            self,
            stats,  # type: ExecTotalStats
    ):  # type: (...) -> ExecTotalStats
        """
        Integrates a tier :class:`ExecTotalStats` instance into this one.

        :param stats: Tier :class:`ExecTotalStats` instance.
        :return: Self (named parameter idiom).

        Increments both *executed* and *total* counts with the tier's values.
        """
        self.total += stats.total
        self.executed += stats.executed
        return self

    def tojson(self):  # type: (...) -> JSONDict
        """
        Converts the :class:`ExecTotalStats` instance into a JSON dictionary.

        :return: JSON dictionary, with 'executed' and 'total' ``int`` fields.
        """
        return {
            "executed": self.executed,
            "total": self.total
        }

    @staticmethod
    def fromjson(
            json_data,  # type: JSONDict
    ):  # type: (...) -> ExecTotalStats
        """
        Builds a :class:`ExecTotalStats` instance from its JSON representation.

        :param json_data: JSON dictionary, with 'executed' and 'total' ``int`` fields.
        :return: New :class:`ExecTotalStats` instance.
        """
        _stat = ExecTotalStats()  # type: ExecTotalStats
        if ("executed" in json_data) and isinstance(json_data["executed"], int):
            _stat.executed = json_data["executed"]
        if ("total" in json_data) and isinstance(json_data["total"], int):
            _stat.total = json_data["total"]
        return _stat
