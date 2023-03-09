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
Scenario events.
"""

import abc
import typing

from .enumutils import StrEnum  # `StrEnum` used for inheritance.

if typing.TYPE_CHECKING:
    from .campaignexecution import CampaignExecution as _CampaignExecutionType
    from .campaignexecution import TestCaseExecution as _TestCaseExecutionType
    from .campaignexecution import TestSuiteExecution as _TestSuiteExecutionType
    from .scenariodefinition import ScenarioDefinition as _ScenarioDefinitionType
    from .stepdefinition import StepDefinition as _StepDefinitionType
    from .testerrors import TestError as _TestErrorType


class ScenarioEvent(StrEnum):
    """
    Events described by the `scenario` framework.

    :const:`BEFORE_TEST_CASE` differs from :const:`BEFORE_TEST` in that
    :const:`BEFORE_TEST_CASE` is triggered within the context of a campaign execution
    while :const:`BEFORE_TEST` is triggered within the context of a scenario execution.

    The same for :const:`AFTER_TEST_CASE` compared with :const:`AFTER_TEST`.
    """

    #: *Before campaign* event: triggers handlers at the beginning of the campaign.
    BEFORE_CAMPAIGN = "scenario.before-campaign"
    #: *Before test suite* event: triggers handlers at the beginning of each test suite.
    BEFORE_TEST_SUITE = "scenario.before-test-suite"
    #: *Before test case* event: triggers handlers at the beginning of each test case.
    BEFORE_TEST_CASE = "scenario.before-test-case"

    #: *Before test* event: triggers handlers at the beginning of the scenario.
    BEFORE_TEST = "scenario.before-test"
    #: *Before step* event: triggers handlers before each regular step.
    BEFORE_STEP = "scenario.before-step"
    #: Error event: triggers handlers on test errors.
    ERROR = "scenario.error"
    #: *After step* event: triggers handlers after each regular step.
    AFTER_STEP = "scenario.after-step"
    #: *After test* event: triggers handlers at the end of the scenario.
    AFTER_TEST = "scenario.after-test"

    #: *After test case* event: triggers handlers after each test case.
    AFTER_TEST_CASE = "scenario.after-test-case"
    #: *After test suite* event: triggers handlers after each test suite.
    AFTER_TEST_SUITE = "scenario.after-test-suite"
    #: *After campaign* event: triggers handlers after the campaign.
    AFTER_CAMPAIGN = "scenario.after-campaign"


class ScenarioEventData(abc.ABC):
    """
    Container classes associated with :class:`ScenarioEvent` events.
    """

    class Campaign:
        """
        :const:`ScenarioEvent.BEFORE_CAMPAIGN` and :const:`ScenarioEvent.AFTER_CAMPAIGN` data container.
        """

        def __init__(
                self,
                campaign_execution,  # type: _CampaignExecutionType
        ):  # type: (...) -> None
            """
            :param campaign_execution: Campaign notified.
            """
            #: Campaign notified.
            self.campaign = campaign_execution  # type: _CampaignExecutionType

    class TestSuite:
        """
        :const:`ScenarioEvent.BEFORE_TEST_SUITE` and :const:`ScenarioEvent.AFTER_TEST_SUITE` data container.
        """

        def __init__(
                self,
                test_suite_execution,  # type: _TestSuiteExecutionType
        ):  # type: (...) -> None
            """
            :param test_suite_execution: Test suite notified.
            """
            #: Test suite notified.
            self.test_suite = test_suite_execution  # type: _TestSuiteExecutionType

    class TestCase:
        """
        :const:`ScenarioEvent.BEFORE_TEST_CASE` and :const:`ScenarioEvent.AFTER_TEST_CASE` data container.
        """

        def __init__(
                self,
                test_case_execution,  # type: _TestCaseExecutionType
        ):  # type: (...) -> None
            """
            :param test_case_execution: Test case notified.
            """
            #: Test case notified.
            self.test_case = test_case_execution  # type: _TestCaseExecutionType

    class Scenario:
        """
        :const:`ScenarioEvent.BEFORE_TEST` and :const:`ScenarioEvent.AFTER_TEST` data container.
        """

        def __init__(
                self,
                scenario_definition,  # type: _ScenarioDefinitionType
        ):  # type: (...) -> None
            """
            :param scenario_definition: Scenario notified.
            """
            #: Scenario notified.
            self.scenario = scenario_definition  # type: _ScenarioDefinitionType

    class Step:
        """
        :const:`ScenarioEvent.BEFORE_STEP` and :const:`ScenarioEvent.AFTER_STEP` data container.
        """

        def __init__(
                self,
                step_definition,  # type: _StepDefinitionType
        ):  # type: (...) -> None
            """
            :param step_definition: Step notified.
            """
            #: Step notified.
            self.step = step_definition  # type: _StepDefinitionType

    class Error:
        """
        :const:`ScenarioEvent.ERROR` data container.
        """

        def __init__(
                self,
                error,  # type: _TestErrorType
        ):  # type: (...) -> None
            """
            :param error: Error notified.
            """
            #: Error notified.
            self.error = error  # type: _TestErrorType
