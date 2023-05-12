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
Campaign execution logging.
"""

import logging
import typing

if True:
    from ._enumutils import StrEnum as _StrEnumImpl  # `StrEnum` used for inheritance.
if typing.TYPE_CHECKING:
    from ._campaignexecution import CampaignExecution as _CampaignExecutionType
    from ._campaignexecution import TestCaseExecution as _TestCaseExecutionType
    from ._campaignexecution import TestSuiteExecution as _TestSuiteExecutionType


class CampaignLogging:
    """
    Campaign execution logging management.
    """

    class _Call(_StrEnumImpl):
        """
        :class:`CampaignLogging` call identifiers.
        """
        BEGIN_CAMPAIGN = "begincampaign"
        BEGIN_TEST_SUITE = "begintestsuite"
        BEGIN_TEST_CASE = "begintestcase"
        END_TEST_CASE = "endtestcase"
        END_TEST_SUITE = "endtestsuite"
        END_CAMPAIGN = "endcampaign"

    def __init__(self):  # type: (...) -> None
        """
        Initializes private instance members.
        """
        #: History of this class's method calls.
        #:
        #: Makes it possible to adjust the display depending on the sequence of information.
        self._calls = []  # type: typing.List[CampaignLogging._Call]

    def begincampaign(
            self,
            campaign_execution,  # type: _CampaignExecutionType
    ):  # type: (...) -> None
        """
        Displays the beginning of the campaign.

        :param campaign_execution: Campaign being executed.
        """
        from ._loggermain import MAIN_LOGGER

        MAIN_LOGGER.rawoutput("CAMPAIGN")
        MAIN_LOGGER.rawoutput("------------------------------------------------")

        self._calls.append(CampaignLogging._Call.BEGIN_CAMPAIGN)

    def begintestsuite(
            self,
            test_suite_execution,  # type: _TestSuiteExecutionType
    ):  # type: (...) -> None
        """
        Displays the beginning of a test suite.

        :param test_suite_execution: Test suite being executed.
        """
        from ._loggermain import MAIN_LOGGER

        MAIN_LOGGER.rawoutput(f"  TEST SUITE '{test_suite_execution.test_suite_file.path}'")
        MAIN_LOGGER.rawoutput("  ----------------------------------------------")

        self._calls.append(CampaignLogging._Call.BEGIN_TEST_SUITE)

    def begintestcase(
            self,
            test_case_execution,  # type: _TestCaseExecutionType
    ):  # type: (...) -> None
        """
        Displays the beginning of a test case.

        :param test_case_execution: Test case being executed.
        """
        from ._loggermain import MAIN_LOGGER

        MAIN_LOGGER.rawoutput(f"    Executing '{test_case_execution.name}'")

        # Ensure consecutive loggings will be indented below the line before.
        MAIN_LOGGER.pushindentation("      ")

        self._calls.append(CampaignLogging._Call.BEGIN_TEST_CASE)

    def endtestcase(
            self,
            test_case_execution,  # type: _TestCaseExecutionType
    ):  # type: (...) -> None
        """
        Displays the end of a test case.

        :param test_case_execution:Test case being executed.
        """
        from ._executionstatus import ExecutionStatus
        from ._loggermain import MAIN_LOGGER
        from ._testerrors import TestError

        if test_case_execution.log.path and test_case_execution.log.path.is_file():
            MAIN_LOGGER.debug("Log file:    '%s'", test_case_execution.log.path)
        if test_case_execution.json.path and test_case_execution.json.path.is_file():
            MAIN_LOGGER.debug("JSON report: '%s'", test_case_execution.json.path)

        if test_case_execution.status == ExecutionStatus.WARNINGS:
            MAIN_LOGGER.warning(str(test_case_execution.status))
        elif test_case_execution.status != ExecutionStatus.SUCCESS:
            MAIN_LOGGER.error(str(test_case_execution.status))

        for _warning in test_case_execution.warnings:  # type: TestError
            _warning.logerror(MAIN_LOGGER, level=logging.WARNING)
        for _error in test_case_execution.errors:  # type: TestError
            _error.logerror(MAIN_LOGGER, level=logging.ERROR)

        # Break the test case logging indentation set in :meth:`begintestcase()`.
        MAIN_LOGGER.popindentation("      ")

        self._calls.append(CampaignLogging._Call.END_TEST_CASE)

    def endtestsuite(
            self,
            test_suite_execution,  # type: _TestSuiteExecutionType
    ):  # type: (...) -> None
        """
        Displays the end of a test suite.

        :param test_suite_execution:Test suite being executed.
        """
        from ._datetimeutils import f2strduration
        from ._loggermain import MAIN_LOGGER

        MAIN_LOGGER.rawoutput("")
        MAIN_LOGGER.rawoutput(f"  END OF TEST SUITE '{test_suite_execution.test_suite_file.path}'")
        MAIN_LOGGER.rawoutput("  ----------------------------------------------")
        MAIN_LOGGER.rawoutput(f"             Number of test cases: {test_suite_execution.counts.total}")
        MAIN_LOGGER.rawoutput(f"         Number of tests in error: {test_suite_execution.counts.errors + test_suite_execution.counts.failures}")
        MAIN_LOGGER.rawoutput(f"    Number of tests with warnings: {test_suite_execution.counts.warnings}")
        MAIN_LOGGER.rawoutput(f"                  Number of steps: {test_suite_execution.steps}")
        MAIN_LOGGER.rawoutput(f"                Number of actions: {test_suite_execution.actions}")
        MAIN_LOGGER.rawoutput(f"                Number of results: {test_suite_execution.results}")
        MAIN_LOGGER.rawoutput(f"                             Time: {f2strduration(test_suite_execution.time.elapsed)}")
        MAIN_LOGGER.rawoutput("")

        self._calls.append(CampaignLogging._Call.END_TEST_SUITE)

    def endcampaign(
            self,
            campaign_execution,  # type: _CampaignExecutionType
    ):  # type: (...) -> None
        """
        Displays the end of the campaign.

        :param campaign_execution: Campaign being executed.

        Displays the campaign statistics
        """
        from ._datetimeutils import f2strduration
        from ._loggermain import MAIN_LOGGER

        MAIN_LOGGER.rawoutput("END OF CAMPAIGN")
        MAIN_LOGGER.rawoutput("------------------------------------------------")
        MAIN_LOGGER.rawoutput(f"          Number of test suites: {len(campaign_execution.test_suite_executions)}")
        if len(campaign_execution.test_suite_executions) > 1:
            MAIN_LOGGER.rawoutput(f"           Number of test cases: {campaign_execution.counts.total}")
            MAIN_LOGGER.rawoutput(f"       Number of tests in error: {campaign_execution.counts.failures}")
            MAIN_LOGGER.rawoutput(f"  Number of tests with warnings: {campaign_execution.counts.warnings}")
            MAIN_LOGGER.rawoutput(f"                Number of steps: {campaign_execution.steps}")
            MAIN_LOGGER.rawoutput(f"              Number of actions: {campaign_execution.actions}")
            MAIN_LOGGER.rawoutput(f"              Number of results: {campaign_execution.results}")
            MAIN_LOGGER.rawoutput(f"                           Time: {f2strduration(campaign_execution.time.elapsed)}")
        MAIN_LOGGER.rawoutput("")

        MAIN_LOGGER.debug("JUnit report: '%s'", campaign_execution.junit_path)

        self._calls.append(CampaignLogging._Call.END_CAMPAIGN)


#: Main instance of :class:`CampaignLogging`.
CAMPAIGN_LOGGING = CampaignLogging()  # type: CampaignLogging
