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
Requirement class definition.
"""

import abc
import typing

if True:
    from ._fastpath import FAST_PATH as _FAST_PATH  # `FAST_PATH` imported once for performance concerns.
    from ._setutils import orderedset as _orderedset  # `orderedset()` imported once for performance concerns.
if typing.TYPE_CHECKING:
    from ._reqlink import ReqLink as _ReqLinkType
    from ._reqref import ReqRef as _ReqRefType
    from ._reqtypes import SetWithReqLinksType as _SetWithReqLinksType
    from ._reqverifier import ReqVerifier as _ReqVerifierType
    from ._scenariodefinition import ScenarioDefinition as _ScenarioDefinitionType
    from ._setutils import OrderedSetType as _OrderedSetType
    from ._textutils import AnyLongTextType as _AnyLongTextType


class Req:
    """
    Requirement class.
    """

    @staticmethod
    def orderedset(
            reqs,  # type: typing.Iterable[Req]
    ):  # type: (...) -> _OrderedSetType[Req]
        """
        Ensures an ordered set of unique :class:`Req` items.

        :param reqs: Unordered list of :class:`Req` items.
        :return: Ordered set of unique :class:`Req` items, ordered by requirement id.
        """
        return _orderedset(
            reqs,
            key=ReqHelper.sortkeyfunction,
        )

    def __init__(
            self,
            *,
            id,  # type: str  # noqa  ## Shadows built-in name 'id'
            title="",  # type: str
            text="",  # type: _AnyLongTextType
    ):  # type: (...) -> None
        """
        Initializes a requirement instance with the given input data,
        and a empty link set.

        Named parameters only.

        :param id: Identifier of the requirement.
        :param title: Short title for the requirement.
        :param text: Full text of the requirement.
        """
        from ._textutils import anylongtext2str

        #: Requirement identifier.
        #:
        #: Mandatory.
        self.id = id  # type: str

        #: Requirement short title.
        #:
        #: Optional.
        self.title = title  # type: str

        #: Requirement full text.
        #:
        #: Optional.
        self.text = anylongtext2str(text)  # type: str

    def __repr__(self):  # type: () -> str
        """
        Canonical string representation of the requirement instance.
        """
        from ._reflection import qualname

        return "".join([
            f"<{qualname(type(self))}",
            f" id={self.id!r}",
            f" title={self.title!r}" if self.title else "",
            f">",
        ])

    def __str__(self):  # type: () -> str
        """
        Human readable string representation of the requirement.

        Identifier, with short title if any.
        """
        return "".join([
            f"{self.id}",
            f": {self.title!r}" if self.title else "",
        ])

    def __hash__(self):  # type: (...) -> int
        """
        Ensures :class:`Req` objects are hashable, so that they can be used in sets.
        """
        return id(self)

    def __truediv__(
            self,
            sub,  # type: str
    ):  # type: (...) -> _ReqRefType
        """
        Gives a requirement sub-item reference.

        :param sub: Requirement sub-item specification.
        :return: :class:`._reqref.ReqRef` instance computed from the current :class:`Req` and the given requirement sub-item specification.
        """
        return _FAST_PATH.req_ref_cls(self, sub)

    @property
    def main_ref(self):  # type: () -> _ReqRefType
        """
        Reference to the main part of this requirement.
        """
        return _FAST_PATH.req_db.getreqref(self)

    @property
    def subrefs(self):  # type: () -> _OrderedSetType[_ReqRefType]
        """
        References to subparts of this requirement.

        See :meth:`._reqref.ReqRef.orderedset()` for order details.
        """
        return _FAST_PATH.req_ref_cls.orderedset(
            # Filter requirement references that point to subparts of this requirement.
            filter(
                lambda req_ref: (req_ref.req is self) and req_ref.issubref(),
                _FAST_PATH.req_db.getallrefs(),
            ),
        )

    def getreqlinks(
            self,
            req_verifier=None,  # type: _ReqVerifierType
            *,
            walk_subrefs=False,  # type: bool
            walk_steps=False,  # type: bool
    ):  # type: (...) -> _OrderedSetType[_ReqLinkType]
        """
        Requirement links attached with this requirement,
        filtered with the given predicates.

        :param req_verifier:
            Requirement verifier predicate to search links for.

            Optional.
            All requirement links when ``None``.
        :param walk_subrefs:
            Option to include requirement subreference links.

            If ``True``, links held by the requirement subreferences will be included in the result.

            ``False`` by default.

            .. tip::
                The links held by the main part only of the requirement
                can also be retrieved through the :attr:`._reqref.ReqRef.req_links` member of the :attr:`main_ref`.
        :param walk_steps:
            When ``req_verifier`` is a scenario,
            ``True`` makes the links match if they come from a step of the scenario.

            Ignored when ``req_verifier`` is not set.
        :return:
            Filtered set of requirement links (see :meth:`._reqlink.ReqLink.orderedset()` for order details).
        """
        from ._reqlink import ReqLink

        # Compute requirement references depending on `walk_subrefs`.
        _req_refs = [self.main_ref]  # type: typing.List[_ReqRefType]
        if walk_subrefs:
            _req_refs.extend(self.subrefs)

        # Walk through requirement references.
        _req_links = []  # type: typing.List[_ReqLinkType]
        for _req_ref in _req_refs:  # type: _ReqRefType
            # Filter links with the requirement predicates.
            _req_links.extend(filter(
                lambda req_link: req_link.matches(req_verifier=req_verifier, walk_steps=walk_steps),
                _req_ref.req_links,
            ))

        return ReqLink.orderedset(_req_links)

    def getverifiers(
            self,
            *,
            walk_subrefs=False,  # type: bool
    ):  # type: (...) -> _SetWithReqLinksType[_ReqVerifierType]
        """
        Returns verifiers linked with this requirement, with related links.

        :param walk_subrefs:
            Option to include requirement subreference verifiers.

            If ``True``, verifiers tracing subreferences of the requirement will be included in the result.

            ``False`` by default.

            .. tip::
                The verifiers tracing the main part only of the requirement
                can also be retrieved through the :meth:`._reqref.ReqRef.getverifiers()` method of the :attr:`main_ref`.
        :return:
            Requirement verifiers, with related links (see :meth:`._reqlink.ReqLink.orderedset()` for order details).

        Does not return :class:`._scenariodefinition.ScenarioDefinition` instances that track this requirement through steps only.
        See :meth:`getscenarios()` for the purpose.
        """
        from ._reqlink import ReqLinkHelper

        return ReqLinkHelper.buildsetwithreqlinks(
            # Determine the list of requirement references to walk through, depending on `walk_subrefs`.
            [self.main_ref] if not walk_subrefs else [self.main_ref, *self.subrefs],
            # Get requirement verifiers from each link.
            lambda req_link: req_link.req_verifiers,
        )

    def getscenarios(
            self,
            *,
            walk_subrefs=False,  # type: bool
    ):  # type: (...) -> _SetWithReqLinksType[_ScenarioDefinitionType]
        """
        Returns all scenarios linked with this requirement, with related links.

        :param walk_subrefs:
            Option to include requirement subreference scenarios.

            If ``True``, scenarios verifying subreferences of the requirement will be included in the result.

            ``False`` by default.

            .. tip::
                The scenarios verifying the main part only of the requirement
                can also be retrieved through the :meth:`._reqref.ReqRef.getscenarios()` method of the :attr:`main_ref`.
        :return:
            Scenario definitions, with related links (see :meth:`._reqlink.ReqLink.orderedset()` for order details).

        Returns scenarios linked with this requirement, either directly or through one of their steps.
        """
        from ._reqlink import ReqLinkHelper

        return ReqLinkHelper.buildsetwithreqlinks(
            # Determine the list of requirement references to walk through, depending on `walk_subrefs`.
            [self.main_ref] if not walk_subrefs else [self.main_ref, *self.subrefs],
            # Get scenarios from each link.
            lambda req_link: map(_FAST_PATH.req_verifier_helper_cls.getscenario, req_link.req_verifiers),
        )


class ReqHelper(abc.ABC):
    """
    Helper class for :class:`Req`.
    """

    @staticmethod
    def sortkeyfunction(
            req,  # type: Req
    ):  # type: (...) -> str
        """
        Key function used to sort :class:`Req` items.

        By requirement id.

        :param req: :class:`Req` item.
        :return: Requirement id.
        """
        return req.id
