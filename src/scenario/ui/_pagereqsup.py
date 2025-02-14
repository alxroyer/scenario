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
    from ._htmlgenlists import ListGenerator as _ListGeneratorType
    from ._htmlgentables import TableGenerator as _TableGeneratorType
    from ._httprequest import HttpRequest as _HttpRequestType


class UpstreamTraceabilityPage(_HttpRequestHandlerImpl):
    """
    Upstream traceability page.
    """

    #: Base URL for the upstream traceability page.
    _URL = "/upstream-traceability"  # type: str

    @staticmethod
    def mkurl(
            obj=None,  # type: typing.Union[scenario.ReqBaseline, scenario.ScenarioDefinition, scenario.StepDefinition]
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
            anchor=(
                scenario.ReqTraceability.Upstream.ReqVerifier(obj).full_name if isinstance(obj, (scenario.ScenarioDefinition, scenario.StepDefinition))
                else None
            ),
        )

    @staticmethod
    def reqverifier2htmllink(
            html,  # type: _HtmlDocumentType
            req_verifier,  # type: typing.Union[scenario.ScenarioDefinition, scenario.StepDefinition]
            *,
            text="",  # type: str
    ):  # type: (...) -> None
        """
        Builds a HTML link to the given scenario in the upstream tracebility page.

        :param html: HTML output page to feed.
        :param req_verifier: Scenario or step to build an upstream traceability link for.
        :param text: Link text. Sets the ``.default-text`` class and ``@title`` attribute if not provided.
        """
        from ._htmlgenlinks import LinkGenerator

        _classes = ["upstream", "traceability"]  # type: typing.List[str]
        _title = ""  # type: str
        if not text:
            _classes.append("default-text")
            _title = "Upstream traceability"
            text = "(<<)"

        with LinkGenerator(html).addlink(classes=_classes, href=UpstreamTraceabilityPage.mkurl(req_verifier), title=_title):
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
        from ._htmlgentables import TableGenerator

        with html.addnode("div", id="upstream-traceability"):
            # Compute upstream traceability.
            _upstream_traceability = scenario.ReqTraceability(req_baseline).getupstream()  # type: scenario.ReqUpstreamTraceabilityType

            # Instantiate the table generator.
            _table_generator = TableGenerator(
                html,
                table_cid="upstream-traceability",
            )  # type: TableGenerator

            # Expand/collapse all buttons.
            _table_generator.addexpandallbutton()
            _table_generator.addcollapseallbutton()

            with _table_generator.addtable():
                # Heading row.
                with html.addnode("tr", classes=["head"]):
                    html.addnode("th", classes=["req-verifier"], text="Scenario")
                    html.addnode("th", classes=["req-ref"], text="Requirement coverage")

                # Scenario rows.
                for _upstream_req_verifier in _upstream_traceability:  # type: scenario.ReqTraceability.Upstream.ReqVerifier
                    self._reqverifier2html(_table_generator, _upstream_req_verifier)

    def _reqverifier2html(
            self,
            table_generator,  # type: _TableGeneratorType
            upstream_req_verifier,  # type: scenario.ReqTraceability.Upstream.ReqVerifier
    ):  # type: (...) -> None
        """
        Builds the HTML content for a scenario.

        :param table_generator: Table generator. Provides the HTML output page to feed.
        :param upstream_req_verifier: Scenario or step to build HTML content for.
        """
        from ._htmlgenanchors import AnchorGenerator
        from ._htmlgenlinks import LinkGenerator
        from ._htmlgenlists import ListGenerator
        from ._htmlgentypes import CollapsibleState
        from ._pagescenario import ScenarioPage

        with (
            table_generator.addrow(
                tr1_cid=upstream_req_verifier.req_verifier.name,
                default_state=CollapsibleState.COLLAPSED,
                classes=["scenario"],
            )
            if isinstance(upstream_req_verifier.req_verifier, scenario.ScenarioDefinition) else
            table_generator.addsubrow(
                classes=["step"],
            )
        ):
            # Scenario.
            with table_generator.html.addnode("td", classes=["req-verifier"]):
                if isinstance(upstream_req_verifier.req_verifier, scenario.ScenarioDefinition):
                    # Expand/collapse button.
                    table_generator.addtogglebutton()

                # Anchor.
                with AnchorGenerator(table_generator.html, name=upstream_req_verifier.full_name).addanchor():
                    # Scenario / step name, with link to scenario details page.
                    LinkGenerator(table_generator.html).addlink(
                        classes=["req-verifier", "name"],
                        href=ScenarioPage.mkurl(upstream_req_verifier.req_verifier),
                        title="Scenario details",
                        text=upstream_req_verifier.name,
                    )

                    # Scenario title / step description.
                    if isinstance(upstream_req_verifier.req_verifier, scenario.ScenarioDefinition) and upstream_req_verifier.req_verifier.title:
                        table_generator.html.addnode("span", classes=["scenario", "sep"], text=":")
                        table_generator.html.addnode("span", classes=["scenario", "title"], text=upstream_req_verifier.req_verifier.title)
                    if isinstance(upstream_req_verifier.req_verifier, scenario.StepDefinition) and upstream_req_verifier.req_verifier.description:
                        table_generator.html.addnode("span", classes=["step", "sep"], text=":")
                        table_generator.html.addnode("span", classes=["step", "description"], text=upstream_req_verifier.req_verifier.description)

            # Requirement coverage.
            with table_generator.html.addnode("td", classes=["req-ref"]):
                # Instantiate a list generator so that `_req2html()` can generate collapsible list items.
                _list_generator = ListGenerator(table_generator.html)  # type: ListGenerator

                with _list_generator.addlist():
                    for _upstream_req in upstream_req_verifier.reqs:  # type: scenario.ReqTraceability.Upstream.Req
                        self._req2html(_list_generator, _upstream_req)

    def _req2html(
            self,
            list_generator,  # type: _ListGeneratorType
            upstream_req,  # type: scenario.ReqTraceability.Upstream.Req
    ):  # type: (...) -> None
        """
        Builds the HTML content for a requirement.

        :param list_generator: List generator. Provides the HTML output page to feed.
        :param upstream_req: Requirement to build HTML content for.
        """
        from ._htmlgenlinks import LinkGenerator
        from ._htmlgentypes import CollapsibleState
        from ._pagereqs import RequirementsPage
        from ._pagereqsdown import DownstreamTraceabilityPage

        # Generate a collapsible list item.
        with list_generator.additem(
            li1_cid=upstream_req.req.id,
            default_state=CollapsibleState.COLLAPSED,
            classes=["req"],
        ):
            # Requirement id.
            with list_generator.html.addnode("span", classes=["req", "id"]):
                # With link to requirements page.
                LinkGenerator(list_generator.html).addlink(
                    href=RequirementsPage.mkurl(upstream_req.req.main_ref),
                    title="Requirement details",
                    text=upstream_req.req.id,
                )

            # Downstream traceability link.
            DownstreamTraceabilityPage.reqref2htmllink(list_generator.html, upstream_req.req.main_ref)

            # Traceability comments.
            list_generator.addcomment(upstream_req.comments, classes=["req"])

            # Optional subrefs.
            if upstream_req.req_subrefs:
                for _upstream_req_subref in upstream_req.req_subrefs:  # type: scenario.ReqTraceability.Upstream.ReqSubref
                    self._subref2html(list_generator, _upstream_req_subref)

    def _subref2html(
            self,
            list_generator,  # type: _ListGeneratorType
            upstream_req_subref,  # type: scenario.ReqTraceability.Upstream.ReqSubref
    ):  # type: (...) -> None
        """
        Builds the HTML content for a requirement subreference.

        :param list_generator: List generator. Provides the HTML output page to feed.
        :param upstream_req_subref: Requirement subreference to build HTML content for.
        """
        from ._htmlgenlinks import LinkGenerator
        from ._pagereqs import RequirementsPage
        from ._pagereqsdown import DownstreamTraceabilityPage

        with list_generator.addsubitem(classes=["subref"]):
            # Requirement subreference id.
            with list_generator.html.addnode("span", classes=["subref", "id"]):
                # With link to requirement details.
                LinkGenerator(list_generator.html).addlink(
                    href=RequirementsPage.mkurl(upstream_req_subref.req_subref),
                    title="Requirement details",
                    text=upstream_req_subref.req_subref.id,
                )

            # Downstream traceability link.
            DownstreamTraceabilityPage.reqref2htmllink(list_generator.html, upstream_req_subref.req_subref)

            # Traceability comments.
            list_generator.addcomment(upstream_req_subref.comments, classes=["subref"])
