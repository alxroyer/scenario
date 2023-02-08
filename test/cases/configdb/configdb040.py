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
import scenario.test

# Steps:
from .steps.currentprocess import StoreConfigValue
from .steps.currentprocess import RemoveConfigValue
from .steps.currentprocess import CheckConfigValue
from .steps.currentprocess import CheckDictConfigNode


class ConfigDb040(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        scenario.test.TestCase.__init__(
            self,
            title="Configuration value unset",
            objective="Check that a configuration value can be unset.",
            features=[scenario.test.features.CONFIG_DB],
        )

        self.tmp_root_key = scenario.Path(__file__).stem  # type: str
        _config_key1 = f"{self.tmp_root_key}.a.b"  # type: str
        _config_key2 = f"{self.tmp_root_key}.c"  # type: str

        self.section("unset() function")
        self.addstep(StoreConfigValue(_config_key1, 5))
        self.addstep(CheckConfigValue(_config_key1, read_as=None, expected_type=int, expected_value=5))
        self.addstep(RemoveConfigValue(_config_key1))
        self.addstep(CheckConfigValue(_config_key1, read_as=None, expected_type=type(None), expected_value=None))
        self.addstep(CheckDictConfigNode("", ["scenario"]))

        self.section("set(None)")
        self.addstep(StoreConfigValue(_config_key1, 5))
        self.addstep(CheckConfigValue(_config_key1, read_as=None, expected_type=int, expected_value=5))
        self.addstep(StoreConfigValue(_config_key1, None))
        self.addstep(CheckConfigValue(_config_key1, read_as=None, expected_type=type(None), expected_value=None))
        self.addstep(CheckDictConfigNode("", ["scenario"]))

        self.section("Partial removals")
        self.addstep(StoreConfigValue(_config_key1, 5))
        self.addstep(StoreConfigValue(_config_key2, 10))
        self.addstep(RemoveConfigValue(_config_key1))
        self.addstep(CheckConfigValue(_config_key1, read_as=None, expected_type=type(None), expected_value=None))
        self.addstep(CheckDictConfigNode("", ["scenario", self.tmp_root_key]))

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
