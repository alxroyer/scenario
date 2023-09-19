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

if typing.TYPE_CHECKING:
    from ._req import Req as _ReqType
    from ._reqlink import ReqLink as _ReqLinkType
    from ._reqtracker import ReqTracker as _ReqTrackerType
    from ._reqtypes import AnyReqRefType as _AnyReqRefType
    from ._reqtypes import AnyReqType as _AnyReqType
    from ._reqtypes import SetWithReqLinksType as _SetWithReqLinksType
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
        from ._setutils import orderedset

        return orderedset(
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

        #: Unordered links with requirement trackers.
        self._req_links = set()  # type: typing.Set[_ReqLinkType]

    def __repr__(self):  # type: () -> str
        """
        Canonical string representation of the requirement reference.
        """
        from ._reflection import qualname

        return f"<{qualname(type(self))} id={self.id!r}>"

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
        from ._req import Req

        return "/".join([
            # Don't sollicitate the requirement database if we already have a `Req` instance for `_any_req`.
            self._any_req.id if isinstance(self._any_req, Req) else self.req.id,
            *self.subs,
        ])

    @property
    def req(self):  # type: () -> _ReqType
        """
        Requirement this :class:`ReqRef` refers to.

        Resolution of :attr:`_any_req`.
        Cached with :attr:`_req`.
        """
        from ._reqdb import REQ_DB

        if self._req is None:
            self._req = REQ_DB.getreq(self._any_req, push_unknown=True)
        return self._req

    @property
    def req_links(self):  # type: () -> _OrderedSetType[_ReqLinkType]
        """
        Links with requirement trackers.

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
        from ._req import Req

        if isinstance(other, (ReqRef, Req, str)):
            return self.matches(other)
        else:
            raise TypeError(f"Can't compare {self!r} with {other!r}")

    def gettrackers(self):  # type: (...) -> _SetWithReqLinksType[_ReqTrackerType]
        """
        Returns all trackers linked directly with this requirement reference.

        :return: Requirement trackers, with related links (see :meth:`._reqlink.ReqLink.orderedset()` for order details).

        Does not return :class:`._scenariodefinition.ScenarioDefinition` instances that track this reference through steps only.
        See :meth:`getscenarios()` for the purpose.
        """
        from ._reqlink import ReqLinkHelper

        return ReqLinkHelper.buildsetwithreqlinks(
            # Walk requirement links from the current requirement reference.
            [self],
            # Get requirement trackers from each link.
            lambda req_link: req_link.req_trackers,
        )

    def getscenarios(self):  # type: (...) -> _SetWithReqLinksType[_ScenarioDefinitionType]
        """
        Returns all scenarios linked with this requirement reference.

        :return: Scenario definitions, with related links (see :meth:`._reqlink.ReqLink.orderedset()` for order details).

        Returns scenarios linked with this requirement reference, either directly or through one of their steps.
        """
        from ._reqlink import ReqLinkHelper
        from ._reqtracker import ReqTrackerHelper

        return ReqLinkHelper.buildsetwithreqlinks(
            # Walk requirement links from the current requirement reference.
            [self],
            # Get scenarios from each link.
            lambda req_link: map(ReqTrackerHelper.getscenario, req_link.req_trackers),
        )

    def getreqlinks(
            self,
            req_tracker=None,  # type: _ReqTrackerType
            *,
            walk_steps=False,  # type: bool
    ):  # type: (...) -> _OrderedSetType[_ReqLinkType]
        """
        Requirement links attached with this requirement reference,
        filtered with the given predicates.

        :param req_tracker:
            Requirement tracker predicate to search links for.

            Optional.
            All requirement links when ``None``.
        :param walk_steps:
            When ``req_tracker`` is a scenario,
            ``True`` makes the link match if it comes from a step of the scenario.
        :return:
            Filtered set of requirement links (see :meth:`._reqlink.ReqLink.orderedset()` for order details).
        """
        from ._reqlink import ReqLink

        return ReqLink.orderedset(
            # Filter links with the requirement predicates.
            filter(
                lambda req_link: req_link.matches(req_tracker=req_tracker, walk_steps=walk_steps),
                self._req_links,
            ),
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
