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
User interface home page.
"""

import typing

if True:
    from ._httprequesthandler import HttpRequestHandler as _HttpRequestHandlerImpl  # @inheritance
if typing.TYPE_CHECKING:
    from ._httprequest import HttpRequest as _HttpRequestType


class Homepage(_HttpRequestHandlerImpl):
    """
    Home page.
    """

    #: Base URL for the homepage.
    _URL = "/"  # type: str

    @staticmethod
    def mkurl():  # type: (...) -> str
        """
        Builds a homepage URL.

        :return: Homepage URL.
        """
        from ._httprequest import HttpRequest

        return HttpRequest.encodeurl(
            Homepage._URL,
            args=HttpRequest.mkurlargs(obj=None),
        )

    def __init__(self):  # type: (...) -> None
        """
        Configures the logger instance.
        """
        from ._debugclasses import UIDebugClass

        _HttpRequestHandlerImpl.__init__(self, UIDebugClass.PAGE_HOME)

    def process(
            self,
            request,  # type: _HttpRequestType
    ):  # type: (...) -> bool
        from ._htmldoc import HtmlDocument
        from ._pagecampaigns import CampaignListPage
        from ._pagereqs import RequirementsPage
        from ._pagereqsdown import DownstreamTraceabilityPage
        from ._pagereqsup import UpstreamTraceabilityPage
        from ._pagescenarios import ScenarioListPage

        # Filter `request`.
        if request.base_path != Homepage._URL:
            self.debug("Request base path %r not matching %r", request.base_path, Homepage._URL)
            self.debug("%r not processed", request)
            return False
        self.debug("Processing %r", request)

        self.debug("Generating HTML content")
        _html = HtmlDocument(request)  # type: HtmlDocument
        _html.settitle("Scenario User Interface", campaign_subtitle=False)

        with _html.addnode("p"):
            _html.addnode("span", text="Browse ")
            _html.addlink(text="scenarios", href=ScenarioListPage.mkurl(), title="Scenario list")
            _html.addnode("span", text=" described in test scripts, and ")
            _html.addlink(text="campaign results", href=CampaignListPage.mkurl(), title="Campaign results")
            _html.addnode("span", text=".")

        with _html.addnode("p"):
            _html.addnode("span", text="Working with ")
            _html.addlink(text="requirements", href=RequirementsPage.mkurl(), title="Requirement list")
            _html.addnode("span", text="? Browse ")
            _html.addlink(text="downstream", href=DownstreamTraceabilityPage.mkurl(), title="Downstream traceability")
            _html.addnode("span", text=" and ")
            _html.addlink(text="upstream", href=UpstreamTraceabilityPage.mkurl(), title="Upstream traceability")
            _html.addnode("span", text=" traceability tables.")

        request.sendhtml(_html)
        return True
