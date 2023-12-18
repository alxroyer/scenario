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

if True:
    from ._requesthandler import RequestHandler as _RequestHandlerImpl  # `RequestHandler` used for inheritance.
if typing.TYPE_CHECKING:
    from ._htmldoc import HtmlDocument as _HtmlDocumentType
    from ._httprequest import HttpRequest as _HttpRequestType


class Scenarios(_RequestHandlerImpl):
    """
    Scenario list page.
    """

    #: Base URL for the scenario list page.
    URL = "/scenarios"

    def matches(
            self,
            request,  # type: _HttpRequestType
    ):  # type: (...) -> bool
        return request.base_path == Scenarios.URL

    def process(
            self,
            request,  # type: _HttpRequestType
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        from .._reqtraceability import REQ_TRACEABILITY
        from .._scenariodefinition import ScenarioDefinition

        html.settitle("Scenarios")

        with html.addcontent('<div id="scenarios"></div>'):
            with html.addcontent('<ul></ul>'):
                for _scenario in REQ_TRACEABILITY.scenarios:  # type: ScenarioDefinition
                    with html.addcontent('<li class="scenario"></li>'):
                        html.addcontent(f'<span class="scenario name">{html.encode(_scenario.name)}</span>')
                        if _scenario.title:
                            html.addcontent('<span class="scenario sep">:</span>')
                            html.addcontent(f'<span class="scenario title">{html.encode(_scenario.title)}</span>')
