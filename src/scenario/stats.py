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
Common statistics.
"""

import time
import typing

if typing.TYPE_CHECKING:
    from .typing import JsonDictType


class TimeStats:
    """
    Common time statistics.
    """

    def __init__(self):  # type: (...) -> None
        """
        Initializes the time statistics with ``None`` values.
        """
        #: Start time, if specified.
        self._start = None  # type: typing.Optional[float]
        #: Elapsed time, if specified.
        self._elapsed = None  # type: typing.Optional[float]
        #: End time, if specified.
        self._end = None  # type: typing.Optional[float]

    def __str__(self):  # type: () -> str
        """
        Computes a string representation of the time interval in the '[%s - %s]' form.

        :return: String representation of the time interval.
        """
        from .datetimeutils import f2strtime

        return f"[{f2strtime(self.start)} - {f2strtime(self.end)}]"

    @property
    def start(self):  # type: () -> typing.Optional[float]
        """
        *Start* time getter.
        """
        if self._start is None:
            # Try to compute from *end* and *elapsed* times.
            if (self._end is not None) and (self._elapsed is not None):
                return self._end - self._elapsed

        return self._start

    @start.setter
    def start(self, start):  # type: (float) -> None
        """
        *Start* time setter.

        Invalidates the *elapsed* time if *elapsed* and *end* are already both set.
        """
        self._start = start

        # Possibly invalidate the *elapsed* time.
        if (self._elapsed is not None) and (self._end is not None):
            self._elapsed = None

    @property
    def elapsed(self):  # type: () -> typing.Optional[float]
        """
        *Elapsed* time getter.
        """
        if self._elapsed is None:
            # Try to compute from *start* and *end* times.
            if (self.start is not None) and (self.end is not None):
                return self.end - self.start

        return self._elapsed

    @elapsed.setter
    def elapsed(self, elapsed):  # type: (float) -> None
        """
        *Elapsed* time setter.

        Invalidates the *end* time if *start* and *end* are already both set.
        """
        self._elapsed = elapsed

        # Possibly invalidate the *end* time.
        if (self._start is not None) and (self._end is not None):
            self._end = None

    @property
    def end(self):  # type: () -> typing.Optional[float]
        """
        *End* time getter.
        """
        if self._end is None:
            # Try to compute from *start* and *elapsed* times.
            if (self._start is not None) and (self._elapsed is not None):
                return self._start + self._elapsed

        return self._end

    @end.setter
    def end(self, end):  # type: (float) -> None
        """
        *End* time setter.

        Invalidates the *elapsed* time if *start* and *elapsed* are already both set.
        """
        self._end = end

        # Possibly invalidate the *elapsed* time.
        if (self._elapsed is not None) and (self._end is not None):
            self._elapsed = None

    def setstarttime(self):  # type: (...) -> None
        """
        Starts the time statistics with the current time.
        """
        # Don't use the :attr:`start` setter.
        # Set all values as expected when this method is called.
        self._start = time.time()
        self._elapsed = None
        self._end = None

    def setendtime(self):  # type: (...) -> None
        """
        Ends the time statistics with the current time.
        """
        # This method should follow a :meth:`setstarttime()` call.
        # In any, let's use the :attr:`end` setter this time in order to ensure everything is consistent whatever.
        self.end = time.time()

    def tojson(self):  # type: (...) -> JsonDictType
        """
        Converts the :class:`TimeStats` instance into a JSON dictionary.

        :return: JSON dictionary, with optional 'start', 'end' and 'elapsed' ``float`` fields, when the values are set.
        """
        from .datetimeutils import toiso8601

        _json = {"start": None, "end": None, "elapsed": None}  # type: JsonDictType
        if self.start is not None:
            _json["start"] = toiso8601(self.start)
        if self.end is not None:
            _json["end"] = toiso8601(self.end)
        if self.elapsed is not None:
            _json["elapsed"] = self.elapsed
        return _json

    @staticmethod
    def fromjson(
            json_data,  # type: JsonDictType
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
        # Let it be recomputed from 'start' and 'end' values.
        return _stat


class ExecTotalStats:
    """
    Executable item statistics: number of executed items over a total count.
    """

    def __init__(self):  # type: (...) -> None
        """
        Initializes the count statistics with ``0``.
        """
        #: Total count of executable items.
        self.total = 0  # type: int
        #: Count of items executed.
        self.executed = 0  # type: int

    def __str__(self):  # type: () -> str
        """
        Computes a '%d' or '%d/%d' string representation of the statistics,
        depending on the :attr:`.args.Args.doc_only` parameter.

        :return: String representation of the statistics.
        """
        from .scenarioargs import ScenarioArgs
        from .campaignargs import CampaignArgs

        if ScenarioArgs.isset() and ScenarioArgs.getinstance().doc_only:
            return f"{self.total}"
        elif CampaignArgs.isset() and CampaignArgs.getinstance().doc_only:
            return f"{self.total}"
        else:
            return f"{self.executed}/{self.total}"

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

    def tojson(self):  # type: (...) -> JsonDictType
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
            json_data,  # type: JsonDictType
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
