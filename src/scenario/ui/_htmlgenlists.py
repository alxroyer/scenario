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
HTML list generators.
"""

import typing

import scenario

if True:
    from ._collapsible import CollapsibleState as _CollapsibleStateImpl  # @default-parameter-value
if typing.TYPE_CHECKING:
    from ._collapsible import CollapsibleState as _CollapsibleStateType
    from ._htmldoc import HtmlDocument as _HtmlDocumentType


class NamedListGenerator:
    """
    HTML generator for an unordered list (``<ul></ul>``) with a leading name.
    """

    def __init__(
            self,
            arg,  # type: typing.Union[_HtmlDocumentType, CollapsibleListGenerator]
    ):  # type: (...) -> None
        """
        Instantiates a :class:`NamedListGenerator` with
        either a :class:`._htmldoc.HtmlDocument` directly,
        or a :class:`CollapsibleListGenerator`.

        :param arg:
            :class:`._htmldoc.HtmlDocument` or :class:`CollapsibleListGenerator` giving the HTML output page to feed at least.

            If a :class:`CollapsibleListGenerator` is given, a named collapsible list will be generated,
            with expand/collapse all buttons.
        """
        #: HTML output page to feed.
        self.html = arg.html if isinstance(arg, CollapsibleListGenerator) else arg  # type: _HtmlDocumentType
        #: Optional list generator.
        self.list_generator = arg if isinstance(arg, CollapsibleListGenerator) else None  # type: typing.Optional[CollapsibleListGenerator]

    def addlist(
            self,
            *,
            div_classes=(),  # type: typing.Sequence[str]
            name,  # type: str
            ul_classes=(),  # type: typing.Sequence[str]
    ):  # type: (...) -> _HtmlDocumentType.NodeContext
        """
        Adds a unordered list with a leading name.

        In the form of a ``<div class="named ul"><span class="name">...</span><ul></ul><div>`` structure.

        :param div_classes: Additional classes to add to the ``.named.ul`` div.
        :param name: Name to set in the ``span.name`` element.
        :param ul_classes: Additional classes to add to the ``<ul></ul>`` element.
        :return: HTML node context focused on the ``<ul></ul>`` element created.

        If a :class:`CollapsibleListGenerator` had been given,
        expand/collapse all buttons may be generated between the ``span`` and ``ul`` elements,
        and the ``ul`` element becomes the collapsible list.
        """
        with self.html.addnode("div", classes=["named", "ul", *div_classes]):
            self.html.addnode("span", classes=["name"], text=name)

            if self.list_generator:
                self.list_generator.addexpandallbutton()
                self.list_generator.addcollapseallbutton()
                return self.list_generator.addlist(classes=ul_classes)
            else:
                return self.html.addnode("ul", classes=ul_classes)


class CollapsibleListGenerator:
    """
    HTML generator for a list of collapsible list items.
    """

    def __init__(
            self,
            html,  # type: _HtmlDocumentType
            *,
            list_id,  # type: str
            default_state=_CollapsibleStateImpl.EXPANDED,  # type: _CollapsibleStateType
    ):  # type: (...) -> None
        """
        Instantiates a :class:`CollapsibleListGenerator` with configurations.

        :param html: HTML output page to feed.
        :param list_id: List identifier used in HTML classes.
        :param default_state: Default state for collapsible list items. Default is `expanded`.
        """
        #: HTML output page to feed.
        self.html = html  # type: _HtmlDocumentType
        #: List identifier to set in HTML classes.
        self.list_id = list_id  # type: str
        #: Default state for collapsible rows.
        self.default_state = default_state  # type: _CollapsibleStateType

        #: Main list items.
        self._main_list_items = []  # type: typing.List[CollapsibleListItemGenerator]

    def addexpandallbutton(self):  # type: (...) -> None
        """
        Adds a ``.expand-all`` button for the list being generated.
        """
        self.html.addnode(
            "a",
            classes=[
                "button", "expand-all", "list",
                self.html.mkcsscompatibleclass(f"list={self.list_id}"),
            ],
            href="#",
            text="Expand all",
        )

    def addcollapseallbutton(self):  # type: (...) -> None
        """
        Adds a ``.collapse-all`` button for the list being generated.
        """
        self.html.addnode(
            "a",
            classes=[
                "button", "collapse-all", "list",
                self.html.mkcsscompatibleclass(f"list={self.list_id}"),
            ],
            href="#",
            text="Collapse all",
        )

    def addlist(
            self,
            *,
            classes=(),  # type: typing.Sequence[str]
    ):  # type: (...) -> _HtmlDocumentType.NodeContext
        """
        Starts generating the list.

        :param classes: Additional HTML classes to add to the ``<ul></ul>`` element.
        :return: HTML node context focused on the ``<ul></ul>`` created.
        """
        # Have the related .js content be embedded at the end of the HTML page.
        self.html.addfinaljs(scenario.Path(__file__).with_suffix(".js"))

        return self.html.addnode(
            "ul",
            classes=[
                *classes,
                "collapsible",
                self.html.mkcsscompatibleclass(f"list={self.list_id}"),
            ],
        )

    def addmainlistitem(
            self,
            *,
            main_list_item_id,  # type: str
            classes=(),  # type: typing.Sequence[str]
    ):  # type: (...) -> _HtmlDocumentType.NodeContext
        """
        Adds a main collapsible list item.

        :param main_list_item_id: Main list item identifier used in HTML classes.
        :param classes: Optional additional HTML classes.
        :return: HTML node context focused on the ``<li></li>`` created.
        """
        # Feed `_main_list_items` with a new `CollapsibleListItemGenerator` instance.
        self._main_list_items.append(CollapsibleListItemGenerator(
            self.html,
            main_list_item_id=main_list_item_id,
            default_state=self.default_state,
        ))

        # Call `CollapsibleListItemGenerator.addmainlistitem()`.
        return self._main_list_items[-1].addmainlistitem(classes=[
            *classes,
            self.html.mkcsscompatibleclass(f"list={self.list_id}"),
            # Memo: `CollapsibleListItemGenerator.addmainlistitem()` adds the `f"main-list-item={self.main_list_item_id}"` class.
        ])

    def addcollapsiblelistitem(
            self,
            *,
            classes=(),  # type: typing.Sequence[str]
    ):  # type: (...) -> _HtmlDocumentType.NodeContext
        """
        Adds a ``.collapsible-list-item`` list item under the current main list item.

        Basically inside a ``<ul></ul>`` node.

        :param classes: Optional additional HTML classes.
        :return: HTML node context focused on the ``<li></li>`` created.
        """
        # Call `CollapsibleListItemGenerator.addcollapsiblelistitem()`.
        return self._main_list_items[-1].addcollapsiblelistitem(classes=[
            *classes,
            self.html.mkcsscompatibleclass(f"list={self.list_id}"),
            # Memo: `CollapsibleListItemGenerator.addcollapsiblelistitem()` adds the `f"main-list-item={self.main_list_item_id}"` class.
        ])


class CollapsibleListItemGenerator:
    """
    HTML generator for lists with collapsible commented items.
    """

    def __init__(
            self,
            html,  # type: _HtmlDocumentType
            *,
            main_list_item_id,  # type: str
            default_state=_CollapsibleStateImpl.EXPANDED,  # type: _CollapsibleStateImpl
    ):  # type: (...) -> None
        """
        Instantiates a :class:`CollapsibleListItemGenerator` with configurations.

        :param html: HTML output page to feed.
        :param main_list_item_id: Main list item identifier used in HTML classes.
        :param default_state: Default state for collapsible items. Default is `expanded`.
        """
        #: HTML output page to feed.
        self.html = html  # type: _HtmlDocumentType
        #: Main list item identifier to set in HTML classes.
        self.main_list_item_id = main_list_item_id  # type: str
        #: Default state for collapsible rows.
        self.default_state = default_state

        #: Main ``<li></li>`` node context, saved in :meth:`addmainlistitem()`.
        self._main_li_ctx = None  # type: typing.Optional[_HtmlDocumentType.NodeContext]
        #: ``.toggle-list-item`` button ``<a></a>`` node context, saved in :meth:`_addtogglebutton()`.
        self._toggle_button_a_ctx = None  # type: typing.Optional[_HtmlDocumentType.NodeContext]
        #: ``.toggle-list-item`` button ``<span></span>`` node context, saved in :meth:`_addtogglebutton()`.
        self._toggle_button_span_ctx = None  # type: typing.Optional[_HtmlDocumentType.NodeContext]
        #: Main comments text, as given initially by :meth:`addcomments()`, or eventually computed in :meth:`_finalize()`.
        self._main_comments_text = ""  # type: str
        #: Main list item comments separator ``<span></span>`` node context, saved in :meth:`addcomments()` when called for the main list item.
        self._main_sep_span_ctx = None  # type: typing.Optional[_HtmlDocumentType.NodeContext]
        #: Main list item comments text ``<span></span>`` node context, saved in :meth:`addcomments()` when called for the main list item.
        self._main_comments_span_ctx = None  # type: typing.Optional[_HtmlDocumentType.NodeContext]
        #: ``<li></li>`` node contexts of related collapsible list items, fed in :meth:`addcollapsiblelistitem()`.
        self._collapsible_li_ctxs = []  # type: typing.List[_HtmlDocumentType.NodeContext]
        #: Collabsible list items comments, saved in :meth:`addcomments()` when called for a collapsible list item.
        self._collapsible_comments = []  # type: typing.List[str]

    def addmainlistitem(
            self,
            *,
            classes=(),  # type: typing.Sequence[str]
    ):  # type: (...) -> _HtmlDocumentType.NodeContext
        """
        Defines the main collapsible list item.

        :param classes: Optional additional HTML classes.
        :return: HTML node context focused on the ``<li></li>`` created.
        """
        from ._htmldoc import HtmlDocument

        # Have '_collapsiblelist.js' be embedded at the end of the HTML page.
        self.html.addfinaljs(scenario.Path(__file__).with_suffix(".js"))

        # Save `_main_li`.
        self._main_li_ctx = self.html.addnode(
            "li",
            classes=[
                *classes,
                "collapsible", "main-list-item",
                self.html.mkcsscompatibleclass(f"main-list-item={self.main_list_item_id}"),
            ],
        )

        # Automatically add the toggle button at the beginning of the main item.
        with self._main_li_ctx:
            self._addtogglebutton()

        # Return a `HtmlDocument.NodeContext` wrapper
        # to ensure `_finalize()` be called at the end of the list item definition.
        class _MainListItemNodeContext(HtmlDocument.NodeContext):
            """
            :class:`._htmldoc.HtmlDocument.NodeContext` override
            in order to call :meth:`CollapsibleListItemGenerator._finalize()`
            at the end of the main list item definition.
            """

            def __init__(
                    self,
                    list_item_generator,  # type: CollapsibleListItemGenerator
                    li_ctx,  # type: _HtmlDocumentType.NodeContext
            ):  # type: (...) -> None
                """
                :param list_item_generator: Current list item generator with HTML output page to feed.
                :param li_ctx: Main list item node context.
                """
                HtmlDocument.NodeContext.__init__(
                    self,
                    html_doc=list_item_generator.html,
                    new_child=li_ctx.new_child,
                )

                #: List item generator being processed.
                self.list_item_generator = list_item_generator  # type: CollapsibleListItemGenerator

            def __exit__(
                    self,
                    exc_type,  # type: typing.Any
                    exc_val,  # type: typing.Any
                    exc_tb,  # type: typing.Any
            ):  # type: (...) -> None
                super().__exit__(exc_type, exc_val, exc_tb)

                if not exc_type:
                    # Finalize the main list item.
                    self.list_item_generator._finalize()  # noqa  ## Access to protected method

        return _MainListItemNodeContext(
            list_item_generator=self,
            li_ctx=self._main_li_ctx,
        )

    def addcollapsiblelistitem(
            self,
            *,
            classes=(),  # type: typing.Sequence[str]
    ):  # type: (...) -> _HtmlDocumentType.NodeContext
        """
        Adds a ``.collapsible-list-item`` list item under the main list item.

        Basically inside a ``<ul></ul>`` node.

        :param classes: Optional additional HTML classes.
        :return: HTML node context focused on the ``<li></li>`` created.
        """
        self._collapsible_li_ctxs.append(
            self.html.addnode(
                "li",
                classes=[
                    *classes,
                    "collapsible-list-item",
                    self.html.mkcsscompatibleclass(f"main-list-item={self.main_list_item_id}"),
                ],
            )
        )
        return self._collapsible_li_ctxs[-1]

    def _addtogglebutton(self):  # type: (...) -> None
        """
        Adds a ``.toggle-list-item`` button.
        """
        self._toggle_button_a_ctx = self.html.addnode(
            "a",
            classes=[
                "button", "toggle-list-item",
                self.html.mkcsscompatibleclass(f"main-list-item={self.main_list_item_id}"),
            ],
        )
        with self._toggle_button_a_ctx:
            # Create a span node without text.
            # The text will be set when the main list item is terminated.
            self._toggle_button_span_ctx = self.html.addnode("span")

    def addcomments(
            self,
            comments,  # type: str
            *,
            classes=(),  # type: typing.Sequence[str]
    ):  # type: (...) -> None
        """
        Adds comments to the current main or collapsible list item.

        :param comments: Comments.
        :param classes: Optional additional HTML classes.
        """
        _li_item_class = "main-list-item" if (not self._collapsible_li_ctxs) else "collapsible-list-item"  # type: str

        _sep_ctx = self.html.addnode("span", classes=[*classes, _li_item_class, "sep"], text=":")  # type: _HtmlDocumentType.NodeContext
        if not self._collapsible_li_ctxs:
            self._main_sep_span_ctx = _sep_ctx

        _comments_ctx = self.html.addnode("span", classes=[*classes, _li_item_class, "comments"], text=comments)  # type: _HtmlDocumentType.NodeContext
        if not self._collapsible_li_ctxs:
            self._main_comments_text = comments
            self._main_comments_span_ctx = _comments_ctx
        else:
            self._collapsible_comments.append(comments)

    def _finalize(self):  # type: (...) -> None
        """
        Finalizes the collapsible list item.

        Depending on whether on the main list item has related collapsible list itesms attached to it or not:

        - sets `.expanded`/`.collapsed` state classes,
        - sets `.toggle-list-item` button text,
        - computes main sum-up comments, if none already set, with visibility,
        - sets related collapsible list items visibility.
        """
        if not self._collapsible_li_ctxs:
            # No `.collapsible-list-item`s attached.

            # Toggle button text.
            if self._toggle_button_span_ctx is not None:
                with self._toggle_button_span_ctx:
                    self.html.addtext("o")

        else:
            # `.collapsible-list-item`s attached.

            # Main list item `.expanded`/`.collapsed` class.
            if self._main_li_ctx:
                with self._main_li_ctx:
                    self.html.addclass(self.default_state)

            # Toggle button `.expanded`/`.collapsed` class.
            if self._toggle_button_a_ctx is not None:
                with self._toggle_button_a_ctx:
                    self.html.addclass(self.default_state)
            # Toggle button text.
            if self._toggle_button_span_ctx is not None:
                with self._toggle_button_span_ctx:
                    if self.default_state == _CollapsibleStateImpl.EXPANDED:
                        self.html.addtext("-")
                    else:
                        self.html.addtext("+")

            # Main list item comments.
            # Hide if auto sum-up comments and expanded.
            if (not self._main_comments_text) and (self.default_state == _CollapsibleStateImpl.EXPANDED):
                if self._main_sep_span_ctx is not None:
                    with self._main_sep_span_ctx:
                        self.html.addstyle(f"display: none")
                if self._main_comments_span_ctx is not None:
                    with self._main_comments_span_ctx:
                        self.html.addstyle(f"display: none")
            # Auto sum-up comments.
            if not self._main_comments_text:
                # Add `.comments-sum-up` class to the main list item.
                if self._main_li_ctx:
                    with self._main_li_ctx:
                        self.html.addclass("comments-sum-up")
                # Compute comments from collapsible list item comments.
                if self._collapsible_comments:
                    self._main_comments_text = f"{', '.join(self._collapsible_comments)}"
                # Install the text computed in the dedicated span.
                if self._main_comments_span_ctx is not None:
                    with self._main_comments_span_ctx:
                        self.html.addtext(self._main_comments_text)

            # Collapsible list items.
            for _collapsible_li_ctx in self._collapsible_li_ctxs:  # type: _HtmlDocumentType.NodeContext
                with _collapsible_li_ctx:
                    # `.expanded`/`.collapsed` class.
                    self.html.addclass(self.default_state)
                    # Visbility.
                    if self.default_state == _CollapsibleStateImpl.EXPANDED:
                        self.html.addstyle("display: block")
                    else:
                        self.html.addstyle("display: none")
