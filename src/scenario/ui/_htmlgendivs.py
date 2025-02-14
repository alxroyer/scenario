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
HTML div generator.
"""

import typing

import scenario

if True:
    from ._htmlgentypes import CollapsibleState as _CollapsibleStateImpl  # @default-parameter-value
if typing.TYPE_CHECKING:
    from ._htmldoc import HtmlDocument as _HtmlDocumentType
    from ._htmlgentypes import CollapsibleState as _CollapsibleStateType


class DivGenerator:
    """
    HTML generator for a ``<div></div>`` section.

    Optional features:

    - Section name.
    - Collapsible content.

        .. note:: :meth:`addtogglebutton()`/:meth:`addcollapsiblediv()`/:meth:`setstate()` can be used without prior call to :meth:`adddiv()`.
    """

    def __init__(
            self,
            html,  # type: _HtmlDocumentType
            *,
            name="",  # type: str
            collapsible_cid="",  # type: str
            default_state=_CollapsibleStateImpl.EXPANDED,  # type: typing.Optional[_CollapsibleStateType]
    ):  # type: (...) -> None
        """
        Instantiates a :class:`DivGenerator` with configurations.

        :param html:
            HTML output page to feed.
        :param name:
            Optional section name.
        :param collapsible_cid:
            Optional CID for the collapsible content.
        :param default_state:
            Default state for the collapsible content, when ``collapsible_cid`` is defined.

            Default is `expanded`.

            When ``None``, may be set with :meth:`setstate()` in the end.
        """
        from ._htmlgenbuttons import ButtonGenerator

        #: HTML output page to feed.
        self.html = html  # type: _HtmlDocumentType

        #: Optional section name.
        self.name = name  # type: str

        #: Optional collapsible CID.
        self.collapsible_cid = collapsible_cid  # type: str

        #: Default state for the collapsible content.
        #:
        #: Not expandable/callapsible if ``None`` in the end.
        self.default_state = default_state  # type: typing.Optional[_CollapsibleStateType]

        #: Main ``<div></div>`` node context.
        self._main_div_ctx = None  # type: typing.Optional[_HtmlDocumentType.NodeContext]
        #: ``.toggle-div`` button generator.
        self._button_generator = ButtonGenerator(
            html,
            toggle_type="div" if collapsible_cid else "",
            toggle_cid=collapsible_cid,
        )  # type: ButtonGenerator
        #: ``div.collapsible`` node context.
        self._collapsible_div_ctx = None  # type: typing.Optional[_HtmlDocumentType.NodeContext]

        # Have the related .js content be embedded at the end of the HTML page.
        self.html.addfinaljs(scenario.Path(__file__).with_suffix(".js"))

    def __repr__(self):  # type: () -> str
        """
        Canonical string representation.

        For debugging purpose.
        """
        return "DivGenerator(%s)" % (", ".join([
            f"name={self.name!r}",
            f"collapsible_cid={self.collapsible_cid!r}",
        ]))

    def adddiv(
            self,
            *,
            classes=(),  # type: typing.Sequence[str]
    ):  # type: (...) -> _HtmlDocumentType.NodeContext
        """
        Adds the main ``<div></div>``.

        :param classes: Optional additional HTML classes.
        :return: HTML node context focused on the ``<div></div>`` node created.
        """
        # Create the main div.
        self._main_div_ctx = self.html.addnode(
            "div",
            classes=[
                *classes,
                "named" if self.name else "",
            ],
        )

        # Initiate the content.
        with self._main_div_ctx:
            # In case of collapsible content, add a toggle button.
            if self.collapsible_cid:
                self.addtogglebutton()

            # In case of a named section, add the name in a `span.name` element.
            if self.name:
                self.html.addnode(
                    "span",
                    classes=[
                        *classes,
                        "name",
                    ],
                    text=self.name,
                )

        return self._main_div_ctx

    def addtogglebutton(
            self,
            *,
            classes=(),  # type: typing.Sequence[str]
    ):  # type: (...) -> None
        """
        Adds a ``.toggle-div`` button.

        :param classes: Optional additional HTML classes.
        """
        assert self.collapsible_cid, "Please provide a CID for collapsible content"

        self._button_generator.addbutton(
            classes=classes,
        )

    def addcollapsiblediv(
            self,
            *,
            classes=(),  # type: typing.Sequence[str]
    ):  # type: (...) -> _HtmlDocumentType.NodeContext
        """
        Adds the div for the collapsible content.

        :param classes: Optional additional HTML classes.
        :return: HTML node context focused on the ``<div></div>`` node created.
        """
        assert self.collapsible_cid, "Please provide a CID for collapsible content"

        # Create the div.
        self._collapsible_div_ctx = self.html.addnode(
            "div",
            classes=[
                *classes,
                "collapsible",
                self.html.mkcsscompatibleclass(f"div={self.collapsible_cid}"),
            ],
        )

        # Finalize straight away if `default_state` is set.
        if self.default_state is not None:
            self.setstate(self.default_state)

        return self._collapsible_div_ctx

    def setstate(
            self,
            state,  # type: typing.Optional[_CollapsibleStateType]
    ):  # type: (...) -> None
        """
        Sets the default state for the collapsible content.

        :param state:
            State for the collapsible content.

            If ``None``, eventually sets the collapsible stuff as not-applicable.
        """
        from ._htmlgentypes import CollapsibleState

        assert self.collapsible_cid, "Please provide a CID for collapsible content"

        # Set toggle button `.expanded`/`.collapsed` class and text.
        self._button_generator.setstate(state)

        # Set collaspible `.expanded`/`.collapsed` class and visibility.
        # Memo: `addcollapsiblediv()` may have not been called.
        if self._collapsible_div_ctx is not None:
            with self._collapsible_div_ctx:
                if state is not None:
                    self.html.addclass(state)

                if state == CollapsibleState.EXPANDED:
                    self.html.addstyle("display: block")
                if state == CollapsibleState.COLLAPSED:
                    self.html.addstyle("display: none")
