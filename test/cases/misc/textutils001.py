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


class TextUtils001(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        scenario.test.TestCase.__init__(
            self,
            title="Long texts",
            description="Check the `anylongtext2str()` function.",
        )
        self.verifies(
            (scenario.test.reqs.ATTRIBUTES, "Long texts for scenario descriptions"),
            (scenario.test.reqs.SCENARIO_EXECUTION, "Long texts for actions & expected results"),
            (scenario.test.reqs.REQUIREMENT_MANAGEMENT, "Long texts for requirements & requirement link comments"),
            (scenario.test.reqs.EVIDENCE, "Long texts for evidence"),
        )

    def step001(self):  # type: (...) -> None
        from scenario._textutils import anylongtext2str  # noqa  ## Access to protected module

        self.STEP("Multiline string")

        _multiline_string = """
            This is a multiline string with:
            1. one first item,
            2. and a second item, with:
               2.1. one first subitem,
               2.2. and a last subitem.

            Final line after a blank line.
        """  # type: str
        _expected_string = (
            "This is a multiline string with:\n"
            "1. one first item,\n"
            "2. and a second item, with:\n"
            "   2.1. one first subitem,\n"
            "   2.2. and a last subitem.\n"
            "\n"
            "Final line after a blank line."
        )  # type: str

        _parsed_string = ""  # type: str
        if self.ACTION(f"Parse the multiline string {_multiline_string!r} with the `anylongtext2str()` function."):
            _parsed_string = anylongtext2str(_multiline_string)

        if self.RESULT(f"The resulting string is {_expected_string!r}."):
            self.assertequal(
                _parsed_string, _expected_string,
                evidence=True,
            )

    def step002(self):  # type: (...) -> None
        from scenario._textutils import anylongtext2str  # noqa  ## Access to protected module

        self.STEP("String list")

        _string_list = [
            "This is a multiline string with:",
            "1. one first item,",
            "2. and a second item, with:",
            "   2.1. one first subitem,",
            "   2.2. and a last subitem.",
            "",
            "Final line after a blank line.",
        ]  # type: typing.List[str]
        _expected_string = (
            "This is a multiline string with:\n"
            "1. one first item,\n"
            "2. and a second item, with:\n"
            "   2.1. one first subitem,\n"
            "   2.2. and a last subitem.\n"
            "\n"
            "Final line after a blank line."
        )  # type: str

        _parsed_string = ""  # type: str
        if self.ACTION(f"Parse the string list {_string_list!r} with the `anylongtext2str()` function."):
            _parsed_string = anylongtext2str(_string_list)

        if self.RESULT(f"The resulting string is {_expected_string!r}."):
            self.assertequal(
                _parsed_string, _expected_string,
                evidence=True,
            )
