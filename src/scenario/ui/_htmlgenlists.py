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
HTML list generator.
"""

import typing

import scenario

if typing.TYPE_CHECKING:
    from ._htmldoc import HtmlDocument as _HtmlDocumentType
    from ._htmlgentypes import CollapsibleState as _CollapsibleStateType


class ListGenerator:
    """
    HTML generator for an unordered list (``<ul></ul>``).

    Optional features:

    - ``.li1`` main items and optional ``.li2`` subitems.
    - ``.li2`` subitems may collapse below ``.li1`` main items.
    - ``.li1`` and ``.li2`` items may both hold a comment:

        - When the ``.li1`` main item does not have one defined, default main comment summed up from ``.li2`` subitem comments.
        - ``.li1`` summed up comment hidden when main item is expanded, displayed when collapsed.
    """

    def __init__(
            self,
            html,  # type: _HtmlDocumentType
            *,
            list_cid="",  # type: str
    ):  # type: (...) -> None
        """
        Instantiates a :class:`ListGenerator` with configurations.

        :param html:
            HTML output page to feed.
        :param list_cid:
            Optional list CID.

            Must be set for collapsible items.
        """
        #: HTML output page to feed.
        self.html = html  # type: _HtmlDocumentType

        #: List CID. Optional.
        self.list_cid = list_cid  # type: str

        #: ``.li1`` main items.
        self._li1s = []  # type: typing.List[ListGenerator._Li1]

        # Have the related .js content be embedded at the end of the HTML page.
        self.html.addfinaljs(scenario.Path(__file__).with_suffix(".js"))

    def __repr__(self):  # type: () -> str
        """
        Canonical string representation.

        For debugging purpose.
        """
        return "ListGenerator(%s)" % (", ".join([
            f"list_cid={self.list_cid!r}",
        ]))

    @property
    def _li1(self):  # type: () -> ListGenerator._Li1
        """
        Current ``.li1`` main item.
        """
        return self._li1s[-1]

    def _listidclasses(self):  # type: (...) -> typing.Sequence[str]
        """
        Computes identifier classes for the list.

        :return: Identifier classes for the list.
        """
        _classes = []  # type: typing.List[str]
        if self.list_cid:
            _classes.append(self.html.mkcsscompatibleclass(f"list={self.list_cid}"))
        return _classes

    def _li1idclasses(self):  # type: (...) -> typing.Sequence[str]
        """
        Computes identifier classes for the current ``.li1`` main item.

        Includes the identifier classes for the list.

        :return: Identifier classes for the current ``.li1`` main item.
        """
        _classes = [*self._listidclasses()]  # type: typing.List[str]
        if self._li1.li1_cid:
            _classes.append(self.html.mkcsscompatibleclass(f"li1={self._li1.li1_cid}"))
        return _classes

    def addexpandallbutton(self):  # type: (...) -> None
        """
        Adds a ``.expand-all`` button for the list with collapsible items being generated.
        """
        from ._htmlgenbuttons import ButtonGenerator

        assert self.list_cid, "Please provide a list CID for a list with collapsible items"

        ButtonGenerator(self.html).addbutton(
            classes=[
                "expand-all", "list",
                *self._listidclasses(),
            ],
            title="Expand all list items",
            text="Expand all",
        )

    def addcollapseallbutton(self):  # type: (...) -> None
        """
        Adds a ``.collapse-all`` button for the list with collapsible items being generated.
        """
        from ._htmlgenbuttons import ButtonGenerator

        assert self.list_cid, "Please provide a list identifier for a list with collapsible items"

        ButtonGenerator(self.html).addbutton(
            classes=[
                "collapse-all", "list",
                *self._listidclasses(),
            ],
            title="Collapse all list items",
            text="Collapse all",
        )

    def addlist(
            self,
            *,
            classes=(),  # type: typing.Sequence[str]
    ):  # type: (...) -> _HtmlDocumentType.NodeContext
        """
        Starts generating the list.

        :param classes: Optional additional HTML classes.
        :return: HTML node context focused on the ``<ul></ul>`` node created.
        """
        from ._htmldoc import HtmlDocument

        # Create the `ul` node.
        _ul_ctx = self.html.addnode(
            "ul",
            classes=[
                *classes,
                *self._listidclasses(),
                "li1",
            ],
        )  # type: _HtmlDocumentType.NodeContext

        # Return a `HtmlDocument.NodeContext` wrapper
        # to ensure `_finalize()` be called at the end of the list definition.
        class _ListNodeContext(HtmlDocument.NodeContext):
            """
            :class:`._htmldoc.HtmlDocument.NodeContext` override
            in order to call :meth:`ListGenerator._Li1.finalize()` for each ``.li1`` main item
            at the end of the list definition.
            """

            def __init__(
                    self,
                    list_generator,  # type: ListGenerator
                    ul_ctx,  # type: _HtmlDocumentType.NodeContext
            ):  # type: (...) -> None
                """
                :param list_generator: Current list generator with HTML output page to feed.
                :param ul_ctx: ``ul`` node context.
                """
                HtmlDocument.NodeContext.__init__(
                    self,
                    html_doc=list_generator.html,
                    new_child=ul_ctx.new_child,
                )

                #: List generator being processed.
                self.list_generator = list_generator  # type: ListGenerator

            def __exit__(
                    self,
                    exc_type,  # type: typing.Any
                    exc_val,  # type: typing.Any
                    exc_tb,  # type: typing.Any
            ):  # type: (...) -> None
                super().__exit__(exc_type, exc_val, exc_tb)

                if not exc_type:
                    # Finalize `.li1` main items.
                    for _li1 in self.list_generator._li1s:  # type: ListGenerator._Li1  # noqa  ## Access to protected member
                        _li1.finalize()

        return _ListNodeContext(
            list_generator=self,
            ul_ctx=_ul_ctx,
        )

    def additem(
            self,
            *,
            li1_cid="",  # type: str
            default_state=None,  # type: _CollapsibleStateType
            classes=(),  # type: typing.Sequence[str]
    ):  # type: (...) -> _HtmlDocumentType.NodeContext
        """
        Adds a main ``.li1`` item.

        :param li1_cid:
            Optional main item CID.

            Must be set for a collapsible item (i.e. ``default_state`` is not ``None``).
        :param default_state:
            Default state for a collapsible item.

            ``None`` (default) for a non-collapsible item.
        :param classes:
            Optional additional HTML classes.
        :return:
            HTML node context focused on the ``<li></li>`` node created.
        """
        # Check input parameters.
        if default_state is not None:
            assert li1_cid, "Please provide an item CID for a collapsible item"

        # Feed `_li1s` with a new `_Li1` instance.
        self._li1s.append(ListGenerator._Li1(
            list_generator=self,
            li1_cid=li1_cid,
            default_state=default_state,
        ))

        # Create the HTML node.
        self._li1.li1_ctx = self.html.addnode(
            "li",
            classes=[
                *classes,
                "li1",
                *self._li1idclasses(),
                "collapsible" if (default_state is not None) else "",
            ],
        )

        # Automatically add the toggle button at the beginning of the list item.
        if self._li1.collapsible_div_generator is not None:
            with self._li1.li1_ctx:
                self._li1.collapsible_div_generator.addtogglebutton(
                    classes=[
                        # Memo: `ButtonGenerator` already sets `.li1` CID HTML classes, use `_li1idclasses()` only here.
                        *self._li1idclasses(),
                        # Set additional `.toggle-li1` HTML class with `.toggle-div`.
                        "toggle-li1",
                    ],
                )

        return self._li1.li1_ctx

    def addsubitem(
            self,
            *,
            classes=(),  # type: typing.Sequence[str]
    ):  # type: (...) -> _HtmlDocumentType.NodeContext
        """
        Adds a ``.li2`` subitem under the current ``.li1`` main item.

        ``<ul></ul>`` node automatically created for the first subitem.

        :param classes: Optional additional HTML classes.
        :return: HTML node context focused on the ``<li></li>`` node created.
        """
        from ._htmldoc import HtmlDocument

        # Automatically create the `ul` node with the first `.li2` subitem.
        if self._li1.ul_ctx is None:
            with (
                self._li1.collapsible_div_generator.addcollapsiblediv(classes=[*self._li1idclasses()])
                if (self._li1.collapsible_div_generator is not None) else
                HtmlDocument.NodeContext(self.html, self.html.current_node)
            ):
                self._li1.ul_ctx = self.html.addnode(
                    "ul",
                    classes=[
                        *classes,
                        *self._li1idclasses(),
                        "li2",
                    ],
                )

        with self._li1.ul_ctx:
            self._li1.li2_ctxs.append(
                self.html.addnode(
                    "li",
                    classes=[
                        *classes,
                        *self._li1idclasses(),
                        "li2",
                    ],
                )
            )

        return self._li1.li2_ctxs[-1]

    def addcomment(
            self,
            comment,  # type: str
            *,
            classes=(),  # type: typing.Sequence[str]
    ):  # type: (...) -> None
        """
        Adds a comment to the current ``.li1`` or ``.li2`` item.

        :param comment: Comment.
        :param classes: Optional additional HTML classes.
        """
        _starter_classes = [
            *classes,
            "li1" if (not self._li1.li2_ctxs) else "li2",
            *self._li1idclasses(),
        ]  # type: typing.List[str]

        # Separator span.
        _sep_ctx = self.html.addnode("span", classes=[*_starter_classes, "sep"], text=":")  # type: _HtmlDocumentType.NodeContext
        if not self._li1.li2_ctxs:
            self._li1.li1_sep_span_ctx = _sep_ctx

        # Comment span.
        _comment_ctx = self.html.addnode("span", classes=[*_starter_classes, "comment"], text=comment)  # type: _HtmlDocumentType.NodeContext
        if not self._li1.li2_ctxs:
            self._li1.li1_comment_text = comment
            self._li1.li1_comment_span_ctx = _comment_ctx
        else:
            self._li1.li2_comments.append(comment)

    class _Li1:
        """
        ``.li1`` main item building context.
        """

        def __init__(
                self,
                *,
                list_generator,  # type: ListGenerator
                li1_cid,  # type: str
                default_state,  # type: typing.Optional[_CollapsibleStateType]
        ):  # type: (...) -> None
            """
            Creates a ``.li1`` main item building context.

            Stacked in :attr:`ListGenerator._li1s`.

            :param list_generator: Owner list generator.
            :param li1_cid: Main item CID. May be empty.
            :param default_state: Default state for a collapsible ``.li1`` main item. ``None`` for a non collapsible item.
            """
            from ._htmlgendivs import DivGenerator

            #: Owner list generator.
            self.list_generator = list_generator  # type: ListGenerator
            #: ``.li1`` main item CID. May be empty.
            self.li1_cid = li1_cid  # type: str
            #: Default state for a collapsible ``.li1`` main item. ``None`` for a non collapsible item.
            self.default_state = default_state  # type: typing.Optional[_CollapsibleStateType]

            #: ``.li1`` main item node context.
            self.li1_ctx = None  # type: typing.Optional[_HtmlDocumentType.NodeContext]
            #: ``.li1`` main item comment text,
            #: as given initially by :meth:`ListGenerator.addcomment()`, or eventually computed in :meth:`finalize()`.
            self.li1_comment_text = ""  # type: str
            #: ``.li1`` main item comment separator ``<span></span>`` node context.
            self.li1_sep_span_ctx = None  # type: typing.Optional[_HtmlDocumentType.NodeContext]
            #: ``.li1`` main item comment text ``<span></span>`` node context.
            self.li1_comment_span_ctx = None  # type: typing.Optional[_HtmlDocumentType.NodeContext]

            #: Collapsible div generator, when applicable.
            self.collapsible_div_generator = None  # type: typing.Optional[DivGenerator]
            #: ``.li2`` subitems' ``<ul></ul>`` node context.
            self.ul_ctx = None  # type: typing.Optional[_HtmlDocumentType.NodeContext]
            #: ``.li2`` subitems ``<li></li>`` node contexts.
            self.li2_ctxs = []  # type: typing.List[_HtmlDocumentType.NodeContext]
            #: ``.li2`` subitems comments.
            self.li2_comments = []  # type: typing.List[str]

            if self.default_state is not None:
                self.collapsible_div_generator = DivGenerator(
                    self.html,
                    collapsible_cid=self.li1_cid,
                    # Set `None` for now. Will be set in the end in `finalize()`.
                    default_state=None,
                )

        def __repr__(self):  # type: () -> str
            """
            Canonical string representation.

            For debugging purpose.
            """
            return "ListGenerator._Li1(%s)" % (", ".join([
                f"li1_cid={self.li1_cid!r}",
                f"default_state={self.default_state!r}",
            ]))

        @property
        def html(self):  # type: () -> _HtmlDocumentType
            """
            Shortcut to HTML output page to feed.
            """
            return self.list_generator.html

        def finalize(self):  # type: (...) -> None
            """
            Finalizes the ``.li1`` main item with ``.li2`` subitems.

            Depending on the configuration:

            - sets ``.expanded``/``.collapsed`` state classes,
            - sets toggle button state and ``.li2`` subitems visibility,
            - computes ``.li1`` main item sum-up comment, if none already set, with visibility if applicable.
            """
            from ._htmlgentypes import CollapsibleState

            # Finalize collapsible state.
            if (self.default_state is not None) and (self.collapsible_div_generator is not None):
                if not self.li2_ctxs:
                    # No `.li2` subitems attached.

                    # Toggle button + collapsible section.
                    self.collapsible_div_generator.setstate(None)

                else:
                    # `.li2` subitems attached.

                    # `.li1` main item `.expanded`/`.collapsed` class.
                    if self.li1_ctx is not None:
                        with self.li1_ctx:
                            self.html.addclass(self.default_state)

                    # Toggle button + collapsible section.
                    self.collapsible_div_generator.setstate(self.default_state)

                    # `.li1` main item comment.
                    # Hide if auto sum-up comment and expanded.
                    if (not self.li1_comment_text) and (self.default_state == CollapsibleState.EXPANDED):
                        if self.li1_sep_span_ctx is not None:
                            with self.li1_sep_span_ctx:
                                self.html.addstyle(f"display: none")
                        if self.li1_comment_span_ctx is not None:
                            with self.li1_comment_span_ctx:
                                self.html.addstyle(f"display: none")

            # Auto sum-up comments.
            if not self.li1_comment_text:
                # Add `.comments-sum-up` class to the `.li1` main item.
                if self.li1_ctx is not None:
                    with self.li1_ctx:
                        self.html.addclass("comments-sum-up")

                # Sum up comments from `.li2` subitem comments.
                if self.li2_comments:
                    self.li1_comment_text = f"{', '.join(self.li2_comments)}"

                # Install the text computed in the dedicated span.
                if self.li1_comment_span_ctx is not None:
                    with self.li1_comment_span_ctx:
                        self.html.addtext(self.li1_comment_text)
