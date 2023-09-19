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
    from ._req import Req as _ReqType
    from ._reqlink import ReqLink as _ReqLinkType
    from ._reqref import ReqRef as _ReqRefType
    from ._reqtypes import AnyReqLinkType as _AnyReqLinkType
    from ._reqtypes import AnyReqRefType as _AnyReqRefType
    from ._reqtypes import SetWithReqLinksType as _SetWithReqLinksType
    from ._reqtypes import VarReqTrackerType as _VarReqTrackerType
    from ._scenariodefinition import ScenarioDefinition as _ScenarioDefinitionType
    from ._setutils import OrderedSetType as _OrderedSetType


class ReqTracker(abc.ABC):
    """
    Requirement tracker objects.

    Actually, only :class:`._scenariodefinition.ScenarioDefinition` and :class:`._stepdefinition.StepDefinition`
    may subclass this :class:`ReqTracker` abstract class.
    """

    @classmethod
    def orderedset(
            cls,  # type: typing.Type[_VarReqTrackerType]
            req_trackers,  # type: typing.Iterable[_VarReqTrackerType]
    ):  # type: (...) -> _OrderedSetType[_VarReqTrackerType]
        """
        Ensures an ordered set of unique :class:`ReqTracker` items.

        :param req_trackers: Unordered list of :class:`ReqTracker` items.
        :return: Ordered set of unique :class:`ReqTracker` items, ordered by scenario (or owner scenario) names, then step ids.
        """
        from ._setutils import orderedset

        return orderedset(
            req_trackers,
            key=ReqTrackerHelper.sortkeyfunction,
        )

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

    @property
    def req_links(self):  # type: () -> _OrderedSetType[_ReqLinkType]
        """
        Requirement links attached with this tracker.

        See :meth:`._reqlink.ReqLink.orderedset()` for order details.
        """
        from ._reqlink import ReqLink

        return ReqLink.orderedset(self._req_links)

    def covers(
            self,
            first,  # type: typing.Union[_AnyReqLinkType, _OrderedSetType[_ReqLinkType]]
            *others,  # type: typing.Union[_AnyReqLinkType, _OrderedSetType[_ReqLinkType]]
    ):  # type: (...) -> _ReqLinkType
        """
        Declares requirement coverage from this tracker object.

        :param first:
            First requirement link declared.

            May be fed with the result of :meth:`getreqlinks()`.
        :param others:
            More requirement links.

            May be fed with the result of :meth:`getreqlinks()` as well.
        :return:
            First requirement link.
        """
        from ._reqdb import REQ_DB
        from ._reqlink import ReqLink

        # Will store the first link encountered in `first`.
        _first_link = None  # type: typing.Optional[ReqLink]

        # Try to save each link.
        for _req_links in [first, *others]:  # type: typing.Union[_AnyReqLinkType, _OrderedSetType[_ReqLinkType]]
            # Ensure we consider a set of links for the second loop below.
            if (not hasattr(_req_links, "__iter__")) or isinstance(_req_links, str):
                _req_links = [_req_links if isinstance(_req_links, ReqLink) else ReqLink(_req_links)]

            for _req_link in _req_links:  # type: _AnyReqLinkType
                # Ensure we have a `ReqLink` object.
                if not isinstance(_req_link, ReqLink):
                    _req_link = ReqLink(_req_link)

                # Save the first link.
                if _first_link is None:
                    _first_link = _req_link

                if _req_link not in self._req_links:
                    # New link.
                    self._req_links.add(_req_link)

                    # Link <-> tracker cross-reference.
                    _req_link.coveredby(self)

                    # Let's debug the upstream requirement link after.
                    REQ_DB.debug("Requirement link: %s <- %r", _req_link.req_ref.id, self)

        # Return the first link in the end.
        assert _first_link is not None, "Internal error"
        return _first_link

    def getreqs(
            self,
    ):  # type: (...) -> _SetWithReqLinksType[_ReqType]
        """
        Requirements tracked by this tracker, with related links.

        :return:
            Requirements tracked by this tracker,
            either directly or through a sub-reference of it,
            with related links (see :meth:`._reqlink.ReqLink.orderedset()` for order details).
        """
        from ._reqlink import ReqLinkHelper

        return ReqLinkHelper.buildsetwithreqlinks(
            # Walk requirement links from the current requirement tracker.
            [self],
            # Get the requirement for each link.
            lambda req_link: [req_link.req],
        )

    def getreqrefs(
            self,
    ):  # type: (...) -> _SetWithReqLinksType[_ReqRefType]
        """
        Requirement references tracked by this tracker, with related links.

        :return:
            Requirement references tracked by this tracker,
            with related links (see :meth:`._reqlink.ReqLink.orderedset()` for order details).
        """
        from ._reqlink import ReqLinkHelper

        return ReqLinkHelper.buildsetwithreqlinks(
            # Walk requirement links from the current requirement tracker.
            [self],
            # Get the requirement reference for each link.
            lambda req_link: [req_link.req_ref],
        )

    def getreqlinks(
            self,
            req_ref=None,  # type: _AnyReqRefType
            *,
            walk_sub_refs=False,  # type: bool
    ):  # type: (...) -> _OrderedSetType[_ReqLinkType]
        """
        Requirement links attached with this tracker,
        filtered with the given predicates.

        :param req_ref:
            Requirement reference predicate to search links for.

            Optional.
            All requirement links when ``None``.
        :param walk_sub_refs:
            When ``req_ref`` is a main requirement,
            ``True`` makes the requirement link match if it tracks a sub-reference of the requirement.
        :return:
            Filtered set of requirement links (see :meth:`._reqlink.ReqLink.orderedset()` for order details).
        """
        from ._reqlink import ReqLink

        return ReqLink.orderedset(
            # Filter requirement links with the requirement predicates.
            filter(
                lambda req_link: req_link.matches(req_ref=req_ref, walk_sub_refs=walk_sub_refs),
                self._req_links,
            ),
        )


class ReqTrackerHelper:
    """
    Helper class for :class:`ReqTracker`.
    """

    @staticmethod
    def sortkeyfunction(
            req_tracker,  # type: ReqTracker
    ):  # type: (...) -> str
        """
        Key function to sort :class:`ReqTracker` items.

        By scenario (or owner scenario) names, then step ids.

        :param req_tracker: Scenario or step definition to sort.
        :return: Sortable string.
        """
        from ._scenariodefinition import ScenarioDefinition
        from ._stepdefinition import StepDefinition

        if isinstance(req_tracker, ScenarioDefinition):
            return req_tracker.name
        elif isinstance(req_tracker, StepDefinition):
            # Find out the number of digits to consider to format the step number.
            # Depends on the number of steps the owner scenario holds.
            _step_number_digits = len(str(len(req_tracker.scenario.steps)))  # type: int
            _step_number_fmt = f"0{_step_number_digits}d"  # type: str
            return f"{req_tracker.scenario.name}:step#{req_tracker.number:{_step_number_fmt}}"
        raise TypeError(f"Unexpected requirement tracker type {req_tracker!r}")

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
