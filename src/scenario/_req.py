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

import typing

if typing.TYPE_CHECKING:
    from ._reqlink import ReqLink as _ReqLinkType
    from ._reqtracker import ReqTracker as _ReqTrackerType
    from ._reqtypes import ReqIdType as _ReqIdType
    from ._scenariodefinition import ScenarioDefinition as _ScenarioDefinitionType


class Req:
    """
    Requirement class.
    """

    def __init__(
            self,
            *,
            id,  # type: _ReqIdType  # noqa  ## Shadows built-in name 'id'
            title="",  # type: str
            text="",  # type: str
    ):  # type: (...) -> None
        """
        Initializes a requirement instance with the given input data,
        and a empty link set.

        Named parameters only.

        :param id: Identifier of the requirement.
        :param title: Short title for the requirement.
        :param text: Full text of the requirement.
        """
        #: Requirement identifier.
        #:
        #: Mandatory.
        self.id = id  # type: _ReqIdType

        #: Requirement short title.
        #:
        #: Optional.
        self.title = title  # type: str

        #: Requirement full text.
        #:
        #: Optional.
        self.text = text  # type: str

        #: Links with requirement trackers.
        self.req_links = set()  # type: typing.Set[_ReqLinkType]

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

    def gettrackers(
            self,
    ):  # type: (...) -> typing.Dict[_ReqTrackerType, typing.Set[_ReqLinkType]]
        """
        Returns all trackers that reference directly this requirement.

        :return: Requirement trackers, with their related links.
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
        Returns all scenarios that reference this requirement.

        Either directly, or through one of their steps.

        :return: Scenario definitions, with their related links.
        """
        from ._reqtracker import ReqTrackerHelper

        _scenarios = {}  # type: typing.Dict[_ScenarioDefinitionType, typing.Set[_ReqLinkType]]

        # Walk through direct requirement trackers.
        for _req_tracker, _req_links in self.gettrackers().items():  # type: _ReqTrackerType, typing.Set[_ReqLinkType]
            # Find out the final scenario reference from the direct requirement tracker.
            _scenario_definition = ReqTrackerHelper.getscenario(_req_tracker)  # type: _ScenarioDefinitionType

            # Save the scenario reference with the related link.
            if _scenario_definition not in _scenarios:
                _scenarios[_scenario_definition] = set()
            _scenarios[_scenario_definition].update(_req_links)

        return _scenarios
