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

import scenario

if True:
    from ._requesthandler import RequestHandler as _RequestHandlerImpl  # @inheritance
if typing.TYPE_CHECKING:
    from ._debugclasses import UIDebugClass as _UIDebugClassType
    from ._htmldoc import HtmlDocument as _HtmlDocumentType
    from ._httprequest import HttpRequest as _HttpRequestType


class DownstreamTraceabilityPage(_RequestHandlerImpl):
    """
    Downstream traceability page.
    """

    #: Base URL for the downstream traceability page.
    _URL = "/downstream-traceability"  # type: str

    @staticmethod
    def mkurl(
            obj=None,  # type: typing.Union[scenario.ReqBaseline, scenario.ReqRef]
            *,
            html_escape=True,  # type: bool
    ):  # type: (...) -> str
        """
        Builds a downstream traceability page URL.

        :param obj:
            Applicable requirement baseline, or requirement reference to build an anchor URL for.

            If a :class:`scenario._reqref.ReqRef` is given, determines the requirement baseline by the way.

            Main requirement baseline by default.
        :param html_escape:
            ``True`` (default) to get HTML escaped text.
        :return:
            Downstream traceability page URL.
        """
        from ._httprequest import HttpRequest

        return HttpRequest.encodeurl(
            DownstreamTraceabilityPage._URL,
            args=HttpRequest.mkurlargs(obj=obj),
            anchor=obj.id if isinstance(obj, scenario.ReqRef) else None,
            html_escape=html_escape,
        )

    @staticmethod
    def reqref2unnamedhtmllink(
            req_ref,  # type: scenario.ReqRef
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        """
        Builds a HTML link to the given requirement reference in the downstream tracebility page, with default text.

        :param req_ref: Requirement reference to build a downstream traceability link for.
        :param html: HTML output page to feed.
        """
        html.addcontent(f'<a class="unnamed downstream-traceability" href="{DownstreamTraceabilityPage.mkurl(req_ref)}">(downstream traceability)</a>')

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

        _RequestHandlerImpl.__init__(self, debug_class or UIDebugClass.PAGE_REQS_DOWN)

    def process(
            self,
            request,  # type: _HttpRequestType
    ):  # type: (...) -> bool
        from ._htmldoc import HtmlDocument

        # Filter `request`.
        if request.base_path != DownstreamTraceabilityPage._URL:
            self.debug("Request base path %r not matching %r", request.base_path, DownstreamTraceabilityPage._URL)
            self.debug("%r not processed", request)
            return False
        self.debug("Processing %r", request)

        # Applicable baseline.
        self.debug("Requirement baseline: %r", request.req_baseline)

        self.debug("Generating HTML content")
        _html = HtmlDocument()
        _html.settitle(request, "Downstream traceability", campaign_subtitle=True)

        self.downstreamtraceability2html(request.req_baseline, _html)

        request.sendhtml(_html)
        return True

    def downstreamtraceability2html(
            self,
            req_baseline,  # type: scenario.ReqBaseline
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        """
        Builds the HTML content for the downstream traceability given with the requirement baseline.

        :param req_baseline: Requirement baseline holding the requirement database and scenarios to process.
        :param html: HTML output page to feed.
        """
        with html.addcontent('<div id="downstream-traceability"></div>'):
            _downstream_traceability = scenario.ReqTraceability(req_baseline).getdownstream() \
                # type: typing.Sequence[scenario.ReqTraceability.Downstream.ReqRef]

            with html.addcontent('<table></table>'):
                # Heading row.
                with html.addcontent('<tr></tr>'):
                    html.addcontent('<th class="req-ref id">Id</th>')
                    html.addcontent('<th class="req-ref title">Title</th>')
                    html.addcontent('<th class="req-ref coverage">Test coverage</th>')

                # Requirement reference rows.
                for _downstream_req_ref in _downstream_traceability:  # type: scenario.ReqTraceability.Downstream.ReqRef
                    self._reqref2html(_downstream_req_ref, html)

    def _reqref2html(
            self,
            downstream_req_ref,  # type: scenario.ReqTraceability.Downstream.ReqRef
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        """
        Builds the HTML content for a requirement reference.

        :param downstream_req_ref: Requirement reference to build HTML content for.
        :param html: HTML output page to feed.
        """
        from ._pagereqs import RequirementsPage

        with html.addcontent(f'<tr class="req-ref {"main" if downstream_req_ref.req_ref.ismain() else "sub"}"></tr>'):
            # Requirement id.
            with html.addcontent('<td class="req-ref id"></td>'):
                # With anchor.
                html.addcontent(f'<a name="{html.escape(downstream_req_ref.req_ref.id)}" />')
                # With link to requirements page.
                with html.addcontent(f'<a href="{RequirementsPage.mkurl(downstream_req_ref.req_ref)}"></a>'):
                    html.addtext(downstream_req_ref.req_ref.id)

            # Title.
            _title = downstream_req_ref.req_ref.req.title if downstream_req_ref.req_ref.ismain() else ""  # type: str
            html.addcontent(f'<td class="req-ref title">{html.escape(_title)}</td>')

            # Test coverage.
            with html.addcontent(f'<td class="req-ref coverage"></td>'):
                with html.addcontent('<ul></ul>'):
                    for _downstream_scenario in downstream_req_ref.scenarios:  # type: scenario.ReqTraceability.Downstream.Scenario
                        self._scenario2html(_downstream_scenario, html)

    def _scenario2html(
            self,
            downstream_scenario,  # type: scenario.ReqTraceability.Downstream.Scenario
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        """
        Builds the HTML content for a scenario.

        :param downstream_scenario: Scenario to build HTML content for.
        :param html: HTML output page to feed.
        """
        from ._pagereqsup import UpstreamTraceabilityPage
        from ._pagescenario import ScenarioPage

        with html.addcontent('<li class="req-verifier scenario"></li>'):
            # Scenario name.
            with html.addcontent('<span class="req-verifier scenario name"></span>'):
                # With link to scenario details page.
                with html.addcontent(f'<a href="{ScenarioPage.mkurl(downstream_scenario.scenario)}"></a>'):
                    html.addtext(downstream_scenario.scenario.name)

            # Upstream traceability link.
            UpstreamTraceabilityPage.scenario2unnamedhtmllink(downstream_scenario.scenario, html)

            # Traceability comments.
            if downstream_scenario.comments:
                html.addcontent('<span class="req-verifier scenario sep">:</span>')
                html.addcontent(f'<span class="req-verifier scenario comments">{html.escape(downstream_scenario.comments)}</span>')

            # Optional steps.
            if downstream_scenario.steps:
                with html.addcontent('<ul></ul>'):
                    for _downstream_step in downstream_scenario.steps:  # type: scenario.ReqTraceability.Downstream.Step
                        self._step2html(_downstream_step, html)

    def _step2html(
            self,
            downstream_step,  # type: scenario.ReqTraceability.Downstream.Step
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        """
        Builds the HTML content for a step.

        :param downstream_step: Step to build HTML content for.
        :param html: HTML output page to feed.
        """
        from ._pagescenario import ScenarioPage

        with html.addcontent('<li class="req-verifier step"></li>'):
            # Step number and name.
            with html.addcontent(f'<span class="req-verifier step name"></span>'):
                # With link to scenario details.
                with html.addcontent(f'<a href="{ScenarioPage.mkurl(downstream_step.step)}"></a>'):
                    html.addtext(f"step#{downstream_step.step.number} ({downstream_step.step.name})")

            # Traceability comments.
            if downstream_step.comments:
                html.addcontent('<span class="req-verifier step sep">:</span>')
                html.addcontent(f'<span class="req-verifier step comments">{html.escape(downstream_step.comments)}</span>')
