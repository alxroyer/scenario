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
User interface campaign list page.
"""

import typing

if True:
    from ._requesthandler import RequestHandler as _RequestHandlerImpl  # @inheritance
if typing.TYPE_CHECKING:
    from .._campaignexecution import CampaignExecution as _CampaignExecutionType
    from .._campaignexecution import TestCaseExecution as _TestCaseExecutionType
    from .._campaignexecution import TestSuiteExecution as _TestSuiteExecutionType
    from ._htmldoc import HtmlDocument as _HtmlDocumentType
    from ._httprequest import HttpRequest as _HttpRequestType


class CampaignListPage(_RequestHandlerImpl):
    """
    Campaign list page.
    """

    #: Base URL for the campaign list page.
    URL = "/campaigns"  # type: str

    def __init__(self):  # type: (...) -> None
        """
        Configures the logger instance.
        """
        from .._debugclasses import DebugClass

        _RequestHandlerImpl.__init__(self, DebugClass.UI_PAGE_CAMPAIGNS)

    def process(
            self,
            request,  # type: _HttpRequestType
    ):  # type: (...) -> bool
        from ._htmldoc import HtmlDocument

        # Filter `request`.
        if request.base_path != CampaignListPage.URL:
            self.debug("Request base path %r not matching %r", request.base_path, CampaignListPage.URL)
            self.debug("%r not processed", request)
            return False
        self.debug("Processing %r", request)

        # Sort campaign executions.
        _campaign_executions = self._sortedcampaignlist()  # type: typing.Sequence[_CampaignExecutionType]

        # Identify common list of test suites & test cases reference.
        _campaign_execution_ref = self._mergecampaignexecutionref(_campaign_executions)  # type: _CampaignExecutionType

        self.debug("Generating HTML content")
        _html = HtmlDocument()
        _html.settitle("Campaigns")

        with _html.addcontent('<div id="campaigns"></div>'):
            with _html.addcontent('<table></table>'):
                # Table head: list of campaign names (recent first order, as given by `_sortedcampaignlist()` before).
                self._campaignlist2tablehead(_campaign_executions, _html)

                # Test suites and cases with execution status.
                for _test_suite_execution_ref in _campaign_execution_ref.test_suite_executions:  # type: _TestSuiteExecutionType
                    self._testsuiteexecution2html(_campaign_executions, _test_suite_execution_ref, _html)

        request.sendhtml(_html)
        return True

    def _sortedcampaignlist(self):  # type: (...) -> typing.Sequence[_CampaignExecutionType]
        """
        Returns a sorted list of campaign executions from the campaign database.

        Recent first order.

        :return: Sorted list of campaign executions.
        """
        from .._campaigndb import CAMPAIGN_DB

        return tuple(sorted(
            CAMPAIGN_DB.campaign_executions,
            key=lambda campaign_execution: campaign_execution.campaign_report_path.parent.name,
            reverse=True,
        ))

    def _mergecampaignexecutionref(
            self,
            campaign_executions,  # type: typing.Sequence[_CampaignExecutionType]
    ):  # type: (...) -> _CampaignExecutionType
        """
        Returns a reference :class:`scenario._campaignexecution.CampaignExecution` instance
        that merges tests suites and test cases listed in ``campaign_executions``.

        Ensure test case reports are loaded by the way.

        :param campaign_executions: List of campaign executions to merge test suites and cases from.
        :return: Reference :class:`scenario._campaignexecution.CampaignExecution` instance.
        """
        from .._campaignexecution import CampaignExecution, TestCaseExecution, TestSuiteExecution
        from .._path import Path

        self.debug("Identifying reference test suite and test case lists")
        _campaign_execution_ref = CampaignExecution(
            outdir=Path(),  # Whatever. This is not a real campaign execution.
        )
        for _campaign_execution in campaign_executions:  # type: _CampaignExecutionType
            for _test_suite_execution in _campaign_execution.test_suite_executions:  # type: _TestSuiteExecutionType
                _test_suite_execution_ref = _campaign_execution_ref.gettestsuite(from_path=_test_suite_execution.test_suite_file.path) \
                    # type: typing.Optional[TestSuiteExecution]
                if not _test_suite_execution_ref:
                    self.debug("New suite %s (from %s)", _test_suite_execution.name, _campaign_execution.name)
                    _test_suite_execution_ref = TestSuiteExecution(_campaign_execution_ref, _test_suite_execution.test_suite_file.path)
                    _campaign_execution_ref.test_suite_executions.append(_test_suite_execution_ref)

                for _test_case_execution in _test_suite_execution.test_case_executions:  # type: TestCaseExecution
                    _test_case_execution_ref = _test_suite_execution_ref.gettestcase(from_path=_test_case_execution.script_path) \
                        # type: typing.Optional[TestCaseExecution]
                    if not _test_case_execution_ref:
                        self.debug("New case %s.%s (from %s)", _test_suite_execution.name, _test_case_execution.name, _campaign_execution.name)
                        _test_case_execution_ref = TestCaseExecution(_test_suite_execution_ref, _test_case_execution.script_path)
                        _test_suite_execution_ref.test_case_executions.append(_test_case_execution_ref)

                    # Ensure test case report is loaded.
                    if not _test_case_execution.report.content:
                        try:
                            self.debug("Reading '%s'", _test_case_execution.report.path)
                            _test_case_execution.report.read()
                        except Exception as _err:
                            self.warning(f"Error while reading '%s': %r", _test_case_execution.report.path, _err)

        return _campaign_execution_ref

    def _campaignlist2tablehead(
            self,
            campaign_executions,  # type: typing.Sequence[_CampaignExecutionType]
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        """
        Generates HTML for the table head: one column per campaign.

        :param campaign_executions: Ordered list of campaigns.
        :param html: HTML output page to feed.
        """
        from ._pagecampaign import CampaignPage

        with html.addcontent('<tr></tr>'):
            # First column.
            html.addcontent('<th>Name</th>')

            # One column per campaign.
            for _campaign_execution in campaign_executions:  # type: _CampaignExecutionType
                with html.addcontent('<th></th>'):
                    html.addcontent(f'<a href="{CampaignPage.mkurl(_campaign_execution)}">{_campaign_execution.name}</a>')

    def _testsuiteexecution2html(
            self,
            campaign_executions,  # type: typing.Sequence[_CampaignExecutionType]
            test_suite_execution_ref,  # type: _TestSuiteExecutionType
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        """
        Generates HTML for a given reference test suite across every campaign.

        :param campaign_executions: Ordered list of campaigns to displays execution status for.
        :param test_suite_execution_ref: Reference test suite to search in each campaign of ``campaign_executions``.
        :param html: HTML output page to feed.
        """
        from .._executionstatus import ExecutionStatus

        # One first line for the test suite name, with execution status for each campaign.
        with html.addcontent('<tr></tr>'):
            # Test suite name.
            html.addcontent(f'<th class="suite">{test_suite_execution_ref.name}</th>')

            # Test suite result for each campaign.
            for _campaign_execution in campaign_executions:  # type: _CampaignExecutionType
                # Determine execution status.
                _execution_status = None  # type: typing.Optional[ExecutionStatus]
                _test_suite_execution = _campaign_execution.gettestsuite(from_path=test_suite_execution_ref.test_suite_file.path) \
                    # type: typing.Optional[_TestSuiteExecutionType]
                if _test_suite_execution:
                    _execution_status = _test_suite_execution.status

                # Display execution status, or empty cell.
                if _execution_status is not None:
                    html.addcontent(f'<td>{_execution_status}</td>')
                else:
                    html.addcontent('<td></td>')

        # Test case lines.
        for _test_case_execution_ref in test_suite_execution_ref.test_case_executions:  # type: _TestCaseExecutionType
            self._testcaseexecution2html(campaign_executions, test_suite_execution_ref, _test_case_execution_ref, html)

    def _testcaseexecution2html(
            self,
            campaign_executions,  # type: typing.Sequence[_CampaignExecutionType]
            test_suite_execution_ref,  # type: _TestSuiteExecutionType
            test_case_execution_ref,  # type: _TestCaseExecutionType
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        """
        Generates HTML for a given reference test case across every campaign.

        :param campaign_executions: Ordered list of campaigns to displays execution status for.
        :param test_suite_execution_ref: Reference test suite to search in each campaign of ``campaign_executions``.
        :param test_case_execution_ref: Reference test case to search in each campaign test suite found from ``test_suite_execution_ref``.
        :param html: HTML output page to feed.
        """
        from .._executionstatus import ExecutionStatus
        from .._reqtraceability import REQ_TRACEABILITY
        from .._scenariodefinition import ScenarioDefinition
        from ._pagescenario import ScenarioPage

        with html.addcontent('<tr></tr>'):
            # Test case name, with scenario URL from the `REQ_TRACEABILITY.scenarios` database if available.
            _url = ""  # type: str
            for _scenario_definition in REQ_TRACEABILITY.scenarios:  # type: ScenarioDefinition
                if _scenario_definition.script_path == test_case_execution_ref.script_path:
                    _url = ScenarioPage.mkurl(_scenario_definition)
                    break
            if _url:
                html.addcontent(f'<th><a href="{_url}">{test_case_execution_ref.name}</a></th>')
            else:
                html.addcontent(f'<th>{test_case_execution_ref.name}</th>')

            # Test case result for each campaign.
            for _campaign_execution in campaign_executions:  # type: _CampaignExecutionType
                # Determine execution status.
                _execution_status = None  # type: typing.Optional[ExecutionStatus]
                _test_suite_execution = _campaign_execution.gettestsuite(from_path=test_suite_execution_ref.test_suite_file.path) \
                    # type: typing.Optional[_TestSuiteExecutionType]
                if _test_suite_execution:
                    _test_case_execution = _test_suite_execution.gettestcase(from_path=test_case_execution_ref.script_path) \
                        # type: typing.Optional[_TestCaseExecutionType]
                    if _test_case_execution:
                        _execution_status = _test_case_execution.status

                # Display execution status, or empty cell.
                if _execution_status is not None:
                    html.addcontent(f'<td>{_execution_status}</td>')
                else:
                    html.addcontent('<td></td>')
