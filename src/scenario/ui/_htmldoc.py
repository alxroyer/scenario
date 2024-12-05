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

    def __init__(
            self,
            request,  # type: _HttpRequestType
    ):  # type: (...) -> None
        """
        Initializes an HTML document for the given request
        and sets the current node with the main div of the page.

        :param request: Input request.
        """
        from .._xmlutils import Xml  # Access `scenario` inner symbols.
        from ._debugclasses import UIDebugClass

        scenario.Logger.__init__(self, UIDebugClass.HTML_DOCUMENT)

        #: Input request.
        self.request = request  # type: _HttpRequestType

        #: XML document of the HTML page.
        self.xml_doc = Xml.Document()  # type: Xml.Document
        self.xml_doc.root = self.xml_doc.createnode("html")
        #: Auto-closing condidate nodes.
        self._auto_closing = []  # type: typing.List[_XmlType.Node]
        #: Root ``<html/>`` node.
        self.html = self.xml_doc.root  # type: Xml.Node
        #: Current node, which content can be added to with :meth:`addcontent()`.
        self.current_node = self.html  # type: Xml.Node

        #: HTML ``<head/>`` section node.
        self.head = self.xml_doc.createnode("head")  # type: Xml.Node
        #: HTML head title node, which text content will be set with :meth:`settitle()`.
        self._head_title = self.xml_doc.createnode("title")  # type: Xml.Node
        #: HTML ``<body/>`` section node.
        self.body = self.xml_doc.createnode("body")  # type: Xml.Node
        #: Main ``<h1/>`` node, which text content will be set with :meth:`settitle()`.
        self._h1 = self.xml_doc.createnode("h1")  # type: Xml.Node
        #: Main ``<div/>`` node, which page content will be added to by :class:`._httprequesthandler.HttpRequestHandler` subclasses.
        self.main_div = self.xml_doc.createnode("div")  # type: Xml.Node

        self._head2html()
        self._body2html()

        # Add inner scripts at the end of the document (for readability of the HTML output).
        self.jscontent2html("_anchors.js")
        self.jscontent2html("_exec.js")

        # Set main <div/> as the current node in the end.
        self.current_node = self.main_div

    def _head2html(self):  # type: (...) -> None
        """
        Generates ``<head></head>`` content.

        Instantiates :attr:`head` and :attr:`_head_title`.
        """
        from ._configdb import UI_CONFIG

        with self.addcontent('<head></head>') as self.head:
            self.addcontent(f'<link rel="shortcut icon" href="{self.escape(UI_CONFIG.faviconurl())}" />')
            self.addcontent('<meta http-equiv="Content-type" content="text/html; charset=utf-8" />')
            self._head_title = self.addcontent('<title>...</title>').new_child
            self.addcontent(f'<link rel="stylesheet" href="{self.escape(UI_CONFIG.cssurl())}" type="text/css" />')
            self.jscontent2html("_global.js")
            self.addcontent(f'<script src="{self.escape(UI_CONFIG.jsurl())}"></script>')

    def _body2html(self):  # type: (...) -> None
        """
        Generates ``<body></body>`` content.

        Instantiates :attr:`body`, :attr:`_h1` and :attr:`main_div`.
        """
        with self.addcontent('<body></body>') as self.body:
            # Menu and reload button.
            self._menu2html()
            self._execresultdiv2html()
            self._h1 = self.addcontent('<h1></h1>').new_child
            self.main_div = self.addcontent('<div id="main"></div>').new_child

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
            self.addlink(classes=["menu"], href=Homepage.mkurl(), text="Home")
            self.addlink(classes=["menu"], href=ScenarioListPage.mkurl(), text="Scenarios")
            self.addlink(classes=["menu"], href=CampaignListPage.mkurl(), text="Campaigns")
            self.addlink(classes=["menu"], href=RequirementsPage.mkurl(), text="Requirements")
            self.addlink(classes=["menu"], href=DownstreamTraceabilityPage.mkurl(), text="Downstream traceability")
            self.addlink(classes=["menu"], href=UpstreamTraceabilityPage.mkurl(), text="Upstream traceability")
            self.addlink(classes=["menu"], href=ConfigurationPage.mkurl(), text="Configuration")

    def _execresultdiv2html(self):  # type: (...) -> None
        """
        Generates the hidden ``.exec-result`` popup div.

        Hidden by default.
        Used by '_exec.js' to display execution results.
        """
        with self.addcontent('<div id="exec-result" style="display: none;"></div>'):
            self.addcontent('<div class="exec-result title"></div>')
            self.addcontent('<div class="exec-result text"></div>')
            self.addlink(href="#", classes=["exec-result", "button", "validate"], text="OK")

    def jscontent2html(
            self,
            filename,  # type: str
    ):  # type: (...) -> None
        """
        Embeds ``filename`` in an inner ``<script></script>`` element.

        :param filename: Javascript file name in the 'src/scenario/ui/' directory.
        """
        with self.addcontent('<script></script>'):
            _js_path = scenario.Path(__file__).parent / filename  # type: scenario.Path
            for _line in _js_path.read_text(encoding="utf-8").splitlines():  # type: str
                self.addtext(_line, html_escape=False)

    def settitle(
            self,
            title,  # type: str
            *,
            campaign_subtitle=False,  # type: bool
    ):  # type: (...) -> None
        """
        Sets the title of the HTML page.

        :param title: New title. Not HTML-encoded.
        :param campaign_subtitle: Set to ``True`` to add campaign subtitle.
        """
        from ._pagecampaign import CampaignPage
        from ._reqbl import UI_REQ_BASELINES

        _req_baseline_desc = UI_REQ_BASELINES.getdesc(self.request.req_baseline)  # type: str

        self._head_title.gettextnodes()[0].data = self.escape(title)
        if campaign_subtitle and self.request.campaign_execution:
            self._head_title.gettextnodes()[0].data += f" ({self.escape(_req_baseline_desc)})"

        with HtmlDocument.NodeContext(self, self._h1):
            self.addcontent(f'<span class="title main">{self.escape(title)}</span>')
            if campaign_subtitle and self.request.campaign_execution:
                self.addcontent('<span class="title sep"></span>')

                with self.addcontent('<span class="title req-baseline"></span>'):
                    self.addlink(href=CampaignPage.mkurl(self.request.campaign_execution), title="Campaign details", text=_req_baseline_desc)

    def addcontent(
            self,
            content,  # type: str
            *,
            auto_closing=False,  # type: bool
    ):  # type: (...) -> HtmlDocument.NodeContext
        """
        Adds HTML content to the current node.

        :param content:
            HTML content.

            .. note:: The :meth:`escape()` method shall be used to ensure HTML encoding for uncontrolled text data.
        :param auto_closing:
            Set to ``True`` to allow auto-closing node.
            ``False`` by default.
        :return:
            Context manager that controls the current node further content will be added to.
        """
        from .._xmlutils import Xml  # Access `scenario` inner symbols.

        # Parse the XML content as a new node.
        _child = self.xml_doc.parsestream(content)  # type: Xml.INode
        if not isinstance(_child, Xml.Node):
            raise ValueError(f"Unexpected XML content {content!r}, parsed as {_child!r} (not a node)")

        # Append it as a child to the current node.
        self.current_node.appendchild(_child)
        self.debug("current_node=%r: addcontent(%r) -> %r", self.current_node, content, _child)

        # Register as auto-closing node if required.
        if auto_closing:
            self._auto_closing.append(_child)

        # Return a context that positions the new child as the current node.
        return HtmlDocument.NodeContext(self, _child)

    def addlink(
            self,
            *,
            classes=(),  # type: typing.Sequence[str]
            html_escape_classes=True,  # type: bool
            href,  # type: str
            html_escape_href=True,  # type: bool
            title="",  # type: str
            html_escape_title=True,  # type: bool
            text="",  # type: str
            html_escape_text=True,  # type: bool
    ):  # type: (...) -> HtmlDocument.NodeContext
        """
        Adds a ``<a ...>...</a>`` link in the document,
        with ``@class``, ``@href``, ``@title`` attributes and text content.

        :param classes: Classes to set for ``@class`` attribute. No ``@class`` attribute if no class provided.
        :param html_escape_classes: ``True`` (default) to HTML escape class names.
        :param href: URL to set for ``@href`` attribute.
        :param html_escape_href: ``True`` (default) to HTML escape the ``@href`` URL.
        :param title: ``@title`` attribute value, used for popup info on link hover. None by default for no ``@title`` attribute.
        :param html_escape_title: ``True`` (default) to HTML escape the ``@title`` value.
        :param text: Text content for the link. Empty by default.
        :param html_escape_text: ``True`` (default) to HTML escape the text content.
        :return: Context manager focused on the new ``<a ...></a>`` node created.
        """
        if html_escape_classes:
            classes = [self.escape(_class) for _class in classes]
        if html_escape_href:
            href = self.escape(href)
        if html_escape_title:
            title = self.escape(title)
        if html_escape_text:
            text = self.escape(text)

        _attrs = []  # type: typing.List[str]
        if classes:
            _attrs.append(f'class="{" ".join(classes)}"')
        if href:
            _attrs.append(f'href="{href}"')
        if title:
            _attrs.append(f'title="{title}"')

        return self.addcontent(f'<a {" ".join(_attrs)}>{text}</a>')

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
        return self.current_node.appendchild(self.xml_doc.createtextnode(text, xml_escape=html_escape))

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
        def _avoidautoclosing(node):  # type: (_XmlType.Node) -> None
            """
            Recursively avoids auto-closing nodes in the output XML tree,
            unless for candidate nodes registered in the :attr:`_auto_closing` list.

            .. seealso:: :meth:`addcontent()`
            """
            # Inspect node content.
            _children = node.getchildren("*")  # type: typing.Sequence[_XmlType.Node]
            _text_nodes = node.gettextnodes()  # type: typing.Sequence[_XmlType.TextNode]

            # Avoid auto-closing by default.
            if (not _children) and (not _text_nodes):
                if node in self._auto_closing:
                    self.debug("Auto-closing node %r", node)
                else:
                    # Add empty text node to avoid auto-closing.
                    node.appendchild(self.xml_doc.createtextnode(""))

            # Recursive calls.
            for _child in _children:  # type: _XmlType.Node
                _avoidautoclosing(_child)
        _avoidautoclosing(self.xml_doc.root)

        return b'\n'.join([
            b'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">',
            self.xml_doc.dumpstream(encoding="utf-8"),
        ])
