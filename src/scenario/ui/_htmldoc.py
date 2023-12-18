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

if True:
    from .._logger import Logger as _LoggerImpl  # `Logger` used for inheritance.
if typing.TYPE_CHECKING:
    from .._xmlutils import Xml as _XmlType


class HtmlDocument(_LoggerImpl):
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
        from .._debugclasses import DebugClass
        from .._xmlutils import Xml

        _LoggerImpl.__init__(self, DebugClass.UI_HTML_DOCUMENT)

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

        #: HTML ``<body/>`` section node.
        self.body = self.xml_doc.createnode("body")  # type: Xml.Node
        with self.addcontent('<body></body>') as self.body:
            #: Main ``<h1/>`` node, which text content will be set with :meth:`settitle()`.
            self._h1 = self.addcontent('<h1>...</h1>').new_child   # type: Xml.Node

            # Menu.
            self._buildmenu()

            #: Main ``<div/>`` node, which page content will be added to by :class:`._requesthandler.RequestHandler` subclasses.
            self.main_div = self.addcontent('<div id="main"></div>').new_child  # type: Xml.Node

        # Set main <div/> as the current node in the end.
        self.current_node = self.main_div

    def _buildmenu(self):  # type: (...) -> None
        """
        Builds the navigation menu.
        """
        from ._configuration import Configuration
        from ._homepage import Homepage
        from ._requirements import Requirements
        from ._scenarios import Scenarios

        with self.addcontent('<div id="menu"></div>'):
            self.addcontent(f'<a class="menu" href="{Homepage.URL}">Home</a>')
            self.addcontent(f'<a class="menu" href="{Configuration.URL}">Configuration</a>')
            self.addcontent(f'<a class="menu" href="{Requirements.URL}">Requirements</a>')
            self.addcontent(f'<a class="menu" href="{Scenarios.URL}">Scenarios</a>')

    def settitle(
            self,
            title,  # type: str
    ):  # type: (...) -> None
        """
        Sets the title of the HTML page.

        :param title: New title. Not HTML-encoded.
        """
        self._head_title.gettextnodes()[0].data = self.encode(title)
        self._h1.gettextnodes()[0].data = self.encode(title)

    def addcontent(
            self,
            content,  # type: str
    ):  # type: (...) -> HtmlDocument.NodeContext
        """
        Adds HTML content to the current node.

        :param content: HTML content.
        :return: Context manager that controls the current node further content will be added to.
        """
        from .._xmlutils import Xml

        # Parse the XML content as a new node.
        _child = self.xml_doc.parsestream(content)  # type: Xml.INode
        if not isinstance(_child, Xml.Node):
            raise ValueError(f"Unexpected XML content {content!r}, parsed as {_child!r} (not a node)")

        # Append it as a child to the current node.
        self.current_node.appendchild(_child)
        self.debug("current_node=%r: addcontent(%r) -> %r", self.current_node, content, _child)

        # Return a context that positions the new child as the current node.
        return HtmlDocument.NodeContext(self, _child)

    @staticmethod
    def encode(
            text,  # type: str
    ):  # type: (...) -> str
        """
        Encodes text for HTML.

        :param text: Text to encode.
        :return: HTML-encoded text.
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
