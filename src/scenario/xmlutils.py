# -*- coding: utf-8 -*-

# Copyright 2020-2022 Alexis Royer <https://github.com/Alexis-ROYER/scenario>
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
import typing
import xml.dom.minidom

if typing.TYPE_CHECKING:
    # `AnyPathType` used in method signatures.
    # Type declared for type checking only.
    from .path import AnyPathType


class Xml:
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

        def __init__(self):  # type: (...) -> None
            """
            Instanciates an XML document, either for reading or writing.
            """
            #: Underlying library document reference.
            self._xml_doc = xml.dom.minidom.Document()  # type: xml.dom.minidom.Document

        @property
        def root(self):  # type: (...) -> Xml.Node
            """
            :return: Retrieves the root node of the document.
            """
            assert self._xml_doc.documentElement, "No root node"
            return Xml.Node(xml_element=self._xml_doc.documentElement)

        @root.setter
        def root(
                self,
                root,  # type: Xml.Node
        ):  # type: (...) -> None
            """
            Set the root node of the document.

            :param root: Root node for the document.
            """
            self._xml_doc.appendChild(  # type: ignore  ## Call to untyped function "appendChild" in typed context
                getattr(root, "_xml_element"),
            )

        @staticmethod
        def read(
                path,  # type: AnyPathType
        ):  # type: (...) -> Xml.Document
            """
            Reads from an XML file.

            :param path: File to read from.
            :return: XML document read from the file.
            """
            from .path import Path

            _doc = Xml.Document()  # type: Xml.Document
            _doc._xml_doc = xml.dom.minidom.parseString(  # type?: ignore  ## Call to untyped function "parseString" in typed context
                Path(path).read_bytes(),
            )
            return _doc

        def write(
                self,
                path,  # type: AnyPathType
        ):  # type: (...) -> None
            """
            Writes the document into a file.

            :param path: File to write to.
            """
            from .path import Path

            _xml_stream = self._xml_doc.toprettyxml(  # type?: ignore  ## Call to untyped function "toprettyxml" in typed context
                encoding="utf-8",
            )  # type: bytes
            Path(path).write_bytes(_xml_stream)

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
                xml_element=self._xml_doc.createElement(  # type?: ignore  ## Call to untyped function "createElement" in typed context
                    tag_name,
                ),
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
                xml_text=self._xml_doc.createTextNode(  # type: ignore  ## Call to untyped function "createTextNode" in typed context
                    text,
                ),
            )

    class INode(abc.ABC):
        """
        Abstract interface for regular nodes and text nodes.
        """
        pass

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
            #: Underlying library node reference.
            self._xml_element = xml_element  # type: xml.dom.minidom.Element

        @property
        def tag_name(self):  # type: (...) -> str
            """
            :return: Tag name of the node.
            """
            return self._xml_element.tagName

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
            _attr_value = self._xml_element.getAttribute(  # type: ignore  ## Call to untyped function "getAttribute" in typed context
                name,
            )  # type: str
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
            _attr_value = self._xml_element.getAttribute(  # type: ignore  ## Call to untyped function "getAttribute" in typed context
                name,
            )  # type: str
            return _attr_value

        def setattr(
                self,
                name,  # type: str
                value,  # type: str
        ):  # type: (...) -> None
            """
            Set an attribute.

            :param name: Attribute name.
            :param value: Attribute value.
            """
            self._xml_element.setAttribute(  # type?: ignore  ## Call to untyped function "setAttribute" in typed context
                name,
                value,
            )

        def getchildren(
                self,
                tag_name,  # type: str
        ):  # type: (...) -> typing.List[Xml.Node]
            """
            Retrieves direct children with the given tag name.

            :param tag_name: Children tag name.
            :return: List of children nodes.
            """
            _children = []  # type: typing.List[Xml.Node]
            for _xml_child in self._xml_element.getElementsByTagName(  # type: ignore  ## Call to untyped function "getElementsByTagName" in typed context
                    tag_name,
            ):  # xml.dom.minidom.Element
                _children.append(Xml.Node(_xml_child))
            return _children

        def gettextnodes(self):  # type: (...) -> typing.List[Xml.TextNode]
            """
            Retrieves direct children text nodes.

            :return: List of children text nodes.
            """
            _text_nodes = []  # type: typing.List[Xml.TextNode]
            for _xml_child in self._xml_element.childNodes:  # type: xml.dom.minidom.Node
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
            assert isinstance(child, (Xml.Node, Xml.TextNode))
            self._xml_element.appendChild(  # type: ignore  ## Call to untyped function "appendChild" in typed context
                getattr(child, "_xml_element") if isinstance(child, Xml.Node)
                else getattr(child, "_xml_text"),
            )
            return child  # type: ignore  ## Incompatible return value type (got "Union[Node, TextNode]", expected "VarNodeType")

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
            #: Underlying library text node reference.
            self._xml_text = xml_text  # type: xml.dom.minidom.Text

        @property
        def data(self):  # type: (...) -> str
            """
            Text content.
            """
            _data = self._xml_text.data  # type: str
            return _data

        def append(
                self,
                data,  # type: str
        ):  # type: (...) -> None
            """
            Adds some text to the text node.

            :param data: Additional text.
            """
            self._xml_text.data += data


if typing.TYPE_CHECKING:
    #: Variable step definition type.
    VarNodeType = typing.TypeVar("VarNodeType", bound=Xml.INode)
