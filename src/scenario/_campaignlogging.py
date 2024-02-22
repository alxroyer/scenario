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
    from ._fastpath import FAST_PATH as _FAST_PATH  # `FAST_PATH` imported once for performance concerns.
    from ._logextradata import LogExtraData as _LogExtraDataImpl  # `LogExtraData` imported once for performance concerns.
if typing.TYPE_CHECKING:
    from ._campaignexecution import CampaignExecution as _CampaignExecutionType
    from ._campaignexecution import TestCaseExecution as _TestCaseExecutionType
    from ._campaignexecution import TestSuiteExecution as _TestSuiteExecutionType


class CampaignLogging:
    """
    Campaign execution logging management.

    Instantiated once with the :data:`CAMPAIGN_LOGGING` singleton.
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
            campaign_execution,  # type: _CampaignExecutionType  # noqa  ## Parameter unused
    ):  # type: (...) -> None
        """
        Displays the beginning of the campaign.

        :param campaign_execution: Campaign being executed.
        """
        _FAST_PATH.main_logger.rawoutput("CAMPAIGN")
        _FAST_PATH.main_logger.rawoutput("------------------------------------------------")

        self._calls.append(CampaignLogging._Call.BEGIN_CAMPAIGN)

    def begintestsuite(
            self,
            test_suite_execution,  # type: _TestSuiteExecutionType
    ):  # type: (...) -> None
        """
        Displays the beginning of a test suite.

        :param test_suite_execution: Test suite being executed.
        """
        _FAST_PATH.main_logger.rawoutput(f"  TEST SUITE '{test_suite_execution.test_suite_file.path}'")
        _FAST_PATH.main_logger.rawoutput("  ----------------------------------------------")

        self._calls.append(CampaignLogging._Call.BEGIN_TEST_SUITE)

    def begintestcase(
            self,
            test_case_execution,  # type: _TestCaseExecutionType
    ):  # type: (...) -> None
        """
        Displays the beginning of a test case.

        :param test_case_execution: Test case being executed.
        """
        _FAST_PATH.main_logger.rawoutput(f"    Executing '{test_case_execution.name}'")

        # Ensure consecutive loggings will be indented below the line before.
        _FAST_PATH.main_logger.setextradata(_LogExtraDataImpl.HEAD_INDENTATION, "      ")

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
        from ._testerrors import TestError

        if test_case_execution.log.path and test_case_execution.log.path.is_file():
            _FAST_PATH.main_logger.debug("Log file:        '%s'", test_case_execution.log.path)
        if test_case_execution.report.path and test_case_execution.report.path.is_file():
            _FAST_PATH.main_logger.debug("Scenario report: '%s'", test_case_execution.report.path)

        if test_case_execution.status == ExecutionStatus.WARNINGS:
            _FAST_PATH.main_logger.warning(test_case_execution.status)
        elif test_case_execution.status != ExecutionStatus.SUCCESS:
            _FAST_PATH.main_logger.error(test_case_execution.status)

        for _warning in test_case_execution.warnings:  # type: TestError
            _warning.logerror(_FAST_PATH.main_logger, level=logging.WARNING)
        for _error in test_case_execution.errors:  # type: TestError
            _error.logerror(_FAST_PATH.main_logger, level=logging.ERROR)

        # Break the test case logging indentation set in :meth:`begintestcase()`.
        _FAST_PATH.main_logger.setextradata(_LogExtraDataImpl.HEAD_INDENTATION, None)

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

        _FAST_PATH.main_logger.rawoutput("")
        _FAST_PATH.main_logger.rawoutput(f"  END OF TEST SUITE '{test_suite_execution.test_suite_file.path}'")
        _FAST_PATH.main_logger.rawoutput("  ----------------------------------------------")
        _FAST_PATH.main_logger.rawoutput(f"             Number of test cases: {test_suite_execution.counts.total}")
        _FAST_PATH.main_logger.rawoutput(f"         Number of tests in error: {test_suite_execution.counts.errors + test_suite_execution.counts.failures}")
        _FAST_PATH.main_logger.rawoutput(f"    Number of tests with warnings: {test_suite_execution.counts.warnings}")
        _FAST_PATH.main_logger.rawoutput(f"                  Number of steps: {test_suite_execution.steps}")
        _FAST_PATH.main_logger.rawoutput(f"                Number of actions: {test_suite_execution.actions}")
        _FAST_PATH.main_logger.rawoutput(f"                Number of results: {test_suite_execution.results}")
        _FAST_PATH.main_logger.rawoutput(f"                             Time: {f2strduration(test_suite_execution.time.elapsed)}")
        _FAST_PATH.main_logger.rawoutput("")

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

        _FAST_PATH.main_logger.rawoutput("END OF CAMPAIGN")
        _FAST_PATH.main_logger.rawoutput("------------------------------------------------")
        _FAST_PATH.main_logger.rawoutput(f"          JUnit campaign report: {campaign_execution.campaign_report_path}")
        if campaign_execution.req_db_path.is_file():
            _FAST_PATH.main_logger.rawoutput(f"                   Requirements: {campaign_execution.req_db_path}")
        if campaign_execution.downstream_traceability_path.is_file():
            _FAST_PATH.main_logger.rawoutput(f"        Downstream traceability: {campaign_execution.downstream_traceability_path}")
        if campaign_execution.upstream_traceability_path.is_file():
            _FAST_PATH.main_logger.rawoutput(f"          Upstream traceability: {campaign_execution.upstream_traceability_path}")
        _FAST_PATH.main_logger.rawoutput(f"          Number of test suites: {len(campaign_execution.test_suite_executions)}")
        if len(campaign_execution.test_suite_executions) > 1:
            _FAST_PATH.main_logger.rawoutput(f"       _FAST_PATH.main_logger    Number of test cases: {campaign_execution.counts.total}")
            _FAST_PATH.main_logger.rawoutput(f"       Number of tests in error: {campaign_execution.counts.failures}")
            _FAST_PATH.main_logger.rawoutput(f"  Number of tests with warnings: {campaign_execution.counts.warnings}")
            _FAST_PATH.main_logger.rawoutput(f"                Number of steps: {campaign_execution.steps}")
            _FAST_PATH.main_logger.rawoutput(f"              Number of actions: {campaign_execution.actions}")
            _FAST_PATH.main_logger.rawoutput(f"              Number of results: {campaign_execution.results}")
            _FAST_PATH.main_logger.rawoutput(f"                           Time: {f2strduration(campaign_execution.time.elapsed)}")
        _FAST_PATH.main_logger.rawoutput("")

        self._calls.append(CampaignLogging._Call.END_CAMPAIGN)


#: Main instance of :class:`CampaignLogging`.
CAMPAIGN_LOGGING = CampaignLogging()  # type: CampaignLogging
