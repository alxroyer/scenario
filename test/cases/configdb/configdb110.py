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

import scenario.test

# Steps:
from .steps.currentprocess import LoadConfigFile
from .steps.currentprocess import CheckConfigValue, CheckDictConfigNode, CheckListConfigNode


class ConfigDb110(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        scenario.test.TestCase.__init__(
            self,
            title="INI default values & sub-sections",
            objective="Check the way sub-sections are emulated in INI files, and default values are propagated along sections.",
            features=[scenario.test.features.CONFIG_DB],
        )

        self.knownissue("#44", "Implicit INI sections don't inherit from default values")

        self.section("Load INI file")
        self.addstep(LoadConfigFile(scenario.test.paths.datapath("conf.ini")))

        self.section("Root section: 'a' and 'x' main sections")
        # Do not check that the root node only has 'a' and 'x' sub-sections in as much as other things may be set in the configuration database,
        # either due to previous tests executed in the same commad line,
        # or due to `scenario` configurations when executed within a campaign.
        # self.addstep(CheckDictConfigNode("", ["a", "x"]))

        self.section("Implicit section 'a': sub-section 'b', but no default values (issue #xxx)")
        self.addstep(CheckDictConfigNode("a", ["b"]))

        self.section("Explicit sub-section 'a.b': final values 'c1' and 'c2', and default value 'd' overriden")
        self.addstep(CheckDictConfigNode("a.b", ["c1", "c2", "d"]))
        self.addstep(CheckConfigValue("a.b.c1", read_as=None, expected_type=str, expected_value="55"))
        self.addstep(CheckConfigValue("a.b.c2", read_as=None, expected_type=str, expected_value="0.050"))
        self.addstep(CheckConfigValue("a.b.d", read_as=None, expected_type=str, expected_value="8"))

        self.section("Implicit section 'x': list 'y', but no default values (issue #xxx)")
        self.addstep(CheckDictConfigNode("x", ["y"]))
        self.addstep(CheckListConfigNode("x.y", length=4))

        self.section("List items x.y[%d], i.e. explicit sub-sections: final value 'z', and default value 'd'")
        for _index in range(4):  # type: int
            self.addstep(CheckDictConfigNode("x.y[%d]" % _index, ["z", "d"]))
            self.addstep(CheckConfigValue("x.y[%d].z" % _index, read_as=None, expected_type=str, expected_value="%d" % (100 + _index)))
            self.addstep(CheckConfigValue("x.y[%d].d" % _index, read_as=None, expected_type=str, expected_value="7"))
