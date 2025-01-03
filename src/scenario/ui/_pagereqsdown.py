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
    from ._httprequesthandler import HttpRequestHandler as _HttpRequestHandlerImpl  # @inheritance
if typing.TYPE_CHECKING:
    from ._collapsiblelist import CollapsibleListItemGenerator as _CollapsibleListItemGeneratorType
    from ._collapsibletable import CollapsibleTableGenerator as _CollapsibleTableGeneratorType
    from ._debugclasses import UIDebugClass as _UIDebugClassType
    from ._htmldoc import HtmlDocument as _HtmlDocumentType
    from ._httprequest import HttpRequest as _HttpRequestType


class DownstreamTraceabilityPage(_HttpRequestHandlerImpl):
    """
    Downstream traceability page.
    """

    #: Base URL for the downstream traceability page.
    _URL = "/downstream-traceability"  # type: str

    @staticmethod
    def mkurl(
            obj=None,  # type: typing.Union[scenario.ReqBaseline, scenario.ReqRef]
    ):  # type: (...) -> str
        """
        Builds a downstream traceability page URL.

        :param obj:
            Applicable requirement baseline, or requirement reference to build an anchor URL for.

            If a :class:`scenario._reqref.ReqRef` is given, determines the requirement baseline by the way.

            Main requirement baseline by default.
        :return:
            Downstream traceability page URL.
        """
        from ._httprequest import HttpRequest

        return HttpRequest.encodeurl(
            DownstreamTraceabilityPage._URL,
            args=HttpRequest.mkurlargs(obj=obj),
            anchor=obj.id if isinstance(obj, scenario.ReqRef) else None,
        )

    @staticmethod
    def reqref2htmllink(
            html,  # type: _HtmlDocumentType
            req_ref,  # type: scenario.ReqRef
            *,
            text="",  # type: str
    ):  # type: (...) -> None
        """
        Builds a HTML link to the given requirement reference in the downstream tracebility page.

        :param html: HTML output page to feed.
        :param req_ref: Requirement reference to build a downstream traceability link for.
        :param text: Link text. Sets the ``.default-text`` class and ``@title`` attribute if not provided.
        """
        _classes = ["downstream", "traceability"]  # type: typing.List[str]
        _title = ""  # type: str
        if not text:
            _classes.append("default-text")
            _title = "Downstream traceability"
            text = "(>>)"

        with html.addlink(classes=_classes, href=DownstreamTraceabilityPage.mkurl(req_ref), title=_title):
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

        _HttpRequestHandlerImpl.__init__(self, debug_class or UIDebugClass.PAGE_REQS_DOWN)

    def process(
            self,
            request,  # type: _HttpRequestType
    ):  # type: (...) -> bool
        from ._exec import Exec
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
        _html = HtmlDocument(request)
        _html.settitle("Downstream traceability", campaign_subtitle=True)

        Exec.actionbutton2html(_html, request, Exec.Action.RELOAD_MAIN_REQ_BASELINE)

        self.downstreamtraceability2html(_html, request.req_baseline)

        request.sendhtml(_html)
        return True

    def downstreamtraceability2html(
            self,
            html,  # type: _HtmlDocumentType
            req_baseline,  # type: scenario.ReqBaseline
    ):  # type: (...) -> None
        """
        Builds the HTML content for the downstream traceability given with the requirement baseline.

        :param html: HTML output page to feed.
        :param req_baseline: Requirement baseline holding the requirement database and scenarios to process.
        """
        from ._collapsiblestate import CollapsibleState
        from ._collapsibletable import CollapsibleTableGenerator

        with html.addnode("div", id="downstream-traceability"):
            # Compute downstream traceability.
            _downstream_traceability = scenario.ReqTraceability(req_baseline).getdownstream()  # type: scenario.ReqDownstreamTraceabilityType

            # Instantiate the table generator.
            _table_generator = CollapsibleTableGenerator(
                html,
                table_id="downstream-traceability",
                default_state=CollapsibleState.COLLAPSED,
            )  # type: CollapsibleTableGenerator

            # Expand/collapse all buttons.
            _table_generator.addexpandallbutton()
            _table_generator.addcollapseallbutton()

            with _table_generator.addtable():
                # Heading row.
                with html.addnode("tr", classes=["head"]):
                    html.addnode("th", classes=["req-ref"], text="Requirement")
                    html.addnode("th", classes=["req-verifier"], text="Test coverage")

                # Requirement reference rows.
                for _downstream_req_ref in _downstream_traceability:  # type: scenario.ReqTraceability.Downstream.ReqRef
                    self._reqref2html(_table_generator, _downstream_req_ref)

    def _reqref2html(
            self,
            table_generator,  # type: _CollapsibleTableGeneratorType
            downstream_req_ref,  # type: scenario.ReqTraceability.Downstream.ReqRef
    ):  # type: (...) -> None
        """
        Builds the HTML content for a requirement reference.

        :param table_generator: Table generator. Provides the HTML output page to feed.
        :param downstream_req_ref: Requirement reference to build HTML content for.
        """
        from ._anchors import Anchor
        from ._pagereqs import RequirementsPage

        with (
            table_generator.addmainrow(main_row_id=downstream_req_ref.req_ref.id, classes=["main"])
            if downstream_req_ref.req_ref.ismain() else
            table_generator.addcollapsiblerow(classes=["sub"])
        ):
            # Requirement.
            with table_generator.html.addnode("td", classes=["req-ref"]):
                if downstream_req_ref.req_ref.ismain():
                    # Expand/collapse button.
                    table_generator.addtogglebutton()

                # Anchor.
                with Anchor.add(table_generator.html, name=downstream_req_ref.req_ref.id):
                    # Requirement id, with link to requirement details.
                    table_generator.html.addlink(
                        classes=["req-ref", "id"],
                        href=RequirementsPage.mkurl(downstream_req_ref.req_ref),
                        title="Requirement details",
                        text=downstream_req_ref.req_ref.id,
                    )

                    # Title.
                    if downstream_req_ref.req_ref.ismain() and downstream_req_ref.req_ref.req.title:
                        table_generator.html.addnode("span", classes=["req-ref", "sep"], text=":")
                        table_generator.html.addnode("span", classes=["req-ref", "title"], text=downstream_req_ref.req_ref.req.title)

            # Test coverage.
            with table_generator.html.addnode("td", classes=["req-verifier"]):
                with table_generator.html.addnode("ul"):
                    for _downstream_scenario in downstream_req_ref.scenarios:  # type: scenario.ReqTraceability.Downstream.Scenario
                        self._scenario2html(table_generator.html, _downstream_scenario)

    def _scenario2html(
            self,
            html,  # type: _HtmlDocumentType
            downstream_scenario,  # type: scenario.ReqTraceability.Downstream.Scenario
    ):  # type: (...) -> None
        """
        Builds the HTML content for a scenario.

        :param html: HTML output page to feed.
        :param downstream_scenario: Scenario to build HTML content for.
        """
        from ._collapsiblelist import CollapsibleListItemGenerator
        from ._collapsiblestate import CollapsibleState
        from ._pagereqsup import UpstreamTraceabilityPage
        from ._pagescenario import ScenarioPage

        # Instantiate the list item generator.
        _list_item_generator = CollapsibleListItemGenerator(
            html,
            main_list_item_id=downstream_scenario.scenario.name,
            default_state=CollapsibleState.COLLAPSED,
        )

        with _list_item_generator.addmainlistitem(classes=["req-verifier", "scenario"]):
            # Upstream traceability link.
            UpstreamTraceabilityPage.reqverifier2htmllink(html, downstream_scenario.scenario)

            # Scenario name.
            with html.addnode("span", classes=["req-verifier", "scenario", "name"]):
                # With link to scenario details page.
                html.addlink(
                    href=ScenarioPage.mkurl(downstream_scenario.scenario),
                    title="Scenario details",
                    text=downstream_scenario.scenario.name,
                )

            # Traceability comments.
            _list_item_generator.addcomments(downstream_scenario.comments, classes=["req-verifier", "scenario"])

            # Optional steps.
            if downstream_scenario.steps:
                with html.addnode("ul"):
                    for _downstream_step in downstream_scenario.steps:  # type: scenario.ReqTraceability.Downstream.Step
                        self._step2html(_list_item_generator, _downstream_step)

    def _step2html(
            self,
            list_item_generator,  # type: _CollapsibleListItemGeneratorType
            downstream_step,  # type: scenario.ReqTraceability.Downstream.Step
    ):  # type: (...) -> None
        """
        Builds the HTML content for a step.

        :param list_item_generator: List item generator. Provides the HTML output page to feed.
        :param downstream_step: Step to build HTML content for.
        """
        from ._pagereqsup import UpstreamTraceabilityPage
        from ._pagescenario import ScenarioPage

        with list_item_generator.addcollapsiblelistitem(classes=["req-verifier", "step"]):
            # Step number and name.
            with list_item_generator.html.addnode("span", classes=["req-verifier", "step", "name"]):
                # With link to scenario details.
                list_item_generator.html.addlink(
                    href=ScenarioPage.mkurl(downstream_step.step),
                    title="Scenario details",
                    text=downstream_step.name,
                )

            # Upstream traceability link.
            UpstreamTraceabilityPage.reqverifier2htmllink(list_item_generator.html, downstream_step.step)

            # Traceability comments.
            list_item_generator.addcomments(downstream_step.comments, classes=["req-verifier", "step"])
