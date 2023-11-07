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
    from ._jsondictutils import JsonDictType as _JsonDictType
    from ._path import Path as _PathType
    from ._req import Req as _ReqType
    from ._reqlink import ReqLink as _ReqLinkType
    from ._reqref import ReqRef as _ReqRefType
    from ._reqtypes import AnyReqRefType as _AnyReqRefType
    from ._reqtypes import AnyReqType as _AnyReqType
    from ._reqverifier import ReqVerifier as _ReqVerifierType
    from ._scenariodefinition import ScenarioDefinition as _ScenarioDefinitionType
    from ._setutils import OrderedSetType as _OrderedSetType


class ReqDatabase(_LoggerImpl):
    """
    Requirement database.

    Instantiated once with the :data:`REQ_DB` singleton.

    Stores requirements and links with verifiers (:meth:`push()`).

    Provides a couple of query methods:

    :requirement access:
        :meth:`getreq()`.
    :all items:
        :meth:`getallreqs()`, :meth:`getalllinks()`, :meth:`getallverifiers()`, :meth:`getallscenarios()`.
    :requirements to verifiers:
        See :class:`._req.Req`.
    :verifiers to requirements:
        See :class:`._reqverifier.ReqVerifier`.
    """

    #: JSON schema subpath from :attr:`._pkginfo.PackageInfo.repo_url`, for requirement database files.
    JSON_SCHEMA_SUBPATH = "schema/reqdb.schema.json"  # type: str

    def __init__(self):  # type: (...) -> None
        """
        Initializes a empty database.
        """
        from ._debugclasses import DebugClass

        _LoggerImpl.__init__(self, DebugClass.REQ_DATABASE)

        #: Database of requirement references, keyed by identifiers.
        self._req_db = {}  # type: typing.Dict[str, _ReqRefType]

    def clear(self):  # type: (...) -> None
        """
        Clears the database.

        Removes all requirement, requirement references with links and related verifiers.
        """
        self._req_db.clear()

    def load(
            self,
            reqdb_file,  # type: _PathType
    ):  # type: (...) -> None
        """
        Load requirements from a JSON file.

        :param reqdb_file: JSON file to read.
        """
        from ._jsondictutils import JsonDict
        from ._req import Req
        from ._reqref import ReqRef

        # Read the JSON file.
        self.debug("Reading '%s'", reqdb_file)
        _reqdb_json = JsonDict.readfile(reqdb_file)  # type: _JsonDictType

        # Feed the database from the JSON content.
        for _key in _reqdb_json:  # type: str
            if _key.startswith("$"):
                continue
            _req_id = _key  # type: str

            _req_json = _reqdb_json[_req_id]  # type: _JsonDictType

            # Check requirement id redundancy in the input file.
            if _req_id != _req_json["id"]:
                self.warning(
                    f"{reqdb_file}: Requirement id mismatch: {_req_id!r} (JSON key) != {_req_json['id']!r} (\"id\" field), "
                    f"keeping {_req_json['id']!r}"
                )

            _req = self.push(Req(
                id=_req_json["id"],
                title=_req_json["title"],
                text=_req_json["text"],
            ))  # type: Req

            for _reqref_id in _req_json["sub-refs"]:  # type: str
                self.push(ReqRef(
                    _req,
                    *_reqref_id.split("/")[1:],
                ))

    def dump(
            self,
            reqdb_file,  # type: _PathType
    ):  # type: (...) -> None
        """
        Dump the requirement database to a JSON file.

        :param reqdb_file: JSON file to write.
        """
        from ._jsondictutils import JsonDict

        # Build JSON content from requirement information stored in the database.
        _reqdb_json = {}  # type: _JsonDictType

        for _req in self.getallreqs():  # type: _ReqType
            _reqdb_json[_req.id] = {
                "id": _req.id,
                "title": _req.title,
                "text": _req.text,
                "sub-refs": [_sub_ref.id for _sub_ref in _req.sub_refs],
            }

        # Write the JSON file.
        self.debug(f"Writing {reqdb_file}")
        JsonDict.writefile(
            schema_subpath=ReqDatabase.JSON_SCHEMA_SUBPATH,
            content=_reqdb_json,
            output_path=reqdb_file,
        )

    @typing.overload
    def push(self, obj):  # type: (_ReqType) -> _ReqType
        ...

    @typing.overload
    def push(self, obj):  # type: (_ReqRefType) -> _ReqRefType
        ...

    def push(
            self,
            obj,  # type: typing.Union[_ReqType, _ReqRefType]
    ):  # type: (...) -> typing.Union[_ReqType, _ReqRefType]
        """
        Feeds the database with requirements.

        :param obj:
            Requirement or requirement reference to ensure registration for.

            Requirement references with empty sub-item specifications will be interpreted as the related requirement itself.
        :return:
            Object actually saved in the database.

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

        # Return the object eventually saved in the database.
        if isinstance(obj, Req):
            return self._req_db[_req_key].req
        else:
            return self._req_db[_req_key]

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
                return self.push(req)
            else:
                return self.getreq(req.id)

        # Requirement as a string.
        elif isinstance(req, str):
            if req not in self._req_db:
                if push_unknown:
                    return self.push(Req(id=req))
                else:
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
                req_ref = self.push(req_ref)
                return req_ref if isinstance(req_ref, ReqRef) else req_ref.main_ref
            else:
                return self.getreqref(req_ref.id)

        # Requirement reference as a string.
        elif isinstance(req_ref, str):
            if req_ref not in self._req_db:
                if push_unknown:
                    _req_id = req_ref.split("/")[0]  # type: str
                    _req = self.getreq(_req_id, push_unknown=push_unknown)  # type: Req
                    if req_ref != _req.id:
                        self._req_db[req_ref] = ReqRef(_req, *req_ref.split("/")[1:])
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
                    lambda req_ref: req_ref.ismain(),
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

    def getallverifiers(self):  # type: (...) -> _OrderedSetType[_ReqVerifierType]
        """
        Returns all final requirement verifiers saved in the database,
        either scenarios or steps.

        :return: :class:`._reqverifier.ReqVerifier` ordered set (see :meth:`._reqverifier.ReqVerifier.orderedset()` for order details).
        """
        from ._reqverifier import ReqVerifier

        _req_verifier_list = []  # type: typing.List[ReqVerifier]
        for _req_ref in self._req_db.values():  # type: _ReqRefType
            for _req_link in _req_ref.req_links:  # type: _ReqLinkType
                _req_verifier_list.extend(_req_link.req_verifiers)
        _req_verifiers = ReqVerifier.orderedset(_req_verifier_list)  # type: _OrderedSetType[ReqVerifier]

        self.debug("getallverifiers() -> %r", _req_verifiers)
        return _req_verifiers

    def getallscenarios(self):  # type: (...) -> _OrderedSetType[_ScenarioDefinitionType]
        """
        Returns all scenarios that track requirements.

        Either directly, or through one of their steps.

        :return: :class:`._scenariodefinition.ScenarioDefinition` ordered set (see :meth:`._reqverifier.ReqVerifier.orderedset()` for order details).
        """
        from ._reqverifier import ReqVerifierHelper
        from ._scenariodefinition import ScenarioDefinition

        _scenario_list = []  # type: typing.List[ScenarioDefinition]
        for _req_ref in self._req_db.values():  # type: _ReqRefType
            for _req_link in _req_ref.req_links:  # type: _ReqLinkType
                _scenario_list.extend(
                    # Ensure `ScenarioDefinition` from `ReqVerifier` objects.
                    map(ReqVerifierHelper.getscenario, _req_link.req_verifiers),
                )
        _scenarios = ScenarioDefinition.orderedset(_scenario_list)  # type: _OrderedSetType[ScenarioDefinition]

        self.debug("getallscenarios() -> %r", _scenarios)
        return _scenarios


#: Main instance of :class:`ReqDatabase`.
REQ_DB = ReqDatabase()  # type: ReqDatabase
