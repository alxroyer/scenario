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

if True:
    from .._logger import Logger as _LoggerImpl  # @inheritance
if typing.TYPE_CHECKING:
    from .._path import Path as _PathType
    from ._httprequest import HttpRequest as _HttpRequestType


class HttpServer(_LoggerImpl):
    """
    :mod:`scenario.ui` HTTP server.

    Instantiated once with the :data:`HTTP_SERVER` singleton.
    """

    def __init__(self):  # type: (...) -> None
        """
        Configures logging for the :class:`HttpServer` class,
        and initializes request handlers / page generators.
        """
        from .._debugclasses import DebugClass
        from ._filedelivery import FileDelivery
        from ._pagecampaign import CampaignPage
        from ._pagecampaigns import CampaignListPage
        from ._pageconfig import ConfigurationPage
        from ._pagehome import Homepage
        from ._pagereqs import RequirementsPage
        from ._pagereqsdown import DownstreamTraceabilityPage
        from ._pagereqsup import UpstreamTraceabilityPage
        from ._pagescenario import ScenarioPage
        from ._pagescenarios import ScenarioListPage
        from ._requesthandler import RequestHandler

        _LoggerImpl.__init__(self, DebugClass.UI_HTTP_SERVER)

        #: Request handlers / page generators.
        self._request_handlers = [
            Homepage(),
            ConfigurationPage(),
            RequirementsPage(),
            ScenarioListPage(),
            ScenarioPage(),
            CampaignListPage(),
            CampaignPage(),
            DownstreamTraceabilityPage(),
            UpstreamTraceabilityPage(),
            FileDelivery(),
        ]  # type: typing.Sequence[RequestHandler]

    @property
    def main_path(self):  # type: () -> _PathType
        """
        `scenario.ui` main execution path.
        """
        from .._scenarioconfig import SCENARIO_CONFIG

        return SCENARIO_CONFIG.uimainpath()

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
        from ._requesthandler import RequestHandler

        self.debug("Processing %r", request)

        try:
            for _request_handler in self._request_handlers:  # type: RequestHandler
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
