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
Requirement verifiers.
"""

import abc
import typing

if typing.TYPE_CHECKING:
    from ._req import Req as _ReqType
    from ._reqlink import ReqLink as _ReqLinkType
    from ._reqref import ReqRef as _ReqRefType
    from ._reqtypes import AnyReqLinkType as _AnyReqLinkType
    from ._reqtypes import AnyReqRefType as _AnyReqRefType
    from ._reqtypes import SetWithReqLinksType as _SetWithReqLinksType
    from ._reqtypes import VarReqVerifierType as _VarReqVerifierType
    from ._scenariodefinition import ScenarioDefinition as _ScenarioDefinitionType
    from ._setutils import OrderedSetType as _OrderedSetType


class ReqVerifier(abc.ABC):
    """
    Requirement verifier objects.

    Actually, only :class:`._scenariodefinition.ScenarioDefinition` and :class:`._stepdefinition.StepDefinition`
    may subclass this :class:`ReqVerifier` abstract class.
    """

    @classmethod
    def orderedset(
            cls,  # type: typing.Type[_VarReqVerifierType]
            req_verifiers,  # type: typing.Iterable[_VarReqVerifierType]
    ):  # type: (...) -> _OrderedSetType[_VarReqVerifierType]
        """
        Ensures an ordered set of unique :class:`ReqVerifier` items.

        :param req_verifiers: Unordered list of :class:`ReqVerifier` items.
        :return: Ordered set of unique :class:`ReqVerifier` items, ordered by scenario (or owner scenario) names, then step ids.
        """
        from ._setutils import orderedset

        return orderedset(
            req_verifiers,
            key=ReqVerifierHelper.sortkeyfunction,
        )

    def __init__(self):  # type: (...) -> None
        """
        Initializes an empty requirement link set.

        Checks that only :class:`._scenariodefinition.ScenarioDefinition` and :class:`._stepdefinition.StepDefinition`
        inherit from :class:`ReqVerifier`.
        """
        from ._scenariodefinition import ScenarioDefinition
        from ._stepdefinition import StepDefinition

        if not any([
            isinstance(self, ScenarioDefinition),
            isinstance(self, StepDefinition),
        ]):
            raise TypeError(f"Cannot subclass ReqVerifier if not a scenario nor step definition")

        #: Links to the verified requirements.
        self._req_links = set()  # type: typing.Set[_ReqLinkType]

    @property
    def req_links(self):  # type: () -> _OrderedSetType[_ReqLinkType]
        """
        Requirement links through which this verifier traces requirement references.

        See :meth:`._reqlink.ReqLink.orderedset()` for order details.
        """
        from ._reqlink import ReqLink

        return ReqLink.orderedset(self._req_links)

    def verifies(
            self,  # type: _VarReqVerifierType
            first,  # type: _AnyReqLinkType
            *others,  # type: _AnyReqLinkType
    ):  # type: (...) -> _VarReqVerifierType
        """
        Declares requirement coverage from this verifier object.

        :param first:
            First requirement link declared.
        :param others:
            More requirement links.
        :return:
            ``self``
        """
        from ._reqdb import REQ_DB
        from ._reqlink import ReqLink

        # Try to save each link.
        for _req_link in [first, *others]:  # type: _AnyReqLinkType
            # Ensure we have a `ReqLink` object.
            if not isinstance(_req_link, ReqLink):
                _req_link = ReqLink(_req_link)

            if _req_link not in self._req_links:
                # New link.
                self._req_links.add(_req_link)

                # Link <-> verifier cross-reference.
                _req_link.verifiedby(self)

                # Let's debug the upstream requirement link after.
                REQ_DB.debug("Requirement link: %s <- %r", _req_link.req_ref.id, self)

        return self

    def getreqlinks(
            self,
            req_ref=None,  # type: _AnyReqRefType
            *,
            walk_subrefs=False,  # type: bool
    ):  # type: (...) -> _OrderedSetType[_ReqLinkType]
        """
        Requirement links attached with this verifier,
        filtered with the given predicates.

        :param req_ref:
            Requirement reference predicate to search links for.

            Optional.
            All requirement links when ``None``.
        :param walk_subrefs:
            When ``req_ref`` is a main requirement,
            ``True`` makes the links match if they trace a subreference of the requirement.

            Ignored when ``req_ref`` is not set.
        :return:
            Filtered set of requirement links (see :meth:`._reqlink.ReqLink.orderedset()` for order details).
        """
        from ._reqlink import ReqLink

        return ReqLink.orderedset(
            # Filter requirement links with the requirement predicates.
            filter(
                lambda req_link: req_link.matches(req_ref=req_ref, walk_subrefs=walk_subrefs),
                self._req_links,
            ),
        )

    def getreqrefs(
            self,
    ):  # type: (...) -> _SetWithReqLinksType[_ReqRefType]
        """
        Requirement references traced by this verifier, with related links.

        :return:
            Requirement references traced by this verifier,
            with related links (see :meth:`._reqlink.ReqLink.orderedset()` for order details).
        """
        from ._reqlink import ReqLinkHelper

        return ReqLinkHelper.buildsetwithreqlinks(
            # Walk requirement links from the current requirement verifier.
            [self],
            # Get the requirement reference for each link.
            lambda req_link: [req_link.req_ref],
        )

    def getreqs(
            self,
    ):  # type: (...) -> _SetWithReqLinksType[_ReqType]
        """
        Requirements traced by this verifier, with related links.

        :return:
            Requirements traced by this verifier,
            either directly or through a subreference of it,
            with related links (see :meth:`._reqlink.ReqLink.orderedset()` for order details).
        """
        from ._reqlink import ReqLinkHelper

        return ReqLinkHelper.buildsetwithreqlinks(
            # Walk requirement links from the current requirement verifier.
            [self],
            # Get the requirement for each link.
            lambda req_link: [req_link.req],
        )


class ReqVerifierHelper:
    """
    Helper class for :class:`ReqVerifier`.
    """

    @staticmethod
    def tolongstring(
            req_verifier,  # type: ReqVerifier
            *,
            sortable=False,  # type: bool
    ):  # type: (...) -> str
        """
        Computes a long string representing the given :class:`ReqVerifier` item.

        :param req_verifier: Scenario or step to compute a string representation for.
        :param sortable: Set to ``True`` to compute a sortable string.
        :return: String representation of the scenario or step.
        """
        from ._scenariodefinition import ScenarioDefinition
        from ._stepdefinition import StepDefinition

        if isinstance(req_verifier, ScenarioDefinition):
            return req_verifier.name
        elif isinstance(req_verifier, StepDefinition):
            _step_number_fmt = "d"  # type: str
            if sortable:
                # Find out the number of digits to consider to format the step number.
                # Depends on the number of steps the owner scenario holds.
                _step_number_digits = len(str(len(req_verifier.scenario.steps)))  # type: int
                _step_number_fmt = f"0{_step_number_digits}d"
            return f"{req_verifier.scenario.name}:step#{req_verifier.number:{_step_number_fmt}}"
        raise TypeError(f"Unexpected requirement verifier type {req_verifier!r}")

    @staticmethod
    def sortkeyfunction(
            req_verifier,  # type: ReqVerifier
    ):  # type: (...) -> str
        """
        Key function to sort :class:`ReqVerifier` items.

        By scenario (or owner scenario) names, then step ids.

        :param req_verifier: Scenario or step definition to sort.
        :return: Sortable string.
        """
        return ReqVerifierHelper.tolongstring(req_verifier, sortable=True)

    @staticmethod
    def getscenario(
            req_verifier,  # type: ReqVerifier
    ):  # type: (...) -> _ScenarioDefinitionType
        """
        Retrieves the :class:`._scenariodefinition.ScenarioDefinition` instance from a :class:`ReqVerifier`.

        :param req_verifier: Scenario or step definition as a :class:`ReqVerifier` instance.
        :return: Scenario definition.
        """
        from ._scenariodefinition import ScenarioDefinition
        from ._stepdefinition import StepDefinition

        if isinstance(req_verifier, ScenarioDefinition):
            return req_verifier
        if isinstance(req_verifier, StepDefinition):
            return req_verifier.scenario
        raise TypeError(f"Unexpected requirement verifier type {req_verifier!r}")
