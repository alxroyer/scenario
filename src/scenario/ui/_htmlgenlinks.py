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
HTML link generator.
"""

import typing

if typing.TYPE_CHECKING:
    from ._htmldoc import HtmlDocument as _HtmlDocumentType


class LinkGenerator:
    """
    HTML generator for links.
    """

    def __init__(
            self,
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        """
        Instantiates a :class:`LinkGenerator` with configurations.

        :param html: HTML output page to feed.
        """
        #: HTML output page to feed.
        self.html = html  # type: _HtmlDocumentType

    def __repr__(self):  # type: () -> str
        """
        Canonical string representation.

        For debugging purpose.
        """
        return "LinkGenerator(%s)" % (", ".join([
        ]))

    def addlink(
            self,
            *,
            classes=(),  # type: typing.Sequence[str]
            href,  # type: str
            title=None,  # type: str
            text=None,  # type: str
    ):  # type: (...) -> _HtmlDocumentType.NodeContext
        """
        Adds a ``<a ...>...</a>`` link in the document,
        with ``@class``, ``@href``, ``@title`` attributes and text content.

        :param classes: Classes to set for ``@class`` attribute. No ``@class`` attribute if no class provided.
        :param href: URL to set for ``@href`` attribute.
        :param title: ``@title`` attribute value, used for popup info on link hover. None by default for no ``@title`` attribute.
        :param text: Text content for the link. Empty by default.
        :return: HTML node context focused on the ``<a></a>`` node created.
        """
        return self.html.addnode(
            "a",
            classes=classes,
            href=href,
            title=title,
            text=text,
        )
