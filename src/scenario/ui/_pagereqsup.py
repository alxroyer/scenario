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
User interface upstream traceability page.
"""

import typing

import scenario

if True:
    from ._requesthandler import RequestHandler as _RequestHandlerImpl  # @inheritance
if typing.TYPE_CHECKING:
    from ._debugclasses import UIDebugClass as _UIDebugClassType
    from ._htmldoc import HtmlDocument as _HtmlDocumentType
    from ._httprequest import HttpRequest as _HttpRequestType


class UpstreamTraceabilityPage(_RequestHandlerImpl):
    """
    Upstream traceability page.
    """

    #: Base URL for the upstream traceability page.
    _URL = "/upstream-traceability"  # type: str

    @staticmethod
    def mkurl(
            obj=None,  # type: typing.Union[scenario.ReqBaseline, scenario.ScenarioDefinition]
            *,
            html_escape=True,  # type: bool
    ):  # type: (...) -> str
        """
        Builds an upstream traceability page URL.

        :param obj:
            Applicable requirement baseline, or scenario to build an anchor URL for.

            If a :class:`scenario._scenariodefinition.ScenarioDefinition` is given, determines the requirement baseline by the way.

            Main requirement baseline used by default.
        :param html_escape:
            ``True`` (default) to get HTML escaped text.
        :return:
            Upstream traceability page URL.
        """
        from ._httprequest import HttpRequest

        return HttpRequest.encodeurl(
            UpstreamTraceabilityPage._URL,
            args=HttpRequest.mkurlargs(obj=obj),
            anchor=obj.name if isinstance(obj, scenario.ScenarioDefinition) else None,
            html_escape=html_escape,
        )

    @staticmethod
    def scenario2unnamedhtmllink(
            scenario_definition,  # type: scenario.ScenarioDefinition
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        """
        Builds a HTML link to the given scenario in the upstream tracebility page, with default text.

        :param scenario_definition: Scenario to build an upstream traceability link for.
        :param html: HTML output page to feed.
        """
        html.addcontent(f'<a class="unnamed upstream-traceability" href="{UpstreamTraceabilityPage.mkurl(scenario_definition)}">(upstream traceability)</a>')

    def __init__(
            self,
            *,
            debug_class=None,  # type: _UIDebugClassType
    ):  # type: (...) -> None
        """
        Configures the logger instance.

        :param debug_class:
            Optional debug class, in case of instantiation as a member of another page.

            .. seealso:: :class:`._pagecampaign.CampaignPage`
        """
        from ._debugclasses import UIDebugClass

        _RequestHandlerImpl.__init__(self, debug_class or UIDebugClass.PAGE_REQS_UP)

    def process(
            self,
            request,  # type: _HttpRequestType
    ):  # type: (...) -> bool
        from ._htmldoc import HtmlDocument

        # Filter `request`.
        if request.base_path != UpstreamTraceabilityPage._URL:
            self.debug("Request base path %r not matching %r", request.base_path, UpstreamTraceabilityPage._URL)
            self.debug("%r not processed", request)
            return False
        self.debug("Processing %r", request)

        # Applicable baseline.
        self.debug("Requirement baseline: %r", request.req_baseline)

        self.debug("Generating HTML content")
        _html = HtmlDocument()
        _html.settitle(request, "Upstream traceability", campaign_subtitle=True)

        self.upstreamtraceability2html(request.req_baseline, _html)

        request.sendhtml(_html)
        return True

    def upstreamtraceability2html(
            self,
            req_baseline,  # type: scenario.ReqBaseline
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        """
        Builds the HTML content for the upstream traceability given with the requirement baseline.

        :param req_baseline: Requirement baseline holding the requirement database and scenarios to process.
        :param html: HTML output page to feed.
        """
        with html.addcontent('<div id="upstream-traceability"></div>'):
            _upstream_traceability = scenario.ReqTraceability(req_baseline).getupstream() \
                # type: typing.Sequence[scenario.ReqTraceability.Upstream.Scenario]

            with html.addcontent('<table></table>'):
                # Heading row.
                with html.addcontent('<tr></tr>'):
                    html.addcontent('<th class="scenario name">Name</th>')
                    html.addcontent('<th class="scenario title">Title</th>')
                    html.addcontent('<th class="scenario coverage">Requirement coverage</th>')

                # Scenario rows.
                for _upstream_scenario in _upstream_traceability:  # type: scenario.ReqTraceability.Upstream.Scenario
                    self._scenario2html(_upstream_scenario, html)

    def _scenario2html(
            self,
            upstream_scenario,  # type: scenario.ReqTraceability.Upstream.Scenario
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        """
        Builds the HTML content for a scenario.

        :param upstream_scenario: Scenario to build HTML content for.
        :param html: HTML output page to feed.
        """
        from ._pagescenario import ScenarioPage

        with html.addcontent(f'<tr class="scenario"></tr>'):
            # Scenario name.
            with html.addcontent('<td class="scenario name"></td>'):
                # With anchor.
                html.addcontent(f'<a name="{html.escape(upstream_scenario.scenario.name)}" />')
                # With link to scenario details page.
                with html.addcontent(f'<a href="{ScenarioPage.mkurl(upstream_scenario.scenario)}"></a>'):
                    html.addtext(upstream_scenario.scenario.name)

            # Title.
            html.addcontent(f'<td class="scenario title">{html.escape(upstream_scenario.scenario.title)}</td>')

            # Requirement coverage.
            with html.addcontent(f'<td class="scenario coverage"></td>'):
                with html.addcontent('<ul></ul>'):
                    for _upstream_req in upstream_scenario.reqs:  # type: scenario.ReqTraceability.Upstream.Req
                        self._req2html(_upstream_req, html)

    def _req2html(
            self,
            upstream_req,  # type: scenario.ReqTraceability.Upstream.Req
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        """
        Builds the HTML content for a requirement.

        :param upstream_req: Requirement to build HTML content for.
        :param html: HTML output page to feed.
        """
        from ._pagereqs import RequirementsPage
        from ._pagereqsdown import DownstreamTraceabilityPage

        with html.addcontent('<li class="req"></li>'):
            # Requirement id.
            with html.addcontent('<span class="req id"></span>'):
                # With link to requirements page.
                with html.addcontent(f'<a href="{RequirementsPage.mkurl(upstream_req.req.main_ref)}"></a>'):
                    html.addtext(upstream_req.req.id)

            # Downstream traceability link.
            DownstreamTraceabilityPage.reqref2unnamedhtmllink(upstream_req.req.main_ref, html)

            # Traceability comments.
            if upstream_req.comments:
                html.addcontent('<span class="req sep">:</span>')
                html.addcontent(f'<span class="req comments">{html.escape(upstream_req.comments)}</span>')

            # Optional subrefs.
            if upstream_req.req_subrefs:
                with html.addcontent('<ul></ul>'):
                    for _upstream_req_subref in upstream_req.req_subrefs:  # type: scenario.ReqTraceability.Upstream.ReqSubref
                        self._subref2html(_upstream_req_subref, html)

    def _subref2html(
            self,
            upstream_req_subref,  # type: scenario.ReqTraceability.Upstream.ReqSubref
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        """
        Builds the HTML content for a requirement subreference.

        :param upstream_req_subref: Requirement subreference to build HTML content for.
        :param html: HTML output page to feed.
        """
        from ._pagereqs import RequirementsPage
        from ._pagereqsdown import DownstreamTraceabilityPage

        with html.addcontent('<li class="req-subref"></li>'):
            # Requirement subreference id.
            with html.addcontent('<span class="req-subref id"></span>'):
                # With link to requirements page.
                with html.addcontent(f'<a href="{RequirementsPage.mkurl(upstream_req_subref.req_subref)}"></a>'):
                    html.addtext(upstream_req_subref.req_subref.id)

            # Downstream traceability link.
            DownstreamTraceabilityPage.reqref2unnamedhtmllink(upstream_req_subref.req_subref, html)

            # Traceability comments.
            if upstream_req_subref.comments:
                html.addcontent('<span class="req-subref sep">:</span>')
                html.addcontent(f'<span class="req-subref comments">{html.escape(upstream_req_subref.comments)}</span>')
