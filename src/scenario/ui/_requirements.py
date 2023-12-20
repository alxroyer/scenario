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
    from .._req import Req as _ReqType
    from .._reqref import ReqRef as _ReqRefType
    from ._htmldoc import HtmlDocument as _HtmlDocumentType
    from ._httprequest import HttpRequest as _HttpRequestType


class Requirements(_RequestHandlerImpl):
    """
    Requirements page.
    """

    #: Base URL for the requirements page.
    URL = "/requirements"

    @staticmethod
    def mkurl(
            req_ref,  # type: _ReqRefType
    ):  # type: (...) -> str
        """
        Builds an anchor URL in the requirements page, for the given requirement reference.

        :param req_ref: Requirement reference to build an anchor URL for.
        :return: Anchor URL for the given requirement reference.
        """
        from ._httprequest import HttpRequest

        return HttpRequest.encodeurl(Requirements.URL, anchor=req_ref.id)

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

        html.settitle("Requirements")

        with html.addcontent('<div id="requirements"></div>'):
            with html.addcontent('<ul></ul>'):
                for _req in REQ_DB.getallreqs():  # type: Req
                    self._req2html(_req, html)

    def _req2html(
            self,
            req,  # type: _ReqType
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        """
        Buils the HTML content for a requirement.

        :param req: Requirement to build HTML content for.
        :param html: HTML output page to feed.
        """
        from ._downstreamtraceability import DownstreamTraceability

        with html.addcontent('<li class="req"></li>'):
            # Anchor.
            html.addcontent(f'<a name="{html.encode(req.id)}" />')

            # Requirement id, with anchor.
            html.addcontent(f'<span class="req id">{html.encode(req.id)}</span>')

            # Title.
            if req.title:
                html.addcontent('<span class="req sep">:</span>')
                html.addcontent(f'<span class="req title">{html.encode(req.title)}</span>')

            # Downstream traceability link.
            DownstreamTraceability.reqref2unnamedhtmllink(req.main_ref, html)

            # Text.
            if req.text:
                with html.addcontent('<div class="req text"></div>'):
                    _html_encoded_text = (
                        html.encode(req.text)
                        # Add `<br/>` before each leading dash character.
                        .replace("\n-", "<br/>\n-")
                        # Add double `<br/>`s to seperate paragraphs.
                        .replace("\n\n", "<br/>\n<br/>\n")
                    )  # type: str
                    html.addcontent(f'<p>{_html_encoded_text}</p>')

            # Subreferences.
            if req.subrefs:
                with html.addcontent('<div class="subrefs"></div>'):
                    with html.addcontent('<ul></ul>'):
                        for _req_ref in req.subrefs:  # type: _ReqRefType
                            self._reqsubref2html(_req_ref, html)

    def _reqsubref2html(
            self,
            req_subref,  # type: _ReqRefType
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        """
        Buils the HTML content for a requirement subreference.

        :param req_subref: Requirement subreference to build HTML content for.
        :param html: HTML output page to feed.
        """
        with html.addcontent('<li class="req-subref"></li>'):
            # Anchor.
            html.addcontent(f'<a name="{html.encode(req_subref.id)}" />')

            # Requirement reference id.
            html.addcontent(f'<span class="req-subref id">{html.encode(req_subref.id)}</span>')
