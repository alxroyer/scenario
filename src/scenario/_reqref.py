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
    from ._reqtracker import ReqTracker as _ReqTrackerType
    from ._reqtypes import AnyReqRefType as _AnyReqRefType
    from ._reqtypes import AnyReqType as _AnyReqType
    from ._scenariodefinition import ScenarioDefinition as _ScenarioDefinitionType


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
        from ._req import Req
        from ._reqdb import REQ_DB

        #: Requirement this :class:`ReqRef` refers to.
        self.req = (
            # Note:
            #  In order to avoid logging before the logging system is ready,
            #  don't sollicitate the requirement database if we already have a `Req` instance.
            req if isinstance(req, Req)
            else REQ_DB.getreq(req)
        )  # type: _ReqType

        #: Requirement sub-item specifications.
        #:
        #: Ordered sequence of keywords.
        #:
        #: If empty, the :class:`ReqRef` instance refers to the main part of the requirement.
        self.subs = subs  # type: typing.Sequence[str]

        #: Links with requirement trackers.
        self.req_links = set()  # type: typing.Set[_ReqLinkType]

    def __repr__(self):  # type: () -> str
        """
        Canonical string representation of the requirement reference.
        """
        from ._reflection import qualname

        return "".join([
            f"<{qualname(type(self))}",
            f" req.id={self.req.id!r}",
            f" subs={self.subs!r}",
            ">",
        ])

    def __str__(self):  # type: () -> str
        """
        Human readable string representation of the requirement reference.
        """
        return self.id

    @property
    def id(self):  # type: () -> str
        """
        Requirement reference identifier.
        """
        return "/".join([
            self.req.id,
            *self.subs,
        ])

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

    def gettrackers(
            self,
    ):  # type: (...) -> typing.Dict[_ReqTrackerType, typing.Set[_ReqLinkType]]
        """
        Returns all trackers linked with directly this requirement reference.

        :return: Requirement trackers, with their related links.

        For :class:`._scenariodefinition.ScenarioDefinition` instances,
        the scenario won't be returned if it is not linked with the requirement reference directly,
        but only through one of its steps.
        See :meth:`getscenarios()` for the purpose.
        """
        _req_trackers = {}  # type: typing.Dict[_ReqTrackerType, typing.Set[_ReqLinkType]]

        # Walk through requirement links.
        for _req_link in self.req_links:  # type: _ReqLinkType
            # For each direct tracker.
            for _req_tracker in _req_link.req_trackers:  # type: _ReqTrackerType
                # Save the tracker with the related link.
                if _req_tracker not in _req_trackers:
                    _req_trackers[_req_tracker] = set()
                _req_trackers[_req_tracker].add(_req_link)

        return _req_trackers

    def getscenarios(
            self,
    ):  # type: (...) -> typing.Dict[_ScenarioDefinitionType, typing.Set[_ReqLinkType]]
        """
        Returns all scenarios linked with this requirement reference.

        :return: Scenario definitions, with their related links.

        Returns scenarios linked with this requirement reference, either directly or through one of their steps.
        """
        from ._reqtracker import ReqTrackerHelper

        _scenario_definitions = {}  # type: typing.Dict[_ScenarioDefinitionType, typing.Set[_ReqLinkType]]

        # Walk through direct requirement trackers.
        for _req_tracker, _req_links in self.gettrackers().items():  # type: _ReqTrackerType, typing.Set[_ReqLinkType]
            # Find out the final scenario reference from the direct requirement tracker.
            _scenario_definition = ReqTrackerHelper.getscenario(_req_tracker)  # type: _ScenarioDefinitionType

            # Save the scenario reference with the related link.
            if _scenario_definition not in _scenario_definitions:
                _scenario_definitions[_scenario_definition] = set()
            _scenario_definitions[_scenario_definition].update(_req_links)

        return _scenario_definitions
