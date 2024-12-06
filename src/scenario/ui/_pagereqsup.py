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
    from ._httprequesthandler import HttpRequestHandler as _HttpRequestHandlerImpl  # @inheritance
if typing.TYPE_CHECKING:
    from ._debugclasses import UIDebugClass as _UIDebugClassType
    from ._htmldoc import HtmlDocument as _HtmlDocumentType
    from ._httprequest import HttpRequest as _HttpRequestType


class UpstreamTraceabilityPage(_HttpRequestHandlerImpl):
    """
    Upstream traceability page.
    """

    #: Base URL for the upstream traceability page.
    _URL = "/upstream-traceability"  # type: str

    @staticmethod
    def mkurl(
            obj=None,  # type: typing.Union[scenario.ReqBaseline, scenario.ScenarioDefinition]
    ):  # type: (...) -> str
        """
        Builds an upstream traceability page URL.

        :param obj:
            Applicable requirement baseline, or scenario to build an anchor URL for.

            If a :class:`scenario._scenariodefinition.ScenarioDefinition` is given, determines the requirement baseline by the way.

            Main requirement baseline used by default.
        :return:
            Upstream traceability page URL.
        """
        from ._httprequest import HttpRequest

        return HttpRequest.encodeurl(
            UpstreamTraceabilityPage._URL,
            args=HttpRequest.mkurlargs(obj=obj),
            anchor=obj.name if isinstance(obj, scenario.ScenarioDefinition) else None,
        )

    @staticmethod
    def scenario2htmllink(
            html,  # type: _HtmlDocumentType
            scenario_definition,  # type: scenario.ScenarioDefinition
            *,
            text="",  # type: str
    ):  # type: (...) -> None
        """
        Builds a HTML link to the given scenario in the upstream tracebility page.

        :param html: HTML output page to feed.
        :param scenario_definition: Scenario to build an upstream traceability link for.
        :param text: Link text. Sets the ``.default-text`` class and ``@title`` attribute if not provided.
        """
        _classes = ["upstream", "traceability"]  # type: typing.List[str]
        _title = ""  # type: str
        if not text:
            _classes.append("default-text")
            _title = "Upstream traceability"
            text = "(<<)"

        with html.addlink(classes=_classes, href=UpstreamTraceabilityPage.mkurl(scenario_definition), title=_title):
            html.addnode("span", text=text)

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

        _HttpRequestHandlerImpl.__init__(self, debug_class or UIDebugClass.PAGE_REQS_UP)

    def process(
            self,
            request,  # type: _HttpRequestType
    ):  # type: (...) -> bool
        from ._exec import Exec
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
        _html = HtmlDocument(request)
        _html.settitle("Upstream traceability", campaign_subtitle=True)

        Exec.actionbutton2html(_html, request, Exec.Action.RELOAD_MAIN_REQ_BASELINE)

        self.upstreamtraceability2html(_html, request.req_baseline)

        request.sendhtml(_html)
        return True

    def upstreamtraceability2html(
            self,
            html,  # type: _HtmlDocumentType
            req_baseline,  # type: scenario.ReqBaseline
    ):  # type: (...) -> None
        """
        Builds the HTML content for the upstream traceability given with the requirement baseline.

        :param html: HTML output page to feed.
        :param req_baseline: Requirement baseline holding the requirement database and scenarios to process.
        """
        with html.addnode("div", id="upstream-traceability"):
            _upstream_traceability = scenario.ReqTraceability(req_baseline).getupstream() \
                # type: typing.Sequence[scenario.ReqTraceability.Upstream.Scenario]

            with html.addnode("table"):
                # Heading row.
                with html.addnode("tr", classes=["head"]):
                    html.addnode("th", classes=["req-verifier"], text="Scenario")
                    html.addnode("th", classes=["req-ref"], text="Requirement coverage")

                # Scenario rows.
                for _upstream_scenario in _upstream_traceability:  # type: scenario.ReqTraceability.Upstream.Scenario
                    self._scenario2html(html, _upstream_scenario)

    def _scenario2html(
            self,
            html,  # type: _HtmlDocumentType
            upstream_scenario,  # type: scenario.ReqTraceability.Upstream.Scenario
    ):  # type: (...) -> None
        """
        Builds the HTML content for a scenario.

        :param html: HTML output page to feed.
        :param upstream_scenario: Scenario to build HTML content for.
        """
        from ._anchors import Anchor
        from ._pagescenario import ScenarioPage

        with html.addnode("tr", classes=["scenario"]):
            # Scenario.
            with html.addnode("td", classes=["req-verifier"]):
                # Anchor.
                with Anchor.add(html, name=upstream_scenario.scenario.name):
                    # Scenario name, with link to scenario details page.
                    html.addlink(
                        classes=["scenario", "name"],
                        href=ScenarioPage.mkurl(upstream_scenario.scenario),
                        title="Scenario details",
                        text=upstream_scenario.scenario.name,
                    )

                    # Title.
                    html.addnode("span", classes=["scenario", "sep"], text=":")
                    html.addnode("span", classes=["scenario", "title"], text=upstream_scenario.scenario.title)

            # Requirement coverage.
            with html.addnode("td", classes=["req-ref"]):
                with html.addnode("ul"):
                    for _upstream_req in upstream_scenario.reqs:  # type: scenario.ReqTraceability.Upstream.Req
                        self._req2html(html, _upstream_req)

    def _req2html(
            self,
            html,  # type: _HtmlDocumentType
            upstream_req,  # type: scenario.ReqTraceability.Upstream.Req
    ):  # type: (...) -> None
        """
        Builds the HTML content for a requirement.

        :param html: HTML output page to feed.
        :param upstream_req: Requirement to build HTML content for.
        """
        from ._pagereqs import RequirementsPage
        from ._pagereqsdown import DownstreamTraceabilityPage

        with html.addnode("li", classes=["req"]):
            # Requirement id.
            with html.addnode("span", classes=["req", "id"]):
                # With link to requirements page.
                html.addlink(
                    href=RequirementsPage.mkurl(upstream_req.req.main_ref),
                    title="Requirement details",
                    text=upstream_req.req.id,
                )

            # Downstream traceability link.
            DownstreamTraceabilityPage.reqref2htmllink(html, upstream_req.req.main_ref)

            # Traceability comments.
            if upstream_req.comments:
                html.addnode("span", classes=["req", "sep"], text=":")
                html.addnode("span", classes=["req", "comments"], text=upstream_req.comments)

            # Optional subrefs.
            if upstream_req.req_subrefs:
                with html.addnode("ul"):
                    for _upstream_req_subref in upstream_req.req_subrefs:  # type: scenario.ReqTraceability.Upstream.ReqSubref
                        self._subref2html(html, _upstream_req_subref)

    def _subref2html(
            self,
            html,  # type: _HtmlDocumentType
            upstream_req_subref,  # type: scenario.ReqTraceability.Upstream.ReqSubref
    ):  # type: (...) -> None
        """
        Builds the HTML content for a requirement subreference.

        :param html: HTML output page to feed.
        :param upstream_req_subref: Requirement subreference to build HTML content for.
        """
        from ._pagereqs import RequirementsPage
        from ._pagereqsdown import DownstreamTraceabilityPage

        with html.addnode("li", classes=["subref"]):
            # Requirement subreference id.
            with html.addnode("span", classes=["subref", "id"]):
                # With link to requirement details.
                html.addlink(
                    href=RequirementsPage.mkurl(upstream_req_subref.req_subref),
                    title="Requirement details",
                    text=upstream_req_subref.req_subref.id,
                )

            # Downstream traceability link.
            DownstreamTraceabilityPage.reqref2htmllink(html, upstream_req_subref.req_subref)

            # Traceability comments.
            if upstream_req_subref.comments:
                html.addnode("span", classes=["subref", "sep"], text=":")
                html.addnode("span", classes=["subref", "comments"], text=upstream_req_subref.comments)
