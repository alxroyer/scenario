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
HTML page generation.
"""

import html
import typing

import scenario
if typing.TYPE_CHECKING:
    from .._xmlutils import Xml as _XmlType  # Access `scenario` inner symbols.

if typing.TYPE_CHECKING:
    from ._httprequest import HttpRequest as _HttpRequestType


class HtmlDocument(scenario.Logger):
    """
    HTML document generator.
    """

    class NodeContext:
        """
        Context that installs a new child node as the :attr:`HtmlDocument.current_node`.

        Returned by :meth:`HtmlDocument.addcontent()`.
        """

        def __init__(
                self,
                html_doc,  # type: HtmlDocument
                new_child,  # type: _XmlType.Node
        ):  # type: (...) -> None
            """
            :param html_doc: HTML document to set the current node for.
            :param new_child: New child node to set as the current node.
            """
            #: HTML document to set the current node for.
            self.html = html_doc  # type: HtmlDocument
            #: Parent node of the :attr:`new_child`.
            self.parent_node = html_doc.current_node  # type: _XmlType.Node
            #: New child node to set as the current node.
            self.new_child = new_child  # type: _XmlType.Node

        def __enter__(self):  # type: (...) -> _XmlType.Node
            """
            Installs :attr:`new_child` as the current node.

            :return: The new child just installed as the current node.
            """
            self.html.current_node = self.new_child

            return self.new_child

        def __exit__(
                self,
                exc_type,  # type: typing.Any
                exc_val,  # type: typing.Any
                exc_tb,  # type: typing.Any
        ):  # type: (...) -> None
            """
            Restores the current node with :attr:`parent_node`.
            """
            self.html.current_node = self.parent_node

    def __init__(self):  # type: (...) -> None
        """
        Initializes the HTML document
        and sets the current node with the main div of the page.
        """
        from .._xmlutils import Xml  # Access `scenario` inner symbols.
        from ._configdb import UI_CONFIG
        from ._debugclasses import UIDebugClass

        scenario.Logger.__init__(self, UIDebugClass.HTML_DOCUMENT)

        #: XML document of the HTML page.
        self.xml_doc = Xml.Document()  # type: Xml.Document
        self.xml_doc.root = self.xml_doc.createnode("html")
        #: Root ``<html/>`` node.
        self.html = self.xml_doc.root  # type: Xml.Node
        #: Current node, which content can be added to with :meth:`addcontent()`.
        self.current_node = self.html  # type: Xml.Node

        #: HTML ``<head/>`` section node.
        self.head = self.xml_doc.createnode("head")  # type: Xml.Node
        with self.addcontent('<head></head>') as self.head:
            self.addcontent('<meta http-equiv="Content-type" content="text/html; charset=utf-8" />')
            #: HTML head title node, which text content will be set with :meth:`settitle()`.
            self._head_title = self.addcontent('<title>...</title>').new_child  # type: Xml.Node
            self.addcontent(f'<link rel="stylesheet" href="{self.escape(UI_CONFIG.cssurl())}" type="text/css" />')
            self.addcontent(f'<script src="{self.escape(UI_CONFIG.jsurl())}"></script>', auto_closing=False)

        #: HTML ``<body/>`` section node.
        self.body = self.xml_doc.createnode("body")  # type: Xml.Node
        with self.addcontent('<body></body>') as self.body:
            # Menu and reload button.
            self._menu2html()
            self._reloadbutton2html()

            #: Main ``<h1/>`` node, which text content will be set with :meth:`settitle()`.
            self._h1 = self.addcontent('<h1>...</h1>').new_child   # type: Xml.Node

            #: Main ``<div/>`` node, which page content will be added to by :class:`._requesthandler.RequestHandler` subclasses.
            self.main_div = self.addcontent('<div id="main"></div>').new_child  # type: Xml.Node

        # Set main <div/> as the current node in the end.
        self.current_node = self.main_div

    def _menu2html(self):  # type: (...) -> None
        """
        Builds the navigation menu HTML.
        """
        from ._pagecampaigns import CampaignListPage
        from ._pageconfig import ConfigurationPage
        from ._pagehome import Homepage
        from ._pagereqs import RequirementsPage
        from ._pagereqsdown import DownstreamTraceabilityPage
        from ._pagereqsup import UpstreamTraceabilityPage
        from ._pagescenarios import ScenarioListPage

        with self.addcontent('<div id="menu"></div>'):
            self.addcontent(f'<a class="menu" href="{Homepage.mkurl()}">Home</a>')
            self.addcontent(f'<a class="menu" href="{ConfigurationPage.mkurl()}">Configuration</a>')
            self.addcontent(f'<a class="menu" href="{RequirementsPage.mkurl()}">Requirements</a>')
            self.addcontent(f'<a class="menu" href="{ScenarioListPage.mkurl()}">Scenarios</a>')
            self.addcontent(f'<a class="menu" href="{CampaignListPage.mkurl()}">Campaigns</a>')
            self.addcontent(f'<a class="menu" href="{DownstreamTraceabilityPage.mkurl()}">Downstream traceability</a>')
            self.addcontent(f'<a class="menu" href="{UpstreamTraceabilityPage.mkurl()}">Upstream traceability</a>')

    def _reloadbutton2html(self):  # type: (...) -> None
        """
        Builds the reload button HTML.
        """
        from ._pageconfig import ConfigurationPage

        with self.addcontent('<div id="reload-default"></div>'):
            self.addcontent(f'<a href="{ConfigurationPage.mkurl(reload_default=True)}">Reload default data</a>')

    def settitle(
            self,
            request,  # type: _HttpRequestType
            title,  # type: str
            *,
            campaign_subtitle=False,  # type: bool
    ):  # type: (...) -> None
        """
        Sets the title of the HTML page.

        :param request: Input request.
        :param title: New title. Not HTML-encoded.
        :param campaign_subtitle: Set to ``True`` to add campaign subtitle.
        """
        from ._pagecampaign import CampaignPage
        from ._reqbl import UI_REQ_BASELINES

        _req_baseline_desc = UI_REQ_BASELINES.getdesc(request.req_baseline)  # type: str

        self._head_title.gettextnodes()[0].data = self.escape(title)
        if campaign_subtitle and request.campaign_execution:
            self._head_title.gettextnodes()[0].data += f" ({self.escape(_req_baseline_desc)})"

        self._h1.gettextnodes()[0].data = ""
        with HtmlDocument.NodeContext(self, self._h1):
            self.addcontent(f'<span class="title main">{self.escape(title)}</span>')
            if campaign_subtitle and request.campaign_execution:
                self.addcontent('<span class="title sep"></span>')

                _url = CampaignPage.mkurl(request.campaign_execution)  # type: str
                self.addcontent(f'<span class="title req-baseline"><a href="{_url}">{self.escape(_req_baseline_desc)}</a></span>')

    def addcontent(
            self,
            content,  # type: str
            *,
            auto_closing=True,  # type: bool
    ):  # type: (...) -> HtmlDocument.NodeContext
        """
        Adds HTML content to the current node.

        :param content:
            HTML content.

            .. note:: The :meth:`escape()` method shall be used to ensure HTML encoding for uncontrolled text data.
        :param auto_closing:
            Set to ``False`` to avoid auto-closing node.
        :return:
            Context manager that controls the current node further content will be added to.
        """
        from .._xmlutils import Xml  # Access `scenario` inner symbols.

        # Parse the XML content as a new node.
        _child = self.xml_doc.parsestream(content)  # type: Xml.INode
        if not isinstance(_child, Xml.Node):
            raise ValueError(f"Unexpected XML content {content!r}, parsed as {_child!r} (not a node)")

        # Avoid auto-closing.
        if not auto_closing:
            _child.appendchild(self.xml_doc.createtextnode(""))

        # Append it as a child to the current node.
        self.current_node.appendchild(_child)
        self.debug("current_node=%r: addcontent(%r) -> %r", self.current_node, content, _child)

        # Return a context that positions the new child as the current node.
        return HtmlDocument.NodeContext(self, _child)

    def addtext(
            self,
            text,  # type: str
            *,
            html_escape=True,  # type: bool
    ):  # type: (...) -> _XmlType.TextNode
        """
        Adds text to the current node.

        :param text:
            Text to add.
        :param html_escape:
            If ``True`` (default), :meth:`escape()` will be automatically called on ``text``.

            Set to ``False`` to avoid :meth:`escape()` being called.
        :return:
            Text node created.
        """
        if html_escape:
            # HTML encoding.
            text = self.escape(text)
        return self.current_node.appendchild(self.xml_doc.createtextnode(text))

    @staticmethod
    def escape(
            text,  # type: str
    ):  # type: (...) -> str
        """
        Encodes text for HTML.

        :param text: Text to encode.
        :return: HTML-encoded text.

        .. tip:: Use only in case of risk of uncontrolled data.
        """
        return html.escape(text)

    def dump(self) -> bytes:
        """
        Dumps the HTML document into bytes.

        :return: HTML document as bytes.
        """
        return b'\n'.join([
            b'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">',
            self.xml_doc.dumpstream(encoding="utf-8"),
        ])
