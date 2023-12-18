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
import io
import shutil
import typing

if True:
    from .._logger import Logger as _LoggerImpl  # `Logger` used for inheritance.
if typing.TYPE_CHECKING:
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
        from ._configuration import Configuration
        from ._homepage import Homepage
        from ._requesthandler import RequestHandler
        from ._requirements import Requirements
        from ._scenariodetails import ScenarioDetails
        from ._scenarios import Scenarios

        _LoggerImpl.__init__(self, DebugClass.UI_HTTP_SERVER)

        #: Request handlers / page generators.
        self._request_handlers = [
            Homepage,
            Configuration,
            Requirements,
            Scenarios,
            ScenarioDetails,
        ]  # type: typing.Sequence[typing.Type[RequestHandler]]

    def serve(self):  # type: (...) -> None
        """
        Launches the HTTP server.
        """
        from ._httprequest import HttpRequest

        self.info("Serving on http://localhost:8000/")
        _server = http.server.HTTPServer(
            ("localhost", 8000),
            # The `HttpRequest` class will be instantiated for each request.
            # The `do_GET()` and `do_POST()` methods will be called automatically.
            HttpRequest,
        )  # type: http.server.HTTPServer
        _server.serve_forever()

    def process(
            self,
            request,  # type: _HttpRequestType
    ):  # type: (...) -> None
        """
        Processes GET and POST requests.

        :param request: GET or POST request to process.
        """
        from ._htmldoc import HtmlDocument
        from ._requesthandler import RequestHandler

        self.debug("Processing %r", request)

        try:
            for _request_handler_cls in self._request_handlers:  # type: typing.Type[RequestHandler]
                _request_handler = _request_handler_cls()  # type: RequestHandler
                if _request_handler.matches(request):
                    _html = HtmlDocument()  # type: HtmlDocument
                    _request_handler.process(request, _html)
                    _content = _html.dump()  # type: bytes

                    request.send_response(http.HTTPStatus.OK)
                    request.send_header("Content-type", "text/html; charset=utf-8")
                    request.send_header("Content-Length", str(len(_content)))
                    request.end_headers()

                    _stream = io.BytesIO()  # type: io.BytesIO
                    try:
                        _stream.write(_content)
                        _stream.seek(0)
                        shutil.copyfileobj(_stream, request.wfile)
                    finally:
                        _stream.close()

                    break
            else:
                self.warning(f"404 error for {request!r}")
                try:
                    request.send_error(
                        http.HTTPStatus.NOT_FOUND,
                        f"404 error for {request!r}",
                    )
                except ConnectionAbortedError as _err:
                    self.warning(str(_err))

        except Exception as _err:
            self.logexceptiontraceback(_err)

            request.send_error(
                http.HTTPStatus.INTERNAL_SERVER_ERROR,
                repr(_err),
            )


#: Main instance of :class:`HttpServer`.
HTTP_SERVER = HttpServer()  # type: HttpServer
