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

    class State(scenario.enum.StrEnum):
        """
        State for collapsible rows.
        """
        #: Expanded state.
        EXPANDED = "expanded"
        #: Collapsed state.
        COLLAPSED = "collapsed"

    class _MainRow:
        """
        Main row information.
        """
        def __init__(
                self,
                id,  # type: str  # noqa  ## Shadows built-in name 'id'
                tr_ctx,  # type: _HtmlDocumentType.NodeContext
        ):  # type: (...) -> None
            """
            :param id: Main row identifier.
            :param tr_ctx: `tr.main-row` node context.
            """
            #: Main row identifier.
            self.id = id  # type: str
            #: Main row `<tr></tr>` node.
            self.tr = tr_ctx  # type: _HtmlDocumentType.NodeContext
            #: `.toggle-row` button `<a></a>` node.
            self.toggle_button_a = None  # type: typing.Optional[_HtmlDocumentType.NodeContext]
            #: `.toggle-row` button `<span></span>` node.
            self.toggle_button_span = None  # type: typing.Optional[_HtmlDocumentType.NodeContext]
            #: `<tr></tr>` nodes of related collapsible rows.
            self.collapsible_trs = []  # type: typing.List[_HtmlDocumentType.NodeContext]

    def __init__(
            self,
            html,  # type: _HtmlDocumentType
            *,
            table_id,  # type: str
            default_state=State.EXPANDED,  # type: CollapsibleTableGenerator.State
    ):  # type: (...) -> None
        """
        Saves the ``table_id`` for the table to generate in ``html``.

        :param html: HTML output page to feed.
        :param table_id: Table identifier used in HTML classes.
        :param default_state: Default state for collapsible rows. Default is `expanded`.
        """
        #: HTML output page to feed.
        self.html = html  # type: _HtmlDocumentType
        #: Table identifier to set in HTML classes.
        self.table_id = table_id.replace(".", "-")  # type: str
        #: Default state for collapsible rows.
        self.default_state = default_state

        #: Main row data.
        self._main_rows = []  # type: typing.List[CollapsibleTableGenerator._MainRow]

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
            :class:`._htmldoc.HtmlDocument.NodeContext` override for post-processing:

            - adjust `.expanded`/`.collapsed` state classes and `.toggle-row` button texts depending on related `.collapsible-row` counts and default state.
            - automatically include '_tables.js' after the `<table></table>` node.
            """

            def __init__(
                    self,
                    table_generator,  # type: CollapsibleTableGenerator
                    table_ctx,  # type: _HtmlDocumentType.NodeContext
            ):  # type: (...) -> None
                """
                :param table_generator: Current table generator with HTML output page to feed.
                :param table_ctx: Table node context.
                """
                HtmlDocument.NodeContext.__init__(
                    self,
                    html_doc=table_generator.html,
                    new_child=table_ctx.new_child,
                )

                #: Table generator being processed.
                self.table_generator = table_generator  # type: CollapsibleTableGenerator

            def __exit__(
                    self,
                    exc_type,  # type: typing.Any
                    exc_val,  # type: typing.Any
                    exc_tb,  # type: typing.Any
            ):  # type: (...) -> None
                super().__exit__(exc_type, exc_val, exc_tb)

                if not exc_type:
                    # Depending on whether on main rows have related `.collapsible-row`s attached to them or not,
                    # set `.expanded`/`.collapsed` state classes and `.toggle-row` button texts.
                    for _main_row in self.table_generator._main_rows:  # type: CollapsibleTableGenerator._MainRow  # noqa  ## Access to protected member
                        if not _main_row.collapsible_trs:
                            # No `.collapsible-row`s attached.
                            if _main_row.toggle_button_span is not None:
                                with _main_row.toggle_button_span:
                                    self.table_generator.html.addtext("o")
                        else:
                            # `.collapsible-row`s attached.
                            with _main_row.tr:
                                self.table_generator.html.addclass(self.table_generator.default_state)
                            if _main_row.toggle_button_a is not None:
                                with _main_row.toggle_button_a:
                                    self.table_generator.html.addclass(self.table_generator.default_state)
                            if _main_row.toggle_button_span is not None:
                                with _main_row.toggle_button_span:
                                    if self.table_generator.default_state == CollapsibleTableGenerator.State.EXPANDED:
                                        self.table_generator.html.addtext("-")
                                    else:
                                        self.table_generator.html.addtext("+")
                            for _collapsible_tr in _main_row.collapsible_trs:  # type: _HtmlDocumentType.NodeContext
                                with _collapsible_tr:
                                    self.table_generator.html.addclass(self.table_generator.default_state)
                                    if self.table_generator.default_state == CollapsibleTableGenerator.State.EXPANDED:
                                        self.table_generator.html.addstyle("visibility: visible")
                                    else:
                                        self.table_generator.html.addstyle("visibility: collapse")

                    # Include '_table.js' after the `<table></table>` node has been closed.
                    self.html.jscontent2html(scenario.Path(__file__).with_suffix(".js").name)

        return _TableNodeContext(
            table_generator=self,
            table_ctx=self.html.addnode(
                "table",
                classes=[
                    *classes,
                    "collapsible",
                    self.html.mknamedobjectidclass("table", self.table_id),
                ],
            ),
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
        self._main_rows.append(CollapsibleTableGenerator._MainRow(
            id=main_row_id,
            tr_ctx=self.html.addnode(
                "tr",
                classes=[
                    *classes,
                    "main-row",
                    self.html.mknamedobjectidclass("table", self.table_id),
                    self.html.mknamedobjectidclass("main-row", main_row_id),
                ],
            ),
        ))
        return self._main_rows[-1].tr

    def addcollapsiblerow(
            self,
            *,
            classes=(),  # type: typing.Sequence[str]
    ):  # type: (...) -> _HtmlDocumentType.NodeContext
        """
        Adds a ``.collapsible-row`` row in the table.

        :param classes: Optional additional HTML classes.
        :return: HTML node context focused on the ``<tr></tr>`` created.
        """
        self._main_rows[-1].collapsible_trs.append(
            self.html.addnode(
                "tr",
                classes=[
                    *classes,
                    "collapsible-row",
                    self.html.mknamedobjectidclass("table", self.table_id),
                    self.html.mknamedobjectidclass("main-row", self._main_rows[-1].id),
                ],
            )
        )
        return self._main_rows[-1].collapsible_trs[-1]

    def addtogglebutton(self):  # type: (...) -> None
        """
        Adds a ``.toggle-row`` button (normally in a ``.main-row`` row).
        """
        self._main_rows[-1].toggle_button_a = self.html.addnode(
            "a",
            classes=[
                "button", "toggle-row",
                self.html.mknamedobjectidclass("table", self.table_id),
                self.html.mknamedobjectidclass("main-row", self._main_rows[-1].id),
            ],
        )
        with self._main_rows[-1].toggle_button_a:
            # Create a span node without text.
            # The text will be set when the table is terminated.
            self._main_rows[-1].toggle_button_span = self.html.addnode("span")
