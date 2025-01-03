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

if True:
    from ._collapsiblestate import CollapsibleState as _CollapsibleStateImpl  # @default-parameter-value
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
            default_state=_CollapsibleStateImpl.EXPANDED,  # type: _CollapsibleStateImpl
    ):  # type: (...) -> None
        """
        Instantiates a :class:`CollapsibleTableGenerator` with configurations.

        :param html: HTML output page to feed.
        :param table_id: Table identifier used in HTML classes.
        :param default_state: Default state for collapsible rows. Default is `expanded`.
        """
        #: HTML output page to feed.
        self.html = html  # type: _HtmlDocumentType
        #: Table identifier to set in HTML classes.
        self.table_id = table_id  # type: str
        #: Default state for collapsible rows.
        self.default_state = default_state

        #: Main row data, fed in :meth:`addmainrow()`.
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

        # Have '_collapsibletable.js' be embedded at the end of the HTML page.
        self.html.addfinaljs(scenario.Path(__file__).with_suffix(".js"))

        # Create the table node.
        _table_ctx = self.html.addnode(
            "table",
            classes=[
                *classes,
                "collapsible",
                self.html.mknamedobjectidclass("table", self.table_id),
            ],
        )  # type: _HtmlDocumentType.NodeContext

        # Return a `HtmlDocument.NodeContext` wrapper
        # to ensure `finalize()` be called for each main row at the end of the table definition.
        class _TableNodeContext(HtmlDocument.NodeContext):
            """
            :class:`._htmldoc.HtmlDocument.NodeContext` override
            in order to call :meth:`CollapsibleTableGenerator._MainRow.finalize()` for each main row
            at the end of the table definition.
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
                    # Finalize table rows.
                    for _main_row in self.table_generator._main_rows:  # type: CollapsibleTableGenerator._MainRow  # noqa  ## Access to protected member
                        _main_row.finalize()

        return _TableNodeContext(
            table_generator=self,
            table_ctx=_table_ctx,
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
            table_generator=self,
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
        return self._main_rows[-1].main_tr_ctx

    def addtogglebutton(self):  # type: (...) -> None
        """
        Adds a ``.toggle-row`` button (normally in a ``.main-row`` row).
        """
        self._main_rows[-1].toggle_button_a_ctx = self.html.addnode(
            "a",
            classes=[
                "button", "toggle-row",
                self.html.mknamedobjectidclass("table", self.table_id),
                self.html.mknamedobjectidclass("main-row", self._main_rows[-1].id),
            ],
        )
        with self._main_rows[-1].toggle_button_a_ctx:
            # Create a span node without text.
            # The text will be set when the table is terminated.
            self._main_rows[-1].toggle_button_span_ctx = self.html.addnode("span")

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
        self._main_rows[-1].collapsible_tr_ctxs.append(
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
        return self._main_rows[-1].collapsible_tr_ctxs[-1]

    class _MainRow:
        """
        Main row information.
        """

        def __init__(
                self,
                table_generator,  # type: CollapsibleTableGenerator
                id,  # type: str  # noqa  ## Shadows built-in name 'id'
                tr_ctx,  # type: _HtmlDocumentType.NodeContext
        ):  # type: (...) -> None
            """
            :param table_generator: Owner table generator.
            :param id: Main row identifier.
            :param tr_ctx: `tr.main-row` node context.
            """
            #: Owner table generator.
            self.table_generator = table_generator
            #: Main row identifier.
            self.id = id  # type: str
            #: Main row ``<tr></tr>`` node context.
            self.main_tr_ctx = tr_ctx  # type: _HtmlDocumentType.NodeContext
            #: ``.toggle-row`` button ``<a></a>`` node context, saved in :meth:`CollapsibleTableGenerator.addtogglebutton()`.
            self.toggle_button_a_ctx = None  # type: typing.Optional[_HtmlDocumentType.NodeContext]
            #: ``.toggle-row`` button ``<span></span>`` node context, saved in :meth:`CollapsibleTableGenerator.addtogglebutton()`.
            self.toggle_button_span_ctx = None  # type: typing.Optional[_HtmlDocumentType.NodeContext]
            #: ``<tr></tr>`` node contexts of related collapsible rows, fed in :meth:`CollapsibleTableGenerator.addcollapsiblerow()`.
            self.collapsible_tr_ctxs = []  # type: typing.List[_HtmlDocumentType.NodeContext]

        @property
        def html(self):  # type: () -> _HtmlDocumentType
            """
            Shortcut to HTML output page to feed.
            """
            return self.table_generator.html

        def finalize(self):  # type: (...) -> None
            """
            Finalizes the main collapsible row.

            Depending on whether on the main row has related collapsible rows attached to it or not:

            - sets `.expanded`/`.collapsed` state classes,
            - sets `.toggle-row` button text,
            - sets related collapsible rows visibility.
            """
            if not self.collapsible_tr_ctxs:
                # No `.collapsible-row`s attached.

                # Toggle button text.
                if self.toggle_button_span_ctx is not None:
                    with self.toggle_button_span_ctx:
                        self.html.addtext("o")

            else:
                # `.collapsible-row`s attached.

                # Main row `.expanded`/`.collapsed` class.
                with self.main_tr_ctx:
                    self.html.addclass(self.table_generator.default_state)

                # Toggle button `.expanded`/`.collapsed` class.
                if self.toggle_button_a_ctx is not None:
                    with self.toggle_button_a_ctx:
                        self.html.addclass(self.table_generator.default_state)
                # Toggle button text.
                if self.toggle_button_span_ctx is not None:
                    with self.toggle_button_span_ctx:
                        if self.table_generator.default_state == _CollapsibleStateImpl.EXPANDED:
                            self.html.addtext("-")
                        else:
                            self.html.addtext("+")

                # Collapsible rows.
                for _collapsible_tr_ctx in self.collapsible_tr_ctxs:  # type: _HtmlDocumentType.NodeContext
                    with _collapsible_tr_ctx:
                        # `.expanded`/`.collapsed` class.
                        self.html.addclass(self.table_generator.default_state)

                        # Visbility.
                        if self.table_generator.default_state == _CollapsibleStateImpl.EXPANDED:
                            self.html.addstyle("visibility: visible")
                        else:
                            self.html.addstyle("visibility: collapse")
