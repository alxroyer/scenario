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
Action / expected result definition.
"""

import typing

# `StrEnum` use for inheritance.
from .enumutils import StrEnum
# `CodeLocation` used in method signatures.
from .locations import CodeLocation


class ActionResultDefinition:
    """
    This class describes both an action or an expected result.
    """

    class Type(StrEnum):
        """
        Enum that tells whether a user text defines an action or an expected result.
        """
        #: Action type.
        ACTION = "ACTION"
        #: Expected result type.
        RESULT = "RESULT"

    def __init__(
            self,
            type,  # type: ActionResultDefinition.Type  # noqa  ## Shadows built-in name 'type'
            description,  # type: str
    ):  # type: (...) -> None
        """
        :param type: Action/result type.
        :param description: User description for this action/result.

        .. note:: As it makes the API convenient, we deliberately shadow the built-in with the ``type`` parameter.
        """
        from .actionresultexecution import ActionResultExecution
        from .stepdefinition import StepDefinition

        #: Action/result type.
        self.type = type  # type: ActionResultDefinition.Type
        #: Action/result textual description.
        self.description = description  # type: str
        #: Owner step.
        #:
        #: Initially set with a void reference.
        #: Fixed when :meth:`.stepdefinition.StepDefinition.addactionsresults()` is called.
        self.step = StepDefinition.__new__(StepDefinition)  # type: StepDefinition
        #: Executions.
        self.executions = []  # type: typing.List[ActionResultExecution]

    def __repr__(self):  # type: (...) -> str
        """
        Canonical string representation.
        """
        return f"<{self.type} {self.description!r}>"

    def __str__(self):  # type: (...) -> str
        """
        Printable string representation.
        """
        return f"{self.type} {self.description!r}"
