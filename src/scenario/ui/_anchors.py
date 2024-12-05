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
Anchors management.
"""

import abc
import typing

if typing.TYPE_CHECKING:
    from ._htmldoc import HtmlDocument as _HtmlDocumentType


class Anchor(abc.ABC):
    """
    Anchors management.
    """

    @staticmethod
    def add(
            html,  # type: _HtmlDocumentType
            *,
            classes=(),  # type: typing.Sequence[str]
            html_escape_classes=True,  # type: bool
            name,  # type: str
            html_escape_name=True,  # type: bool
            link_title="",  # type: str
            html_escape_link_title=True,  # type: bool
            link_text="",  # type: str
            html_escape_link_text=True,  # type: bool
    ):  # type: (...) -> _HtmlDocumentType.NodeContext
        """
        Adds an anchor.

        :param html: HTML output page to feed.
        :param classes: Extra classes to set for ``@class`` attribute.
        :param html_escape_classes: ``True`` (default) to HTML escape class names.
        :param name: Anchor name.
        :param html_escape_name: ``True`` (default) to HTML escape the anchor name.
        :param link_title: ``@title`` attribute value, used for popup info on anchor link hover. Anchor name by default.
        :param html_escape_link_title: ``True`` (default) to HTML escape the anchor link title.
        :param link_text: Text content for the ancho link. "(<>)" by default.
        :param html_escape_link_text: ``True`` (default) to HTML escape the anchor link text.
        :return: Context manager focused on the highlightable div created.
        """
        if not link_text:
            link_text = "(<>)"
            html_escape_link_text = True

        if html_escape_classes:
            classes = [html.escape(_class) for _class in classes]
        if html_escape_name:
            name = html.escape(name)
        if html_escape_link_title:
            link_title = html.escape(link_title)
        if html_escape_link_text:
            link_text = html.escape(link_text)

        # Container div.
        with html.addcontent(f'<div class="{" ".join(["anchor", "container", f"name={name}", *classes])}"></div>'):
            # Anchor link.
            with html.addlink(
                classes=[*classes, "anchor-link", name], html_escape_classes=False,
                href=f"#{name}", html_escape_href=False,
                title=link_title or name, html_escape_title=False,
            ):
                html.addcontent(f'<span>{link_text}</span>')

            # Focusable div.
            _anchor_div_ctx = html.addcontent(f'<div class="{" ".join(["anchor", "focusable", f"name={name}", *classes])}"></div>') \
                # type: _HtmlDocumentType.NodeContext
            with _anchor_div_ctx:
                # Anchor.
                html.addcontent(f'<a class="{" ".join(["anchor", f"name={name}", *classes])}" name="{name}"></a>')

        return _anchor_div_ctx
