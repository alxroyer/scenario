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

"""
Step section management.
"""

# `StepDefinition` used for inheritance.
from .stepdefinition import StepDefinition


class StepSection(StepDefinition):
    """
    Step section definition.

    Overloads :class:`.stepdefinition.StepDefinition` but does not act as a regular step.

    :class:`.scenariorunner.ScenarioRunner` actually recognizes :class:`StepSection` instances
    and skips their execution.

    :class:`.scenarioreport.ScenarioReport` also recognizes :class:`StepSection` instances,
    and therefore does not generate 'executions' nor 'actions-results' sections for them.
    """

    def __init__(
            self,
            description,  # type: str
    ):  # type: (...) -> None
        """
        :param description: Step section description.
        """
        StepDefinition.__init__(self)

        #: Step section description.
        self.description = description

    def step(self):  # type: (...) -> None
        # Do nothing.
        # Do not call the method of the mother class.
        pass
