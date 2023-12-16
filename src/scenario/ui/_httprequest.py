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
import typing
import urllib.parse

if True:
    from .._enumutils import StrEnum as _StrEnumImpl  # `StrEnum` used for inheritance.


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

    class Method(_StrEnumImpl):
        """
        HTTP methods as an enum.
        """
        #: GET method.
        GET = "GET"
        #: POST method.
        POST = "POST"

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

    def __repr__(self):  # type: () -> str
        """
        Canonical string representation of the request.
        """
        return f"<HttpRequest {self.requestline!r}>"

    def do_GET(self):  # type: (...) -> None  # noqa  ## Function name should be lowercase
        """
        GET request processing.

        Automatically called by the ``http.server`` library.
        Let's redirect to our ``REQ_HTTP_SERVER`` singleton instance.
        """
        from ._httpserver import HTTP_SERVER

        try:
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
        from .._debugutils import jsondump
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
            HTTP_SERVER.debug("HttpRequest._get_args=%s", jsondump(self._get_args, indent=2))

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
            HTTP_SERVER.debug("HttpRequest._post_args=%s", jsondump(self._post_args, indent=2))

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

    def log_error(
            self,
            format: str,  # noqa  ## Shadows built-in name 'format'.
            *args: typing.Any
    ) -> None:
        """
        ``http.server.BaseHTTPRequestHandler`` overload to redirect to our log system.
        """
        from ._httpserver import HTTP_SERVER

        HTTP_SERVER.error(format, *args)

    def log_message(
            self,
            format: str,  # noqa  ## Shadows built-in name 'format'.
            *args: typing.Any,
    ) -> None:
        """
        ``http.server.BaseHTTPRequestHandler`` overload to redirect to our log system.
        """
        from ._httpserver import HTTP_SERVER

        HTTP_SERVER.info(format, *args)
