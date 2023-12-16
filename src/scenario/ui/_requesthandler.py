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

if typing.TYPE_CHECKING:
    from ._htmldoc import HtmlDocument as _HtmlDocumentType
    from ._httprequest import HttpRequest as _HttpRequestType


class RequestHandler(abc.ABC):
    """
    Request handler base class.

    Usually a HTML page generator.
    """

    @abc.abstractmethod
    def matches(
            self,
            request,  # type: _HttpRequestType
    ):  # type: (...) -> bool
        """
        States whether this handler can process the given request.

        :param request: Input request to process.
        :return: ``True`` if the request can been processed, ``False`` if not.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def process(
            self,
            request,  # type: _HttpRequestType
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        """
        Request handling abstract method.

        :param request: Input request to process.
        :param html: HTML output page to feed.
        """
        raise NotImplementedError()
