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

        Context basically returned by :meth:`HtmlDocument.addnode()` (and related).
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
            #: Previous current node installed before :attr:`new_child`.
            #: Saved in :meth:`__enter__()`.
            self.previous_node = self.html.body  # type: _XmlType.Node
            #: New child node to set as the current node.
            self.new_child = new_child  # type: _XmlType.Node

        def __enter__(self):  # type: (...) -> _XmlType.Node
            """
            Installs :attr:`new_child` as the current node.

            :return: The new child just installed as the current node.
            """
            self.previous_node = self.html.current_node
            self.html.current_node = self.new_child

            self.html.debug(">> %r", self.html.current_node)
            self.html.pushindentation("  ")

            return self.new_child

        def __exit__(
                self,
                exc_type,  # type: typing.Any
                exc_val,  # type: typing.Any
                exc_tb,  # type: typing.Any
        ):  # type: (...) -> None
            """
            Restores the current node with :attr:`previous_node`.
            """
            self.html.popindentation("  ")
            self.html.debug("<< %r", self.html.current_node)

            self.html.current_node = self.previous_node

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
        #: Current node, which content can be added to with :meth:`addnode()` and :meth:`addtext()`.
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

        #: Inner JS script files which content to embed at the end of the document.
        #:
        #: .. note:: Embedding JS content at the end of the document improves readability of the HTML output.
        self._final_js_paths = [
            scenario.Path(__file__).parent / "_anchors.js",
            scenario.Path(__file__).parent / "_exec.js",
        ]  # type: typing.List[scenario.Path]

        # Set main <div/> as the current node in the end.
        self.current_node = self.main_div

    def _head2html(self):  # type: (...) -> None
        """
        Generates ``<head></head>`` content.

        Instantiates :attr:`head` and :attr:`_head_title`.
        """
        from ._configdb import UI_CONFIG

        with self.addnode("head") as self.head:
            self.addnode("link", rel="shortcut icon", href=UI_CONFIG.faviconurl(), auto_closing=True)
            self.addnode("meta", {"http-equiv": "Content-type", "content": "text/html; charset=utf-8"}, auto_closing=True)
            self._head_title = self.addnode("title", text="...").new_child
            self.addnode("link", rel="stylesheet", href=UI_CONFIG.cssurl(), type="text/css", auto_closing=True)
            self._jscontent2html(scenario.Path(__file__).parent / "_global.js")
            self.addnode("script", src=UI_CONFIG.jsurl())

    def _body2html(self):  # type: (...) -> None
        """
        Generates ``<body></body>`` content.

        Instantiates :attr:`body`, :attr:`_h1` and :attr:`main_div`.
        """
        from ._exec import Exec

        with self.addnode("body") as self.body:
            # Menu and reload button.
            self._menu2html()
            Exec.execresultdiv2html(self)
            self._h1 = self.addnode("h1").new_child
            self.main_div = self.addnode("div", id="main").new_child

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

        with self.addnode("div", id="menu"):
            self.addlink(classes=["menu"], href=Homepage.mkurl(), text="Home")
            self.addlink(classes=["menu"], href=ScenarioListPage.mkurl(), text="Scenarios")
            self.addlink(classes=["menu"], href=CampaignListPage.mkurl(), text="Campaigns")
            self.addlink(classes=["menu"], href=RequirementsPage.mkurl(), text="Requirements")
            self.addlink(classes=["menu"], href=DownstreamTraceabilityPage.mkurl(), text="Downstream traceability")
            self.addlink(classes=["menu"], href=UpstreamTraceabilityPage.mkurl(), text="Upstream traceability")
            self.addlink(classes=["menu"], href=ConfigurationPage.mkurl(), text="Configuration")

    def _jscontent2html(
            self,
            js_path,  # type: scenario.Path
    ):  # type: (...) -> None
        """
        Embeds ``filename`` in an inner ``<script></script>`` element.

        :param js_path: Path of Javascript file to embed.
        """
        with self.addnode("script"):
            for _line in js_path.read_text(encoding="utf-8").splitlines():  # type: str
                # Don't use `addtext()` in order to avoid HTML/XML escaping.
                self.current_node.appendchild(self.xml_doc.createtextnode(_line, xml_escape=False))

    def addfinaljs(
            self,
            js_path,  # type: scenario.Path
    ):  # type: (...) -> None
        """
        Saves ``js_path`` for embedding at the end of the page.

        Stores ``js_path`` uniquely in the :attr:`_final_js_paths` path list.

        :param js_path: Javascript path which content to embed.
        """
        if js_path not in self._final_js_paths:
            self._final_js_paths.append(js_path)

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

        self._head_title.gettextnodes()[0].data = html.escape(title, quote=False)
        if campaign_subtitle and self.request.campaign_execution:
            self._head_title.gettextnodes()[0].data += f" ({html.escape(_req_baseline_desc, quote=False)})"

        with HtmlDocument.NodeContext(self, self._h1):
            self.addnode("span", classes=["title", "main"], text=title)
            if campaign_subtitle and self.request.campaign_execution:
                self.addnode("span", classes=["title", "sep"])

                with self.addnode("span", classes=["title", "req-baseline"]):
                    self.addlink(href=CampaignPage.mkurl(self.request.campaign_execution), title="Campaign details", text=_req_baseline_desc)

    def addnode(
            self,
            tag_name,  # type: str
            attrs=None,  # type: typing.Dict[str, typing.Optional[str]]
            *,
            id="",  # type: str  # noqa  ## Shadwos built-in name 'id'.
            classes=None,  # type: typing.Sequence[str]
            text=None,  # type: str
            auto_closing=False,  # type: bool
            **kwargs,  # type: typing.Optional[str]
    ):  # type: (...) -> HtmlDocument.NodeContext
        """
        Adds a child node to the current node.

        :param tag_name: Name of tag for the new node.
        :param attrs: Attributes passed as a dictionary. Optional. Useful when ``kwargs`` can't be used (attribute names with a dash, ...).
        :param id: Optional HTML identifier.
        :param classes: List of classes. May complete other classes already defined with ``attrs``.
        :param text: Optional content text.
        :param auto_closing: Set to ``True`` to allow auto-closing node. ``False`` by default.
        :param kwargs: In general, use named parameters to define attributes. Use ``attrs`` when named parameters don't work.
        :return: HTML node context that controls the current node, so that further content can be added to it.

        When an attribute value is ``None`` (either in ``attrs`` or ``kwargs``), the related HTML attribute won't be created.
        """
        from .._xmlutils import Xml  # Access `scenario` inner symbols.

        # Create the node.
        _child = self.xml_doc.createnode(tag_name)  # type: Xml.Node

        # Add attributes:
        if attrs is None:
            # - ensure `attrs` is defined,
            attrs = {}
        if True:
            # - merge `kwargs` in `attrs`,
            attrs.update(kwargs)
        if id:
            attrs["id"] = id
        if classes:
            # - merge `classes` in `attrs`,
            if "class" in attrs:
                classes = [*(attrs["class"] or "").split(), *classes]
            attrs["class"] = " ".join(classes)
        if attrs:
            # - eventually create the attributes when the value is not `None`.
            for _attr_name, _attr_value in attrs.items():  # type: str, typing.Optional[str]
                if _attr_value is not None:
                    _child.setattr(_attr_name, html.escape(_attr_value, quote=True))

        # Append the new node as a child to the current node.
        self.current_node.appendchild(_child)
        self.debug("addnode(%r, %r, text=%r) -> %r", tag_name, attrs, text, _child)

        # Build a node context focused on the new node.
        _child_node_ctx = HtmlDocument.NodeContext(self, _child)  # type: HtmlDocument.NodeContext

        if text:
            # Add content text when provided.
            with _child_node_ctx:
                self.addtext(text)
        elif auto_closing:
            # Register as auto-closing node if required.
            self._auto_closing.append(_child)

        # Return the node context built previously.
        return _child_node_ctx

    def addclass(
            self,
            new_class,  # type: str
    ):  # type: (...) -> None
        """
        Adds ``new_class`` to HTML classes of the current node.

        :param new_class: New HTML class.

        Does not add ``new_class`` twice if already set.
        """
        self.debug("addclass(%r)", new_class)
        try:
            _classes = self.current_node.getattr("class").split()  # type: typing.List[str]
        except KeyError:
            _classes = []
        if new_class not in _classes:
            _classes.append(new_class)
        self.current_node.setattr("class", " ".join(_classes))

    def removeclass(
            self,
            rm_class,  # type: str
    ):  # type: (...) -> None
        """
        Removes ``rm_class`` from HTML classes of the current node.

        :param rm_class: HTML class to remove.

        Removes all occurrences of ``rm_class``.
        Does not raise an error if ``rm_class`` was not set.
        """
        self.debug("removeclass(%r)", rm_class)
        try:
            _classes = self.current_node.getattr("class").split()  # type: typing.List[str]
        except KeyError:
            _classes = []
        _classes = [_class for _class in _classes if _class != rm_class]
        self.current_node.setattr("class", " ".join(_classes))

    def addstyle(
            self,
            new_rules,  # type: str
    ):  # type: (...) -> None
        """
        Adds ``new_rules`` to the ``@style`` attribute of the current node.

        :param new_rules: CSS rule(s) to add. May contain ';' characters to separate rules.

        .. warning:: Systematic style extension. No filtering regarding the previous value of the ``@style`` attribute.
        """
        self.debug("addstyle(%r)", new_rules)
        try:
            _rules = [_rule.strip() for _rule in self.current_node.getattr("style").split(";") if _rule.strip()]  # type: typing.List[str]
        except KeyError:
            _rules = []
        _rules.extend([_rule.strip() for _rule in new_rules.split(";") if _rule.strip()])
        self.current_node.setattr("style", "; ".join(_rules))

    def addlink(
            self,
            *,
            classes=(),  # type: typing.Sequence[str]
            href,  # type: str
            title=None,  # type: str
            text=None,  # type: str
    ):  # type: (...) -> HtmlDocument.NodeContext
        """
        Adds a ``<a ...>...</a>`` link in the document,
        with ``@class``, ``@href``, ``@title`` attributes and text content.

        :param classes: Classes to set for ``@class`` attribute. No ``@class`` attribute if no class provided.
        :param href: URL to set for ``@href`` attribute.
        :param title: ``@title`` attribute value, used for popup info on link hover. None by default for no ``@title`` attribute.
        :param text: Text content for the link. Empty by default.
        :return: HTML node context focused on the ``<a ...></a>`` element created.
        """
        return self.addnode(
            "a",
            classes=classes,
            href=href,
            title=title,
            text=text,
        )

    def addtext(
            self,
            text,  # type: str
    ):  # type: (...) -> _XmlType.TextNode
        """
        Adds text to the current node.

        :param text: Text to add.
        :return: Text node created.
        """
        self.debug("addtext(%r)", text)
        return self.current_node.appendchild(self.xml_doc.createtextnode(
            html.escape(text, quote=False),
            xml_escape=False,  # Already escaped.
        ))

    @staticmethod
    def mkcsscompatibleclass(
            raw,  # type: str
    ):  # type: (...) -> str
        """
        Ensures ``raw`` HTML class is compatible for CSS in class names.

        :param raw: Raw HTML class to ensure CSS compatibility for.
        :return: CSS compatible HTML class.
        """
        return (
            raw
            .replace(".", "-dot-")
            .replace("=", "-eq-")
            .replace("#", "-hash-")
        )

    def dump(self) -> bytes:
        """
        Dumps the HTML document into bytes.

        :return: HTML document as bytes.
        """
        def _avoidautoclosing(node):  # type: (_XmlType.Node) -> None
            """
            Recursively avoids auto-closing nodes in the output XML tree,
            unless for candidate nodes registered in the :attr:`_auto_closing` list.

            .. seealso:: :meth:`addnode()`
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

        # Embed final JS scripts.
        for _js_path in self._final_js_paths:  # type: scenario.Path
            self._jscontent2html(_js_path)

        return b'\n'.join([
            b'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">',
            self.xml_doc.dumpstream(encoding="utf-8"),
        ])
