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
HTML menu generator.
"""

import typing

if typing.TYPE_CHECKING:
    from ._htmldoc import HtmlDocument as _HtmlDocumentType


class MenuGenerator:
    """
    HTML generator for the main menu, at the top of each page.
    """

    def __init__(
            self,
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        """
        Instantiates a :class:`MenuGenerator` with configuration.

        :param html: HTML output page to feed.
        """
        #: HTML output page to feed.
        self.html = html  # type: _HtmlDocumentType

    def __repr__(self):  # type: () -> str
        """
        Canonical string representation.

        For debugging purpose.
        """
        return "MenuGenerator(%s)" % (", ".join([
        ]))

    def addmenu(self):  # type: (...) -> None
        """
        Builds the navigation menu HTML.
        """
        from ._htmlgenlinks import LinkGenerator
        from ._pagecampaigns import CampaignListPage
        from ._pageconfig import ConfigurationPage
        from ._pagehome import Homepage
        from ._pagereqs import RequirementsPage
        from ._pagereqsdown import DownstreamTraceabilityPage
        from ._pagereqsup import UpstreamTraceabilityPage
        from ._pagescenarios import ScenarioListPage

        with self.html.addnode("div", id="menu"):
            LinkGenerator(self.html).addlink(classes=["menu"], href=Homepage.mkurl(), text="Home")
            LinkGenerator(self.html).addlink(classes=["menu"], href=ScenarioListPage.mkurl(), text="Scenarios")
            LinkGenerator(self.html).addlink(classes=["menu"], href=CampaignListPage.mkurl(), text="Campaigns")
            LinkGenerator(self.html).addlink(classes=["menu"], href=RequirementsPage.mkurl(), text="Requirements")
            LinkGenerator(self.html).addlink(classes=["menu"], href=DownstreamTraceabilityPage.mkurl(), text="Downstream traceability")
            LinkGenerator(self.html).addlink(classes=["menu"], href=UpstreamTraceabilityPage.mkurl(), text="Upstream traceability")
            LinkGenerator(self.html).addlink(classes=["menu"], href=ConfigurationPage.mkurl(), text="Configuration")
