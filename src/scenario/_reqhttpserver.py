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
import logging
import shutil
import socketserver
import sys
import typing

if True:
    from ._logger import Logger as _LoggerImpl  # `Logger` used for inheritance.


class ReqHttpServer(_LoggerImpl):

    def __init__(self):  # type: (...) -> None
        from ._debugclasses import DebugClass

        _LoggerImpl.__init__(self, DebugClass.REQ_HTTP_SERVER)

    def serve(self):  # type: (...) -> None
        class _HTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
            """
            This class will be instantiated for each request.

            Let's redirect calls to our ``REQ_HTTP_SERVER`` singleton instance.
            """
            def do_GET(self):  # type: (...) -> None  # noqa  ## Function name should be lowercase
                """
                GET request.
                """
                REQ_HTTP_SERVER.get(self)

        _server = socketserver.TCPServer(("localhost", 8000), _HTTPRequestHandler)  # type: socketserver.TCPServer
        self.info("Serving on port 8000")
        _server.serve_forever()

    def get(
            self,
            request,  # type: http.server.BaseHTTPRequestHandler
    ):  # type: (...) -> None
        from ._testerrors import ExceptionError

        self.debug("request.path = %r", request.path)

        r = []  # type: typing.List[str]
        f = io.BytesIO()  # type: io.BytesIO

        try:
            enc = sys.getfilesystemencoding()  # type: str
            title = "Requirement HTTP server"  # type: str
            r.append('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">')
            r.append('<html>\n<head>')
            r.append('<meta http-equiv="Content-Type" content="text/html; charset=%s">' % enc)
            r.append('<title>%s</title>\n</head>' % title)
            r.append('<body>\n<h1>%s</h1>' % title)
            r.append('</body>\n</html>\n')
            encoded = '\n'.join(r).encode(enc, 'surrogateescape')
            f.write(encoded)
            f.seek(0)

            request.send_response(http.HTTPStatus.OK)
            request.send_header("Content-type", "text/html; charset=%s" % enc)
            request.send_header("Content-Length", str(len(encoded)))
            request.end_headers()

            shutil.copyfileobj(f, request.wfile)
        except Exception as _err:
            ExceptionError(_err).logerror(self, logging.ERROR)

            request.send_error(
                http.HTTPStatus.INTERNAL_SERVER_ERROR,
                repr(_err),
            )
        finally:
            f.close()


REQ_HTTP_SERVER = ReqHttpServer()  # type: ReqHttpServer
