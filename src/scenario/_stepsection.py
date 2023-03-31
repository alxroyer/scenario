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
Step section management.
"""

import abc
import typing

from ._stepdefinition import StepDefinition  # `StepDefinition` used for inheritance.

if typing.TYPE_CHECKING:
    from ._issuelevels import AnyIssueLevelType


class StepSectionDescription(StepDefinition):
    """
    Step section description.

    Overloads :class:`._stepdefinition.StepDefinition` but does not act as a regular step.

    :class:`._scenariorunner.ScenarioRunner` actually recognizes :class:`StepSectionDescription` instances,
    logs them, but skips their execution.

    :class:`._scenarioreport.ScenarioReport` also recognizes :class:`StepSectionDescription` instances,
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


class StepSectionBegin(StepDefinition):
    """
    Beginning of a step section.

    Usage:

    - Override the :meth:`step()` method, in order to check preliminary conditions,
      call the :meth:`skipsection()` method when applicable.
    - When building the scenario, instanciate your :class:`StepSectionBegin` override at the beginning of a step section,
      push other steps after,
      then finish with the :attr:`end` step.
    - When the :meth:`skipsection()` method is called in the :class:`StepSectionBegin` step,
      the scenario execution will skip the step section up to the :attr:`end` step,
      with an appropriate message or known issue.
    """

    def __init__(self):  # type: (...) -> None
        """
        Instanciantes a :class:`StepSectionEnd` available with the :attr:`end` attribute.
        """
        StepDefinition.__init__(self)

        #: Final section step pre-created with this starter step.
        #:
        #: To be added in the scenario at the end of the list of steps defined by this section.
        self.end = StepSectionEnd(self)  # type: StepSectionEnd

    @abc.abstractmethod
    def step(self):  # type: (...) -> None
        """
        Must be overridden by sub-classes.

        Sub-classes' overrides should call this method to display the common step title.
        """
        self.STEP(f"Beginning of section {self} -> {self.end}")

    def skipsection(
            self,
            message,  # type: str
            issue_level=None,  # type: AnyIssueLevelType
            issue_id=None,  # type: str
    ):  # type: (...) -> None
        """
        Shall be called in :meth:`step()` overrides when the section defined should be skipped.

        :param message:
            Message explaining the reason for the section to be skipped.
        :param issue_level:
            Issue level to use in order to track a known issue for skipping this step section.
        :param issue_id:
            Optional issue id to save with the known issue.

        If none of ``issue_level`` or ``issue_id`` is set, a simple info message is displayed.
        """
        # Format the final message:
        # - remove final dot if any (we will add / restore one whatever),
        if message.endswith("."):
            message = message[:-1]
        # - ensure the first letter is a capital letter (don't change the rest of the text),
        if message:
            message = message[:1].capitalize() + message[1:]
        # - compute the final message.
        message = f"{message}. Steps skipped from {self} to {self.end}."

        # Known-issue, or simple info logging.
        if (issue_level is not None) or (issue_id is not None):
            self.knownissue(
                level=issue_level,
                id=issue_id,
                message=message,
            )
        else:
            self.info(message)

        # Eventually jump to the end of the section.
        self.goto(self.end)


class StepSectionEnd(StepDefinition):
    """
    End of a step section.

    Target of :meth:`._stepuserapi.StepUserApi.goto()` call from the :class:`StepSectionBegin` step at the beginning of the section.
    """

    def __init__(
            self,
            begin,  # type: StepSectionBegin
    ):  # type: (...) -> None
        """
        :param begin: Reference to the beginning step of the step section.
        """
        StepDefinition.__init__(self)

        #: Reference to the beginning step of the step section.
        self.begin = begin  # type: StepSectionBegin

    def step(self):  # type: (...) -> None
        self.STEP(f"End of section {self.begin} -> {self}")
