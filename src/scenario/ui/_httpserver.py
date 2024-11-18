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
Requirement management HTTP interface.
"""

import http.server
import os
import typing

import scenario

if typing.TYPE_CHECKING:
    from ._httprequest import HttpRequest as _HttpRequestType


class HttpServer(scenario.Logger):
    """
    :mod:`scenario.ui` HTTP server.

    Instantiated once with the :data:`HTTP_SERVER` singleton.
    """

    def __init__(self):  # type: (...) -> None
        """
        Configures logging for the :class:`HttpServer` class,
        and initializes request handlers / page generators.
        """
        from ._debugclasses import UIDebugClass
        from ._exec import Exec
        from ._filedelivery import FileDelivery
        from ._httprequesthandler import HttpRequestHandler
        from ._pagecampaign import CampaignPage
        from ._pagecampaigns import CampaignListPage
        from ._pageconfig import ConfigurationPage
        from ._pagehome import Homepage
        from ._pagereqs import RequirementsPage
        from ._pagereqsdown import DownstreamTraceabilityPage
        from ._pagereqsup import UpstreamTraceabilityPage
        from ._pagescenario import ScenarioPage
        from ._pagescenarios import ScenarioListPage

        scenario.Logger.__init__(self, UIDebugClass.HTTP_SERVER)

        #: Request handlers / page generators.
        self._request_handlers = [
            CampaignListPage(),
            CampaignPage(),
            ConfigurationPage(),
            DownstreamTraceabilityPage(),
            Exec(),
            FileDelivery(),
            Homepage(),
            RequirementsPage(),
            ScenarioListPage(),
            ScenarioPage(),
            UpstreamTraceabilityPage(),
        ]  # type: typing.Sequence[HttpRequestHandler]

    @property
    def main_path(self):  # type: () -> scenario.Path
        """
        `scenario.ui` main execution path.
        """
        from ._configdb import UI_CONFIG

        return UI_CONFIG.mainpath()

    def serve(self):  # type: (...) -> None
        """
        Launches the HTTP server.
        """
        from ._httprequest import HttpRequest

        # Ensure current working directory.
        os.chdir(self.main_path)

        self.info("Serving on http://localhost:8000/")
        self.debug("Current working directory: '%s'", self.main_path.abspath)
        _server = http.server.HTTPServer(
            ("localhost", 8000),
            # The `HttpRequest` class will be instantiated for each request.
            # The `do_GET()` and `do_POST()` methods will be called automatically.
            HttpRequest,
        )  # type: http.server.HTTPServer
        try:
            _server.serve_forever()
        except KeyboardInterrupt as _err:
            self.debug("KeyboardInterrupt: %s", _err)

    def process(
            self,
            request,  # type: _HttpRequestType
    ):  # type: (...) -> None
        """
        Processes GET and POST requests.

        :param request: GET or POST request to process.
        """
        from ._httprequesthandler import HttpRequestHandler

        self.debug("Processing %r", request)

        try:
            for _request_handler in self._request_handlers:  # type: HttpRequestHandler
                if _request_handler.process(request):
                    break
            else:
                try:
                    request.send_error(http.HTTPStatus.NOT_FOUND, message=f"{request.requestline!r} not found")
                except ConnectionAbortedError as _err:
                    self.warning(repr(_err))

        except Exception as _err:
            self.logexceptiontraceback(_err)

            try:
                request.send_error(http.HTTPStatus.INTERNAL_SERVER_ERROR, message=repr(_err))
            except ConnectionAbortedError as _err:
                self.warning(repr(_err))


#: Main instance of :class:`HttpServer`.
HTTP_SERVER = HttpServer()  # type: HttpServer
