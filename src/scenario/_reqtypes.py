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
    from ._reqref import ReqRef as _ReqRefType
    from ._reqverifier import ReqVerifier as _ReqVerifierType
    from ._setutils import OrderedSetType as _OrderedSetType
    from ._textutils import AnyLongTextType as _AnyLongTextType
    from ._typingutils import VarItemType as _VarItemType


if typing.TYPE_CHECKING:
    #: Requirement definition type.
    #:
    #: Only requirement identifiers, as strings.
    ReqDefType = typing.Union[
        str,
    ]

    #: Any kind of requirement type:
    #:
    #: Either:
    #:
    #: - a :obj:`ReqDefType` definition.
    #: - a :class:`._req.Req` instance.
    AnyReqType = typing.Union[
        ReqDefType,
        _ReqType,
    ]

    #: Variable requirement verifier type.
    #:
    #: Useful to discriminate types of returned objects when calling class methods
    #: - with either :class:`._reqverifier.ReqVerifier`,
    #: - or :class:`._scenariodefinition.ScenarioDefinition` and :class:`._stepdefinition.StepDefinition` subclasses.
    VarReqVerifierType = typing.TypeVar("VarReqVerifierType", bound=_ReqVerifierType)

    #: Requirement reference definition type.
    #:
    #: Either:
    #:
    #: - a requirement identifier (string),
    #: - a requirement reference identifier (string as well),
    #: - a :class:`._req.Req` instance,
    ReqRefDefType = typing.Union[
        str,
        _ReqType,
    ]

    #: Any kind of requirement reference type.
    #:
    #: Either:
    #:
    #: - a :obj:`ReqRefDefType` definition,
    #: - a :class:`._reqref.ReqRef` instance.
    AnyReqRefType = typing.Union[
        ReqRefDefType,
        _ReqRefType,
    ]

    #: Requirement link definition.
    #:
    #: Either:
    #:
    #: - a requirement reference (see :obj:`AnyReqRefType`),
    #: - a tuple of requirement reference with optional comments.
    ReqLinkDefType = typing.Union[
        AnyReqRefType,
        typing.Tuple[AnyReqRefType],
        typing.Tuple[AnyReqRefType, _AnyLongTextType],
    ]

    #: Any kind of requirement link, either:
    #:
    #: - a :obj:`ReqLinkDefType` definition,
    #: - a full :class:`._reqlink.ReqLink` instance.
    AnyReqLinkType = typing.Union[
        ReqLinkDefType,
        _ReqLinkType,
    ]

    #: Set of items with related requirement links.
    #:
    #: See :meth:`._reqlink.ReqLink.orderedset()` for requirement link order details.
    SetWithReqLinksType = typing.Dict[_VarItemType, _OrderedSetType[_ReqLinkType]]
