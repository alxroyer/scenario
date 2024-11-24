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
HTTP request management.
"""

import http.server
import json
import sys
import time
import typing
import urllib.parse

import scenario

if typing.TYPE_CHECKING:
    from ._htmldoc import HtmlDocument as _HtmlDocumentType


class HttpRequest(http.server.BaseHTTPRequestHandler):
    """
    ``http.server.BaseHTTPRequestHandler`` override.

    Automatically called by the ``http.server`` library
    through the :meth:`do_GET()` and :meth:`do_POST()` methods.
    Calls redirected to our ``REQ_HTTP_SERVER`` singleton instance.

    This class provides facilities to manipulate input request data:

    - method (see :attr:`method`),
    - base URL (see :attr:`base_path`),
    - GET and POST arguments (see :meth:`getarg()`).

    This class also overrides the :meth:`log_error()` and :meth:`log_message()` methods
    in order to redirect ``http.server`` logging to our logging system.
    """

    class Method(scenario.enum.StrEnum):
        """
        HTTP methods as an enum.
        """
        #: GET method.
        GET = "GET"
        #: POST method.
        POST = "POST"

    class Arg(scenario.enum.StrEnum):
        """
        URL argument names.
        """
        #: Campaign name (selector).
        CAMPAIGN_NAME = "campaign"

    #: Antireplay requirement identifier memory.
    _processed = set()  # type: typing.Set[int]

    @staticmethod
    def mkurlargs(
            *,
            obj,  # type: typing.Optional[typing.Union[scenario.ReqBaseline, scenario.ReqBaselineObject]]
    ):  # type: (...) -> typing.Dict[str, str]
        """
        Returns general URL arguments.

        Mainly sets the selected campaign name,
        or no arguments if the applicable baseline is the main one.

        :param obj: Target object. Can be either a requirement baseline, or a requirement baseline owner, or ``None``.
        :return: General URL arguments as a dictionary.
        """
        from ._reqbl import UI_REQ_BASELINES

        # Determine the campaign execution from `obj`.
        _campaign_execution = None  # type: typing.Optional[scenario.CampaignExecution]
        if isinstance(obj, scenario.CampaignExecution):
            _campaign_execution = obj
        elif isinstance(obj, scenario.TestSuiteExecution):
            _campaign_execution = obj.campaign_execution
        elif isinstance(obj, scenario.TestCaseExecution):
            _campaign_execution = obj.test_suite_execution.campaign_execution
        elif isinstance(obj, scenario.ReqBaseline):
            if obj is not UI_REQ_BASELINES.main:
                _campaign_execution = scenario.campaign_db.get(req_baseline=obj)
        elif isinstance(obj, scenario.ReqBaselineObject):
            if obj.req_baseline is not UI_REQ_BASELINES.main:
                _campaign_execution = scenario.campaign_db.get(req_baseline=obj.req_baseline)

        # Build common arguments.
        _url_args = {}  # type: typing.Dict[str, str]
        if _campaign_execution:
            _url_args[HttpRequest.Arg.CAMPAIGN_NAME] = _campaign_execution.name
        return _url_args

    def __init__(
            self,
            *args  # type: typing.Any
    ):  # type: (...) -> None
        """
        Declares enriched request attributes.

        :param args: Uncontrolled list of arguments, passed on as is to the base ``http.server.BaseHTTPRequestHandler`` class initializer.
        """
        http.server.BaseHTTPRequestHandler.__init__(self, *args)

        #: Bath path, before the optional '?' character with query.
        self.base_path = ""  # type: str
        #: GET arguments, if any, in the query part of the URL, after the '?' character.
        self._get_args = {}  # type: typing.Dict[str, str]
        #: POST arguments, if any.
        self._post_args = {}  # type: typing.Dict[str, str]

        #: Request starting time.
        #:
        #: ..warning::
        #:     Don't save :attr:`start_time` in :meth:`__init__()`
        #:     since ``http.server`` seems to clone objects in a certain way that :attr:`start_time` may be lost
        #:     when the execution reaches in :meth:`do_GET()` or :meth:`do_POST()` with another instance.
        #:
        #:     Let's declare :attr:`start_time` in :meth:`__init__()`,
        #:     but set it for real in :meth:`do_GET()` or :meth:`do_POST()`.
        self.start_time = 0.0  # type: float

        #: Number of bytes of content sent.
        #:
        #: .. warning::
        #:     Same as for :attr:`start_time`:
        #:     set for real to ``None`` in :meth:`do_GET()` or :meth:`do_POST()`.
        self.content_size = None  # type: typing.Optional[int]

    def __repr__(self):  # type: () -> str
        """
        Canonical string representation of the request.
        """
        return f"<HttpRequest {self.requestline!r}>"

    def version_string(self):  # type: (...) -> str
        """
        ``http.server.BaseHTTPRequestHandler`` override.

        Used by ``http.server.BaseHTTPRequestHandler.send_response()`` for header information.
        """
        return f"scenario.ui/{scenario.info.version} Python/{sys.version.split()[0]}"

    def do_GET(self):  # type: (...) -> None  # noqa  ## Function name should be lowercase
        """
        GET request processing.

        Automatically called by the ``http.server`` library.
        Let's redirect to our ``REQ_HTTP_SERVER`` singleton instance.
        """
        from ._httpserver import HTTP_SERVER

        try:
            # Initialize/ensure members.
            self.start_time = time.time()
            self.content_size = None

            self._parseurl()
            HTTP_SERVER.process(self)
        except Exception as _err:
            HTTP_SERVER.error(f"Error while processing {self!r}: {_err}")
            HTTP_SERVER.logexceptiontraceback(_err)

    def do_POST(self):  # type: (...) -> None  # noqa  ## Function name should be lowercase
        """
        POST request processing.

        Automatically called by the ``http.server`` library.
        Let's redirect to our ``REQ_HTTP_SERVER`` singleton instance.
        """
        from ._httpserver import HTTP_SERVER

        try:
            # Initialize/ensure members.
            self.start_time = time.time()
            self.content_size = None

            self._parseurl()
            HTTP_SERVER.process(self)
        except Exception as _err:
            HTTP_SERVER.error(f"Error while processing {self!r}: {_err}")
            HTTP_SERVER.logexceptiontraceback(_err)

    def _parseurl(self):  # type: (...) -> None
        """
        Parses the input URL.

        Parses:

        - the base path of the URL (without the query part, after the '?' character, if any),
        - GET arguments (in the query part, if any),
        - POST arguments (if any).
        """
        from ._httpserver import HTTP_SERVER

        HTTP_SERVER.debug("HTTP request: %r", self)

        _url = urllib.parse.urlparse(self.path)  # type: urllib.parse.ParseResult
        self.base_path = _url.path
        HTTP_SERVER.debug("HttpRequest.base_path=%r", self.base_path)

        # Restore the attribute, which may be deleted at this point...
        self._get_args = {}
        if _url.query:
            _get_args = urllib.parse.parse_qs(_url.query)  # type: typing.Dict[str, typing.List[str]]
            for _get_arg_name in _get_args:  # type: str
                if len(_get_args[_get_arg_name]) != 1:
                    HTTP_SERVER.warning(f"Unexpected GET argument {_get_arg_name!r}: {_get_args[_get_arg_name]!r}")
                self._get_args[_get_arg_name] = ",".join(_get_args[_get_arg_name])
            HTTP_SERVER.debug("HttpRequest._get_args=%s", scenario.debug.jsondump(self._get_args, indent=2))

        # Restore the attribute, which may be deleted at this point...
        self._post_args = {}
        if self.method == HttpRequest.Method.POST:
            _content_length = int(self.headers.get("content-length"))  # type: int
            if _content_length > 0:
                _post_args = urllib.parse.parse_qs(self.rfile.read(_content_length).decode("utf-8"))  # type: typing.Dict[str, typing.List[str]]
                for _post_arg_name in _post_args:  # type: str
                    if len(_post_args[_post_arg_name]) != 1:
                        HTTP_SERVER.warning(f"Unexpected POST argument {_post_arg_name!r}: {_post_args[_post_arg_name]!r}")
                    self._post_args[_post_arg_name] = ",".join(_post_args[_post_arg_name])
            HTTP_SERVER.debug("HttpRequest._post_args=%s", scenario.debug.jsondump(self._post_args, indent=2))

    @property
    def method(self):  # type: () -> Method
        """
        :return: HTTP method as an enum.

        .. note::
            The ``command`` property gives the same information as a string,
            but is not guaranteed to be safe regarding upper/lower case.
        """
        return HttpRequest.Method(self.command.upper())

    def getarg(
            self,
            name,  # type: str
            default=None,  # type: str
    ):  # type: (...) -> str
        """
        Returns the GET or POST argument of the given name.

        :param name: Argument name.
        :param default: Default value if no such argument. Optional.
        :return: Argument value, or default value if provided and argument not found.
        :raise KeyError: If argument not found and no default value provided.
        """
        if name in self._get_args:
            return self._get_args[name]
        if name in self._post_args:
            return self._post_args[name]
        if default is not None:
            return default
        raise KeyError(f"No such argument {name!r}")

    @property
    def campaign_execution(self):  # type: () -> typing.Optional[scenario.CampaignExecution]
        """
        Campaign execution corresponding to the campaign name if given in URL arguments.

        :return: Campaign execution corresponding to the name given in URL arguments if any, or ``None`` otherwise.
        """
        _campaign_name = self.getarg(HttpRequest.Arg.CAMPAIGN_NAME, default="")  # type: str
        if _campaign_name:
            return scenario.campaign_db.get(name=_campaign_name)
        return None

    @property
    def req_baseline(self):  # type: () -> scenario.ReqBaseline
        """
        Applicable requirement baseline for the given request.
        """
        from ._reqbl import UI_REQ_BASELINES

        if self.campaign_execution:
            UI_REQ_BASELINES.checkcampaignloaded(self.campaign_execution)
            return self.campaign_execution.req_baseline

        return UI_REQ_BASELINES.main

    def sendhtml(
            self,
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        """
        Responds the request successfully with HTML content.

        :param html: HTML content to send.
        """
        _content = html.dump()  # type: bytes
        self.content_size = len(_content)

        self.send_response(http.HTTPStatus.OK)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(self.content_size))
        self.end_headers()
        self.wfile.write(_content)

    def sendjson(
            self,
            data,  # type: scenario.types.JsonDict
    ):  # type: (...) -> None
        """
        Responds the request successfully with JSON content.

        :param data: JSON content to send.
        """
        _content = json.dumps(data).encode("utf-8")  # type: bytes
        self.content_size = len(_content)

        self.send_response(http.HTTPStatus.OK)
        self.send_header("Content-type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(self.content_size))
        self.end_headers()
        self.wfile.write(_content)

    def sendfile(
            self,
            path,  # type: scenario.Path
            *,
            mime_type=None,  # type: str
    ):  # type: (...) -> None
        """
        Responds the request successfully with file content.

        :param path: File to send the content.
        :param mime_type: Optional MIME type.
        """
        _content = path.read_bytes()  # type: bytes
        self.content_size = len(_content)

        self.send_response(http.HTTPStatus.OK)
        if mime_type:
            self.send_header("Content-Type", mime_type)
        self.send_header("Content-Length", str(self.content_size))
        self.end_headers()
        self.wfile.write(_content)

    def log_request(
            self,
            code=None,  # type: typing.Any
            size=None,  # type: typing.Any
    ):  # type: (...) -> None
        """
        Logs the request when done.

        ``http.server.BaseHTTPRequestHandler`` override.

        :param code: Return code.
        :param size: Unused parameter (inherited from ``http.server.BaseHTTPRequestHandler`` API). Replaced by :attr:`content_size`.
        """
        from ._httpserver import HTTP_SERVER

        if isinstance(code, http.HTTPStatus):
            code = f"{code.value} ({code.phrase})"

        _log_parts = [
            f"'{self.requestline}'",
            f"{code}",
        ]  # type: typing.List[str]
        if self.content_size is not None:
            _log_parts.append(f"{self.content_size} {'byte' if self.content_size == 1 else 'bytes'}")
        _log_parts.extend([
            f"{time.time() - self.start_time:.6f} seconds",
        ])
        HTTP_SERVER.info(", ".join(_log_parts))

    def log_error(
            self,
            format: str,  # noqa  ## Shadows built-in name 'format'.
            *args: typing.Any
    ) -> None:
        """
        ``http.server.BaseHTTPRequestHandler`` override to redirect to our log system.
        """
        from ._httpserver import HTTP_SERVER

        HTTP_SERVER.error(format, *args)

    def log_message(
            self,
            format: str,  # noqa  ## Shadows built-in name 'format'.
            *args: typing.Any,
    ) -> None:
        """
        ``http.server.BaseHTTPRequestHandler`` override to redirect to our log system.
        """
        from ._httpserver import HTTP_SERVER

        HTTP_SERVER.info(format, *args)

    @staticmethod
    def encodeurl(
            base_path,  # type: str
            *,
            args=None,  # type: typing.Optional[typing.Dict[str, str]]
            anchor=None,  # type: typing.Optional[str]
            html_escape=False,  # type: bool
    ):  # type: (...) -> str
        """
        Encodes an URL with GET arguments.

        :param base_path: Base path of the URL.
        :param args: GET arguments to encode.
        :param anchor: Optional anchor name.
        :param html_escape: ``True`` to get HTML escaped URL. ``False`` by default.
        :return: URL string.
        """
        from ._htmldoc import HtmlDocument

        _url = urllib.parse.quote(base_path)  # type: str
        if args:
            _url += f"?{urllib.parse.urlencode(args)}"
        if anchor:
            _url += f"#{urllib.parse.quote(anchor)}"
        if html_escape:
            _url = HtmlDocument.escape(_url)
        return _url
