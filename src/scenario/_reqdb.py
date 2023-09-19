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
    from ._setutils import OrderedSetType as _OrderedSetType


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

        _req_ref = obj if isinstance(obj, ReqRef) else ReqRef(obj)  # type: ReqRef
        # Ensure the `ReqRef._req` cache is set for `Req` registrations. Infinite cyclic calls otherwise.
        if isinstance(obj, Req):
            _req_ref._req = obj
        _req_key = _req_ref.id  # type: str
        _req_type = "requirement reference" if isinstance(obj, ReqRef) else "requirement"  # type: str
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
            *,
            push_unknown=False,  # type: bool
    ):  # type: (...) -> _ReqType
        """
        Retrieves the registered :class:`._req.Req` instance
        corresponding to the :obj:`._reqtypes.AnyReqType` description.

        :param req: Any requirement description.
        :param push_unknown: ``True`` to push the new :class:`._req.Req` instance if not already known.
        :return: Requirement instance registered in the database.
        """
        from ._req import Req

        # `Req` instance.
        if isinstance(req, Req):
            if push_unknown and (req.id not in self._req_db):
                self.push(req)
            return self.getreq(req.id)

        # Requirement as a string.
        elif isinstance(req, str):
            if req not in self._req_db:
                raise KeyError(f"Unknown requirement id {req!r}")
            return self._req_db[req].req

        raise ValueError(f"Invalid requirement {req!r}")

    def getreqref(
            self,
            req_ref,  # type: _AnyReqRefType
            *,
            push_unknown=False,  # type: bool
    ):  # type: (...) -> _ReqRefType
        """
        Retrieves the registered :class:`._reqref.ReqRef` instance
        corresponding to the :obj:`._reqtypes.AnyReqRefType` description.

        :param req_ref: Any requirement reference description.
        :param push_unknown: ``True`` to push a new :class:`._reqref.ReqRef` instance if not already known.
        :return: Requirement reference instance registered in the database.
        """
        from ._req import Req
        from ._reqref import ReqRef

        # `Req` or `ReqRef` instance.
        if isinstance(req_ref, (Req, ReqRef)):
            if push_unknown and (req_ref.id not in self._req_db):
                self.push(req_ref)
            return self.getreqref(req_ref.id)

        # Requirement reference as a string.
        elif isinstance(req_ref, str):
            if req_ref not in self._req_db:
                if push_unknown:
                    _req_id = req_ref.split("/")[0]  # type: str
                    self._req_db[req_ref] = ReqRef(self.getreq(_req_id), *req_ref.split("/")[1:])
                else:
                    raise KeyError(f"Unknown requirement reference {req_ref!r}")
            return self._req_db[req_ref]

        raise ValueError(f"Invalid requirement reference {req_ref!r}")

    def getallreqs(self):  # type: (...) -> _OrderedSetType[_ReqType]
        """
        Returns all requirements saved in the database.

        :return: :class:`._req.Req` ordered set (see :meth:`._req.Req.orderedset()` for order details).
        """
        from ._req import Req

        _reqs = Req.orderedset(
            map(
                # Convert `ReqRef` to `Req` objects.
                lambda req_ref: req_ref.req,
                # Filter-out sub requirement references from the database.
                filter(
                    lambda req_ref: not req_ref.subs,
                    self._req_db.values(),
                ),
            ),
        )  # type: _OrderedSetType[Req]

        self.debug("getallreqs() -> %r", _reqs)
        return _reqs

    def getallrefs(self):  # type: (...) -> _OrderedSetType[_ReqRefType]
        """
        Returns all requirement references saved in the database.

        :return: :class:`._reqref.ReqRef` ordered set (see :meth:`._reqref.ReqRef.orderedset()` for order details).
        """
        from ._reqref import ReqRef

        _req_refs = ReqRef.orderedset(
            # All requirement references in the database.
            self._req_db.values(),
        )  # type: _OrderedSetType[ReqRef]

        self.debug("getallrefs() -> %r", _req_refs)
        return _req_refs

    def getalllinks(self):  # type: () -> _OrderedSetType[_ReqLinkType]
        """
        Returns all requirement links saved in the database.

        :return: :class:`._reqlink.ReqLink` ordered set (see :meth:`._reqlink.ReqLink.orderedset()` for order details).
        """
        from ._reqlink import ReqLink

        _req_link_list = []  # type: typing.List[ReqLink]
        for _req_ref in self._req_db.values():  # type: _ReqRefType
            _req_link_list.extend(_req_ref.req_links)
        _req_links = ReqLink.orderedset(_req_link_list)  # type: _OrderedSetType[ReqLink]

        self.debug("getalllinks() -> %r", _req_links)
        return _req_links

    def getalltrackers(self):  # type: (...) -> _OrderedSetType[_ReqTrackerType]
        """
        Returns all final requirement trackers saved in the database,
        either scenarios or steps.

        :return: :class:`._reqtracker.ReqTracker` ordered set (see :meth:`._reqtracker.ReqTracker.orderedset()` for order details).
        """
        from ._reqtracker import ReqTracker

        _req_tracker_list = []  # type: typing.List[ReqTracker]
        for _req_ref in self._req_db.values():  # type: _ReqRefType
            for _req_link in _req_ref.req_links:  # type: _ReqLinkType
                _req_tracker_list.extend(_req_link.req_trackers)
        _req_trackers = ReqTracker.orderedset(_req_tracker_list)  # type: _OrderedSetType[ReqTracker]

        self.debug("getalltrackers() -> %r", _req_trackers)
        return _req_trackers

    def getallscenarios(self):  # type: (...) -> _OrderedSetType[_ScenarioDefinitionType]
        """
        Returns all scenarios that track requirements.

        Either directly, or through one of their steps.

        :return: :class:`._scenariodefinition.ScenarioDefinition` ordered set (see :meth:`._reqtracker.ReqTracker.orderedset()` for order details).
        """
        from ._reqtracker import ReqTrackerHelper
        from ._scenariodefinition import ScenarioDefinition

        _scenario_list = []  # type: typing.List[ScenarioDefinition]
        for _req_ref in self._req_db.values():  # type: _ReqRefType
            for _req_link in _req_ref.req_links:  # type: _ReqLinkType
                _scenario_list.extend(
                    # Convert `ReqTracker` to `ScenarioDefinition` objects.
                    map(
                        lambda req_tracker: ReqTrackerHelper.getscenario(req_tracker),
                        _req_link.req_trackers,
                    ),
                )
        _scenarios = ScenarioDefinition.orderedset(_scenario_list)  # type: _OrderedSetType[ScenarioDefinition]

        self.debug("getallscenarios() -> %r", _scenarios)
        return _scenarios


#: Main instance of :class:`ReqDatabase`.
REQ_DB = ReqDatabase()  # type: ReqDatabase
