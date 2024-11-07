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
User interface home page.
"""

import typing

if True:
    from ._requesthandler import RequestHandler as _RequestHandlerImpl  # @inheritance
if typing.TYPE_CHECKING:
    from ._httprequest import HttpRequest as _HttpRequestType


class Homepage(_RequestHandlerImpl):
    """
    Home page.
    """

    #: Base URL for the homepage.
    _URL = "/"  # type: str

    @staticmethod
    def mkurl(
            *,
            html_escape=True,  # type: bool
    ):  # type: (...) -> str
        """
        Builds a homepage URL.

        :param html_escape: ``True`` (default) to get HTML escaped text.
        :return: Homepage URL.
        """
        from ._httprequest import HttpRequest

        return HttpRequest.encodeurl(
            Homepage._URL,
            args=HttpRequest.mkurlargs(obj=None),
            html_escape=html_escape,
        )

    def __init__(self):  # type: (...) -> None
        """
        Configures the logger instance.
        """
        from ._debugclasses import UIDebugClass

        _RequestHandlerImpl.__init__(self, UIDebugClass.PAGE_HOME)

    def process(
            self,
            request,  # type: _HttpRequestType
    ):  # type: (...) -> bool
        from ._htmldoc import HtmlDocument

        # Filter `request`.
        if request.base_path != Homepage._URL:
            self.debug("Request base path %r not matching %r", request.base_path, Homepage._URL)
            self.debug("%r not processed", request)
            return False
        self.debug("Processing %r", request)

        self.debug("Generating HTML content")
        _html = HtmlDocument()  # type: HtmlDocument
        _html.settitle(request, "Scenario User Interface", campaign_subtitle=False)

        _html.addcontent('<p>Hello world!</p>')

        request.sendhtml(_html)
        return True
