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

import enum
import typing

import scenario.test


class ConfigDb030(scenario.test.TestCase):

    class SampleEnum(enum.Enum):
        A = 0
        B = 1

    class SampleIntEnum(enum.IntEnum):
        A = 0
        B = 1

    def __init__(self):  # type: (...) -> None
        from configdb.steps.currentprocess import CheckConfigValue, StoreConfigValue

        scenario.test.TestCase.__init__(
            self,
            title="Configuration value types and conversions",
            description="Check the way configuration values are converted at use.",
        )
        self.verifies(
            scenario.test.reqs.CONFIG_DB,
        )

        # Make this scenario continue on errors, in order to make sure temporary configuration keys are removed in the end.
        self.continueonerror(True)

        _code_location_origin = scenario.Path(scenario.CodeLocation.fromclass(StoreConfigValue).file).prettypath  # type: str

        self.section("Integer number string")
        self.addstep(StoreConfigValue("val", "100"))
        self.addstep(CheckConfigValue("val", read_as=None, expected_type=str, expected_value="100"))
        self.addstep(CheckConfigValue("val", read_as=str, expected_type=str, expected_value="100"))
        self.addstep(CheckConfigValue("val", read_as=int, expected_type=int, expected_value=100))
        self.addstep(CheckConfigValue("val", read_as=float, expected_type=float, expected_value=100.0))

        self.section("Float number string")
        self.addstep(StoreConfigValue("val", "100.0"))
        self.addstep(CheckConfigValue("val", read_as=None, expected_type=str, expected_value="100.0"))
        self.addstep(CheckConfigValue("val", read_as=str, expected_type=str, expected_value="100.0"))
        self.addstep(CheckConfigValue("val", read_as=int, expected_type=ValueError, origin=_code_location_origin))
        self.addstep(CheckConfigValue("val", read_as=float, expected_type=float, expected_value=100.0))

        self.section("Boolean strings")
        self.addstep(StoreConfigValue("val", "True"))
        self.addstep(CheckConfigValue("val", read_as=None, expected_type=str, expected_value="True"))
        self.addstep(CheckConfigValue("val", read_as=bool, expected_type=bool, expected_value=True))
        self.addstep(StoreConfigValue("val", "true"))
        self.addstep(CheckConfigValue("val", read_as=None, expected_type=str, expected_value="true"))
        self.addstep(CheckConfigValue("val", read_as=bool, expected_type=bool, expected_value=True))
        self.addstep(StoreConfigValue("val", "yes"))
        self.addstep(CheckConfigValue("val", read_as=None, expected_type=str, expected_value="yes"))
        self.addstep(CheckConfigValue("val", read_as=bool, expected_type=bool, expected_value=True))
        self.addstep(StoreConfigValue("val", "Yes"))
        self.addstep(CheckConfigValue("val", read_as=None, expected_type=str, expected_value="Yes"))
        self.addstep(CheckConfigValue("val", read_as=bool, expected_type=bool, expected_value=True))
        self.addstep(StoreConfigValue("val", "YES"))
        self.addstep(CheckConfigValue("val", read_as=None, expected_type=str, expected_value="YES"))
        self.addstep(CheckConfigValue("val", read_as=bool, expected_type=bool, expected_value=True))
        self.addstep(StoreConfigValue("val", "y"))
        self.addstep(CheckConfigValue("val", read_as=None, expected_type=str, expected_value="y"))
        self.addstep(CheckConfigValue("val", read_as=bool, expected_type=bool, expected_value=True))
        self.addstep(StoreConfigValue("val", "Y"))
        self.addstep(CheckConfigValue("val", read_as=None, expected_type=str, expected_value="Y"))
        self.addstep(CheckConfigValue("val", read_as=bool, expected_type=bool, expected_value=True))
        self.addstep(StoreConfigValue("val", "1"))
        self.addstep(CheckConfigValue("val", read_as=None, expected_type=str, expected_value="1"))
        self.addstep(CheckConfigValue("val", read_as=bool, expected_type=bool, expected_value=True))
        self.addstep(StoreConfigValue("val", "False"))
        self.addstep(CheckConfigValue("val", read_as=None, expected_type=str, expected_value="False"))
        self.addstep(CheckConfigValue("val", read_as=bool, expected_type=bool, expected_value=False))
        self.addstep(StoreConfigValue("val", "false"))
        self.addstep(CheckConfigValue("val", read_as=None, expected_type=str, expected_value="false"))
        self.addstep(CheckConfigValue("val", read_as=bool, expected_type=bool, expected_value=False))
        self.addstep(StoreConfigValue("val", "no"))
        self.addstep(CheckConfigValue("val", read_as=None, expected_type=str, expected_value="no"))
        self.addstep(CheckConfigValue("val", read_as=bool, expected_type=bool, expected_value=False))
        self.addstep(StoreConfigValue("val", "No"))
        self.addstep(CheckConfigValue("val", read_as=None, expected_type=str, expected_value="No"))
        self.addstep(CheckConfigValue("val", read_as=bool, expected_type=bool, expected_value=False))
        self.addstep(StoreConfigValue("val", "NO"))
        self.addstep(CheckConfigValue("val", read_as=None, expected_type=str, expected_value="NO"))
        self.addstep(CheckConfigValue("val", read_as=bool, expected_type=bool, expected_value=False))
        self.addstep(StoreConfigValue("val", "n"))
        self.addstep(CheckConfigValue("val", read_as=None, expected_type=str, expected_value="n"))
        self.addstep(CheckConfigValue("val", read_as=bool, expected_type=bool, expected_value=False))
        self.addstep(StoreConfigValue("val", "N"))
        self.addstep(CheckConfigValue("val", read_as=None, expected_type=str, expected_value="N"))
        self.addstep(CheckConfigValue("val", read_as=bool, expected_type=bool, expected_value=False))
        self.addstep(StoreConfigValue("val", "0"))
        self.addstep(CheckConfigValue("val", read_as=None, expected_type=str, expected_value="0"))
        self.addstep(CheckConfigValue("val", read_as=bool, expected_type=bool, expected_value=False))
        self.addstep(StoreConfigValue("val", "val"))
        self.addstep(CheckConfigValue("val", read_as=None, expected_type=str, expected_value="val"))
        self.addstep(CheckConfigValue("val", read_as=bool, expected_type=ValueError, origin=_code_location_origin))

        self.section("Enum values")
        self.addstep(StoreConfigValue("val", ConfigDb030.SampleEnum.A))
        self.addstep(CheckConfigValue("val", read_as=None, expected_type=str, expected_value=str(ConfigDb030.SampleEnum.A.value)))
        self.addstep(StoreConfigValue("val", ConfigDb030.SampleIntEnum.A))
        self.addstep(CheckConfigValue("val", read_as=None, expected_type=int, expected_value=ConfigDb030.SampleIntEnum.A.value))

        self.section("Enum definitions")
        self.addstep(StoreConfigValue("str-list", ConfigDb030.SampleEnum))
        self.addstep(CheckConfigValue("str-list", read_as=None, expected_type=list))
        self.addstep(CheckConfigValue("str-list[0]", read_as=None, expected_type=str, expected_value=str(ConfigDb030.SampleEnum.A.value)))
        self.addstep(CheckConfigValue("str-list[1]", read_as=None, expected_type=str, expected_value=str(ConfigDb030.SampleEnum.B.value)))
        self.addstep(StoreConfigValue("int-list", ConfigDb030.SampleIntEnum))
        self.addstep(CheckConfigValue("int-list", read_as=None, expected_type=list))
        self.addstep(CheckConfigValue("int-list[0]", read_as=None, expected_type=int, expected_value=ConfigDb030.SampleIntEnum.A.value))
        self.addstep(CheckConfigValue("int-list[1]", read_as=None, expected_type=int, expected_value=ConfigDb030.SampleIntEnum.B.value))

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
            self.info(f"Removing configuration values 'val', 'str-list' and 'int-list'")
            scenario.conf.remove("val")
            scenario.conf.remove("str-list")
            scenario.conf.remove("int-list")
