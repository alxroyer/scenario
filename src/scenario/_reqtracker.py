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
    from ._scenariodefinition import ScenarioDefinition as _ScenarioDefinitionType
    from ._setutils import OrderedSetType as _OrderedSetType


class ReqTracker(abc.ABC):
    """
    Requirement tracker objects.

    Actually, only :class:`._scenariodefinition.ScenarioDefinition` and :class:`._stepdefinition.StepDefinition`
    may subclass this :class:`ReqTracker` abstract class.
    """

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
        Requirement links attached with this tracker, ordered by requirement reference ids.
        """
        from ._reqlink import ReqLinkHelper
        from ._setutils import OrderedSetHelper

        return OrderedSetHelper.build(
            self._req_links,
            # Sort by requirement reference ids.
            key=ReqLinkHelper.key,
        )

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
            *,
            walk_steps=True,  # type: bool
    ):  # type: (...) -> _OrderedSetType[_ReqType]
        """
        Requirements tracked by this tracker, ordered by ids.

        :param walk_steps:
            Option to include step requirements.

            If ``True``, and the current tracker is a :class:`._scenariodefinition.ScenarioDefinition`,
            requirements tracked by the scenario steps will be included in the result.

            Ignored for :class:`._stepdefinition.StepDefinition` trackers.

            ``True`` by default.
        """
        from ._setutils import OrderedSetHelper

        return OrderedSetHelper.build(
            # Convert link >> requirement.
            map(
                lambda p_req_link: p_req_link.req_ref.req,
                self.getreqlinks(walk_steps=walk_steps),
            ),
            # Sort by requirement ids.
            key=lambda req: req.id,
        )

    def getreqrefs(
            self,
            *,
            walk_steps=True,  # type: bool
    ):  # type: (...) -> _OrderedSetType[_ReqRefType]
        """
        Requirement references tracked by this tracker, ordered by ids.

        :param walk_steps:
            Option to include step requirement references.

            If ``True``, and the current tracker is a :class:`._scenariodefinition.ScenarioDefinition`,
            requirement references tracked by the scenario steps will be included in the result.

            Ignored for :class:`._stepdefinition.StepDefinition` trackers.

            ``True`` by default.
        """
        from ._setutils import OrderedSetHelper

        return OrderedSetHelper.build(
            # Convert link >> requirement reference.
            map(
                lambda p_req_link: p_req_link.req_ref,
                self.getreqlinks(walk_steps=walk_steps),
            ),
            # Sort by requirement reference ids.
            key=lambda req_ref: req_ref.id,
        )

    def getreqlinks(
            self,
            req_ref=None,  # type: _AnyReqRefType
            *,
            walk_steps=True,  # type: bool
    ):  # type: (...) -> _OrderedSetType[_ReqLinkType]
        """
        Requirement links attached with this tracker,
        filtered with the given predicates.

        :param req_ref:
            Requirement reference predicate to search links for.

            Optional.
            All requirement links when ``None``.
        :param walk_steps:
            Option to include step requirement links.

            If ``True``, and the current tracker is a :class:`._scenariodefinition.ScenarioDefinition`,
            links held by the scenario steps will be included in the result.

            Ignored for :class:`._stepdefinition.StepDefinition` trackers.

            ``True`` by default.

            .. tip::
                Retrieving the direct requirement links from the current tracker
                can be done through the :attr:`req_links` attribute.
        :return:
            Filtered set of requirement links, ordered by requirement reference ids.
        """
        from ._reqlink import ReqLinkHelper
        from ._scenariodefinition import ScenarioDefinition
        from ._setutils import OrderedSetHelper
        from ._stepdefinition import StepDefinition

        # Constitute the whole list of requirement links to consider.
        _req_links = list(self._req_links)  # type: typing.List[_ReqLinkType]
        if isinstance(self, ScenarioDefinition) and walk_steps:
            for _step in self.steps:  # type: StepDefinition
                _req_links.extend(_step._req_links)

        return OrderedSetHelper.build(
            # Filter this list with the requirement predicates.
            filter(
                lambda req_link: req_link.matches(req_ref=req_ref),
                _req_links,
            ),
            # Sort by requirement reference ids.
            key=ReqLinkHelper.key,
        )


class ReqTrackerHelper:
    """
    Helper class for :class:`ReqTracker`.
    """

    @staticmethod
    def key(
            req_tracker,  # type: ReqTracker
    ):  # type: (...) -> str
        """
        Key function to sort :class:`ReqTracker` items.

        By scenario (or owner scenario) names, then step ids

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
