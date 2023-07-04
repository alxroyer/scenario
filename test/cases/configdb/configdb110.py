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


class ConfigDb110(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        from configdb.steps.currentprocess import CheckConfigValue, LoadConfigFile, SaveConfigFile

        scenario.test.TestCase.__init__(
            self,
            title="Save INI configuration file",
            description=(
                "Check that a INI configuration file can be loaded with a given root configuration key, "
                "then saved as a new INI file."
            ),
            features=[
                scenario.test.features.CONFIG_DB,
            ],
        )

        # Make this scenario continue on errors, in order to make sure temporary configuration keys are removed in the end.
        self.continue_on_error = True

        self.section("Load INI file")
        self.tmp_root_key1 = scenario.Path(__file__).stem + "-1"  # type: str
        self.addstep(LoadConfigFile(scenario.test.paths.datapath("conf.ini"), root_key=self.tmp_root_key1))
        # The following steps ensure that configurations have been loaded from the expected root key, and not at the top level.
        self.addstep(CheckConfigValue(f"a.b.c1", read_as=None, expected_type=type(None), expected_value=None))
        self.addstep(CheckConfigValue(f"{self.tmp_root_key1}.a.b.c1", read_as=None, expected_type=str, expected_value="55"))

        self.section("Save INI file")
        self.addstep(SaveConfigFile(self.mktmppath(suffix=".ini"), root_key=self.tmp_root_key1))

        self.section("Reload saved INI file")
        self.tmp_root_key2 = scenario.Path(__file__).stem + "-2"  # type: str
        self.addstep(LoadConfigFile(SaveConfigFile.getinstance().output_path, root_key=self.tmp_root_key2))
        self.addstep(CheckConfigValue(f"{self.tmp_root_key2}.a.b.c1", read_as=None, expected_type=str, expected_value="55"))
        self.addstep(CheckConfigValue(f"{self.tmp_root_key2}.a.b.c2", read_as=None, expected_type=str, expected_value="0.050"))
        self.addstep(CheckConfigValue(f"{self.tmp_root_key2}.x.y[0].z", read_as=None, expected_type=str, expected_value="100"))
        self.addstep(CheckConfigValue(f"{self.tmp_root_key2}.x.y[1].z", read_as=None, expected_type=str, expected_value="101"))
        self.addstep(CheckConfigValue(f"{self.tmp_root_key2}.x.y[2].z", read_as=None, expected_type=str, expected_value="102"))
        self.addstep(CheckConfigValue(f"{self.tmp_root_key2}.x.y[3].z", read_as=None, expected_type=str, expected_value="103"))

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
            self.info(f"Removing configuration values {self.tmp_root_key1!r} and {self.tmp_root_key2!r}")
            scenario.conf.remove(self.tmp_root_key1)
            scenario.conf.remove(self.tmp_root_key2)
