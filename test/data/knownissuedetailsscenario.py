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

import typing

import scenario


class KnownIssueDetailsScenario(scenario.Scenario):

    class ConfigKey(scenario.enum.StrEnum):
        LEVEL = "scenario.test.KnownIssue.level"
        ID = "scenario.test.KnownIssue.id"
        URL_BASE = "scenario.test.KnownIssue.url_base"

    def __init__(self):  # type: (...) -> None
        scenario.Scenario.__init__(self)

        self.setattribute("TITLE", "Known issue details scenario sample")

    def step010(self):  # type: (...) -> None
        from scenario.scenarioconfig import SCENARIO_CONFIG

        self.STEP("Known issue details")

        if self.ACTION("Track the error issue level threshold."):
            self.evidence(f"Error issue level threshold: {SCENARIO_CONFIG.issuelevelerror()!r}")

        if self.ACTION("Track the ignored issue level threshold."):
            self.evidence(f"Ignored issue level threshold: {SCENARIO_CONFIG.issuelevelignored()!r}")

        _url_base = scenario.conf.get(self.ConfigKey.URL_BASE, type=str)  # type: typing.Optional[str]
        if _url_base:
            if self.ACTION(f"Install a URL builder handler with {_url_base!r}."):
                def _urlbuilder(issue_id):  # type: (str) -> typing.Optional[str]
                    assert _url_base
                    return f"{_url_base.rstrip('/')}/{issue_id.lstrip('#')}"
                scenario.KnownIssue.seturlbuilder(_urlbuilder)

        if self.ACTION(f"Read the '{self.ConfigKey.LEVEL}' and '{self.ConfigKey.ID}' configurations "
                       "and track a known issue with this info."):
            _level = scenario.IssueLevel.parse(
                scenario.conf.get(self.ConfigKey.LEVEL, type=int)
            )  # type: typing.Optional[scenario.AnyIssueLevelType]
            # Note: Work with `int` values only in order to stay independent from issue level name settings.
            if _level is not None:
                _level = int(_level)
            self.evidence(f"{self.ConfigKey.LEVEL} = {_level!r}")

            _id = scenario.conf.get(self.ConfigKey.ID, type=str)  # type: typing.Optional[str]
            self.evidence(f"{self.ConfigKey.ID} = {_id!r}")

            self.knownissue(
                level=_level,
                id=_id,
                message=f"Known issue with level {_level!r} and id {_id!r}",
            )
