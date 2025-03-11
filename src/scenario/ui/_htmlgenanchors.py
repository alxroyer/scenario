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
HTML anchor generator.
"""

import typing

import scenario

if typing.TYPE_CHECKING:
    from ._htmldoc import HtmlDocument as _HtmlDocumentType


class AnchorGenerator:
    """
    HTML generator for anchors.
    """

    def __init__(
            self,
            html,  # type: _HtmlDocumentType
            *,
            name,  # type: str
    ):  # type: (...) -> None
        """
        Instantiates a :class:`AnchorGenerator` with configurations.

        :param html: HTML output page to feed.
        :param name: Anchor name.
        """
        #: HTML output page to feed.
        self.html = html  # type: _HtmlDocumentType
        #: Anchor name.
        self.name = name  # type: str

        # Have the related .js content be embedded at the end of the HTML page.
        self.html.addfinaljs(scenario.Path(__file__).with_suffix(".js"))

    def __repr__(self):  # type: () -> str
        """
        Canonical string representation.

        For debugging purpose.
        """
        return "AnchorGenerator(%s)" % (", ".join([
            f"name={self.name!r}",
        ]))

    def addanchor(
            self,
            *,
            classes=(),  # type: typing.Sequence[str]
            link_title="",  # type: str
            link_text="",  # type: str
    ):  # type: (...) -> _HtmlDocumentType.NodeContext
        """
        Adds an anchor.

        :param classes: Extra classes to set for ``@class`` attribute.
        :param link_title: ``@title`` attribute value, used for popup info on anchor link hover. Anchor name by default.
        :param link_text: Text content for the ancho link. "(<>)" by default.
        :return: HTML node context focused on the highlightable ``<div></div>`` node created.
        """
        from ._htmlgenlinks import LinkGenerator

        if not link_text:
            link_text = "(<>)"

        # Container div.
        with self.html.addnode(
            "div",
            classes=[
                *classes,
                "anchor", "container",
                self.html.mkcsscompatibleclass(f"anchor={self.name}"),
            ],
        ):
            # Anchor link.
            with LinkGenerator(self.html).addlink(
                classes=[
                    *classes,
                    "anchor-link",
                    self.html.mkcsscompatibleclass(f"anchor={self.name}"),
                ],
                # Memo: Use `mkcsscompatibleclass()` to escape anchor names.
                href=f"#{self.html.mkcsscompatibleclass(self.name)}",
                title=link_title or self.name,
            ):
                self.html.addnode("span", text=link_text)

            # Focusable div.
            _anchor_div_ctx = self.html.addnode(
                "div",
                classes=[
                    *classes,
                    "anchor", "focusable",
                    self.html.mkcsscompatibleclass(f"anchor={self.name}"),
                ],
            )  # type: _HtmlDocumentType.NodeContext
            with _anchor_div_ctx:
                # Anchor.
                self.html.addnode(
                    "a",
                    classes=[
                        *classes,
                        "anchor",
                        self.html.mkcsscompatibleclass(f"anchor={self.name}"),
                    ],
                    # Memo: Use `mkcsscompatibleclass()` to escape anchor names.
                    name=self.html.mkcsscompatibleclass(self.name),
                )

        return _anchor_div_ctx
