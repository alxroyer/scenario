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

import logging
import typing

import scenario


class ConfigDbScenario(scenario.Scenario):

    def __init__(self):  # type: (...) -> None
        scenario.Scenario.__init__(self)

        self.setattribute("TITLE", "Configuration database sample scenario")

    def step000(self):  # type: (...) -> None
        self.STEP("Set configuration value from code")

        if self.ACTION("Set a 'foo.bar' configuration value to 1 from the code."):
            scenario.conf.set("foo.bar", 1)  # location: set

    def step010(self):  # type: (...) -> None
        self.STEP("Read final configuration values")

        if self.ACTION("Read and display final configuration values from the configuration database with their origin."):
            for _key in scenario.conf.getkeys():  # type: str
                _conf_node = scenario.conf.getnode(_key)  # type: typing.Optional[scenario.ConfigNode]
                if _conf_node:
                    self.evidence(f"{_conf_node.key} ({_conf_node.origin}): {_conf_node.data!r}")

    def step020(self):  # type: (...) -> None
        self.STEP("Show configuration database")

        if self.ACTION("Show the configuration database tree."):
            scenario.conf.show(logging.INFO)
