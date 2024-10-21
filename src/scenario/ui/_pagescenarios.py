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
    from ._requesthandler import RequestHandler as _RequestHandlerImpl  # @inheritance
if typing.TYPE_CHECKING:
    from ._httprequest import HttpRequest as _HttpRequestType


class ScenarioListPage(_RequestHandlerImpl):
    """
    Scenario list page.
    """

    #: Base URL for the scenario list page.
    URL = "/scenarios"  # type: str

    def __init__(self):  # type: (...) -> None
        """
        Configures the logger instance.
        """
        from ._debugclasses import UIDebugClass

        _RequestHandlerImpl.__init__(self, UIDebugClass.PAGE_SCENARIOS)

    def process(
            self,
            request,  # type: _HttpRequestType
    ):  # type: (...) -> bool
        from ._htmldoc import HtmlDocument
        from ._pagereqsup import UpstreamTraceabilityPage
        from ._pagescenario import ScenarioPage

        # Filter `request`.
        if request.base_path != ScenarioListPage.URL:
            self.debug("Request base path %r not matching %r", request.base_path, ScenarioListPage.URL)
            self.debug("%r not processed", request)
            return False
        self.debug("Processing %r", request)

        self.debug("Generating HTML content")
        _html = HtmlDocument()
        _html.settitle("Scenarios")

        with _html.addcontent('<div id="scenarios"></div>'):
            with _html.addcontent('<ul></ul>'):
                for _scenario in request.req_baseline.scenarios:  # type: scenario.ScenarioDefinition
                    with _html.addcontent('<li class="scenario"></li>'):
                        # Scenario name.
                        with _html.addcontent(f'<span class="scenario name"></span>'):
                            with _html.addcontent(f'<a href="{ScenarioPage.mkurl(_scenario)}"></a>'):
                                _html.addtext(_scenario.name)

                        # Upstream traceability link.
                        UpstreamTraceabilityPage.scenario2unnamedhtmllink(_scenario, _html)

                        # Title.
                        if _scenario.title:
                            _html.addcontent('<span class="scenario sep">:</span>')
                            _html.addcontent(f'<span class="scenario title">{_html.encode(_scenario.title)}</span>')

        request.sendhtml(_html)
        return True
