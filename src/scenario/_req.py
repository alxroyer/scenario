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
    from ._reqref import ReqRef as _ReqRefType
    from ._reqtracker import ReqTracker as _ReqTrackerType
    from ._scenariodefinition import ScenarioDefinition as _ScenarioDefinitionType


class Req:
    """
    Requirement class.
    """

    def __init__(
            self,
            *,
            id,  # type: str  # noqa  ## Shadows built-in name 'id'
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
        self.id = id  # type: str

        #: Requirement short title.
        #:
        #: Optional.
        self.title = title  # type: str

        #: Requirement full text.
        #:
        #: Optional.
        self.text = text  # type: str

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

    def __truediv__(
            self,
            sub,  # type: str
    ):  # type: (...) -> _ReqRefType
        """
        Gives a requirement sub-item reference.

        :param sub: Requirement sub-item specification.
        :return: :class:`._reqref.ReqRef` instance computed from the current :class:`Req` and the given requirement sub-item specification.
        """
        from ._reqref import ReqRef

        return ReqRef(self, sub)

    @property
    def main_ref(self):  # type: () -> _ReqRefType
        """
        Reference to the main part of this requirement.
        """
        from ._reqdb import REQ_DB

        return REQ_DB.getreqref(self)

    @property
    def sub_refs(self):  # type: () -> typing.Set[_ReqRefType]
        """
        References to sub-parts of this requirement.
        """
        from ._reqdb import REQ_DB

        return set(filter(
            lambda req_ref: (req_ref.req is self) and req_ref.subs,
            REQ_DB.getallrefs(),
        ))

    def gettrackers(
            self,
    ):  # type: (...) -> typing.Dict[_ReqTrackerType, typing.Set[_ReqLinkType]]
        """
        Returns all trackers linked with this requirement.

        :return: Requirement trackers, with their related links.

        This method returns trackers linked with the main part of the requirement, or a sub-part of it.
        In order to get trackers for the main part of the requirement only,
        please use :attr:`main_ref` and :meth:`._reqref.ReqRef.gettrackers()`.

        For :class:`._scenariodefinition.ScenarioDefinition` instances,
        the scenario won't be returned if it is not linked with the requirement directly,
        but only through one of its steps.
        See :meth:`getscenarios()` for the purpose.
        """
        _req_trackers = {}  # type: typing.Dict[_ReqTrackerType, typing.Set[_ReqLinkType]]

        # Walk through all requirement references attached with this requirement.
        for _req_ref in [self.main_ref, *self.sub_refs]:  # type: _ReqRefType
            # Integrate `gettrackers()` results for each.
            for _req_tracker, _req_links in _req_ref.gettrackers().items():  # type: _ReqTrackerType, typing.Set[_ReqLinkType]
                if _req_tracker not in _req_trackers:
                    _req_trackers[_req_tracker] = set()
                _req_trackers[_req_tracker].update(_req_links)

        return _req_trackers

    def getscenarios(
            self,
    ):  # type: (...) -> typing.Dict[_ScenarioDefinitionType, typing.Set[_ReqLinkType]]
        """
        Returns all scenarios linked with this requirement.

        :return: Scenario definitions, with their related links.

        This method returns scenarios that reference the main part of the requirement, or a sub-part of it.
        In order to get scenarios for the main part of the requirement only,
        please use :attr:`main_ref` and :meth:`._reqref.ReqRef.getscenarios()`.

        Returns scenarios linked with this requirement, either directly or through one of their steps.
        """
        _scenario_definitions = {}  # type: typing.Dict[_ScenarioDefinitionType, typing.Set[_ReqLinkType]]

        # Walk through all requirement references attached with this requirement.
        for _req_ref in [self.main_ref, *self.sub_refs]:  # type: _ReqRefType
            # Integrate `getscenarios()` results for each.
            for _scenario_definition, _req_links in _req_ref.getscenarios().items():  # type: _ScenarioDefinitionType, typing.Set[_ReqLinkType]
                if _scenario_definition not in _scenario_definitions:
                    _scenario_definitions[_scenario_definition] = set()
                _scenario_definitions[_scenario_definition].update(_req_links)

        return _scenario_definitions
