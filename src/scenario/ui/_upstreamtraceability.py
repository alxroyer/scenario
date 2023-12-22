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

if True:
    from ._requesthandler import RequestHandler as _RequestHandlerImpl  # `RequestHandler` used for inheritance.
if typing.TYPE_CHECKING:
    from .._reqtraceability import ReqTraceability as _ReqTraceabilityType
    from .._scenariodefinition import ScenarioDefinition as _ScenarioDefinitionType
    from ._htmldoc import HtmlDocument as _HtmlDocumentType
    from ._httprequest import HttpRequest as _HttpRequestType


class UpstreamTraceability(_RequestHandlerImpl):
    """
    Upstream traceability page.
    """

    #: Base URL for the upstream traceability page.
    URL = "/upstream-traceability"

    @staticmethod
    def mkurl(
            scenario,  # type: _ScenarioDefinitionType
    ):  # type: (...) -> str
        """
        Builds an anchor URL in the upstream traceability page, for the given scenario.

        :param scenario: Scenario to build an anchor URL for.
        :return: Anchor URL for the given scenario.
        """
        from ._httprequest import HttpRequest

        return HttpRequest.encodeurl(UpstreamTraceability.URL, anchor=scenario.name)

    @staticmethod
    def scenario2unnamedhtmllink(
            scenario,  # type: _ScenarioDefinitionType
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        """
        Builds a HTML link to the given scenario in the upstream tracebility page, with default text.

        :param scenario: Scenario to build an upstream traceability link for.
        :param html: HTML output page to feed.
        """
        html.addcontent(f'<a class="unnamed upstream-traceability" href="{UpstreamTraceability.mkurl(scenario)}">(upstream traceability)</a>')

    def matches(
            self,
            request,  # type: _HttpRequestType
    ):  # type: (...) -> bool
        return request.base_path == UpstreamTraceability.URL

    def process(
            self,
            request,  # type: _HttpRequestType
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        from .._reqtraceability import REQ_TRACEABILITY

        html.settitle("Upstream traceability")

        with html.addcontent('<div id="downstream-traceability"></div>'):
            _upstream_traceability = REQ_TRACEABILITY.getupstream()  # type: typing.Sequence[_ReqTraceabilityType.Upstream.Scenario]

            with html.addcontent('<table></table>'):
                # Heading row.
                with html.addcontent('<tr></tr>'):
                    html.addcontent('<th class="scenario name">Name</th>')
                    html.addcontent('<th class="scenario title">Title</th>')
                    html.addcontent('<th class="scenario coverage">Requirement coverage</th>')

                # Scenario rows.
                for _upstream_scenario in _upstream_traceability:  # type: _ReqTraceabilityType.Upstream.Scenario
                    self._scenario2html(_upstream_scenario, html)

    def _scenario2html(
            self,
            upstream_scenario,  # type: _ReqTraceabilityType.Upstream.Scenario
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        """
        Builds the HTML content for a scenario.

        :param upstream_scenario: Scenario to build HTML content for.
        :param html: HTML output page to feed.
        """
        from ._scenariodetails import ScenarioDetails

        with html.addcontent(f'<tr class="scenario"></tr>'):
            # Scenario name.
            with html.addcontent('<td class="scenario name"></td>'):
                # With anchor.
                html.addcontent(f'<a name="{html.encode(upstream_scenario.scenario.name)}" />')
                # With link to scenario details page.
                with html.addcontent(f'<a href="{ScenarioDetails.mkurl(upstream_scenario.scenario)}"></a>'):
                    html.addtext(upstream_scenario.scenario.name)

            # Title.
            html.addcontent(f'<td class="scenario title">{html.encode(upstream_scenario.scenario.title)}</td>')

            # Requirement coverage.
            with html.addcontent(f'<td class="scenario coverage"></td>'):
                with html.addcontent('<ul></ul>'):
                    for _upstream_req in upstream_scenario.reqs:  # type: _ReqTraceabilityType.Upstream.Req
                        self._req2html(_upstream_req, html)

    def _req2html(
            self,
            upstream_req,  # type: _ReqTraceabilityType.Upstream.Req
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        """
        Builds the HTML content for a requirement.

        :param upstream_req: Requirement to build HTML content for.
        :param html: HTML output page to feed.
        """
        from ._downstreamtraceability import DownstreamTraceability
        from ._requirements import Requirements

        with html.addcontent('<li class="req"></li>'):
            # Requirement id.
            with html.addcontent('<span class="req id"></span>'):
                # With link to requirements page.
                with html.addcontent(f'<a href="{Requirements.mkurl(upstream_req.req.main_ref)}"></a>'):
                    html.addtext(upstream_req.req.id)

            # Downstream traceability link.
            DownstreamTraceability.reqref2unnamedhtmllink(upstream_req.req.main_ref, html)

            # Traceability comments.
            if upstream_req.comments:
                html.addcontent('<span class="req sep">:</span>')
                html.addcontent(f'<span class="req comments">{html.encode(upstream_req.comments)}</span>')

            # Optional subrefs.
            if upstream_req.req_subrefs:
                with html.addcontent('<ul></ul>'):
                    for _upstream_req_subref in upstream_req.req_subrefs:  # type: _ReqTraceabilityType.Upstream.ReqSubref
                        self._subref2html(_upstream_req_subref, html)

    def _subref2html(
            self,
            upstream_req_subref,  # type: _ReqTraceabilityType.Upstream.ReqSubref
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        """
        Builds the HTML content for a requirement subreference.

        :param upstream_req_subref: Requirement subreference to build HTML content for.
        :param html: HTML output page to feed.
        """
        from ._downstreamtraceability import DownstreamTraceability
        from ._requirements import Requirements

        with html.addcontent('<li class="req-subref"></li>'):
            # Requirement subreference id.
            with html.addcontent('<span class="req-subref id"></span>'):
                # With link to requirements page.
                with html.addcontent(f'<a href="{Requirements.mkurl(upstream_req_subref.req_subref)}"></a>'):
                    html.addtext(upstream_req_subref.req_subref.id)

            # Downstream traceability link.
            DownstreamTraceability.reqref2unnamedhtmllink(upstream_req_subref.req_subref, html)

            # Traceability comments.
            if upstream_req_subref.comments:
                html.addcontent('<span class="req-subref sep">:</span>')
                html.addcontent(f'<span class="req-subref comments">{html.encode(upstream_req_subref.comments)}</span>')
