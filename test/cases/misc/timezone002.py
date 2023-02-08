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

import scenario
import scenario.test

# Steps:
from steps.pippackages import EnsurePipPackage


class Timezone002(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        scenario.test.TestCase.__init__(
            self,
            title="Timezone configuration",
            objective=f"Check the `scenario.datetime.toiso8601()` takes into account the '{scenario.ConfigKey.TIMEZONE}' configuration.",
            features=[],  # No specific feature.
        )

        self.section("Numerical timezones")
        self.addstep(CheckTimezoneConfig("+00:00", "2020-01-01T00:00:00.000000+00:00"))
        self.addstep(CheckTimezoneConfig("+01:00", "2020-01-01T01:00:00.000000+01:00"))
        self.addstep(CheckTimezoneConfig("-01:00", "2019-12-31T23:00:00.000000-01:00"))

        self.section("Literal timezones")
        self.addstep(EnsurePipPackage("pytz", "pytz", True))
        self.addstep(CheckTimezoneConfig("UTC", "2020-01-01T00:00:00.000000+00:00"))
        self.addstep(CheckTimezoneConfig("Z", "2020-01-01T00:00:00.000000+00:00"))
        self.addstep(CheckTimezoneConfig("CET", "2020-01-01T01:00:00.000000+01:00"))
        self.addstep(CheckTimezoneConfig("US/Eastern", "2019-12-31T19:00:00.000000-05:00"))
        self.addstep(CheckTimezoneConfig("US/Pacific", "2019-12-31T16:00:00.000000-08:00"))
        self.addstep(CheckTimezoneConfig("Japan", "2020-01-01T09:00:00.000000+09:00"))


class CheckTimezoneConfig(scenario.test.Step):

    def __init__(
            self,
            tz_config,  # type: str
            iso8601,  # type: str
    ):  # type: (...) -> None
        scenario.test.Step.__init__(self)

        self.tz_config = tz_config  # type: str
        self.expected_iso8601 = iso8601  # type: str

    def step(self):  # type: (...) -> None
        self.STEP(f"{self.tz_config!r} timzeone configuration")

        _iso8601_0 = "2020-01-01T00:00:00.000000+00:00"  # type: str
        _t0 = 0.0  # type: float
        if self.ACTION(f"Parse the {_iso8601_0!r} string with the `scenario.datetime.fromiso8601()` function. Let this timestamp t0."):
            _t0 = scenario.datetime.fromiso8601(_iso8601_0)
            self.evidence(f"Parsed timestamp: {_t0}")

        if self.ACTION(f"Configure {self.tz_config!r} as the '{scenario.ConfigKey.TIMEZONE}' configuration."):
            scenario.conf.set(scenario.ConfigKey.TIMEZONE, self.tz_config)

        _iso8601_1 = ""  # type: str
        if self.ACTION("Compute the ISO8601 date for t0, without specifying a timezone."):
            _iso8601_1 = scenario.datetime.toiso8601(_t0, timezone=None)
            self.evidence(f"ISO8601: {_iso8601_1!r}")

        if self.RESULT(f"The ISO8601 date computed is {self.expected_iso8601!r}."):
            self.assertequal(
                _iso8601_1, self.expected_iso8601,
                evidence=True,
            )
