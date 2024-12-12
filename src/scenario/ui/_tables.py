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
Expandable/collapsible tables.
"""

import typing

import scenario

if typing.TYPE_CHECKING:
    from ._htmldoc import HtmlDocument as _HtmlDocumentType


class CollapsibleTableGenerator:
    """
    HTML generator for tables with collapsible rows.
    """

    def __init__(
            self,
            html,  # type: _HtmlDocumentType
            *,
            table_id,  # type: str
    ):  # type: (...) -> None
        """
        Saves the ``table_id`` for the table to generate in ``html``.

        :param html: HTML output page to feed.
        :param table_id: Table identifier used in HTML classes.
        """
        #: HTML output page to feed.
        self.html = html  # type: _HtmlDocumentType
        #: Table identifier to set in HTML classes.
        self.table_id = table_id.replace(".", "-")  # type: str

    def addexpandallbutton(self):  # type: (...) -> None
        """
        Adds a ``.expand-all`` button for the table being generated.
        """
        self.html.addnode(
            "a",
            classes=[
                "button", "expand-all",
                self.html.mknamedobjectidclass("table", self.table_id),
            ],
            href="#",
            text="Expand all",
        )

    def addcollapseallbutton(
            self,
    ):  # type: (...) -> None
        """
        Adds a ``.collapse-all`` button for the table being generated.
        """
        self.html.addnode(
            "a",
            classes=[
                "button", "collapse-all",
                self.html.mknamedobjectidclass("table", self.table_id),
            ],
            href="#",
            text="Collapse all",
        )

    def addtable(
            self,
            *,
            classes=(),  # type: typing.Sequence[str]
    ):  # type: (...) -> _HtmlDocumentType.NodeContext
        """
        Starts generating the table.

        :param classes: Optional additional HTML classes.
        :return: HTML node context focused on the ``<table></table>`` created.
        """
        from ._htmldoc import HtmlDocument

        class _TableNodeContext(HtmlDocument.NodeContext):
            """
            :class:`._htmldoc.HtmlDocument.NodeContext` override to automatically include '_tables.js' after the `<table></table>` node.
            """
            def __exit__(
                    self,
                    exc_type,  # type: typing.Any
                    exc_val,  # type: typing.Any
                    exc_tb,  # type: typing.Any
            ):  # type: (...) -> None
                super().__exit__(exc_type, exc_val, exc_tb)

                # Include '_table.js' after the `<table></table>` node has been closed.
                if not exc_type:
                    self.html.jscontent2html(scenario.Path(__file__).with_suffix(".js").name)

        return _TableNodeContext(
            html_doc=self.html,
            new_child=self.html.addnode(
                "table",
                classes=[
                    *classes,
                    "collapsible",
                    self.html.mknamedobjectidclass("table", self.table_id),
                ],
            ).new_child,
        )

    def addmainrow(
            self,
            *,
            main_row_id,  # type: str
            classes=(),  # type: typing.Sequence[str]
    ):  # type: (...) -> _HtmlDocumentType.NodeContext
        """
        Adds a ``.main-row`` row in the table.

        :param main_row_id: Main row identifier used in HTML classes.
        :param classes: Optional additional HTML classes.
        :return: HTML node context focused on the ``<tr></tr>`` created.
        """
        return self.html.addnode(
            "tr",
            classes=[
                *classes,
                "main-row",
                self.html.mknamedobjectidclass("table", self.table_id),
                self.html.mknamedobjectidclass("main-row", main_row_id),
            ],
        )

    def addcollapsiblerow(
            self,
            *,
            main_row_id,  # type: str
            classes=(),  # type: typing.Sequence[str]
    ):  # type: (...) -> _HtmlDocumentType.NodeContext
        """
        Adds a ``.collapsible-row`` row in the table.

        :param main_row_id: Main row identifier used in HTML classes.
        :param classes: Optional additional HTML classes.
        :return: HTML node context focused on the ``<tr></tr>`` created.
        """
        return self.html.addnode(
            "tr",
            classes=[
                *classes,
                "collapsible-row",
                self.html.mknamedobjectidclass("table", self.table_id),
                self.html.mknamedobjectidclass("main-row", main_row_id),
            ],
        )

    def addtogglebutton(
            self,
            *,
            main_row_id,  # type: str
    ):  # type: (...) -> None
        """
        Adds a ``.toggle-row`` button (normally in a ``.main-row`` row).

        :param main_row_id: Main row identifier used in HTML classes.
        """
        with self.html.addnode(
            "a",
            classes=[
                "button", "toggle-row",
                self.html.mknamedobjectidclass("table", self.table_id),
                self.html.mknamedobjectidclass("main-row", main_row_id),
            ],
        ):
            self.html.addnode("span", text="-")
