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
Request management.
"""

import abc
import typing

import scenario

if typing.TYPE_CHECKING:
    from ._debugclasses import UIDebugClass as _UIDebugClassType
    from ._httprequest import HttpRequest as _HttpRequestType


class HttpRequestHandler(abc.ABC, scenario.Logger):
    """
    HTTP request handler base class.

    Usually a HTML page generator.
    """

    def __init__(
            self,
            debug_class,  # type: _UIDebugClassType
    ):  # type: (...) -> None
        """
        Configures the logger instance.

        :param debug_class: Debug class for this request handler.
        """
        scenario.Logger.__init__(self, debug_class)

    @abc.abstractmethod
    def process(
            self,
            request,  # type: _HttpRequestType
    ):  # type: (...) -> bool
        """
        Request handling abstract method.

        :param request:
            Input request to process.
        :return:
            ``False`` if this handler does not accept the given request.
            ``True`` if the request has been successfully processed.
        :raise:
            When this handler accepted the request, but an error occurred.
        """
        raise NotImplementedError()
