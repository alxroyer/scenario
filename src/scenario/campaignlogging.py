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
Campaign execution logging.
"""

import logging
import typing

# `CampaignExecution`, `TestCaseExecution` and `TestSuiteExecution` used in method signatures.
from .campaignexecution import CampaignExecution, TestCaseExecution, TestSuiteExecution


class CampaignLogging:
    """
    Campaign execution logging management.
    """

    def __init__(self):  # type: (...) -> None
        """
        Initializes private instance members.
        """
        #: History of this class's method calls. Makes it possible to adjust the display depending on the sequence of information.
        self._calls = []  # type: typing.List[str]

    def begincampaign(
            self,
            campaign_execution,  # type: CampaignExecution
    ):  # type: (...) -> None
        """
        Displays the beginning of the campaign.

        :param campaign_execution: Campaign being executed.
        """
        from .loggermain import MAIN_LOGGER

        MAIN_LOGGER.rawoutput("CAMPAIGN")
        MAIN_LOGGER.rawoutput("------------------------------------------------")

        self._calls.append("begincampaign")

    def begintestsuite(
            self,
            test_suite_execution,  # type: TestSuiteExecution
    ):  # type: (...) -> None
        """
        Displays the beginning of a test suite.

        :param test_suite_execution: Test suite being executed.
        """
        from .loggermain import MAIN_LOGGER

        MAIN_LOGGER.rawoutput("  TEST SUITE '%s'" % test_suite_execution.test_suite_file.path)
        MAIN_LOGGER.rawoutput("  ----------------------------------------------")

        self._calls.append("begintestsuite")

    def begintestcase(
            self,
            test_case_execution,  # type: TestCaseExecution
    ):  # type: (...) -> None
        """
        Displays the beginning of a test case.

        :param test_case_execution: Test case being executed.
        """
        from .loggermain import MAIN_LOGGER

        MAIN_LOGGER.rawoutput("    Executing '%s'" % test_case_execution.name)

        # Ensure consecutive loggings will be indented below the line before.
        MAIN_LOGGER.pushindentation("      ")

        self._calls.append("begintestcase")

    def endtestcase(
            self,
            test_case_execution,  # type: TestCaseExecution
    ):  # type: (...) -> None
        """
        Displays the end of a test case.

        :param test_case_execution:Test case being executed.
        """
        from .executionstatus import ExecutionStatus
        from .loggermain import MAIN_LOGGER
        from .testerrors import TestError

        if test_case_execution.log.path and test_case_execution.log.path.is_file():
            MAIN_LOGGER.debug("Log file:    '%s'" % test_case_execution.log.path)
        if test_case_execution.json.path and test_case_execution.json.path.is_file():
            MAIN_LOGGER.debug("JSON report: '%s'" % test_case_execution.json.path)

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

        self._calls.append("endtestcase")

    def endtestsuite(
            self,
            test_suite_execution,  # type: TestSuiteExecution
    ):  # type: (...) -> None
        """
        Displays the end of a test suite.

        :param test_suite_execution:Test suite being executed.
        """
        from .datetimeutils import f2strduration
        from .loggermain import MAIN_LOGGER

        MAIN_LOGGER.rawoutput("")
        MAIN_LOGGER.rawoutput("  END OF TEST SUITE '%s'" % test_suite_execution.test_suite_file.path)
        MAIN_LOGGER.rawoutput("  ----------------------------------------------")
        MAIN_LOGGER.rawoutput("             Number of test cases: %d" % test_suite_execution.counts.total)
        MAIN_LOGGER.rawoutput("         Number of tests in error: %d" % (test_suite_execution.counts.errors + test_suite_execution.counts.failures))
        MAIN_LOGGER.rawoutput("    Number of tests with warnings: %d" % test_suite_execution.counts.warnings)
        MAIN_LOGGER.rawoutput("                  Number of steps: %s" % str(test_suite_execution.steps))
        MAIN_LOGGER.rawoutput("                Number of actions: %s" % str(test_suite_execution.actions))
        MAIN_LOGGER.rawoutput("                Number of results: %s" % str(test_suite_execution.results))
        MAIN_LOGGER.rawoutput("                             Time: %s" % f2strduration(test_suite_execution.time.elapsed))
        MAIN_LOGGER.rawoutput("")

        self._calls.append("endtestsuite")

    def endcampaign(
            self,
            campaign_execution,  # type: CampaignExecution
    ):  # type: (...) -> None
        """
        Displays the end of the campaign.

        :param campaign_execution: Campaign being executed.

        Displays the campaign statistics
        """
        from .datetimeutils import f2strduration
        from .loggermain import MAIN_LOGGER

        MAIN_LOGGER.rawoutput("END OF CAMPAIGN")
        MAIN_LOGGER.rawoutput("------------------------------------------------")
        MAIN_LOGGER.rawoutput("            Number of test suites: %d" % len(campaign_execution.test_suite_executions))
        if len(campaign_execution.test_suite_executions) > 1:
            MAIN_LOGGER.rawoutput("           Number of test cases: %d" % campaign_execution.counts.total)
            MAIN_LOGGER.rawoutput("       Number of tests in error: %d" % campaign_execution.counts.failures)
            MAIN_LOGGER.rawoutput("  Number of tests with warnings: %d" % campaign_execution.counts.warnings)
            MAIN_LOGGER.rawoutput("                Number of steps: %s" % str(campaign_execution.steps))
            MAIN_LOGGER.rawoutput("              Number of actions: %s" % str(campaign_execution.actions))
            MAIN_LOGGER.rawoutput("              Number of results: %s" % str(campaign_execution.results))
            MAIN_LOGGER.rawoutput("                           Time: %s" % f2strduration(campaign_execution.time.elapsed))
        MAIN_LOGGER.rawoutput("")

        MAIN_LOGGER.debug("JUnit report: '%s'" % campaign_execution.junit_path)

        self._calls.append("endcampaign")


__doc__ += """
.. py:attribute:: CAMPAIGN_LOGGING

    Main instance of :class:`CampaignLogging`.
"""
CAMPAIGN_LOGGING = CampaignLogging()  # type: CampaignLogging
