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
Requirement reference:
either a requirement, or a requiremnt with a sub-item specification.
"""

import abc
import typing

if True:
    from ._fastpath import FAST_PATH as _FAST_PATH  # `FAST_PATH` imported once for performance concerns.
    from ._reflection import qualname as _qualname  # `qualname()` imported once for performance concerns.
    from ._setutils import orderedset as _orderedset  # `orderedset()` imported once for performance concerns.
if typing.TYPE_CHECKING:
    from ._req import Req as _ReqType
    from ._reqlink import ReqLink as _ReqLinkType
    from ._reqtypes import AnyReqRefType as _AnyReqRefType
    from ._reqtypes import AnyReqType as _AnyReqType
    from ._reqtypes import SetWithReqLinksType as _SetWithReqLinksType
    from ._reqverifier import ReqVerifier as _ReqVerifierType
    from ._scenariodefinition import ScenarioDefinition as _ScenarioDefinitionType
    from ._setutils import OrderedSetType as _OrderedSetType


class ReqRef:
    """
    Requirement reference class.

    Makes it possible to point at requirement sub-items.
    """

    @staticmethod
    def orderedset(
            req_refs,  # type: typing.Iterable[ReqRef]
    ):  # type: (...) -> _OrderedSetType[ReqRef]
        """
        Ensures an ordered set of unique :class:`ReqRef` items.

        :param req_refs: Unordered list of :class:`ReqRef` items.
        :return: Ordered set of unique :class:`ReqRef` items, ordered by requirement reference id.
        """
        return _orderedset(
            req_refs,
            key=ReqRefHelper.sortkeyfunction,
        )

    def __init__(
            self,
            req,  # type: _AnyReqType
            *subs,  # type: str
    ):  # type: (...) -> None
        """
        Initializes a requirement reference from the given requirement and optional sub-item specifications.

        :param req: Requirement to define a reference for.
        :param subs: Optional sub-item specifications.
        """
        #: Requirement this :class:`ReqRef` refers to.
        #:
        #: Unresolved input data for the :meth:`req()` property.
        self._any_req = req  # type: _AnyReqType

        #: Resolved requirement reference.
        self._req = None  # type: typing.Optional[_ReqType]

        #: Requirement sub-item specifications.
        #:
        #: Ordered sequence of keywords.
        #:
        #: If empty, the :class:`ReqRef` instance refers to the main part of the requirement.
        self.subs = subs  # type: typing.Sequence[str]

        #: Unordered links with requirement verifiers.
        self._req_links = set()  # type: typing.Set[_ReqLinkType]

    def __repr__(self):  # type: () -> str
        """
        Canonical string representation of the requirement reference.
        """
        return f"<{_qualname(type(self))} id={self.id!r}>"

    def __str__(self):  # type: () -> str
        """
        Human readable string representation of the requirement reference.
        """
        return self.id

    def __hash__(self):  # type: (...) -> int
        """
        Ensures :class:`ReqRef` objects are hashable, so that they can be used in sets.
        """
        return id(self)

    @property
    def id(self):  # type: () -> str
        """
        Requirement reference identifier.
        """
        return "/".join([
            # Don't sollicitate the requirement database if we already have a `Req` instance for `_any_req`.
            self._any_req.id if isinstance(self._any_req, _FAST_PATH.req_cls) else self.req.id,
            *self.subs,
        ])

    @property
    def req(self):  # type: () -> _ReqType
        """
        Requirement this :class:`ReqRef` refers to.

        Resolution of :attr:`_any_req`.
        Cached with :attr:`_req`.
        """
        if self._req is None:
            self._req = _FAST_PATH.req_db.getreq(self._any_req, push_unknown=True)
        return self._req

    @property
    def req_links(self):  # type: () -> _OrderedSetType[_ReqLinkType]
        """
        Links with requirement verifiers.

        See :meth:`._reqlink.ReqLink.orderedset()` for order details.
        """
        from ._reqlink import ReqLink

        return ReqLink.orderedset(self._req_links)

    def join(
            self,
            *subs,  # type: str
    ):  # type: (...) -> ReqRef
        """
        Adds sub-item specifications to the current requirement reference.

        :param subs: Additional requirement sub-item specifications.
        :return: New :class:`ReqRef` instance.
        """
        return ReqRef(
            self.req,
            *self.subs,
            *subs,
        )

    def __truediv__(
            self,
            sub,  # type: str
    ):  # type: (...) -> ReqRef
        """
        Shortcut for :meth:`join()`, with a single sub-item specification.
        """
        return self.join(sub)

    def ismain(self):  # type: (...) -> bool
        """
        Tells whether this requirement reference describes the main part of the requirement.

        :return: ``True`` for a main requirement reference, ``False`` otherwise.
        """
        return not self.subs

    def issubref(self):  # type: (...) -> bool
        """
        Tells whether this requirement reference describes a subpart of the requirement.

        :return: ``True`` for a reference to a subpart of the requirement, ``False`` otherwise.
        """
        return not not self.subs

    def matches(
            self,
            other,  # type: _AnyReqRefType
    ):  # type: (...) -> bool
        """
        Tells whether the given requirement reference matches another one.

        :param other: Other requirement reference.
        :return: ``True`` in case of a match, ``False`` otherwise.
        """
        if not isinstance(other, ReqRef):
            other = ReqRef(other)
        return (other.req is self.req) and (other.subs == self.subs)

    def __eq__(
            self,
            other,  # type: object
    ):  # type: (...) -> bool
        """
        Redirects to :meth:`matches()`.
        """
        if isinstance(other, (ReqRef, _FAST_PATH.req_cls, str)):
            return self.matches(other)
        else:
            raise TypeError(f"Can't compare {self!r} with {other!r}")

    def getreqlinks(
            self,
            req_verifier=None,  # type: _ReqVerifierType
            *,
            walk_steps=False,  # type: bool
    ):  # type: (...) -> _OrderedSetType[_ReqLinkType]
        """
        Requirement links attached with this requirement reference,
        filtered with the given predicates.

        :param req_verifier:
            Requirement verifier predicate to search links for.

            Optional.
            All requirement links when ``None``.
        :param walk_steps:
            When ``req_verifier`` is a scenario,
            ``True`` makes the links match if they come from a step of the scenario.

            Ignored when ``req_verifier`` is not set.
        :return:
            Filtered set of requirement links (see :meth:`._reqlink.ReqLink.orderedset()` for order details).
        """
        from ._reqlink import ReqLink

        return ReqLink.orderedset(
            # Filter links with the requirement predicates.
            filter(
                lambda req_link: req_link.matches(req_verifier=req_verifier, walk_steps=walk_steps),
                self._req_links,
            ),
        )

    def getverifiers(self):  # type: (...) -> _SetWithReqLinksType[_ReqVerifierType]
        """
        Returns all verifiers linked directly with this requirement reference.

        :return: Requirement verifiers, with related links (see :meth:`._reqlink.ReqLink.orderedset()` for order details).

        Does not return :class:`._scenariodefinition.ScenarioDefinition` instances that track this reference through steps only.
        See :meth:`getscenarios()` for the purpose.
        """
        from ._reqlink import ReqLinkHelper

        return ReqLinkHelper.buildsetwithreqlinks(
            # Walk requirement links from the current requirement reference.
            [self],
            # Get requirement verifiers from each link.
            lambda req_link: req_link.req_verifiers,
        )

    def getscenarios(self):  # type: (...) -> _SetWithReqLinksType[_ScenarioDefinitionType]
        """
        Returns all scenarios linked with this requirement reference.

        :return: Scenario definitions, with related links (see :meth:`._reqlink.ReqLink.orderedset()` for order details).

        Returns scenarios linked with this requirement reference, either directly or through one of their steps.
        """
        from ._reqlink import ReqLinkHelper

        return ReqLinkHelper.buildsetwithreqlinks(
            # Walk requirement links from the current requirement reference.
            [self],
            # Get scenarios from each link.
            lambda req_link: map(_FAST_PATH.req_verifier_helper_cls.getscenario, req_link.req_verifiers),
        )


class ReqRefHelper(abc.ABC):
    """
    Helper class for :class:`ReqRef`.
    """

    @staticmethod
    def sortkeyfunction(
            req,  # type: ReqRef
    ):  # type: (...) -> str
        """
        Key function used to sort :class:`ReqRef` items.

        By requirement reference id.

        :param req: :class:`ReqRef` item.
        :return: Requirement reference id.
        """
        return req.id
