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
Requirement database.
"""

import typing

if True:
    from ._logger import Logger as _LoggerImpl  # `Logger` used for inheritance.
if typing.TYPE_CHECKING:
    from ._reqlink import ReqLink as _ReqLinkType
    from ._reqtracker import ReqTracker as _ReqTrackerType
    from ._reqtypes import AnyReqIdType as _AnyReqIdType
    from ._scenariodefinition import ScenarioDefinition as _ScenarioDefinitionType


class ReqDatabase(_LoggerImpl):
    """
    Requirement database.

    Stores requirements and links with trackers (:meth:`push()`).

    Provides a couple of query methods:

    :all items:
        :meth:`allreqids()`, :meth:`alllinks()`, :meth:`alltrackers()`, :meth:`allscenarios()`.
    :requirements to trackers:
        :meth:`reqid2links()`, :meth:`reqid2trackers()`, :meth:`reqid2scenarios()`.
    :trackers to requirements:
        See :class:`._reqtracker.ReqTracker`.
    """

    def __init__(self):  # type: (...) -> None
        """
        Initializes a empty database.
        """
        from ._debugclasses import DebugClass

        _LoggerImpl.__init__(self, DebugClass.REQ_DATABASE)

        #: Database of requirement links, ordered requirements.
        self._req_ids = {}  # type: typing.Dict[_AnyReqIdType, typing.Set[_ReqLinkType]]

    def push(
            self,
            req_item,  # type: typing.Union[_AnyReqIdType, _ReqLinkType]
    ):  # type: (...) -> None
        """
        Feeds the database with requirement items.

        :param req_item: Either a requirement or a link.

        .. note::
            If ``req_item`` already exists in the database, it won't be duplicated.
        """
        from ._reqlink import ReqLink

        if not isinstance(req_item, ReqLink):
            _req_id = req_item  # type: _AnyReqIdType

            # Ensure a set of links exists for the requirement.
            if _req_id not in self._req_ids:
                self.debug("New requirement %s", _req_id)
                self._req_ids[_req_id] = set()

        else:
            _req_link = req_item  # type: ReqLink

            # Ensure the requirement exists in the database.
            self.push(_req_link.req_id)

            # Save the link if not known yet.
            if _req_link not in self._req_ids[_req_link.req_id]:
                self.debug("New link %s", _req_link)
                self._req_ids[_req_link.req_id].add(_req_link)

    def allreqids(self):  # type: (...) -> typing.Set[_AnyReqIdType]
        """
        Returns all requirement identifiers saved in the database.

        :return: Requirement identifiers.
        """
        return set(self._req_ids.keys())

    def alllinks(self):  # type: () -> typing.Set[_ReqLinkType]
        """
        Returns all requirement links saved in the database.

        :return: Requirement links.
        """
        _req_links = set()  # type: typing.Set[_ReqLinkType]
        for _req_id in self._req_ids:  # type: _AnyReqIdType
            _req_links.add(*self._req_ids[_req_id])
        return _req_links

    def alltrackers(self):  # type: (...) -> typing.Set[_ReqTrackerType]
        """
        Returns all final requirement trackers saved in the database,
        either scenarios or steps.

        :return: Requirement trackers.
        """
        _req_trackers = set()  # type: typing.Set[_ReqTrackerType]

        # Walk over requirement links.
        for _req_link in self.alllinks():  # type: _ReqLinkType
            _req_trackers.add(*_req_link.req_trackers)

        return _req_trackers

    def allscenarios(self):  # type: (...) -> typing.Set[_ScenarioDefinitionType]
        """
        Returns all scenarios that track requirements.

        Either directly, or through one of their steps.

        :return: Tracking scenarios.
        """
        from ._reqtracker import ReqTrackerHelper

        return set(map(
            lambda req_tracker: ReqTrackerHelper.getscenario(req_tracker),
            self.alltrackers(),
        ))

    def reqid2links(
            self,
            req_id,  # type: _AnyReqIdType
    ):  # type: (...) -> typing.Set[_ReqLinkType]
        """
        Returns all links that reference a given requirement.

        :param req_id: Searched requirement identifier.
        :return: Requirement links.
        """
        # Ensure the requirement exists in the database.
        self.push(req_id)

        return self._req_ids[req_id]

    def reqid2trackers(
            self,
            req_id,  # type: _AnyReqIdType
    ):  # type: (...) -> typing.Dict[_ReqTrackerType, typing.Set[_ReqLinkType]]
        """
        Returns all trackers that reference the given requirement.

        :param req_id: Searched requirement identifier.
        :return: Requirement trackers, with their related links.
        """
        _req_trackers = {}  # type: typing.Dict[_ReqTrackerType, typing.Set[_ReqLinkType]]

        # Ensure the requirement exists in the database.
        self.push(req_id)

        # Walk over requirement links for the given id.
        for _req_link in self._req_ids[req_id]:  # type: _ReqLinkType
            for _req_tracker in _req_link.req_trackers:  # type: _ReqTrackerType
                # Save requirement trackers with related links.
                if _req_tracker not in _req_trackers:
                    _req_trackers[_req_tracker] = set()
                _req_trackers[_req_tracker].add(_req_link)

        return _req_trackers

    def reqid2scenarios(
            self,
            req_id,  # type: _AnyReqIdType
    ):  # type: (...) -> typing.Dict[_ScenarioDefinitionType, typing.Set[_ReqLinkType]]
        """
        Returns all scenarios that reference a given requirement.

        Either directly, or through one of their steps.

        :param req_id: Searched requirement identifier.
        :return: Scenario definitions, with their related links.
        """
        from ._reqtracker import ReqTrackerHelper

        _scenarios = {}  # type: typing.Dict[_ScenarioDefinitionType, typing.Set[_ReqLinkType]]

        # Ensure the requirement exists in the database.
        self.push(req_id)

        # Walk over trackers for the given requirement id.
        for _req_tracker, _req_links in self.reqid2trackers(req_id).items():  # type: _ReqTrackerType, typing.Set[_ReqLinkType]
            # Find out the final scenario reference from the requirement tracker object.
            _scenario_definition = ReqTrackerHelper.getscenario(_req_tracker)  # type: _ScenarioDefinitionType

            # Save the scenario reference in the `_scenarios` dictionary, with related links.
            if _scenario_definition not in _scenarios:
                _scenarios[_scenario_definition] = set()
            _scenarios[_scenario_definition].add(*_req_links)

        return _scenarios


#: Main instance of :class:`ReqDatabase`.
REQ_DB = ReqDatabase()  # type: ReqDatabase
