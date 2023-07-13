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
    from ._reqtypes import AnyReqLinkType as _AnyReqLinkType
    from ._reqtypes import AnyReqRefType as _AnyReqRefType
    from ._scenariodefinition import ScenarioDefinition as _ScenarioDefinitionType


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

    def covers(
            self,
            first,  # type: typing.Union[_AnyReqLinkType, typing.Set[_ReqLinkType]]
            *others,  # type: typing.Union[_AnyReqLinkType, typing.Set[_ReqLinkType]]
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
        from ._reqlink import ReqLink

        # Will store the first link encountered in `first`.
        _first_link = None  # type: typing.Optional[ReqLink]

        # Try to save each link.
        for _req_links in [first, *others]:  # type: typing.Union[_AnyReqLinkType, typing.Set[_ReqLinkType]]
            # Ensure we consider a set of links for the second loop below.
            if not isinstance(_req_links, set):
                _req_links = {_req_links if isinstance(_req_links, ReqLink) else ReqLink(_req_links)}

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

        # Return the first link in the end.
        assert _first_link is not None, "Internal error"
        return _first_link

    def getreqs(self):  # type: (...) -> typing.Set[_ReqType]
        """
        Requirements tracked by this tracker.
        """
        return set([_req_link.req for _req_link in self._req_links])

    def getreqlinks(
            self,
            req_ref=None,  # type: _AnyReqRefType
            direct_only=False,  # type: bool
    ):  # type: (...) -> typing.Set[_ReqLinkType]
        """
        Requirement links attached with this tracker,
        filtered with the given predicates.

        :param req_ref:
            Requirement reference predicate to search links for.

            Optional.
            All requirement links when ``None``.
        :param direct_only:
            Direct links only.

            If ``False``, and the current tracker is a :class:`._scenariodefinition.ScenarioDefinition`,
            links held by the steps will be included in the result.

            ``False`` by default.
        :return:
            Filtered set of requirement links.
        """
        from ._scenariodefinition import ScenarioDefinition
        from ._stepdefinition import StepDefinition

        # Constitute the whole list of requirement links to consider.
        _req_links = set(self._req_links)  # type: typing.Set[_ReqLinkType]
        if isinstance(self, ScenarioDefinition) and (not direct_only):
            for _step in self.steps:  # type: StepDefinition
                _req_links.update(_step._req_links)

        # Filter this list with the requirement predicates.
        return set(filter(
            lambda req_link: req_link.matches(req_ref),
            _req_links,
        ))


class ReqTrackerHelper:
    """
    Helper class for :class:`ReqTracker`.
    """

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
