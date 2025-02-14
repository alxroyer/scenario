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
HTML button generator.
"""

import typing

import scenario

if typing.TYPE_CHECKING:
    from ._htmldoc import HtmlDocument as _HtmlDocumentType
    from ._htmlgentypes import CollapsibleState as _CollapsibleStateType


class ButtonGenerator:
    """
    HTML generator for a button,
    i.e. a ``<a></a>`` link with ``.button`` HTML class.

    Optional features:

    - Toggle button: adds the ``.toggle`` class to the button.
    - Inner span: add an inner ``<span></span>`` with text.
    """

    def __init__(
            self,
            html,  # type: _HtmlDocumentType
            *,
            toggle_type="",  # type: str
            toggle_cid="",  # type: str
    ):  # type: (...) -> None
        """
        Instantiates a :class:`ButtonGenerator` with configurations.

        :param html: HTML output page to feed.
        :param toggle_type: Type of item for a toggle button.
        :param toggle_cid: CID for a toggle button.
        """
        assert not (bool(toggle_type) ^ bool(toggle_cid)), "Please set both toggle type and CID, or none"

        #: HTML output page to feed.
        self.html = html  # type: _HtmlDocumentType
        #: Type of item for a toggle button.
        self.toggle_type = toggle_type  # type: str
        #: CID for a toggle button.
        self.toggle_cid = toggle_cid  # type: str

        #: Main ``<a></a>`` node context.
        self.a_ctx = None  # type: typing.Optional[_HtmlDocumentType.NodeContext]
        #: Inner optional ``<span></span>`` node context.
        self.inner_span_ctx = None  # type: typing.Optional[_HtmlDocumentType.NodeContext]

        # Have the related .js content be embedded at the end of the HTML page.
        self.html.addfinaljs(scenario.Path(__file__).with_suffix(".js"))
        if self.toggle:
            # .js dependencies:
            # Ensure `scenario.divs` is loaded
            # (`scenario.divs.findAndToggleAll()` called from `scenario.tables._toggle()`, for `.toggle-tr1` buttons).
            self.html.addfinaljs(scenario.Path(__file__).parent / "_htmlgendivs.js")
            # Ensure `scenario.lists` is loaded
            # (`scenario.lists.checkToggleLi1()` called (or may be called for `.toggle-tr1` buttons) from `scenario.divs.toggle()`, for any toggle button).
            self.html.addfinaljs(scenario.Path(__file__).parent / "_htmlgenlists.js")

    def __repr__(self):  # type: () -> str
        """
        Canonical string representation.

        For debugging purpose.
        """
        _attrs = []  # type: typing.List[str]
        if self.toggle:
            _attrs.append(f"toggle_type={self.toggle_type!r}")
            _attrs.append(f"toggle_cid={self.toggle_cid!r}")
        return "ButtonGenerator(%s)" % (", ".join(_attrs))

    @property
    def toggle(self):  # type: () -> bool
        """
        ``True`` for a toggle button.
        """
        return bool(self.toggle_type and self.toggle_cid)

    def addbutton(
            self,
            *,
            classes=(),  # type: typing.Sequence[str]
            href="#",  # type: str
            title=None,  # type: str
            text=None,  # type: str
    ):  # type: (...) -> _HtmlDocumentType.NodeContext
        """
        Adds the button.

        :param classes: Optional additional HTML classes.
        :param href: URL to set for ``@href`` attribute. Defaults to '#'.
        :param title: ``@title`` attribute value, used for popup info on link hover. None by default for no ``@title`` attribute.
        :param text: Text content for the link. Empty by default. Don't use if :meth:`addinnerspan()` is used after.
        :return: Main ``<a></a>`` node context.
        """
        from ._htmlgenlinks import LinkGenerator

        self.a_ctx = LinkGenerator(self.html).addlink(
            classes=[
                *classes,
                "button",
                "toggle" if self.toggle else "",
                f"toggle-{self.toggle_type}" if self.toggle else "",
                self.html.mkcsscompatibleclass(f"{self.toggle_type}={self.toggle_cid}") if self.toggle else "",
            ],
            href=href,
            title=title,
            text=text,
        )
        return self.a_ctx

    def addinnerspan(
            self,
            text,  # type: str
            *,
            classes=(),  # type: typing.Sequence[str]
    ):  # type: (...) -> _HtmlDocumentType.NodeContext
        """
        Adds an inner ``<span></span>`` with text.

        Don't call if :meth:`setstate()` is called.

        :param text: Text to set in the inner span.
        :param classes: Optional additional HTML classes.
        :return: Inner ``<span></span>`` node context.
        """
        assert self.a_ctx is not None, "Please add the button before adding inner span"
        assert self.inner_span_ctx is None, "Inner span already added"

        with self.a_ctx:
            self.inner_span_ctx = self.html.addnode(
                "span",
                classes=classes,
                text=text,
            )

        return self.inner_span_ctx

    def setstate(
            self,
            state,  # type: typing.Optional[_CollapsibleStateType]
    ):  # type: (...) -> None
        """
        Sets the collapsible state for a toggle button.

        Sets inner span by the way.

        :param state:
            Collapsible state.

            If ``None``, sets the toggle button as disabled.
        """
        from ._htmlgentypes import CollapsibleState

        assert self.toggle, "Can't set state for a non-toggle button"
        assert self.a_ctx is not None, "Please add the button before setting its state"
        assert self.inner_span_ctx is None, "Please don't call `ButtonGenerator.addinnerspan()` before `setstate()`"

        with self.a_ctx:
            if state is None:
                # Button disabled: set inner text only.
                self.addinnerspan("o")
            else:
                # Button enabled: set inner text and HTML classes.
                self.html.addclass(state)
                with self.addinnerspan("-" if (state == CollapsibleState.EXPANDED) else "+"):
                    self.html.addclass(state)
