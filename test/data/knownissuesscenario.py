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


class KnownIssuesScenario(scenario.Scenario):

    class ConfigKey(scenario.enum.StrEnum):
        RAISE_EXCEPTIONS = "scenario.test.KnownIssues.raise_exceptions"

    def __init__(self):  # type: (...) -> None
        scenario.Scenario.__init__(self)

        self.setattribute("TITLE", "Known issue scenario sample")

        self.raise_exceptions = scenario.conf.get(KnownIssuesScenario.ConfigKey.RAISE_EXCEPTIONS, type=bool, default=False)  # type: bool

        self.knownissue(id="#---", message="Known issue in KnownIssuesScenario.__init__()")  # location: #---
        self.addstep(KnownIssuesScenario.KnownIssuesStep())

    class KnownIssuesStep(scenario.Step):  # location: KnownIssuesStep

        def __init__(self):  # type: (...) -> None
            scenario.Step.__init__(self)

            self.knownissue(id="#000", message="Known issue in KnownIssuesStep.__init__()")  # location: #000

        def step(self):  # type: (...) -> None
            self.STEP("Object step with known issues")

            self.knownissue(id="#001", message="Known issue in KnownIssuesStep.step() before ACTION/RESULT")  # location: #001

            if self.ACTION("Track a known issue."):
                self.knownissue(id="#002", message="Known issue in KnownIssuesStep.step() under ACTION")  # location: #002

            if self.ACTION("Raise an exception."):
                if KnownIssuesScenario.getinstance().raise_exceptions:
                    self.fail("This is an exception.")  # location: Step-fail
                else:
                    self.evidence("Exception not raised.")

            if self.ACTION("Track another known issue."):
                self.knownissue(id="#003", message="Known issue in KnownIssuesStep.step() under ACTION")  # location: #003

            self.knownissue(id="#004", message="Known issue in KnownIssuesStep.step() after ACTION/RESULT")  # location: #004

    def step010(self):  # type: (...) -> None  # location: step010
        self.STEP("Method step with known issues")

        self.knownissue(id="#011", message="Known issue in KnownIssuesScenario.step010() before ACTION/RESULT")  # location: #011

        if self.ACTION("Track a known issue."):
            self.knownissue(id="#012", message="Known issue in KnownIssuesScenario.step010() under ACTION")  # location: #012

        if self.ACTION("Raise an exception."):
            if self.raise_exceptions:
                self.fail("This is an exception.")  # location: step010-fail
            else:
                self.evidence("Exception not raised.")

        if self.ACTION("Track another known issue."):
            self.knownissue(id="#013", message="Known issue in KnownIssuesScenario.step010() under ACTION")  # location: #013

        self.knownissue(id="#014", message="Known issue in KnownIssuesScenario.step010() after ACTION/RESULT")  # location: #014

    def step020(self):  # type: (...) -> None  # location: step020
        self.STEP("Method step without known issues")

        self.ACTION("Do nothing.")
