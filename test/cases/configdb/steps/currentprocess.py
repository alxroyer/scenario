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

import logging
import typing

import scenario
import scenario.test
import scenario.text


class LoadConfigFile(scenario.test.Step):

    def __init__(
            self,
            input_path,  # type: scenario.Path
            root_key="",  # type: str
    ):  # type: (...) -> None
        scenario.test.Step.__init__(self)

        self.input_path = input_path  # type: scenario.Path
        self.root_key = root_key  # type: str

    def step(self):  # type: (...) -> None
        self.STEP(f"Load '{self.input_path}'")

        _root_key_spec = f" from key {self.root_key!r}" if self.root_key else " at the root level"  # type:str
        if self.ACTION(f"Load the '{self.input_path}' configuration file{_root_key_spec}."):
            scenario.conf.loadfile(self.input_path, root=self.root_key)


class SaveConfigFile(scenario.test.Step):

    def __init__(
            self,
            output_path,  # type: scenario.Path
            root_key="",  # type: str
    ):  # type: (...) -> None
        scenario.test.Step.__init__(self)

        self.output_path = output_path  # type: scenario.Path
        self.root_key = root_key  # type: str

    def step(self):  # type: (...) -> None
        self.STEP(f"Save '{self.output_path}'")

        _root_key_spec = f" from key {self.root_key!r}" if self.root_key else " from the root level"  # type:str
        if self.ACTION(f"Save the configuration database{_root_key_spec} to file '{self.output_path}'"):
            scenario.conf.savefile(self.output_path, root=self.root_key)


class ShowConfigValue(scenario.test.Step):

    def __init__(
            self,
            key,  # type: str
    ):  # type: (...) -> None
        scenario.test.Step.__init__(self)

        self.key = key  # type: str

    def step(self):  # type: (...) -> None
        self.STEP(f"Show {self.key}")

        if self.ACTION(f"Show configuration key {self.key!r}."):
            scenario.conf.show(logging.INFO)


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
        self.STEP(f"Set {self.key}={self.value!r}")

        if self.ACTION(f"Store {self.key}={self.value!r} in the configuration database."):
            scenario.conf.set(self.key, self.value)


class RemoveConfigValue(scenario.test.Step):

    def __init__(
            self,
            key,  # type: str
    ):  # type: (...) -> None
        scenario.test.Step.__init__(self)

        self.key = key  # type: str

    def step(self):  # type: (...) -> None
        self.STEP(f"Unset {self.key}")

        if self.ACTION(f"Remove {self.key!r} from the configuration database."):
            scenario.conf.remove(self.key)


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
        self.STEP(f"Check {self.key!r} section node")

        _data = None  # type: typing.Any
        if self.ACTION(f"Retrieve configuration data for key {self.key!r}."):
            _data = scenario.conf.get(self.key)
            self.evidence(f"Data: {scenario.debug.saferepr(_data)}")
        if self.RESULT("The data retrieved is a dictionary."):
            self.assertisinstance(
                _data, dict,
                evidence=f"{self.key!r} data type",
            )
        _fields_txt = scenario.text.Countable("field", self.field_names)  # type: scenario.text.Countable
        if self.RESULT(f"It contains {len(_fields_txt)} {_fields_txt}{_fields_txt.ifany(':', '.')}"):
            self.assertlen(
                _data, len(self.field_names),
                evidence=f"{self.key!r} number of fields",
            )
        for _field_name in self.field_names:  # type: str
            if self.RESULT(f"- {_field_name!r}"):
                self.assertin(
                    _field_name, _data,
                    evidence=f"{self.key!r} field {_field_name!r}",
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
        self.STEP(f"Check {self.key!r} list node")

        _data = None  # type: typing.Any
        if self.ACTION(f"Retrieve configuration data for key {self.key!r}."):
            _data = scenario.conf.get(self.key)
            self.evidence(f"Data: {scenario.debug.saferepr(_data)}")
        if self.RESULT("The data retrieved is a list."):
            self.assertisinstance(
                _data, list,
                evidence=f"{self.key!r} data type",
            )
        _items_txt = scenario.text.Countable("item", self.length)  # type: scenario.text.Countable
        if self.RESULT(f"It contains {len(_items_txt)} {_items_txt}."):
            self.assertlen(
                _data, self.length,
                evidence=f"{self.key!r} number of items",
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
        from scenario.reflex import qualname

        self.STEP(f"Read {self.key!r}{f' as `{qualname(self.read_as)}`' if self.read_as is not None else ''}")

        if self.read_as is None:
            self.ACTION(f"Read {self.key!r} without specifying the type.")
        else:
            self.ACTION(f"Read {self.key!r} as a `{qualname(self.read_as)}` value.")

        _value_error = None  # type: typing.Optional[ValueError]
        if self.doexecute():
            try:
                if self.read_as is None:
                    self.value_read = scenario.conf.get(self.key)
                else:
                    self.value_read = scenario.conf.get(self.key, type=self.read_as)
                self.evidence(f"Value read: {scenario.debug.saferepr(self.value_read)}")
            except ValueError as _err:
                _value_error = _err

        if self.expected_type is not ValueError:
            if self.RESULT(f"The type of the value read is `{qualname(self.expected_type)}`."):
                self.assertisinstance(
                    self.value_read, self.expected_type,
                    evidence=f"Value type{f' read as `{qualname(self.read_as)}`' if self.read_as is not None else ''}",
                )
            if self.expected_value is not None:
                if self.RESULT(f"The value read is {self.expected_value!r}."):
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
