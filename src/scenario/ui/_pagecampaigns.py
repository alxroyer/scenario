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

import scenario

if True:
    from ._httprequesthandler import HttpRequestHandler as _HttpRequestHandlerImpl  # @inheritance
if typing.TYPE_CHECKING:
    from ._htmldoc import HtmlDocument as _HtmlDocumentType
    from ._httprequest import HttpRequest as _HttpRequestType


class CampaignListPage(_HttpRequestHandlerImpl):
    """
    Campaign list page.
    """

    #: Base URL for the campaign list page.
    _URL = "/campaigns"  # type: str

    class Arg(scenario.enum.StrEnum):
        """
        URL argument names.
        """
        #: Action argument.
        #:
        #: See :class:`CampaignListPage.Action` for possible values.
        ACTION = "action"

    class Action(scenario.enum.StrEnum):
        """
        :attr:`CampaignListPage.Arg.ACTION` values.
        """
        #: Reload campaign database.
        RELOAD_CAMPAIGN_DB = "reload"

    @staticmethod
    def mkurl(
            *,
            reload_campaign_db=False,  # type: bool
            html_escape=True,  # type: bool
    ):  # type: (...) -> str
        """
        Builds a campaign list URL.

        :param reload_campaign_db: ``True`` to set ``action=reload`` URL argument. ``False`` by default.
        :param html_escape: ``True`` (default) to get HTML escaped text.
        :return: Campaign list URL.
        """
        from ._httprequest import HttpRequest

        return HttpRequest.encodeurl(
            CampaignListPage._URL,
            args={
                **({CampaignListPage.Arg.ACTION: CampaignListPage.Action.RELOAD_CAMPAIGN_DB} if reload_campaign_db else {}),
                **HttpRequest.mkurlargs(obj=None),
            },
            html_escape=html_escape,
        )

    def __init__(self):  # type: (...) -> None
        """
        Configures the logger instance.
        """
        from ._debugclasses import UIDebugClass

        _HttpRequestHandlerImpl.__init__(self, UIDebugClass.PAGE_CAMPAIGNS)

    def process(
            self,
            request,  # type: _HttpRequestType
    ):  # type: (...) -> bool
        from ._htmldoc import HtmlDocument

        # Filter `request`.
        if request.base_path != CampaignListPage._URL:
            self.debug("Request base path %r not matching %r", request.base_path, CampaignListPage._URL)
            self.debug("%r not processed", request)
            return False
        self.debug("Processing %r", request)

        self.debug("Generating HTML content")
        _html = HtmlDocument()
        _html.settitle(request, "Campaigns", campaign_subtitle=False)

        # Execution.
        if request.getarg(CampaignListPage.Arg.ACTION, default="") and request.processonce(self):
            self._processaction(request, _html)

        # General page content.
        self._campaigndb2html(request, _html)

        request.sendhtml(_html)
        return True

    def _processaction(
            self,
            request,  # type: _HttpRequestType
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        """
        Process the :attr:`CampaignListPage.Arg.ACTION` argument.

        :param request: Input request being processed.
        :param html: Output HTML document.
        """
        if request.getarg(CampaignListPage.Arg.ACTION, default="") == CampaignListPage.Action.RELOAD_CAMPAIGN_DB:
            scenario.campaign_db.load()

            # Execution results.
            with html.addcontent(f'<div class="{CampaignListPage.Arg.ACTION} result"></div>'):
                html.addcontent('<h2>Execution result</h2>')
                html.addcontent(f'<p>{len(scenario.campaign_db.campaign_executions)} campaigns loaded</p>')

        else:
            raise KeyError(f"Unexpected action {request.getarg(CampaignListPage.Arg.ACTION)!r}")

    def _campaigndb2html(
            self,
            request,  # type: _HttpRequestType
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        """
        Builds the HTML content for the campaigns loaded in the database.

        :param request: Input request being processed.
        :param html: HTML output page to feed.
        """
        html.addcontent(f'<a href="{CampaignListPage.mkurl(reload_campaign_db=True)}">Reload</a>')

        # Sort campaign executions.
        _campaign_executions = self._sortedcampaignlist()  # type: typing.Sequence[scenario.CampaignExecution]

        # Identify common list of test suites & test cases reference.
        _campaign_execution_ref = self._mergecampaignexecutionref(_campaign_executions)  # type: scenario.CampaignExecution

        with html.addcontent('<div id="campaigns"></div>'):
            with html.addcontent('<table></table>'):
                # Table head: list of campaign names (recent first order, as given by `_sortedcampaignlist()` before).
                self._campaignlist2tablehead(_campaign_executions, html)

                # Test suites and cases with execution status.
                for _test_suite_execution_ref in _campaign_execution_ref.test_suite_executions:  # type: scenario.TestSuiteExecution
                    self._testsuiteexecution2tablerow(request, _campaign_executions, _test_suite_execution_ref, html)

    def _sortedcampaignlist(self):  # type: (...) -> typing.Sequence[scenario.CampaignExecution]
        """
        Returns a sorted list of campaign executions from the campaign database.

        Recent first order.

        :return: Sorted list of campaign executions.
        """
        return tuple(sorted(
            scenario.campaign_db.campaign_executions,
            key=lambda campaign_execution: campaign_execution.campaign_report_path.parent.name,
            reverse=True,
        ))

    def _mergecampaignexecutionref(
            self,
            campaign_executions,  # type: typing.Sequence[scenario.CampaignExecution]
    ):  # type: (...) -> scenario.CampaignExecution
        """
        Returns a reference :class:`scenario._campaignexecution.CampaignExecution` instance
        that merges tests suites and test cases listed in ``campaign_executions``.

        Ensure test case reports are loaded by the way.

        :param campaign_executions: List of campaign executions to merge test suites and cases from.
        :return: Reference :class:`scenario._campaignexecution.CampaignExecution` instance.
        """
        from ._debugclasses import UIDebugClass
        from ._reqbl import UI_REQ_BASELINES

        with scenario.ReqBaseline(name=UIDebugClass.PAGE_CAMPAIGNS):
            self.debug("Identifying reference test suite and test case lists")
            _campaign_execution_ref = scenario.CampaignExecution(
                outdir=scenario.Path(),  # Whatever. This is not a real campaign execution.
            )
            for _campaign_execution in campaign_executions:  # type: scenario.CampaignExecution
                for _test_suite_execution in _campaign_execution.test_suite_executions:  # type: scenario.TestSuiteExecution
                    _test_suite_execution_ref = _campaign_execution_ref.gettestsuite(from_path=_test_suite_execution.test_suite_file.path) \
                        # type: typing.Optional[scenario.TestSuiteExecution]
                    if not _test_suite_execution_ref:
                        self.debug("New suite %s (from %s)", _test_suite_execution.name, _campaign_execution.name)
                        _test_suite_execution_ref = scenario.TestSuiteExecution(_campaign_execution_ref, _test_suite_execution.test_suite_file.path)
                        _campaign_execution_ref.test_suite_executions.append(_test_suite_execution_ref)

                    for _test_case_execution in _test_suite_execution.test_case_executions:  # type: scenario.TestCaseExecution
                        _test_case_execution_ref = _test_suite_execution_ref.gettestcase(from_path=_test_case_execution.script_path) \
                            # type: typing.Optional[scenario.TestCaseExecution]
                        if not _test_case_execution_ref:
                            self.debug("New case %s.%s (from %s)", _test_suite_execution.name, _test_case_execution.name, _campaign_execution.name)
                            _test_case_execution_ref = scenario.TestCaseExecution(_test_suite_execution_ref, _test_case_execution.script_path)
                            _test_suite_execution_ref.test_case_executions.append(_test_case_execution_ref)

                        # Ensure test case report is loaded.
                        UI_REQ_BASELINES.checktestcaseloaded(_test_case_execution)

        return _campaign_execution_ref

    def _campaignlist2tablehead(
            self,
            campaign_executions,  # type: typing.Sequence[scenario.CampaignExecution]
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
            for _campaign_execution in campaign_executions:  # type: scenario.CampaignExecution
                with html.addcontent('<th></th>'):
                    html.addcontent(f'<a href="{CampaignPage.mkurl(_campaign_execution)}">{html.escape(_campaign_execution.name)}</a>')

    def _testsuiteexecution2tablerow(
            self,
            request,  # type: _HttpRequestType
            campaign_executions,  # type: typing.Sequence[scenario.CampaignExecution]
            test_suite_execution_ref,  # type: scenario.TestSuiteExecution
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        """
        Generates HTML for a given reference test suite across every campaign.

        :param request: Input request being processed.
        :param campaign_executions: Ordered list of campaigns to displays execution status for.
        :param test_suite_execution_ref: Reference test suite to search in each campaign of ``campaign_executions``.
        :param html: HTML output page to feed.
        """
        # One first line for the test suite name, with execution status for each campaign.
        with html.addcontent('<tr></tr>'):
            # Test suite name.
            html.addcontent(f'<th class="suite">{html.escape(test_suite_execution_ref.name)}</th>')

            # Test suite result for each campaign.
            for _campaign_execution in campaign_executions:  # type: scenario.CampaignExecution
                # Determine execution status.
                _execution_status = None  # type: typing.Optional[scenario.ExecutionStatus]
                _test_suite_execution = _campaign_execution.gettestsuite(from_path=test_suite_execution_ref.test_suite_file.path) \
                    # type: typing.Optional[scenario.TestSuiteExecution]
                if _test_suite_execution:
                    _execution_status = _test_suite_execution.status

                # Display execution status, or empty cell.
                if _execution_status is not None:
                    html.addcontent(f'<td>{_execution_status}</td>')
                else:
                    html.addcontent('<td></td>')

        # Test case lines.
        for _test_case_execution_ref in test_suite_execution_ref.test_case_executions:  # type: scenario.TestCaseExecution
            self._testcaseexecution2tablecell(request, campaign_executions, test_suite_execution_ref, _test_case_execution_ref, html)

    def _testcaseexecution2tablecell(
            self,
            request,  # type: _HttpRequestType
            campaign_executions,  # type: typing.Sequence[scenario.CampaignExecution]
            test_suite_execution_ref,  # type: scenario.TestSuiteExecution
            test_case_execution_ref,  # type: scenario.TestCaseExecution
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        """
        Generates HTML for a given reference test case across every campaign.

        :param request: Input request being processed.
        :param campaign_executions: Ordered list of campaigns to displays execution status for.
        :param test_suite_execution_ref: Reference test suite to search in each campaign of ``campaign_executions``.
        :param test_case_execution_ref: Reference test case to search in each campaign test suite found from ``test_suite_execution_ref``.
        :param html: HTML output page to feed.
        """
        from ._pagescenario import ScenarioPage
        from ._reqbl import UI_REQ_BASELINES

        with html.addcontent('<tr></tr>'):
            # Test case name, with scenario URL from `UI_REQ_BASELINES.main.scenarios` if available.
            _scenario_url = ""  # type: str
            for _main_scenario_definition in UI_REQ_BASELINES.main.scenarios:  # type: scenario.ScenarioDefinition
                if _main_scenario_definition.name == test_case_execution_ref.name:
                    _scenario_url = ScenarioPage.mkurl(_main_scenario_definition)
                    break
            if _scenario_url:
                html.addcontent(f'<th><a href="{_scenario_url}">{html.escape(test_case_execution_ref.name)}</a></th>')
            else:
                html.addcontent(f'<th>{html.escape(test_case_execution_ref.name)}</th>')

            # Test case result for each campaign.
            for _campaign_execution in campaign_executions:  # type: scenario.CampaignExecution
                # Determine execution status.
                _execution_status = None  # type: typing.Optional[scenario.ExecutionStatus]
                _scenario_url = ""  # Type already declared above.
                _test_suite_execution = _campaign_execution.gettestsuite(from_path=test_suite_execution_ref.test_suite_file.path) \
                    # type: typing.Optional[scenario.TestSuiteExecution]
                if _test_suite_execution:
                    _test_case_execution = _test_suite_execution.gettestcase(from_path=test_case_execution_ref.script_path) \
                        # type: typing.Optional[scenario.TestCaseExecution]
                    if _test_case_execution:
                        _execution_status = _test_case_execution.status
                        if _test_case_execution.scenario_definition:
                            _scenario_url = ScenarioPage.mkurl(_test_case_execution.scenario_definition)

                # Display execution status, or empty cell.
                if _scenario_url:
                    html.addcontent(f'<td><a href="{_scenario_url}">{_execution_status or ""}</a></td>')
                else:
                    html.addcontent(f'<td>{_execution_status or ""}</td>')
