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
            name,  # type: str
            link_title="",  # type: str
            link_text="",  # type: str
    ):  # type: (...) -> _HtmlDocumentType.NodeContext
        """
        Adds an anchor.

        :param html: HTML output page to feed.
        :param classes: Extra classes to set for ``@class`` attribute.
        :param name: Anchor name.
        :param link_title: ``@title`` attribute value, used for popup info on anchor link hover. Anchor name by default.
        :param link_text: Text content for the ancho link. "(<>)" by default.
        :return: HTML node context focused on the highlightable ``<div></div>`` created.
        """
        if not link_text:
            link_text = "(<>)"

        # Container div.
        with html.addnode(
            "div",
            classes=[
                *classes,
                "anchor", "container",
                html.mkcsscompatibleclass(f"anchor={name}"),
            ],
        ):
            # Anchor link.
            with html.addlink(
                classes=[
                    *classes,
                    "anchor-link",
                    html.mkcsscompatibleclass(f"anchor={name}"),
                ],
                href=f"#{name}",
                title=link_title or name,
            ):
                html.addnode("span", text=link_text)

            # Focusable div.
            _anchor_div_ctx = html.addnode(
                "div",
                classes=[
                    *classes,
                    "anchor", "focusable",
                    html.mkcsscompatibleclass(f"anchor={name}"),
                ],
            )  # type: _HtmlDocumentType.NodeContext
            with _anchor_div_ctx:
                # Anchor.
                html.addnode(
                    "a",
                    classes=[
                        *classes,
                        "anchor",
                        html.mkcsscompatibleclass(f"anchor={name}"),
                    ],
                    name=name,
                )

        return _anchor_div_ctx
