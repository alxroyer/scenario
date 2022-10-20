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

import time

import scenario.test


class DateTime001(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        scenario.test.TestCase.__init__(
            self,
            title="Date/time ISO8601 formatting & parsing",
            objective="Check the `scenario.datetime.toiso8601()` and `scenario.datetime.fromiso8601()` functions.",
            features=[],  # No specific feature.
        )

    def step001(self):  # type: (...) -> None
        self.STEP("ISO8601 -> float -> ISO8601")

        _iso8601_0 = "2020-01-01T00:00:00.000000+00:00"  # type: str
        _t = 0.0  # type: float
        if self.ACTION("Parse the '%s' string with the `scenario.datetime.fromiso8601()` function." % _iso8601_0):
            _t = scenario.datetime.fromiso8601(_iso8601_0)
            self.evidence("Parsed timestamp: %f" % _t)

        _iso8601_1 = ""  # type: str
        if self.ACTION("Format the timestamp with the `scenario.datetime.toiso8601()` function."):
            _iso8601_1 = scenario.datetime.toiso8601(_t)
            self.evidence("ISO8601: '%s'" % _iso8601_1)

        if self.RESULT("The two ISO8601 strings are the same."):
            self.assertequal(
                _iso8601_1, _iso8601_0,
                evidence=True,
            )

    def step002(self):  # type: (...) -> None
        self.STEP("float -> ISO8601 -> float")

        _t0 = 0.0  # type: float
        if self.ACTION("Get the current timestamp."):
            _t0 = time.time()
            self.evidence("Current timestamp: %f" % _t0)

        _iso8601 = ""  # type: str
        if self.ACTION("Format the timestamp with the `scenario.datetime.toiso8601()` function."):
            _iso8601 = scenario.datetime.toiso8601(_t0)
            self.evidence("ISO8601: '%s'" % _iso8601)

        _t1 = 0.0  # type: float
        if self.ACTION("Parse the ISO8601 string with the `scenario.datetime.fromiso8601()` function."):
            _t1 = scenario.datetime.fromiso8601(_iso8601)
            self.evidence("Parsed timestamp: %f" % _t1)

        if self.RESULT("The parsed timestamp equals the original one."):
            self.assertnear(
                _t1, _t0, margin=1e-6,
                evidence=True,
            )
