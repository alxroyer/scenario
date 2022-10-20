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

import typing

import scenario
from scenario.reflex import qualname
import scenario.test


class LoadConfigFile(scenario.test.Step):

    def __init__(
            self,
            config_file,  # type: scenario.Path
    ):  # type: (...) -> None
        scenario.test.Step.__init__(self)

        self.config_file = config_file  # type: scenario.Path

    def step(self):  # type: (...) -> None
        self.STEP("Load '%s'" % self.config_file)

        if self.ACTION("Load the '%s' configuration file." % self.config_file):
            scenario.conf.loadfile(self.config_file)


class StoreConfigValue(scenario.test.Step):

    def __init__(
            self,
            key,  # type: str
            value,  # type: typing.Any
    ):  # type: (...) -> None
        scenario.test.Step.__init__(self)

        self.key = key  # type: str
        self.value = value  # type: typing.Any

    def step(self):  # type: (...) -> None
        self.STEP("Set %s=%s" % (self.key, repr(self.value)))

        if self.ACTION("Store %s=%s in the configuration database." % (self.key, repr(self.value))):
            scenario.conf.set(self.key, self.value)


class CheckDictConfigNode(scenario.test.Step):

    def __init__(
            self,
            key,  # type: str
            field_names,  # type: typing.List[str]
    ):  # type: (...) -> None
        scenario.test.Step.__init__(self)

        self.key = key  # type: str
        self.field_names = field_names  # type: typing.List[str]

    def step(self):  # type: (...) -> None
        self.STEP("Check '%s' section node" % self.key)

        _data = None  # type: typing.Any
        if self.ACTION("Retrieve configuration data for key '%s'." % self.key):
            _data = scenario.conf.get(self.key)
            self.evidence("Data: %s" % scenario.assertionhelpers.saferepr(_data))
        if self.RESULT("The data retrieved is a dictionary."):
            self.assertisinstance(
                _data, dict,
                evidence="'%s' data type" % self.key,
            )
        if self.RESULT("It contains %d field(s):" % len(self.field_names)):
            self.assertlen(
                _data, len(self.field_names),
                evidence="'%s' number of fields" % self.key,
            )
        for _field_name in self.field_names:  # type: str
            if self.RESULT("- '%s'" % _field_name):
                self.assertin(
                    _field_name, _data,
                    evidence="'%s' field '%s'" % (self.key, _field_name),
                )


class CheckListConfigNode(scenario.test.Step):

    def __init__(
            self,
            key,  # type: str
            length,  # type: int
    ):  # type: (...) -> None
        scenario.test.Step.__init__(self)

        self.key = key  # type: str
        self.length = length  # type: int

    def step(self):  # type: (...) -> None
        self.STEP("Check '%s' list node" % self.key)

        _data = None  # type: typing.Any
        if self.ACTION("Retrieve configuration data for key '%s'." % self.key):
            _data = scenario.conf.get(self.key)
            self.evidence("Data: %s" % scenario.assertionhelpers.saferepr(_data))
        if self.RESULT("The data retrieved is a list."):
            self.assertisinstance(
                _data, list,
                evidence="'%s' data type" % self.key,
            )
        if self.RESULT("It contains %d item(s):" % self.length):
            self.assertlen(
                _data, self.length,
                evidence="'%s' number of items" % self.key,
            )


class CheckConfigValue(scenario.test.Step):

    def __init__(
            self,
            key,  # type: str
            read_as,  # type: typing.Optional[type]
            expected_type,  # type: type
            expected_value=None,  # type: typing.Any
            origin=None,  # type: str
    ):  # type: (...) -> None
        scenario.test.Step.__init__(self)

        self.key = key  # type: str
        self.read_as = read_as  # type: typing.Optional[type]
        self.expected_type = expected_type  # type: type
        self.expected_value = expected_value  # type: typing.Optional[typing.Any]
        self.origin = origin  # type: typing.Optional[str]

        self.value_read = None  # type: typing.Any

    def step(self):  # type: (...) -> None
        if self.read_as is None:
            self.STEP("Read '%s'" % self.key)
        else:
            self.STEP("Read '%s' as `%s`" % (self.key, qualname(self.read_as)))

        if self.read_as is None:
            self.ACTION("Read '%s' without specifying the type." % self.key)
        else:
            self.ACTION("Read '%s' as a `%s` value." % (self.key, qualname(self.read_as)))

        _value_error = None  # type: typing.Optional[ValueError]
        if self.doexecute():
            try:
                if self.read_as is None:
                    self.value_read = scenario.conf.get(self.key)
                else:
                    self.value_read = scenario.conf.get(self.key, type=self.read_as)
                self.evidence("Value read: %s" % scenario.assertionhelpers.saferepr(self.value_read))
            except ValueError as _err:
                _value_error = _err

        if self.expected_type is not ValueError:
            if self.RESULT("The type of the value read is `%s`." % qualname(self.expected_type)):
                self.assertisinstance(
                    self.value_read, self.expected_type,
                    evidence="Value type" if self.read_as is None else "Value type read as `%s`" % qualname(self.read_as),
                )
            if self.expected_value is not None:
                if self.RESULT("The value read is %s." % repr(self.expected_value)):
                    self.assertequal(
                        self.value_read, self.expected_value,
                        evidence="Value",
                    )
        else:
            if self.RESULT("A `ValueError` exception is raised."):
                self.assertisnotnone(
                    _value_error,
                    evidence="Value error",
                )
            if self.origin is not None:
                if self.RESULT("The exception gives the origin of the bad configuration value."):
                    self.assertin(
                        self.origin, str(_value_error),
                        evidence="Configuration value origin",
                    )
