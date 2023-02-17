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

"""
Action / expected result execution management.
"""

import typing

# `ActionResultDefinition` used in method signatures.
from .actionresultdefinition import ActionResultDefinition


class ActionResultExecution:
    """
    Action/result execution tracking object.
    """

    def __init__(
            self,
            definition,  # type: ActionResultDefinition
    ):  # type: (...) -> None
        """
        Sets the start time automatically.
        """
        from .stats import TimeStats
        from .scenarioexecution import ScenarioExecution
        from .testerrors import TestError

        #: Owner action/result reference.
        self.definition = definition  # type: ActionResultDefinition
        #: Time statistics.
        self.time = TimeStats()  # type: TimeStats
        #: Evidence items.
        self.evidence = []  # type: typing.List[str]
        #: Subscenario executions.
        self.subscenarios = []  # type: typing.List[ScenarioExecution]
        #: Errors.
        self.errors = []  # type: typing.List[TestError]
        #: Warnings.
        self.warnings = []  # type: typing.List[TestError]

        self.time.setstarttime()

    def __repr__(self):  # type: () -> str
        """
        Canonical string representation.
        """
        from .reflex import qualname

        return f"<{qualname(type(self))} of {self.definition.type} {self.definition.description!r}>"
