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

import typing

import scenario.test
import scenario.text

# Steps:
from steps.internet import EnsureInternetConnection
from steps.pippackages import EnsurePipPackage


class Timezone001(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        scenario.test.TestCase.__init__(
            self,
            title="Timezones with ISO8601 datetimes and DST",
            objective="Check the `scenario.datetime.toiso8601()` and `scenario.datetime.fromiso8601()` functions handle timezone specifications, "
                      "with or without DST (Daylight Saving Time) shifts.",
            features=[],  # No specific feature.
        )

        self.addstep(CheckFromIso8601())
        self.addstep(CheckToIso8601())

        self.section("'pytz' not installed")
        if not EnsureInternetConnection.isup(self):
            # Avoid going through 'pytz' uninstallation when Internet is not available,
            # otherwise we may not be able to reinstall it afterwards.
            self.knownissue("(tmp)", "No internet connection: behaviour when 'pytz' missing not checked")
        else:
            self.addstep(EnsurePipPackage("pytz", "pytz", False))
            self.addstep(CheckTimezoneNames(pytz_installed=False))

        self.section("'pytz' installed")
        self.addstep(EnsurePipPackage("pytz", "pytz", True))
        self.addstep(CheckTimezoneNames(pytz_installed=True))


class CheckFromIso8601(scenario.test.Step):

    def step(self):  # type: (...) -> None
        self.STEP("ISO8601 timezone parsing")

        _iso8601_0 = "2020-01-01T00:00:00.000000+00:00"  # type: str
        _t0 = 0.0  # type: float
        if self.ACTION(f"Parse the {_iso8601_0!r} string with the `scenario.datetime.fromiso8601()` function. Let this timestamp t0."):
            _t0 = scenario.datetime.fromiso8601(_iso8601_0)
            self.evidence(f"Parsed timestamp: {_t0}")

        def _checkfromiso8601(iso8601_1, hours_before):  # type: (str, int) -> None
            _t1 = 0.0  # type: float
            if self.ACTION(f"Parse the {iso8601_1!r} string with the `scenario.datetime.fromiso8601()` function."):
                _t1 = scenario.datetime.fromiso8601(iso8601_1)
                self.evidence(f"Parsed timestamp: {_t1}")
            _hours_txt = scenario.text.Countable("hour", abs(hours_before))  # type: scenario.text.Countable
            if self.RESULT(f"The timestamp is {len(_hours_txt)} {_hours_txt} {'before' if hours_before > 0 else 'after'} t0."):
                self.assertnear(
                    _t1, _t0 - hours_before * 3600.0, margin=1e-6,
                    evidence=True,
                )
        _checkfromiso8601("2020-01-01T00:00:00.000000+01:00", 1)
        _checkfromiso8601("2020-01-01T00:00:00.000000+02:00", 2)
        _checkfromiso8601("2020-01-01T00:00:00.000000-01:00", -1)


class CheckToIso8601(scenario.test.Step):

    def step(self):  # type: (...) -> None
        self.STEP("ISO8601 timezone formatting")

        _iso8601_0 = "2020-01-01T00:00:00.000000+00:00"  # type: str
        _t0 = 0.0  # type: float
        if self.ACTION(f"Parse the {_iso8601_0!r} string with the `scenario.datetime.fromiso8601()` function. Let this timestamp t0."):
            _t0 = scenario.datetime.fromiso8601(_iso8601_0)
            self.evidence(f"Parsed timestamp: {_t0}")

        def _checktoiso8601(timezone, iso8601_start):  # type: (str, str) -> None
            _iso8601_1 = ""  # type: str
            if self.ACTION(f"Format t0 with the {timezone!r} timezone."):
                _iso8601_1 = scenario.datetime.toiso8601(_t0, timezone=timezone)
                self.evidence(f"ISO8601: {_iso8601_1!r}")
            if self.RESULT(f"The ISO8601 string starts with {iso8601_start!r}."):
                self.assertstartswith(
                    _iso8601_1, iso8601_start,
                    evidence=True,
                )
        _checktoiso8601("+01:00", "2020-01-01T01:00:00")
        _checktoiso8601("+02:00", "2020-01-01T02:00:00")
        _checktoiso8601("-01:00", "2019-12-31T23:00:00")


class CheckTimezoneNames(scenario.test.Step):

    def __init__(
            self,
            pytz_installed,  # type: bool
    ):  # type: (...) -> None
        scenario.test.Step.__init__(self)

        self.pytz_installed = pytz_installed  # type: bool

    def step(self):  # type: (...) -> None
        self.STEP("Timezone names")

        _iso8601_jan_0 = "2020-01-01T00:00:00.000000+00:00"  # type: str
        _jan0 = 0.0  # type: float
        if self.ACTION(f"Parse the {_iso8601_jan_0!r} string with the `scenario.datetime.fromiso8601()` function. Let this timestamp jan0."):
            _jan0 = scenario.datetime.fromiso8601(_iso8601_jan_0)
            self.evidence(f"jan0: {_jan0}")

        _iso8601_jul_0 = "2020-07-01T00:00:00.000000+00:00"  # type: str
        _jul0 = 0.0  # type: float
        if self.ACTION(f"Parse the {_iso8601_jul_0!r} string with the `scenario.datetime.fromiso8601()` function. Let this timestamp jul0."):
            _jul0 = scenario.datetime.fromiso8601(_iso8601_jul_0)
            self.evidence(f"jul0: {_jul0}")

        def _checktimezonename(
                name,  # type: str
                iso8601_jan_end,  # type: str
                iso8601_jul_end,  # type: str
                exception,  # type: bool
        ):  # type: (...) -> None
            _iso8601_1 = ""  # type: str
            _exception = None  # type: typing.Optional[Exception]

            if self.ACTION(f"{'Try to format' if exception else 'Format'} jan0 with the {name!r} timezone."):
                try:
                    _exception = None
                    _iso8601_1 = scenario.datetime.toiso8601(_jan0, timezone=name)
                    self.evidence(f"ISO8601: {_iso8601_1!r}")
                except Exception as _err:
                    _exception = _err

            if exception:
                if self.RESULT("An exception is raised."):
                    self.assertisnotnone(
                        _exception,
                        evidence=True,
                    )
            else:
                if self.RESULT("No exception is raised."):
                    self.assertisnone(
                        _exception,
                        evidence=True,
                    )
                if self.RESULT(f"The ISO8601 string ends with {iso8601_jan_end!r}."):
                    self.assertendswith(
                        _iso8601_1, iso8601_jan_end,
                        evidence=True,
                    )

            if self.ACTION(f"{'Try to format' if exception else 'Format'} jul0 with the {name!r} timezone."):
                try:
                    _exception = None
                    _iso8601_1 = scenario.datetime.toiso8601(_jul0, timezone=name)
                    self.evidence(f"ISO8601: {_iso8601_1!r}")
                except Exception as _err:
                    _exception = _err

            if exception:
                if self.RESULT("An exception is raised."):
                    self.assertisnotnone(
                        _exception,
                        evidence=True,
                    )
            else:
                if self.RESULT("No exception is raised."):
                    self.assertisnone(
                        _exception,
                        evidence=True,
                    )
                if self.RESULT(f"The ISO8601 string ends with {iso8601_jul_end!r}."):
                    self.assertendswith(
                        _iso8601_1, iso8601_jul_end,
                        evidence=True,
                    )

        # Numerical descriptions always work, with no DST shifts.
        _checktimezonename("+00:00", "+00:00", "+00:00", exception=False)
        _checktimezonename("-05:30", "-05:30", "-05:30", exception=False)

        # Well-known UTC descriptions always work as well, no DST shifts neither.
        _checktimezonename("Z", "+00:00", "+00:00", exception=False)
        _checktimezonename("UTC", "+00:00", "+00:00", exception=False)

        # 'pytz' timezone support, depending on 'pytz' installation.
        _checktimezonename("CET", "+01:00", "+02:00", exception=not self.pytz_installed)  # CET = Central European Time.
        _checktimezonename("US/Eastern", "-05:00", "-04:00", exception=not self.pytz_installed)
        _checktimezonename("US/Western", "-08:00", "-07:00", exception=True)  # 'US/Western' does not exist, but 'US/Pacific'.
        _checktimezonename("US/Pacific", "-08:00", "-07:00", exception=not self.pytz_installed)
        _checktimezonename("Japan", "+09:00", "+09:00", exception=not self.pytz_installed)  # No DST shift for Japan.
