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
User interface campaign details page.
"""

import typing

import scenario

if True:
    from ._httprequesthandler import HttpRequestHandler as _HttpRequestHandlerImpl  # @inheritance
if typing.TYPE_CHECKING:
    from ._httprequest import HttpRequest as _HttpRequestType


class CampaignPage(_HttpRequestHandlerImpl):
    """
    Campaign details page.
    """

    #: Base URL for the campaign details page.
    _URL = "/campaign"  # type: str

    @staticmethod
    def mkurl(
            campaign_execution,  # type: scenario.CampaignExecution
            *,
            html_escape=False,  # type: bool
    ):  # type: (...) -> str
        """
        Builds a campaign details URL for the given campaign.

        :param campaign_execution: Campaign execution.
        :param html_escape: ``True`` to get HTML escaped text.
        :return: Campaign details URL for the given path.
        """
        from ._httprequest import HttpRequest

        return HttpRequest.encodeurl(
            CampaignPage._URL,
            args=HttpRequest.mkurlargs(obj=campaign_execution),
            html_escape=html_escape,
        )

    def __init__(self):  # type: (...) -> None
        """
        Configures the logger instance.
        """
        from ._debugclasses import UIDebugClass
        from ._pagereqs import RequirementsPage
        from ._pagereqsdown import DownstreamTraceabilityPage
        from ._pagereqsup import UpstreamTraceabilityPage
        from ._pagescenarios import ScenarioListPage

        _HttpRequestHandlerImpl.__init__(self, UIDebugClass.PAGE_CAMPAIGN)

        #: Scenario list page instantiated as a member for implementation.
        self._page_scenarios = ScenarioListPage(debug_class=UIDebugClass.PAGE_CAMPAIGN)  # type: ScenarioListPage
        #: Requirements page instantiated as a member for implementation.
        self._page_reqs = RequirementsPage(debug_class=UIDebugClass.PAGE_CAMPAIGN)  # type: RequirementsPage
        #: Downstream traceability page instantiated as a member for implementation.
        self._page_reqs_down = DownstreamTraceabilityPage(debug_class=UIDebugClass.PAGE_CAMPAIGN)  # type: DownstreamTraceabilityPage
        #: Upsatream traceability page instantiated as a member for implementation.
        self._page_reqs_up = UpstreamTraceabilityPage(debug_class=UIDebugClass.PAGE_CAMPAIGN)  # type: UpstreamTraceabilityPage

    def process(
            self,
            request,  # type: _HttpRequestType
    ):  # type: (...) -> bool
        from ._htmldoc import HtmlDocument

        # Filter `request`.
        if request.base_path != CampaignPage._URL:
            self.debug("Request base path %r not matching %r", request.base_path, CampaignPage._URL)
            self.debug("%r not processed", request)
            return False
        self.debug("Processing %r", request)

        # Applicable baseline.
        self.debug("Requirement baseline: %r", request.req_baseline)

        # Campaign.
        self.debug("Campaign execution: %r", request.campaign_execution)
        if request.campaign_execution is None:
            self.warning(f"No campaign from {request.req_baseline!r}")
            return False

        self.debug("Generating HTML content")
        _html = HtmlDocument(request)
        _html.settitle(f"Campaign {request.campaign_execution.name}", campaign_subtitle=False)

        _html.addcontent('<a name="scenarios" />')
        with _html.addcontent(f'<h2 class="scenarios"></h2>'):
            _html.addlink(
                href=self._page_scenarios.mkurl(request.req_baseline),
                title="Campaign scenario list",
                text="Scenarios",
            )
        self._page_scenarios.scenarios2html(_html, request.req_baseline)

        if request.req_baseline.req_db.getallreqs():
            _html.addcontent('<a name="reqs" />')
            with _html.addcontent('<h2 class="reqs"></h2>'):
                _html.addlink(
                    href=self._page_reqs.mkurl(request.req_baseline),
                    title="Campaign requirement list",
                    text="Requirements",
                )
            self._page_reqs.reqs2html(_html, request.req_baseline)

            _html.addcontent('<a name="downstream-traceability" />')
            with _html.addcontent('<h2 class="reqs"></h2>'):
                _html.addlink(
                    href=self._page_reqs_down.mkurl(request.req_baseline),
                    title="Campaign downstream traceability",
                    text="Downstream traceability",
                )
            self._page_reqs_down.downstreamtraceability2html(_html, request.req_baseline)

            _html.addcontent('<a name="upstream-traceability" />')
            with _html.addcontent('<h2 class="reqs"></h2>'):
                _html.addlink(
                    href=self._page_reqs_up.mkurl(request.req_baseline),
                    title="Campaign upstream traceability",
                    text="Upstream traceability",
                )
            self._page_reqs_up.upstreamtraceability2html(_html, request.req_baseline)

        request.sendhtml(_html)
        return True
