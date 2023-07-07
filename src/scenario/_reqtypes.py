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
Requirement types.

Defined in a separate module in order to avoid cyclic dependencies with ``typing.TYPE_CHECKING`` set to ``True``.
"""

import typing

if typing.TYPE_CHECKING:
    from ._req import Req as _ReqType
    from ._reqlink import ReqLink as _ReqLinkType
    from ._reqtracker import ReqTracker as _ReqTrackerType


if typing.TYPE_CHECKING:
    #: Requirement identifier type.
    ReqIdType = str

    #: Any kind of requirement type, either:
    #:
    #: - a requirement identifier,
    #: - a full :class:`._req.Req` instance.
    AnyReqType = typing.Union[
        ReqIdType,
        _ReqType,
    ]

    #: Variable requirement tracker type.
    VarReqTrackerType = typing.TypeVar("VarReqTrackerType", bound=_ReqTrackerType)

    #: Any kind of requirement link, either:
    #:
    #: - a requirement (instance or identifier),
    #: - a full :class:`._reqlink.ReqLink` instance.
    AnyReqLinkType = typing.Union[
        AnyReqType,
        _ReqLinkType,
    ]
