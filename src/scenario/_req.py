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
    from ._reqtypes import SetWithReqLinksType as _SetWithReqLinksType
    from ._scenariodefinition import ScenarioDefinition as _ScenarioDefinitionType
    from ._setutils import OrderedSetType as _OrderedSetType


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

    def __hash__(self):  # type: (...) -> int
        """
        Ensures :class:`Req` objects are hashable, so that they can be used in sets.
        """
        return id(self)

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
    def sub_refs(self):  # type: () -> _OrderedSetType[_ReqRefType]
        """
        References to sub-parts of this requirement.

        Sorted by requirement reference ids.
        """
        from ._reqdb import REQ_DB
        from ._setutils import OrderedSetHelper

        return OrderedSetHelper.build(
            # Filter requirement references that point to sub-parts of this requirement.
            filter(
                lambda req_ref: (req_ref.req is self) and req_ref.subs,
                REQ_DB.getallrefs(),
            ),
            # Sort by requirement reference ids.
            key=lambda req_ref: req_ref.id
        )

    def gettrackers(
            self,
            *,
            walk_sub_refs=True,  # type: bool
    ):  # type: (...) -> _SetWithReqLinksType[_ReqTrackerType]
        """
        Returns trackers linked with this requirement.

        :param walk_sub_refs:
            Option to include requirement sub-reference trackers.

            If ``True``, trackers tracking sub-references of the requirement will be included in the result.

            ``True`` by default.

            .. tip::
                The trackers tracking the main part only of the requirement
                can also be retrieved through the :meth:`._reqref.ReqRef.gettrackers()` method of the :attr:`main_ref`.
        :return:
            Requirement trackers, with their related links (ordered by their requirement reference ids).

        Does not return :class:`._scenariodefinition.ScenarioDefinition` instances that track this requirement through steps only.
        See :meth:`getscenarios()` for the purpose.
        """
        from ._reqlink import ReqLinkHelper

        return ReqLinkHelper.buildsetwithreqlinks(
            # Determine the list of requirement references to walk through, depending on `walk_sub_refs`.
            [self.main_ref] if not walk_sub_refs else [self.main_ref, *self.sub_refs],
            # Get requirement trackers from each link.
            lambda req_link: req_link.req_trackers,
        )

    def getscenarios(
            self,
            *,
            walk_sub_refs=True,  # type: bool
    ):  # type: (...) -> _SetWithReqLinksType[_ScenarioDefinitionType]
        """
        Returns all scenarios linked with this requirement.

        :param walk_sub_refs:
            Option to include requirement sub-reference scenarios.

            If ``True``, scenarios tracking sub-references of the requirement will be included in the result.

            ``True`` by default.

            .. tip::
                The scenarios tracking the main part only of the requirement
                can also be retrieved through the :meth:`._reqref.ReqRef.getscenarios()` method of the :attr:`main_ref`.
        :return:
            Scenario definitions, with their related links (ordered by their requirement reference ids).

        Returns scenarios linked with this requirement, either directly or through one of their steps.
        """
        from ._reqlink import ReqLinkHelper
        from ._reqtracker import ReqTrackerHelper

        return ReqLinkHelper.buildsetwithreqlinks(
            # Determine the list of requirement references to walk through, depending on `walk_sub_refs`.
            [self.main_ref] if not walk_sub_refs else [self.main_ref, *self.sub_refs],
            # Get scenarios from each link.
            lambda req_link: map(ReqTrackerHelper.getscenario, req_link.req_trackers),
        )

    def getreqlinks(
            self,
            req_tracker=None,  # type: _ReqTrackerType
            *,
            walk_sub_refs=True,  # type: bool
    ):  # type: (...) -> _OrderedSetType[_ReqLinkType]
        """
        Requirement links attached with this requirement,
        filtered with the given predicates.

        :param req_tracker:
            Requirement tracker predicate to search links for.

            Optional.
            All requirement links when ``None``.
        :param walk_sub_refs:
            Option to include requirement sub-reference links.

            If ``True``, links held by the requirement sub-references will be included in the result.

            ``True`` by default.

            .. tip::
                The links held by the main part only of the requirement
                can also be retrieved through the :attr:`._reqref.ReqRef.req_links` member of the :attr:`main_ref`.
        :return:
            Filtered set of requirement links, ordered by requirement reference ids.
        """
        from ._reqlink import ReqLinkHelper
        from ._setutils import OrderedSetHelper

        # Compute requirement references depending on `sub_ref_links`.
        _req_refs = [self.main_ref]  # type: typing.List[_ReqRefType]
        if walk_sub_refs:
            _req_refs.extend(self.sub_refs)

        # Walk through requirement references.
        _req_links = []  # type: typing.List[_ReqLinkType]
        for _req_ref in _req_refs:  # type: _ReqRefType
            # Filter links with the requirement predicates.
            _req_links.extend(filter(
                lambda req_link: req_link.matches(req_tracker=req_tracker),
                _req_ref.req_links,
            ))

        # Sort by requirement reference ids.
        return OrderedSetHelper.build(
            _req_links,
            key=ReqLinkHelper.key,
        )
