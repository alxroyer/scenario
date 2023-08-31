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

import typing

if typing.TYPE_CHECKING:
    from ._req import Req as _ReqType
    from ._reqlink import ReqLink as _ReqLinkType
    from ._reqlink import SetWithReqLinksType as _SetWithReqLinksType
    from ._reqtracker import ReqTracker as _ReqTrackerType
    from ._reqtypes import AnyReqRefType as _AnyReqRefType
    from ._reqtypes import AnyReqType as _AnyReqType
    from ._scenariodefinition import ScenarioDefinition as _ScenarioDefinitionType
    from ._setutils import OrderedSetType as _OrderedSetType


class ReqRef:
    """
    Requirement reference class.

    Makes it possible to point at requirement sub-items.
    """

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
        Links with requirement trackers, ordered by requirement reference ids.
        """
        from ._reqlink import ReqLinkHelper
        from ._setutils import OrderedSetHelper

        return OrderedSetHelper.build(
            self._req_links,
            # Sort by requirement reference ids.
            key=ReqLinkHelper.key,
        )

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

        :return: Requirement trackers, with their related links (ordered by their requirement reference ids).

        For :class:`._scenariodefinition.ScenarioDefinition` instances,
        the scenario won't be returned if it is not linked with the requirement reference directly,
        but only through one of its steps.
        See :meth:`getscenarios()` for the purpose.
        """
        from ._reqlink import ReqLinkHelper

        _req_trackers = {}  # type: _SetWithReqLinksType[_ReqTrackerType]

        # Walk through requirement links.
        for _req_link in self.req_links:  # type: _ReqLinkType
            # For each direct tracker.
            for _req_tracker in _req_link.req_trackers:  # type: _ReqTrackerType
                # Save the tracker with the related link.
                ReqLinkHelper.updatesetwithreqlinks(_req_trackers, _req_tracker, [_req_link])

        return _req_trackers

    def getscenarios(self):  # type: (...) -> _SetWithReqLinksType[_ScenarioDefinitionType]
        """
        Returns all scenarios linked with this requirement reference.

        :return: Scenario definitions, with their related links (ordered by their requirement reference ids).

        Returns scenarios linked with this requirement reference, either directly or through one of their steps.
        """
        from ._reqlink import ReqLinkHelper
        from ._reqtracker import ReqTrackerHelper

        _scenario_definitions = {}  # type: _SetWithReqLinksType[_ScenarioDefinitionType]

        # Walk through direct requirement trackers.
        for _req_tracker, _req_links in self.gettrackers().items():  # type: _ReqTrackerType, _OrderedSetType[_ReqLinkType]
            # Find out the final scenario reference from the direct requirement tracker.
            _scenario_definition = ReqTrackerHelper.getscenario(_req_tracker)  # type: _ScenarioDefinitionType

            # Save the scenario reference with the related links.
            ReqLinkHelper.updatesetwithreqlinks(_scenario_definitions, _scenario_definition, _req_links)

        return _scenario_definitions
