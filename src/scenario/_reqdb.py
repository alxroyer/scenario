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
    from ._req import Req as _ReqType
    from ._reqlink import ReqLink as _ReqLinkType
    from ._reqtracker import ReqTracker as _ReqTrackerType
    from ._reqtypes import AnyReqType as _AnyReqType
    from ._reqtypes import ReqIdType as _ReqIdType
    from ._scenariodefinition import ScenarioDefinition as _ScenarioDefinitionType


class ReqDatabase(_LoggerImpl):
    """
    Requirement database.

    Stores requirements and links with trackers (:meth:`push()`).

    Provides a couple of query methods:

    :requirement access:
        :meth:`getreq()`.
    :all items:
        :meth:`getallreqs()`, :meth:`getalllinks()`, :meth:`getalltrackers()`, :meth:`getallscenarios()`.
    :requirements to trackers:
        See :class:`._req.Req`.
    :trackers to requirements:
        See :class:`._reqtracker.ReqTracker`.
    """

    def __init__(self):  # type: (...) -> None
        """
        Initializes a empty database.
        """
        from ._debugclasses import DebugClass

        _LoggerImpl.__init__(self, DebugClass.REQ_DATABASE)

        #: Database of requirements, keyed by requirement identifiers.
        self._req_db = {}  # type: typing.Dict[_ReqIdType, _ReqType]

    def push(
            self,
            req,  # type: _ReqType
    ):  # type: (...) -> None
        """
        Feeds the database with requirements.

        :param req: Requirement to ensure registration for.

        .. note::
            If ``req`` already exists in the database, it won't be duplicated.
        """
        if req.id not in self._req_db:
            # Save and log the new requirement.
            self.debug("New requirement %r", req)
            self._req_db[req.id] = req
        else:
            # Check `req` is the instance we already know.
            if req is self._req_db[req.id]:
                self.debug("Requirement already stored %s", req)
            else:
                raise ValueError(f"Duplicate requirement {req.id!r}: {req!r} v/s {self._req_db[req.id]!r}")

    def getreq(
            self,
            req,  # type: _AnyReqType
    ):  # type: (...) -> _ReqType
        """
        Retrieves the registered :class:`._req.Req` instance
        corresponding to the :obj:`._reqtypes.AnyReqType` description.

        :param req: Any requirement description.
        :return: Requirement instance registered in the database.
        """
        from ._req import Req

        # `Req` instance.
        if isinstance(req, Req):
            # Ensure the requirement object exist in the database.
            self.push(req)
            return req

        # Requirement id.
        elif isinstance(req, _ReqIdType):
            if req in self._req_db:
                return self._req_db[req]
            else:
                raise KeyError(f"Unknown requirement identifier {req!r}")

        raise ValueError(f"Invalid requirement {req!r}")

    def getallreqs(self):  # type: (...) -> typing.Set[_ReqType]
        """
        Returns all requirement identifiers saved in the database.

        :return: Requirement identifiers.
        """
        return set(self._req_db.values())

    def getalllinks(self):  # type: () -> typing.Set[_ReqLinkType]
        """
        Returns all requirement links saved in the database.

        :return: Requirement links.
        """
        _req_links = set()  # type: typing.Set[_ReqLinkType]
        for _req in self.getallreqs():  # type: _ReqType
            _req_links.update(_req.req_links)
        return _req_links

    def getalltrackers(self):  # type: (...) -> typing.Set[_ReqTrackerType]
        """
        Returns all final requirement trackers saved in the database,
        either scenarios or steps.

        :return: Requirement trackers.
        """
        _req_trackers = set()  # type: typing.Set[_ReqTrackerType]

        # Walk over requirement links.
        for _req_link in self.getalllinks():  # type: _ReqLinkType
            _req_trackers.update(_req_link.req_trackers)

        return _req_trackers

    def getallscenarios(self):  # type: (...) -> typing.Set[_ScenarioDefinitionType]
        """
        Returns all scenarios that track requirements.

        Either directly, or through one of their steps.

        :return: Tracking scenarios.
        """
        from ._reqtracker import ReqTrackerHelper

        return set(map(
            lambda req_tracker: ReqTrackerHelper.getscenario(req_tracker),
            self.getalltrackers(),
        ))


#: Main instance of :class:`ReqDatabase`.
REQ_DB = ReqDatabase()  # type: ReqDatabase
