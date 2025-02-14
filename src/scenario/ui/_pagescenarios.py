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
User interface scenario list page.
"""

import typing

import scenario

if True:
    from ._httprequesthandler import HttpRequestHandler as _HttpRequestHandlerImpl  # @inheritance
if typing.TYPE_CHECKING:
    from ._debugclasses import UIDebugClass as _UIDebugClassType
    from ._htmldoc import HtmlDocument as _HtmlDocumentType
    from ._httprequest import HttpRequest as _HttpRequestType


class ScenarioListPage(_HttpRequestHandlerImpl):
    """
    Scenario list page.
    """

    #: Base URL for the scenario list page.
    _URL = "/scenarios"  # type: str

    @staticmethod
    def mkurl(
            req_baseline=None,  # type: scenario.ReqBaseline
    ):  # type: (...) -> str
        """
        Builds a scenario list page URL.

        :param req_baseline:
            Applicable requirement baseline

            Main requirement baseline by default.
        :return:
            Scenario list page URL.
        """
        from ._httprequest import HttpRequest

        return HttpRequest.encodeurl(
            ScenarioListPage._URL,
            args=HttpRequest.mkurlargs(obj=req_baseline),
        )

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

        _HttpRequestHandlerImpl.__init__(self, debug_class or UIDebugClass.PAGE_SCENARIOS)

    def process(
            self,
            request,  # type: _HttpRequestType
    ):  # type: (...) -> bool
        from ._exec import Exec
        from ._htmldoc import HtmlDocument

        # Filter `request`.
        if request.base_path != ScenarioListPage._URL:
            self.debug("Request base path %r not matching %r", request.base_path, ScenarioListPage._URL)
            self.debug("%r not processed", request)
            return False
        self.debug("Processing %r", request)

        # Applicable baseline.
        self.debug("Requirement baseline: %r", request.req_baseline)

        self.debug("Generating HTML content")
        _html = HtmlDocument(request)
        _html.settitle("Scenarios", campaign_subtitle=True)

        Exec.actionbutton2html(_html, request, Exec.Action.RELOAD_MAIN_REQ_BASELINE)

        self.scenarios2html(_html, request.req_baseline)

        request.sendhtml(_html)
        return True

    def scenarios2html(
            self,
            html,  # type: _HtmlDocumentType
            req_baseline,  # type: scenario.ReqBaseline
    ):  # type: (...) -> None
        """
        Builds the HTML content for the given scenario list.

        :param html: HTML output page to feed.
        :param req_baseline: Requirement baseline holding the scenario list to process.
        """
        from ._htmlgenlinks import LinkGenerator
        from ._pagereqsup import UpstreamTraceabilityPage
        from ._pagescenario import ScenarioPage

        with html.addnode("div", id="scenarios"):
            with html.addnode("ul"):
                for _scenario_definition in req_baseline.scenarios:  # type: scenario.ScenarioDefinition
                    with html.addnode("li", classes=["scenario"]):
                        # Upstream traceability link.
                        UpstreamTraceabilityPage.reqverifier2htmllink(html, _scenario_definition)

                        # Scenario name.
                        with html.addnode("span", classes=["scenario", "name"]):
                            LinkGenerator(html).addlink(
                                href=ScenarioPage.mkurl(_scenario_definition),
                                title="Scenario details",
                                text=_scenario_definition.name,
                            )

                        # Title.
                        if _scenario_definition.title:
                            html.addnode("span", classes=["scenario", "sep"], text=":")
                            html.addnode("span", classes=["scenario", "title"], text=_scenario_definition.title)
