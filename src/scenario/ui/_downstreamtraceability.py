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
User interface downstream traceability page.
"""

import typing

if True:
    from ._requesthandler import RequestHandler as _RequestHandlerImpl  # `RequestHandler` used for inheritance.
if typing.TYPE_CHECKING:
    from .._reqref import ReqRef as _ReqRefType
    from .._reqtraceability import ReqTraceability as _ReqTraceabilityType
    from ._htmldoc import HtmlDocument as _HtmlDocumentType
    from ._httprequest import HttpRequest as _HttpRequestType


class DownstreamTraceability(_RequestHandlerImpl):
    """
    Downstream traceability page.
    """

    #: Base URL for the downstream traceability page.
    URL = "/downstream-traceability"

    @staticmethod
    def mkurl(
            req_ref,  # type: _ReqRefType
    ):  # type: (...) -> str
        """
        Builds an anchor URL in the downstream traceability page, for the given requirement reference.

        :param req_ref: Requirement reference to build an anchor URL for.
        :return: Anchor URL for the given requirement reference.
        """
        from ._httprequest import HttpRequest

        return HttpRequest.encodeurl(DownstreamTraceability.URL, anchor=req_ref.id)

    @staticmethod
    def reqref2unnamedhtmllink(
            req_ref,  # type: _ReqRefType
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        """
        Builds a HTML link to the given requirement reference in the downstream tracebility page, with default text.

        :param req_ref: Requirement reference to build a downstream traceability link for.
        :param html: HTML output page to feed.
        """
        html.addcontent(f'<a class="unnamed downstream-traceability" href="{DownstreamTraceability.mkurl(req_ref)}">(downstream traceability)</a>')

    def matches(
            self,
            request,  # type: _HttpRequestType
    ):  # type: (...) -> bool
        return request.base_path == DownstreamTraceability.URL

    def process(
            self,
            request,  # type: _HttpRequestType
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        from .._reqtraceability import REQ_TRACEABILITY

        html.settitle("Downstream traceability")

        with html.addcontent('<div id="downstream-traceability"></div>'):
            _downstream_traceability = REQ_TRACEABILITY.getdownstream()  # type: typing.Sequence[_ReqTraceabilityType.Downstream.ReqRef]

            with html.addcontent('<table></table>'):
                # Heading row.
                with html.addcontent('<tr></tr>'):
                    html.addcontent('<th class="req-ref id">Id</th>')
                    html.addcontent('<th class="req-ref title">Title</th>')
                    html.addcontent('<th class="req-ref coverage">Test coverage</th>')

                # Requirement reference rows.
                for _downstream_req_ref in _downstream_traceability:  # type: _ReqTraceabilityType.Downstream.ReqRef
                    self._reqref2html(_downstream_req_ref, html)

    def _reqref2html(
            self,
            downstream_req_ref,  # type: _ReqTraceabilityType.Downstream.ReqRef
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        """
        Builds the HTML content for a requirement reference.

        :param downstream_req_ref: Requirement reference to build HTML content for.
        :param html: HTML output page to feed.
        """
        from ._requirements import Requirements

        with html.addcontent(f'<tr class="req-ref {"main" if downstream_req_ref.req_ref.ismain() else "sub"}"></tr>'):
            # Requirement id.
            with html.addcontent('<td class="req-ref id"></td>'):
                # With anchor.
                html.addcontent(f'<a name="{html.encode(downstream_req_ref.req_ref.id)}" />')
                # With link to requirements page.
                with html.addcontent(f'<a href="{Requirements.mkurl(downstream_req_ref.req_ref)}"></a>'):
                    html.addtext(downstream_req_ref.req_ref.id)

            # Title.
            _title = downstream_req_ref.req_ref.req.title if downstream_req_ref.req_ref.ismain() else ""  # type: str
            html.addcontent(f'<td class="req-ref title">{html.encode(_title)}</td>')

            # Test coverage.
            with html.addcontent(f'<td class="req-ref coverage"></td>'):
                with html.addcontent('<ul></ul>'):
                    for _downstream_scenario in downstream_req_ref.scenarios:  # type: _ReqTraceabilityType.Downstream.Scenario
                        self._scenario2html(_downstream_scenario, html)

    def _scenario2html(
            self,
            downstream_scenario,  # type: _ReqTraceabilityType.Downstream.Scenario
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        """
        Builds the HTML content for a scenario.

        :param downstream_scenario: Scenario to build HTML content for.
        :param html: HTML output page to feed.
        """
        from ._scenariodetails import ScenarioDetails
        from ._upstreamtraceability import UpstreamTraceability

        with html.addcontent('<li class="req-verifier scenario"></li>'):
            # Scenario name.
            with html.addcontent('<span class="req-verifier scenario name"></span>'):
                # With link to scenario details page.
                with html.addcontent(f'<a href="{ScenarioDetails.mkurl(downstream_scenario.scenario)}"></a>'):
                    html.addtext(downstream_scenario.scenario.name)

            # Upstream traceability link.
            UpstreamTraceability.scenario2unnamedhtmllink(downstream_scenario.scenario, html)

            # Traceability comments.
            if downstream_scenario.comments:
                html.addcontent('<span class="req-verifier scenario sep">:</span>')
                html.addcontent(f'<span class="req-verifier scenario comments">{html.encode(downstream_scenario.comments)}</span>')

            # Optional steps.
            if downstream_scenario.steps:
                with html.addcontent('<ul></ul>'):
                    for _downstream_step in downstream_scenario.steps:  # type: _ReqTraceabilityType.Downstream.Step
                        self._step2html(_downstream_step, html)

    def _step2html(
            self,
            downstream_step,  # type: _ReqTraceabilityType.Downstream.Step
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        """
        Builds the HTML content for a step.

        :param downstream_step: Step to build HTML content for.
        :param html: HTML output page to feed.
        """
        from ._scenariodetails import ScenarioDetails

        with html.addcontent('<li class="req-verifier step"></li>'):
            # Step number and name.
            with html.addcontent(f'<span class="req-verifier step name"></span>'):
                # With link to scenario details.
                with html.addcontent(f'<a href="{ScenarioDetails.mkurl(downstream_step.step)}"></a>'):
                    html.addtext(f"step#{downstream_step.step.number} ({downstream_step.step.name})")

            # Traceability comments.
            if downstream_step.comments:
                html.addcontent('<span class="req-verifier step sep">:</span>')
                html.addcontent(f'<span class="req-verifier step comments">{html.encode(downstream_step.comments)}</span>')
