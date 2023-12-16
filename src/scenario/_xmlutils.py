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
XML DOM utils.
"""

import abc
import gc
import typing
import xml.dom.minidom

if typing.TYPE_CHECKING:
    from ._path import AnyPathType as _AnyPathType


class Xml(abc.ABC):
    """
    Because:

    1. there seems to be no obvious portable choice for parsing and writing XML in Python
       (see https://stackoverflow.com/questions/1912434/how-to-parse-xml-and-count-instances-of-a-particular-node-attribute),
    2. standard libraries such as `xml.dom.minidom` are sometimes untyped or partially untyped,

    let's define a wrapper that gives us the opportunity to abstract the final library used and work around typing issues.
    """

    class Document:
        """
        XML document.
        """

        @staticmethod
        def fromunderlyingref(
                xml_doc,  # type: xml.dom.minidom.Document
        ):  # type: (...) -> Xml.Document
            """
            Retrieves the :class:`Xml.Document` instance from its underlying reference.

            :param xml_doc: Underlying document reference.
            :return: :class:`Xml.Document` instance found.

            .. warning::
                Possibly inefficient implementation
                in as much as all objects in the garbage collector are scanned for the purpose.
            """
            for _doc in filter(lambda obj: isinstance(obj, Xml.Document), gc.get_objects()):  # type: Xml.Document
                if _doc._xml_doc is xml_doc.ownerDocument:
                    return _doc
            raise KeyError(f"No such document {xml_doc!r}")

        def __init__(self):  # type: (...) -> None
            """
            Instanciates an XML document, either for reading or writing.
            """
            #: Underlying library document reference.
            self._xml_doc = xml.dom.minidom.Document()  # type: xml.dom.minidom.Document

        @property
        def root(self):  # type: () -> Xml.Node
            """
            :return: Retrieves the root node of the document.
            """
            assert self._xml_doc.documentElement, "No root node"
            return Xml.Node(xml_element=self._xml_doc.documentElement)

        @root.setter
        def root(self, root):  # type: (Xml.Node) -> None
            """
            Set the root node of the document.

            :param root: Root node for the document.
            """
            self._xml_doc.appendChild(  # type: ignore[no-untyped-call]  ## Untyped function "appendChild"
                root._xml_node,  # noqa  # Access to protected member
            )

        @staticmethod
        def readfile(
                path,  # type: _AnyPathType
        ):  # type: (...) -> Xml.Document
            """
            Reads from an XML file.

            :param path: File to read from.
            :return: XML document read from the file.
            """
            from ._path import Path

            _doc = Xml.Document()  # type: Xml.Document
            _doc._xml_doc = xml.dom.minidom.parseString(Path(path).read_bytes())
            return _doc

        def writefile(
                self,
                path,  # type: _AnyPathType
        ):  # type: (...) -> None
            """
            Writes the document into a file.

            :param path: File to write to.
            """
            from ._path import Path

            Path(path).write_bytes(self.dumpstream())

        def dumpstream(
                self,
                encoding="utf-8",  # type: str
        ):  # type: (...) -> bytes
            """
            Dumps the document as bytes.

            :param encoding: Desired encoding.
            :return: XML document as bytes.
            """
            _xml_stream = self._xml_doc.toprettyxml(encoding=encoding)  # type: bytes
            return _xml_stream

        def createcomment(
                self,
                text,  # type: str
        ):  # type: (...) -> Xml.CommentNode
            """
            Create a comment node.

            :param text: Content
            :return: New comment node.
            """
            return Xml.CommentNode(
                xml_comment=self._xml_doc.createComment(text),
            )

        def createnode(
                self,
                tag_name,  # type: str
        ):  # type: (...) -> Xml.Node
            """
            Create a node with the given tag name.

            :param tag_name: Tag name.
            :return: New node.
            """
            return Xml.Node(
                xml_element=self._xml_doc.createElement(tag_name),
            )

        def createtextnode(
                self,
                text,  # type: str
        ):  # type: (...) -> Xml.TextNode
            """
            Create a text node.

            :param text: Initial text for the new node.
            :return: New text node.
            """
            return Xml.TextNode(
                xml_text=self._xml_doc.createTextNode(text),
            )

        def parsestream(
                self,
                stream,  # type: typing.Union[str, bytes]
        ):  # type: (...) -> Xml.INode
            """
            Parse an XML stream into DOM nodes.

            :param stream: XML stream to parse.
            :return: XML node created from ``string``, owned by this document.
            """
            # Parse the XML stream as a DOM document.
            try:
                _xml_content = xml.dom.minidom.parseString(stream)  # type: typing.Any
            except Exception as _err:
                raise ValueError(f"Error while parsing XML string {stream!r}: {_err}")
            if not isinstance(_xml_content, xml.dom.minidom.Document):
                raise ValueError(f"Unexpected XML string {stream!r}, parsed as {_xml_content!r}")

            # Fix owner document reference for each nodes.
            def _fixdoc(
                    xml_node,  # type: xml.dom.minidom.Node
            ):  # type: (...) -> None
                # Fix owner document
                xml_node.ownerDocument = self._xml_doc

                # Recursive calls.
                if isinstance(xml_node, xml.dom.minidom.Element):
                    for _xml_child in xml_node.childNodes:  # type: xml.dom.minidom.Node
                        _fixdoc(_xml_child)
            _fixdoc(_xml_content.documentElement)

            # Return an `Xml.INode` object of the corresponding type.
            if isinstance(_xml_content.documentElement, xml.dom.minidom.Comment):
                return Xml.CommentNode(_xml_content.documentElement)
            if isinstance(_xml_content.documentElement, xml.dom.minidom.Element):
                return Xml.Node(_xml_content.documentElement)
            if isinstance(_xml_content.documentElement, xml.dom.minidom.Text):
                return Xml.TextNode(_xml_content.documentElement)
            raise ValueError(f"Unexpected root XML content {stream!r}, parsed as {_xml_content.documentElement!r}")

    class INode(abc.ABC):
        """
        Abstract interface for regular nodes and text nodes.
        """
        def __init__(
                self,
                xml_node,  # type: xml.dom.minidom.Node
        ):  # type: (...) -> None
            """
            :param xml_node: Underlying library generic node reference.
            """
            #: Underlying library generic node reference.
            #:
            #: Type should be refined in subclasses.
            self._xml_node = xml_node  # type: xml.dom.minidom.Node

        @property
        def doc(self):  # type: () -> Xml.Document
            """
            :return: Owner document.

            .. warning::
                Possibly inefficient implementation.
                See :meth:`Xml.Document.fromunderlyingref()`.
            """
            return Xml.Document.fromunderlyingref(self._xml_node.ownerDocument)

        @property
        def parent(self):  # type: () -> typing.Optional[Xml.Node]
            """
            :return: Parent node. ``None`` for root or detached nodes.
            """
            if self._xml_node.parentNode:
                return Xml.Node(self._xml_node.parentNode)
            return None

    class CommentNode(INode):
        """
        Comment node.
        """

        def __init__(
                self,
                xml_comment,  # type: xml.dom.minidom.Comment
        ):  # type: (...) -> None
            """
            :param xml_comment: Underlying library comment reference.
            """
            Xml.INode.__init__(self, xml_comment)

            #: Underlying library comment reference.
            self._xml_node = xml_comment  # type: xml.dom.minidom.Comment

        @property
        def data(self):  # type: () -> str
            """
            Text content getter.
            """
            _data = self._xml_node.data  # type: str
            return _data

        @data.setter
        def data(self, data):  # type: (str) -> None
            """
            Text content setter.
            """
            self._xml_node.data = data

    class Node(INode):
        """
        Regular XML node.
        """

        def __init__(
                self,
                xml_element,  # type: xml.dom.minidom.Element
        ):  # type: (...) -> None
            """
            :param xml_element: Underlying library node reference.
            """
            Xml.INode.__init__(self, xml_element)

            #: Underlying library node reference.
            self._xml_node = xml_element  # type: xml.dom.minidom.Element

        @property
        def tag_name(self):  # type: () -> str
            """
            :return: Tag name of the node.
            """
            return self._xml_node.tagName

        def hasattr(
                self,
                name,  # type: str
        ):  # type: (...) -> bool
            """
            Tells whether the node has an attribute of the given name.

            :param name: Attribute name.
            :return: ``True`` when the node has an attribute of the given name, ``False`` otherwise.
            """
            # "If no such attribute exists, an empty string is returned, as if the attribute had no value."
            _attr_value = self._xml_node.getAttribute(name)  # type: str
            if _attr_value:
                return True
            else:
                return False

        def getattr(
                self,
                name,  # type: str
        ):  # type: (...) -> str
            """
            Retrives the attribute value of the given name.

            :param name: Attribute name.
            :return: Attribute value, or possibly an empty string if the attribute does not exist.
            """
            _attr_value = self._xml_node.getAttribute(name)  # type: str
            return _attr_value

        def setattr(
                self,
                name,  # type: str
                value,  # type: str
        ):  # type: (...) -> Xml.Node
            """
            Set an attribute.

            :param name: Attribute name.
            :param value: Attribute value.
            :return: ``self``
            """
            self._xml_node.setAttribute(name, value)
            return self

        def getchildren(
                self,
                tag_name,  # type: str
        ):  # type: (...) -> typing.Sequence[Xml.Node]
            """
            Retrieves direct children with the given tag name.

            :param tag_name: Children tag name.
            :return: List of children nodes.
            """
            _children = []  # type: typing.List[Xml.Node]
            for _xml_child in self._xml_node.childNodes:  # type: xml.dom.minidom.Node
                if isinstance(_xml_child, xml.dom.minidom.Element) and (_xml_child.tagName == tag_name):
                    _children.append(Xml.Node(_xml_child))
            return _children

        def gettextnodes(self):  # type: (...) -> typing.Sequence[Xml.TextNode]
            """
            Retrieves direct children text nodes.

            :return: List of children text nodes.
            """
            _text_nodes = []  # type: typing.List[Xml.TextNode]
            for _xml_child in self._xml_node.childNodes:  # type: xml.dom.minidom.Node
                if isinstance(_xml_child, xml.dom.minidom.Text):
                    _text_nodes.append(Xml.TextNode(_xml_child))
            return _text_nodes

        def appendchild(
                self,
                child,  # type: VarNodeType
        ):  # type: (...) -> VarNodeType
            """
            Adds a child to the node.

            :param child: New node or text node to set as a child.
            :return: The child just added.
            """
            if not isinstance(child, (Xml.CommentNode, Xml.Node, Xml.TextNode)):
                raise TypeError(f"Unknown child node {child!r}")
            self._xml_node.appendChild(  # type: ignore[no-untyped-call]  ## Untyped function "appendChild"
                child._xml_node,  # noqa  # Access to protected member
            )
            return child  # type: ignore[return-value]  ## "Union[Node, TextNode]", expected "VarNodeType"

    class TextNode(INode):
        """
        Text node.
        """

        def __init__(
                self,
                xml_text,  # type: xml.dom.minidom.Text
        ):
            """
            :param xml_text: Underlying library text node reference.
            """
            Xml.INode.__init__(self, xml_text)

            #: Underlying library text node reference.
            self._xml_node = xml_text  # type: xml.dom.minidom.Text

        @property
        def data(self):  # type: () -> str
            """
            Text content getter.
            """
            _data = self._xml_node.data  # type: str
            return _data

        @data.setter
        def data(self, data):  # type: (str) -> None
            """
            Text content setter.
            """
            self._xml_node.data = data


if typing.TYPE_CHECKING:
    #: Variable XML node type.
    VarNodeType = typing.TypeVar("VarNodeType", bound=Xml.INode)
