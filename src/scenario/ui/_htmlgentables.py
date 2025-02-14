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
HTML table generator.
"""

import typing

import scenario

if True:
    from ._htmlgentypes import CollapsibleState as _CollapsibleStateImpl  # @default-parameter-value
if typing.TYPE_CHECKING:
    from ._htmldoc import HtmlDocument as _HtmlDocumentType
    from ._htmlgentypes import CollapsibleState as _CollapsibleStateType


class TableGenerator:
    """
    HTML generator for tables with collapsible rows.
    """

    def __init__(
            self,
            html,  # type: _HtmlDocumentType
            *,
            table_cid,  # type: str
    ):  # type: (...) -> None
        """
        Instantiates a :class:`TableGenerator` with configurations.

        :param html: HTML output page to feed.
        :param table_cid: Table CID.
        """
        #: HTML output page to feed.
        self.html = html  # type: _HtmlDocumentType
        #: Table CID.
        self.table_cid = table_cid  # type: str

        #: ``.tr1`` main rows.
        self._tr1s = []  # type: typing.List[TableGenerator._Tr1]

        # Have the related .js content be embedded at the end of the HTML page.
        self.html.addfinaljs(scenario.Path(__file__).with_suffix(".js"))

    def __repr__(self):  # type: () -> str
        """
        Canonical string representation.

        For debugging purpose.
        """
        return "TableGenerator(%s)" % (", ".join([
            f"table_cid={self.table_cid!r}",
        ]))

    @property
    def _tr1(self):  # type: () -> TableGenerator._Tr1
        """
        Current ``.tr1`` main row.
        """
        return self._tr1s[-1]

    def _tableidclasses(self):  # type: (...) -> typing.Sequence[str]
        """
        Computes identifier classes for the table.

        :return: Identifier classes for the table.
        """
        _classes = []  # type: typing.List[str]
        if self.table_cid:
            _classes.append(self.html.mkcsscompatibleclass(f"table={self.table_cid}"))
        return _classes

    def _tr1idclasses(self):  # type: (...) -> typing.Sequence[str]
        """
        Computes identifier classes for the current ``.tr1`` main row.

        Includes the identifier classes for the table.

        :return: Identifier classes for the current ``.tr1`` main row.
        """
        _classes = [*self._tableidclasses()]  # type: typing.List[str]
        if self._tr1.tr1_cid:
            _classes.append(self.html.mkcsscompatibleclass(f"tr1={self._tr1.tr1_cid}"))
        return _classes

    def addexpandallbutton(self):  # type: (...) -> None
        """
        Adds a ``.expand-all`` button for the table being generated.
        """
        from ._htmlgenbuttons import ButtonGenerator

        assert self.table_cid, "Please provide a table CID for a table with collapsible rows"

        ButtonGenerator(self.html).addbutton(
            classes=[
                "expand-all", "table",
                *self._tableidclasses(),
            ],
            title="Expand all rows",
            text="Expand all",
        )

    def addcollapseallbutton(
            self,
    ):  # type: (...) -> None
        """
        Adds a ``.collapse-all`` button for the table being generated.
        """
        from ._htmlgenbuttons import ButtonGenerator

        assert self.table_cid, "Please provide a table CID for a table with collapsible rows"

        ButtonGenerator(self.html).addbutton(
            classes=[
                "collapse-all", "table",
                *self._tableidclasses(),
            ],
            title="Collapse all rows",
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
        :return: HTML node context focused on the ``<table></table>`` node created.
        """
        from ._htmldoc import HtmlDocument

        # Create the `table` node.
        _table_ctx = self.html.addnode(
            "table",
            classes=[
                *classes,
                *self._tableidclasses(),
            ],
        )  # type: _HtmlDocumentType.NodeContext

        # Return a `HtmlDocument.NodeContext` wrapper
        # to ensure `finalize()` be called for each main row at the end of the table definition.
        class _TableNodeContext(HtmlDocument.NodeContext):
            """
            :class:`._htmldoc.HtmlDocument.NodeContext` override
            in order to call :meth:`TableGenerator._Tr1.finalize()` for each main row
            at the end of the table definition.
            """

            def __init__(
                    self,
                    table_generator,  # type: TableGenerator
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
                self.table_generator = table_generator  # type: TableGenerator

            def __exit__(
                    self,
                    exc_type,  # type: typing.Any
                    exc_val,  # type: typing.Any
                    exc_tb,  # type: typing.Any
            ):  # type: (...) -> None
                super().__exit__(exc_type, exc_val, exc_tb)

                if not exc_type:
                    # Finalize table rows.
                    for _tr1 in self.table_generator._tr1s:  # type: TableGenerator._Tr1  # noqa  ## Access to protected member
                        _tr1.finalize()

        return _TableNodeContext(
            table_generator=self,
            table_ctx=_table_ctx,
        )

    def addrow(
            self,
            *,
            tr1_cid,  # type: str
            default_state=None,  # type: _CollapsibleStateType
            classes=(),  # type: typing.Sequence[str]
    ):  # type: (...) -> _HtmlDocumentType.NodeContext
        """
        Adds a ``.tr1`` main row in the table.

        :param tr1_cid:
            Optional main row CID.

            Must be set for a collapsible item (i.e. ``default_state`` is not ``None``).
        :param default_state:
            Default state for a collapsible ``.tr1`` main row.

            ``None`` (default) for a non-collapsible row.
        :param classes:
            Optional additional HTML classes.
        :return:
            HTML node context focused on the ``<tr></tr>`` node created.
        """
        # Check input parameters.
        if default_state is not None:
            assert tr1_cid, "Please provide a main row CID for collapsible rows"

        # Feed `_tr1s` with a new `_Tr1` instance.
        self._tr1s.append(TableGenerator._Tr1(
            table_generator=self,
            tr1_cid=tr1_cid,
            default_state=default_state,
        ))

        # Create the HTML node.
        self._tr1.tr1_ctx = self.html.addnode(
            "tr",
            classes=[
                *classes,
                "tr1",
                *self._tr1idclasses(),
                "collapsible" if (default_state is not None) else "",
            ],
        )

        return self._tr1.tr1_ctx

    def addtogglebutton(self):  # type: (...) -> None
        """
        Adds a ``.toggle-tr1`` button.

        .. note:: Not automatically added by :meth:`addrow()` since it must be done in the appropriate ``<td></td>`` node.
        """
        assert self._tr1.toggle_button_generator is not None, "Can't add a toggle button for a non-collapsible row"

        self._tr1.toggle_button_generator.addbutton(
            classes=[
                # Memo: `ButtonGenerator` already sets `.tr1` CID HTML classes, use `_tableidclasses()` only here.
                *self._tableidclasses(),
            ],
        )

    def addsubrow(
            self,
            *,
            classes=(),  # type: typing.Sequence[str]
    ):  # type: (...) -> _HtmlDocumentType.NodeContext
        """
        Adds a ``.tr2`` row in the table.

        :param classes: Optional additional HTML classes.
        :return: HTML node context focused on the ``<tr></tr>`` node created.
        """
        assert self._tr1.toggle_button_generator is not None, "Can't add a subrow for a non-collapsible row"

        self._tr1.tr2_ctxs.append(
            self.html.addnode(
                "tr",
                classes=[
                    *classes,
                    "tr2",
                    *self._tr1idclasses(),
                ],
            )
        )
        return self._tr1.tr2_ctxs[-1]

    class _Tr1:
        """
        ``.tr1`` main row building context.
        """

        def __init__(
                self,
                *,
                table_generator,  # type: TableGenerator
                tr1_cid,  # type: str
                default_state,  # type: typing.Optional[_CollapsibleStateType]
        ):  # type: (...) -> None
            """
            Creates a ``.tr1`` main row building context.

            Stacked in :attr:`TableGenerator._tr1s`.

            :param table_generator: Owner table generator.
            :param tr1_cid: Main row CID.
            :param default_state: Default state for a collapsible ``.tr1`` main row. ``None`` for a non collapsible row.
            """
            from ._htmlgenbuttons import ButtonGenerator

            #: Owner table generator.
            self.table_generator = table_generator  # type: TableGenerator
            #: Main row CID.
            self.tr1_cid = tr1_cid  # type: str
            #: Default state for a collapsible ``.tr1`` main row. ``None`` for a non collapsible row.
            self.default_state = default_state  # type: typing.Optional[_CollapsibleStateType]

            #: ``.tr1`` main row ``<tr></tr>`` node context.
            self.tr1_ctx = None  # type: typing.Optional[_HtmlDocumentType.NodeContext]
            #: ``.toggle-tr1`` button generator.
            self.toggle_button_generator = None  # type: typing.Optional[ButtonGenerator]
            if self.tr1_cid and self.default_state:
                self.toggle_button_generator = ButtonGenerator(self.html, toggle_type="tr1", toggle_cid=self.tr1_cid)
            #: ``.tr2`` subrow node contexts.
            self.tr2_ctxs = []  # type: typing.List[_HtmlDocumentType.NodeContext]

        def __repr__(self):  # type: () -> str
            """
            Canonical string representation.

            For debugging purpose.
            """
            return "TableGenerator._Tr1(%s)" % (", ".join([
                f"tr1_cid={self.tr1_cid!r}",
                f"default_state={self.default_state!r}",
            ]))

        @property
        def html(self):  # type: () -> _HtmlDocumentType
            """
            Shortcut to HTML output page to feed.
            """
            return self.table_generator.html

        def finalize(self):  # type: (...) -> None
            """
            Finalizes the ``.tr1`` main row with ``.tr2`` subrows.

            Depending on the configuration:

            - sets ``.expanded``/``.collapsed`` state classes,
            - sets ``.toggle-tr1`` button text,
            - sets related ``.tr2`` rows visibility.
            """
            if (self.default_state is not None) and (self.toggle_button_generator is not None):
                if not self.tr2_ctxs:
                    # No `.tr2` rows attached.

                    # Toggle button text.
                    self.toggle_button_generator.setstate(None)

                else:
                    # `.tr2` rows attached.

                    # Main row `.expanded`/`.collapsed` class.
                    if self.tr1_ctx is not None:
                        with self.tr1_ctx:
                            self.html.addclass(self.default_state)

                    # Toggle button `.expanded`/`.collapsed` class and text.
                    self.toggle_button_generator.setstate(self.default_state)

                    # Collapsible rows.
                    for _tr2_ctx in self.tr2_ctxs:  # type: _HtmlDocumentType.NodeContext
                        with _tr2_ctx:
                            # `.expanded`/`.collapsed` class.
                            self.html.addclass(self.default_state)

                            # Visbility.
                            if self.default_state == _CollapsibleStateImpl.EXPANDED:
                                self.html.addstyle("visibility: visible")
                            else:
                                self.html.addstyle("visibility: collapse")
