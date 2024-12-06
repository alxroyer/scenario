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

import scenario

if True:
    from ._httprequesthandler import HttpRequestHandler as _HttpRequestHandlerImpl  # @inheritance
if typing.TYPE_CHECKING:
    from ._debugclasses import UIDebugClass as _UIDebugClassType
    from ._htmldoc import HtmlDocument as _HtmlDocumentType
    from ._httprequest import HttpRequest as _HttpRequestType


class RequirementsPage(_HttpRequestHandlerImpl):
    """
    Requirements page.
    """

    #: Base URL for the requirements page.
    _URL = "/requirements"  # type: str

    @staticmethod
    def mkurl(
            obj=None,  # type: typing.Union[scenario.ReqBaseline, scenario.ReqRef]
    ):  # type: (...) -> str
        """
        Builds a requirement page URL.

        :param obj:
            Applicable requirement baseline, or requirement reference to build an anchor URL for.

            If a :class:`scenario._reqref.ReqRef` is given, determines the requirement baseline by the way.

            Main requirement baseline by default.
        :return:
            Requirement page URL.
        """
        from ._httprequest import HttpRequest

        return HttpRequest.encodeurl(
            RequirementsPage._URL,
            args=HttpRequest.mkurlargs(obj=obj),
            anchor=obj.id if isinstance(obj, scenario.ReqRef) else None,
        )

    def __init__(
            self,
            *,
            debug_class=None,  # type: _UIDebugClassType
    ):  # type: (...) -> None
        """
        Configures the logger instance.

        :param debug_class:
            Optional debug class, in case of instantiation as a member of another page.

            .. seealso:: :class:`._pagecampaign.CampaignPage`
        """
        from ._debugclasses import UIDebugClass

        _HttpRequestHandlerImpl.__init__(self, debug_class or UIDebugClass.PAGE_REQS)

    def process(
            self,
            request,  # type: _HttpRequestType
    ):  # type: (...) -> bool
        from ._exec import Exec
        from ._htmldoc import HtmlDocument

        # Filter `request`.
        if request.base_path != RequirementsPage._URL:
            self.debug("Request base path %r not matching %r", request.base_path, RequirementsPage._URL)
            self.debug("%r not processed", request)
            return False
        self.debug("Processing %r", request)

        # Applicable baseline.
        self.debug("Requirement baseline: %r", request.req_baseline)

        self.debug("Generating HTML content")
        _html = HtmlDocument(request)
        _html.settitle("Requirements", campaign_subtitle=True)

        Exec.actionbutton2html(_html, request, Exec.Action.RELOAD_MAIN_REQ_BASELINE)

        self.reqs2html(_html, request.req_baseline)

        request.sendhtml(_html)
        return True

    def reqs2html(
            self,
            html,  # type: _HtmlDocumentType
            req_baseline,  # type: scenario.ReqBaseline
    ):  # type: (...) -> None
        """
        Builds the HTML content for the requirement database given with the requirement baseline.

        :param html: HTML output page to feed.
        :param req_baseline: Requirement baseline holding the requirement database to process.
        """
        with html.addnode("div", id="requirements"):
            with html.addnode("ul"):
                for _req in req_baseline.req_db.getallreqs():  # type: scenario.Req
                    self._req2html(html, _req)

    def _req2html(
            self,
            html,  # type: _HtmlDocumentType
            req,  # type: scenario.Req
    ):  # type: (...) -> None
        """
        Buils the HTML content for a requirement.

        :param html: HTML output page to feed.
        :param req: Requirement to build HTML content for.
        """
        from ._anchors import Anchor
        from ._pagereqsdown import DownstreamTraceabilityPage

        with html.addnode("li", classes=["req"]):
            # Anchor.
            with Anchor.add(html, name=req.id):
                # Requirement id.
                html.addnode("span", classes=["req", "id"], text=req.id)

                # Title.
                if req.title:
                    html.addnode("span", classes=["req", "sep"], text=":")
                    html.addnode("span", classes=["req", "title"], text=req.title)

                # Downstream traceability link.
                DownstreamTraceabilityPage.reqref2htmllink(html, req.main_ref)

            # Text.
            if req.text:
                with html.addnode("div", classes=["req", "text"]):
                    with html.addnode("p"):
                        for _index, _line in enumerate(req.text.splitlines()):  # type: int, str
                            if _index > 0:
                                html.addnode("br", auto_closing=True)
                            if _line:
                                html.addtext(_line)

            # Subreferences.
            if req.subrefs:
                with html.addnode("div", classes=["subrefs"]):
                    html.addnode("p", classes=["subrefs", "title"], text="Subreferences:")
                    with html.addnode("ul"):
                        for _subref in req.subrefs:  # type: scenario.ReqRef
                            self._subref2html(html, _subref)

    def _subref2html(
            self,
            html,  # type: _HtmlDocumentType
            subref,  # type: scenario.ReqRef
    ):  # type: (...) -> None
        """
        Buils the HTML content for a requirement subreference.

        :param html: HTML output page to feed.
        :param subref: Requirement subreference to build HTML content for.
        """
        from ._anchors import Anchor
        from ._pagereqsdown import DownstreamTraceabilityPage

        with html.addnode("li", classes=["subref"]):
            # Anchor.
            with Anchor.add(html, name=subref.id):
                # Requirement subreference id.
                html.addnode("span", classes=["subref", "id"], text=subref.id)

                # Downstream traceability link.
                DownstreamTraceabilityPage.reqref2htmllink(html, subref)
