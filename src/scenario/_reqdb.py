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
    from ._reqref import ReqRef as _ReqRefType
    from ._reqtracker import ReqTracker as _ReqTrackerType
    from ._reqtypes import AnyReqRefType as _AnyReqRefType
    from ._reqtypes import AnyReqType as _AnyReqType
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

        #: Database of requirement references, keyed by identifiers.
        self._req_db = {}  # type: typing.Dict[str, _ReqRefType]

    def push(
            self,
            obj,  # type: typing.Union[_ReqType, _ReqRefType]
    ):  # type: (...) -> None
        """
        Feeds the database with requirements.

        :param obj:
            Requirement or requirement reference to ensure registration for.

            Requirement references with empty sub-item specifications will be interpreted as the related requirement itself.

        .. note::
            If ``req`` already exists in the database, it won't be duplicated.
        """
        from ._req import Req
        from ._reqref import ReqRef

        if isinstance(obj, ReqRef) and (not obj.subs):
            self.debug("Empty sub-item specifications for %r, %r taken into account", obj, obj.req)
            obj = obj.req

        _req_ref = obj if isinstance(obj, ReqRef) else ReqRef(obj)  # type: ReqRef
        _req_key = _req_ref.id  # type: str
        _req_type = "requirement" if isinstance(obj, ReqRef) else "requirement reference"  # type: str
        if _req_key not in self._req_db:
            # Save and log the new requirement reference.
            self.debug("New %s %r", _req_type, obj)
            self._req_db[_req_key] = _req_ref
        else:
            # Check this is the requirement instance we already know.
            if obj is (self._req_db[_req_key].req if isinstance(obj, Req) else self._req_db[_req_key]):
                self.debug("%s already stored %r", _req_type.capitalize(), obj)
            else:
                raise ValueError(f"Duplicate {_req_type} {_req_key!r}: {obj!r} v/s {self._req_db[_req_key].req!r}")

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
        return self.getreqref(req).req

    def getreqref(
            self,
            req_ref,  # type: _AnyReqRefType
    ):  # type: (...) -> _ReqRefType
        """
        Retrieves the registered :class:`._reqref.ReqRef` instance
        corresponding to the :obj:`._reqtypes.AnyReqRefType` description.

        :param req_ref: Any requirement reference description.
        :return: Requirement reference instance registered in the database.
        """
        from ._req import Req
        from ._reqref import ReqRef

        # `Req` or `ReqRef` instance.
        if isinstance(req_ref, (Req, ReqRef)):
            return self.getreqref(req_ref.id)

        # Requirement reference as a string.
        elif isinstance(req_ref, str):
            if req_ref in self._req_db:
                return self._req_db[req_ref]
            else:
                raise KeyError(f"Unknown requirement reference {req_ref!r}")

        raise ValueError(f"Invalid requirement reference {req_ref!r}")

    def getallreqs(self):  # type: (...) -> typing.Set[_ReqType]
        """
        Returns all requirement identifiers saved in the database.

        :return: Requirements.
        """
        return set(map(
            lambda req_ref: req_ref.req,
            filter(
                lambda req_ref: not req_ref.subs,
                self._req_db.values(),
            ),
        ))

    def getallrefs(self):  # type: (...) -> typing.Set[_ReqRefType]
        """
        Returns all requirement references saved in the database.

        :return: Requirement references.
        """
        return set(self._req_db.values())

    def getalllinks(self):  # type: () -> typing.Set[_ReqLinkType]
        """
        Returns all requirement links saved in the database.

        :return: Requirement links.
        """
        _req_links = set()  # type: typing.Set[_ReqLinkType]
        for _req_ref in self.getallrefs():  # type: _ReqRefType
            _req_links.update(_req_ref.req_links)
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
