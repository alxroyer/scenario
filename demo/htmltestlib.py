# -*- coding: utf-8 -*-

import scenario


class HtmlControl(scenario.Assertions, scenario.Logger):
    def __init__(
            self,
            name,  # type: str
    ):  # type: (...) -> None
        scenario.Assertions.__init__(self)
        scenario.Logger.__init__(self, name)

    def type(
            self,
            text,  # type: str
    ):  # type: (...) -> None
        self.info(f"Typing text {text!r}")

    def click(self):  # type: (...) -> None
        self.info("Clicking on the button")

    def gettext(self):  # type: (...) -> str
        return "<p>Hello john!</p>"


def body():  # type: (...) -> HtmlControl
    return HtmlControl("body")


def getedit(
        id,  # type: str
):  # type: (...) -> HtmlControl
    return HtmlControl(f"edit[@id={id!r}]")


def getbutton(
        id,  # type: str
):  # type: (...) -> HtmlControl
    return HtmlControl(f"edit[@id={id!r}]")
