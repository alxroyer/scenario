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
    from ._requesthandler import RequestHandler as _RequestHandlerImpl  # `RequestHandler` used for inheritance.
if typing.TYPE_CHECKING:
    from ._htmldoc import HtmlDocument as _HtmlDocumentType
    from ._httprequest import HttpRequest as _HttpRequestType


class Homepage(_RequestHandlerImpl):
    """
    Home page.
    """

    #: Base URL for the homepage.
    URL = "/"

    def matches(
            self,
            request,  # type: _HttpRequestType
    ):  # type: (...) -> bool
        return request.base_path == Homepage.URL

    def process(
            self,
            request,  # type: _HttpRequestType
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        html.settitle("Scenario User Interface")

        html.addcontent('<p>Hello world!</p>')
