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

import scenario.test


class ConfigDb120(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        from configdb.steps.currentprocess import CheckConfigValue, CheckDictConfigNode, CheckListConfigNode, LoadConfigFile, ShowConfigValue

        scenario.test.TestCase.__init__(
            self,
            title="INI default values & sub-sections",
            description="Check the way sub-sections are emulated in INI files, and default values are propagated along sections.",
        )
        self.covers(
            scenario.test.reqs.CONFIG_DB,
        )

        # Make this scenario continue on errors, in order to make sure temporary configuration keys are removed in the end.
        self.continue_on_error = True

        self.knownissue(
            level=scenario.test.IssueLevel.SUT, id="#44",
            message="Implicit INI sections don't inherit from default values",
        )

        self.section("Load INI file")
        self.tmp_root_key = scenario.Path(__file__).stem  # type: str
        self.addstep(LoadConfigFile(scenario.test.paths.datapath("conf.ini"), root_key=self.tmp_root_key))
        self.addstep(ShowConfigValue(self.tmp_root_key))

        self.section("Root section: 'a' and 'x' main sections")
        # Do not check that the root node only has 'a' and 'x' sub-sections in as much as other things may be set in the configuration database,
        # either due to previous tests executed in the same commad line,
        # or due to `scenario` configurations when executed within a campaign.
        # self.addstep(CheckDictConfigNode("", ["a", "x"]))

        self.section("Implicit section 'a': sub-section 'b', but no default values (issue #xxx)")
        self.addstep(CheckDictConfigNode(f"{self.tmp_root_key}.a", ["b"]))

        self.section("Explicit sub-section 'a.b': final values 'c1' and 'c2', and default value 'd' overriden")
        self.addstep(CheckDictConfigNode(f"{self.tmp_root_key}.a.b", ["c1", "c2", "d"]))
        self.addstep(CheckConfigValue(f"{self.tmp_root_key}.a.b.c1", read_as=None, expected_type=str, expected_value="55"))
        self.addstep(CheckConfigValue(f"{self.tmp_root_key}.a.b.c2", read_as=None, expected_type=str, expected_value="0.050"))
        self.addstep(CheckConfigValue(f"{self.tmp_root_key}.a.b.d", read_as=None, expected_type=str, expected_value="8"))

        self.section("Implicit section 'x': list 'y', but no default values (issue #xxx)")
        self.addstep(CheckDictConfigNode(f"{self.tmp_root_key}.x", ["y"]))
        self.addstep(CheckListConfigNode(f"{self.tmp_root_key}.x.y", length=4))

        self.section("List items x.y[%d], i.e. explicit sub-sections: final value 'z', and default value 'd'")
        for _index in range(4):  # type: int
            self.addstep(CheckDictConfigNode(f"{self.tmp_root_key}.x.y[{_index}]", ["z", "d"]))
            self.addstep(CheckConfigValue(f"{self.tmp_root_key}.x.y[{_index}].z", read_as=None, expected_type=str, expected_value=str(100 + _index)))
            self.addstep(CheckConfigValue(f"{self.tmp_root_key}.x.y[{_index}].d", read_as=None, expected_type=str, expected_value=str(7)))

        scenario.handlers.install(
            scenario.Event.AFTER_TEST, self._finalize,
            scenario=self, once=True,
        )

    def _finalize(
            self,
            event,  # type: str
            data,  # type: typing.Any
    ):  # type: (...) -> None
        if self.doexecute():
            self.info(f"Removing configuration value {self.tmp_root_key!r}")
            scenario.conf.remove(self.tmp_root_key)
