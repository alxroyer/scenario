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
User interface file handler.
"""

import typing

import scenario

if True:
    from ._httprequesthandler import HttpRequestHandler as _HttpRequestHandlerImpl  # @inheritance
if typing.TYPE_CHECKING:
    from ._httprequest import HttpRequest as _HttpRequestType


class FileDelivery(_HttpRequestHandlerImpl):
    """
    File delivery request handler.

    Delivers requested existing files.
    """

    def __init__(self):  # type: (...) -> None
        """
        Configures the logger instance.
        """
        from ._debugclasses import UIDebugClass

        _HttpRequestHandlerImpl.__init__(self, UIDebugClass.FILE_DELIVERY)

    def process(
            self,
            request,  # type: _HttpRequestType
    ):  # type: (...) -> bool
        from ._httpserver import HTTP_SERVER

        # Filter `request`.
        if not request.base_path.startswith("/"):
            self.debug("Unexpected base path %r", request.base_path)
            self.debug("%r not processed", request)
            return False

        # Read the file.
        _file = HTTP_SERVER.main_path / request.base_path[1:]  # type: scenario.Path
        if not _file.is_file():
            self.debug("No such file '%s'", _file)
            self.debug("%r not processed", request)
            return False
        self.debug("Processing %r", request)

        # Deliver the file.
        self.debug("Delivering file '%s'", _file)
        request.sendfile(_file)
        return True
