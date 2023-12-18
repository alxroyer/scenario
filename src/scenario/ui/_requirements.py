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
User interface requirements page.
"""

import typing

if True:
    from ._requesthandler import RequestHandler as _RequestHandlerImpl  # `RequestHandler` used for inheritance.
if typing.TYPE_CHECKING:
    from ._htmldoc import HtmlDocument as _HtmlDocumentType
    from ._httprequest import HttpRequest as _HttpRequestType


class Requirements(_RequestHandlerImpl):
    """
    Requirements page.
    """

    #: Base URL for the requirements page.
    URL = "/requirements"

    def matches(
            self,
            request,  # type: _HttpRequestType
    ):  # type: (...) -> bool
        return request.base_path == Requirements.URL

    def process(
            self,
            request,  # type: _HttpRequestType
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        from .._req import Req
        from .._reqdb import REQ_DB
        from .._reqref import ReqRef

        html.settitle("Requirements")

        with html.addcontent('<div id="requirements"></div>'):
            with html.addcontent('<ul></ul>'):
                for _req in REQ_DB.getallreqs():  # type: Req
                    with html.addcontent('<li class="req"></li>'):
                        html.addcontent(f'<span class="req id">{html.encode(_req.id)}</span>')
                        if _req.title:
                            html.addcontent('<span class="req sep">:</span>')
                            html.addcontent(f'<span class="req title">{html.encode(_req.title)}</span>')

                        if _req.sub_refs:
                            with html.addcontent('<ul></ul>'):
                                for _req_ref in _req.sub_refs:  # type: ReqRef
                                    html.addcontent(f'<li class="req-ref"><span class="req-ref id">{html.encode(_req_ref.id)}</span></li>')
