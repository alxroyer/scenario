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

import scenario
import scenario.test


class LongTextsScenario(scenario.Scenario):

    def __init__(self):  # type: (...) -> None
        scenario.Scenario.__init__(
            self,
            title="Long texts scenario sample",
            description="""
                Scenario description line#1.

                Scenario description line#2.
            """,
        )

        # Ensure the requirement database is loaded.
        try:
            self.req_db.getreq("REQ-001")
        except KeyError:
            self.req_db.load(scenario.test.paths.SCENARIO_TEST_DATA_REQ_DB_FILE)

        self.verifies(
            ("REQ-001", """
                Requirement link comment line#1.

                Requirement link comment line#2.
            """),
        )

    def step010(self):  # type: (...) -> None  # location: step010
        self.STEP("Multiline strings")

        if self.ACTION("""
            Action line#1.

            Action line#2.
        """):
            self.evidence("""
                Action evidence line#1.

                Action evidence line#2.
            """)

        if self.RESULT("""
            Expected result line#1.

            Expected result line#2.
        """):
            self.evidence("""
                Expected result evidence line#1.

                Expected result evidence line#2.
            """)

    def step020(self):  # type: (...) -> None  # location: step020
        self.STEP("List of strings")

        if self.ACTION([
            "Action line#1.",
            "",
            "Action line#2.",
        ]):
            self.evidence([
                "Action evidence line#1.",
                "",
                "Action evidence line#2.",
            ])

        if self.RESULT([
            "Expected result line#1.",
            "",
            "Expected result line#2.",
        ]):
            self.evidence([
                "Expected result evidence line#1.",
                "",
                "Expected result evidence line#2.",
            ])
