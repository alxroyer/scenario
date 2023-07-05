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
Requirement trackers.
"""

import abc
import typing

if typing.TYPE_CHECKING:
    from ._reqlink import ReqLink as _ReqLinkType
    from ._reqtypes import AnyReqIdType as _AnyReqIdType
    from ._reqtypes import AnyReqLinkType as _AnyReqLinkType
    from ._reqtypes import VarReqTrackerType as _VarReqTrackerType
    from ._scenariodefinition import ScenarioDefinition as _ScenarioDefinitionType


class ReqTracker(abc.ABC):
    """
    Requirement tracker objects.

    Actually, only :class:`._scenariodefinition.ScenarioDefinition` and :class:`._stepdefinition.StepDefinition`
    may subclass this :class:`ReqTracker` abstract class.
    """

    def __init__(self):  # type: (...) -> None
        """
        Initializes requirement tracking members.

        Checks that only :class:`._scenariodefinition.ScenarioDefinition` and :class:`._stepdefinition.StepDefinition`
        inherit from :class:`ReqTracker`.
        """
        from ._scenariodefinition import ScenarioDefinition
        from ._stepdefinition import StepDefinition

        if not any([
            isinstance(self, ScenarioDefinition),
            isinstance(self, StepDefinition),
        ]):
            raise TypeError(f"Cannot subclass ReqTracker if not a scenario nor step definition")

        #: Links to tracked requirements.
        self._req_links = set()  # type: typing.Set[_ReqLinkType]

    def covers(
            self,  # type: _VarReqTrackerType
            *req_links,  # type: typing.Union[_AnyReqLinkType, typing.Set[_ReqLinkType]]
    ):  # type: (...) -> _VarReqTrackerType
        """
        Declares requirement coverage from this tracker object.

        :param req_links: Requirement links declared. May be the result of :meth:`reqlinks()`.
        :return: ``self``
        """
        from ._reqdb import REQ_DB
        from ._reqlink import ReqLink

        # Try to save each link.
        for _req_links in req_links:  # type: typing.Union[_AnyReqLinkType, typing.Set[_ReqLinkType]]
            # Ensure we consider a set of links for the second loop below.
            if not isinstance(_req_links, set):
                _req_links = {_req_links if isinstance(_req_links, ReqLink) else ReqLink(_req_links)}

            for _req_link in _req_links:  # type: _AnyReqLinkType
                # Ensure we have a `ReqLink` object.
                if not isinstance(_req_link, ReqLink):
                    _req_link = ReqLink(_req_link)

                if _req_link not in self._req_links:
                    # New link.
                    self._req_links.add(_req_link)

                    # Link <-> tracker cross-reference.
                    _req_link.coveredby(self)

                # Push the link to the requirement database.
                REQ_DB.push(_req_link)

        return self

    @property
    def req_ids(self):  # type: (...) -> typing.Set[_AnyReqIdType]
        """
        Requirements tracked by this tracker.
        """
        return set([_req_link.req_id for _req_link in self._req_links])

    @property
    def req_links(self):  # type: (...) -> typing.Set[_ReqLinkType]
        """
        Requirement links attached with this tracker.
        """
        return self._req_links

    def reqlinks(
            self,
            req_id,  # type: _AnyReqIdType
            sub_req_item=None,  # type: str
    ):  # type: (...) -> typing.Set[_ReqLinkType]
        """
        Requirement links attached with this tracker, for the given requirement reference.

        :param req_id: Requirement identifier to search links for.
        :param sub_req_item: Sub-requirement item that specifies a particular point in the requirement.
        :return: Set of requirement links.
        """
        return set(filter(
            lambda req_link: req_link.matches(req_id, sub_req_item),
            self._req_links,
        ))


class ReqTrackerHelper:
    """
    Helper class for :class:`ReqTracker`.
    """

    @staticmethod
    def getscenario(
            req_tracker,  # type: ReqTracker
    ):  # type: (...) -> _ScenarioDefinitionType
        """
        Retrieves the :class:`._scenariodefinition.ScenarioDefinition` instance from a :class:`ReqTracker`.

        :param req_tracker: Scenario or step definition as a :class:`ReqTracker` instance.
        :return: Scenario definition.
        """
        from ._scenariodefinition import ScenarioDefinition
        from ._stepdefinition import StepDefinition

        if isinstance(req_tracker, ScenarioDefinition):
            return req_tracker
        if isinstance(req_tracker, StepDefinition):
            return req_tracker.scenario
        raise TypeError(f"Unexpected requirement tracker type {req_tracker!r}")
