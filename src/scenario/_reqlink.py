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
Requirement / test coverage links.
"""

import abc
import typing

if typing.TYPE_CHECKING:
    from ._req import Req as _ReqType
    from ._reqref import ReqRef as _ReqRefType
    from ._reqtracker import ReqTracker as _ReqTrackerType
    from ._reqtypes import AnyReqRefType as _AnyReqRefType
    from ._reqtypes import ReqLinkDefType as _ReqLinkDefType
    from ._reqtypes import SetWithReqLinksType as _SetWithReqLinksType
    from ._reqtypes import VarReqTrackerType as _VarReqTrackerType
    from ._setutils import OrderedSetType as _OrderedSetType
    from ._typingutils import VarItemType as _VarItemType


class ReqLink:
    """
    Link between
    a requirement item (requirement or part of requirement)
    and a test item (scenario or step),
    with optional justification.
    """

    @staticmethod
    def orderedset(
            req_links,  # type: typing.Iterable[ReqLink]
    ):  # type: (...) -> _OrderedSetType[ReqLink]
        """
        Ensures a sorted set of unique :class:`ReqLink` items.

        :param req_links: Unordered list of :class:`ReqLink` items.
        :return: Ordered set of unique :class:`ReqLink` items, by requirement reference ids, then scenario names and steps.
        """
        from ._setutils import orderedset

        return orderedset(
            req_links,
            key=ReqLinkHelper.sortkeyfunction,
        )

    def __init__(
            self,
            req_link_def,  # type: _ReqLinkDefType
    ):  # type: (...) -> None
        """
        Initializes a requirement / test coverage link,
        possibly on a subitem of the requirement,
        and with optional justification comments.

        :param req_link_def: Requirement link definition.
        """
        from ._textutils import anylongtext2str

        #: Tracked requirement reference.
        #:
        #: Unresolved input data for the :meth:`req_ref()` property.
        self._any_req_ref = ""  # type: _AnyReqRefType
        #: Justification comments.
        self.comments = ""  # type: str
        #: Unordered attached requirement trackers.
        self._req_trackers = set()  # type: typing.Set[_ReqTrackerType]

        # Analyze the requirement link definition.
        if isinstance(req_link_def, tuple):
            # 1st member of the tuple is a requirement reference.
            self._any_req_ref = req_link_def[0]
            # 2nd member is optional comments.
            if len(req_link_def) > 1:
                self.comments = anylongtext2str(
                    req_link_def[1],  # type: ignore[misc]  ## Tuple index out of range (mypy@1.0.1 bug?)
                )
        else:
            # If not a tuple, `req_link_def` is just a requirement reference.
            self._any_req_ref = req_link_def

    def __repr__(self):  # type: () -> str
        """
        Canonical string representation of the requirement link.
        """
        from ._reflection import qualname
        from ._reqtracker import ReqTrackerHelper

        return "".join([
            f"<{qualname(type(self))}",
            f" req_ref={self.req_ref!r}",
            f" req_trackers={[ReqTrackerHelper.sortkeyfunction(_req_tracker) for _req_tracker in self.req_trackers]!r}",
            f" comments={self.comments!r}" if self.comments else "",
            ">",
        ])

    def __str__(self):  # type: () -> str
        """
        Human readable string representation of the requirement link.
        """
        return "".join([
            str(self.req_ref),
            " <- ",
            "{", ", ".join([str(_req_tracker) for _req_tracker in self.req_trackers]), "}",
            f" | {self.comments}" if self.comments else "",
        ])

    def __hash__(self):  # type: (...) -> int
        """
        Ensures :class:`ReqLink` objects are hashable, so that they can be used in sets.
        """
        return id(self)

    @property
    def req(self):  # type: () -> _ReqType
        """
        Tracked :class:`._req.Req` instance.
        """
        return self.req_ref.req

    @property
    def req_ref(self):  # type: () -> _ReqRefType
        """
        Tracked requirement reference.

        Resolution of :attr:`_any_req_ref`.
        """
        from ._reqdb import REQ_DB

        return REQ_DB.getreqref(self._any_req_ref, push_unknown=True)

    @property
    def req_trackers(self):  # type: () -> _OrderedSetType[_ReqTrackerType]
        """
        Attached requirement trackers.

        See :meth:`._reqtracker.ReqTracker.orderedset()` for order details.
        """
        from ._reqtracker import ReqTracker

        return ReqTracker.orderedset(self._req_trackers)

    def matches(
            self,
            *,
            req_ref=None,  # type: _AnyReqRefType
            walk_sub_refs=False,  # type: bool
            req_tracker=None,  # type: _ReqTrackerType
            walk_steps=False,  # type: bool
    ):  # type: (...) -> bool
        """
        Tells whether the given requirement with optional subitem matches this link.

        :param req_ref:
            Optional requirement reference predicate.
        :param walk_sub_refs:
            When ``req_ref`` is a main requirement,
            ``True`` makes the requirement link match if it tracks a sub-reference of the requirement.
        :param req_tracker:
            Optional requirement tracker predicate.
        :param walk_steps:
            When ``req_tracker`` is a scenario,
            ``True`` makes the link match if it comes from a step of the scenario.
        :return:
            ``True`` in case of a match, ``False`` otherwise.

            ``True`` when the ``req_ref`` predicate is ``None``.
        """
        from ._reqdb import REQ_DB
        from ._scenariodefinition import ScenarioDefinition
        from ._stepdefinition import StepDefinition

        # Requirement reference predicate.
        if req_ref is not None:
            req_ref = REQ_DB.getreqref(req_ref)
            if not self.req_ref.matches(req_ref):
                # Requirement reference mismatch.
                if (not walk_sub_refs) or req_ref.subs:
                    # No sub-reference to walk through.
                    return False
                else:
                    # Walk through requirement sub-references.
                    for _sub_ref in req_ref.req.sub_refs:  # type: _ReqRefType
                        if self.req_ref.matches(_sub_ref):
                            # Match with a sub-reference of the requirement.
                            break
                    else:
                        # No sub-reference matches neither.
                        return False

        # Requirement tracker predicate.
        if req_tracker is not None:
            if req_tracker not in self._req_trackers:
                # Requirement tracker mismatch.
                if (not walk_steps) or (not isinstance(req_tracker, ScenarioDefinition)):
                    # No steps to walk through.
                    return False
                else:
                    # Walk through scenario steps.
                    for _step in req_tracker.steps:  # type: StepDefinition
                        if _step in self._req_trackers:
                            # Match with a step of the scenario.
                            break
                    else:
                        # No step matches neither.
                        return False

        # All predicates passed.
        return True

    def coveredby(
            self,
            req_tracker,  # type: _VarReqTrackerType
    ):  # type: (...) -> ReqLink
        """
        Attaches a requirement tracker with this link.

        :param req_tracker: Requirement tracker to attach.
        :return: ``self``
        """
        from ._reqdb import REQ_DB

        # As soon as the link is actually bound with trackers:
        # - ensure the database knows the requirement reference (non main references only),
        if self.req_ref.subs:
            REQ_DB.push(self.req_ref)
        # - ensure the link is saved in the requirement reference link set,
        if self not in self.req_ref.req_links:
            self.req_ref._req_links.add(self)  # noqa  ## Access to protected member.

        # Try to save the requirement tracker reference with this link.
        if req_tracker not in self.req_trackers:
            # New tracker reference.
            self._req_trackers.add(req_tracker)

            # Debug the downstream requirement link.
            REQ_DB.debug("Requirement link: %s -> %r", self.req_ref.id, req_tracker)

            # Link <-> tracker cross-reference.
            req_tracker.covers(self)

        return self


class ReqLinkHelper(abc.ABC):
    """
    Helper class for :class:`ReqLink` items.
    """

    @staticmethod
    def sortkeyfunction(
            req_link,  # type: ReqLink
    ):  # type: (...) -> typing.Tuple[str, ...]
        """
        Key function used to sort :class:`ReqLink` items.

        By requirement reference ids, then scenario names and steps.

        :param req_link: Requirement link item to sort.
        :return: Key tuple.
        """
        from ._reqtracker import ReqTrackerHelper

        return (
            req_link.req_ref.id,
            *[ReqTrackerHelper.sortkeyfunction(req_tracker) for req_tracker in req_link.req_trackers],
        )

    @staticmethod
    def buildsetwithreqlinks(
            req_link_holders,  # type: typing.Sequence[typing.Union[_ReqRefType, _ReqTrackerType]]
            items_from_link,  # type: typing.Callable[[ReqLink], typing.Iterable[_VarItemType]]
    ):  # type: (...) -> _SetWithReqLinksType[_VarItemType]
        """
        Builds a set of items with related requirement links.

        :param req_link_holders: List of requirement references or requirement trackers to walk through.
        :param items_from_link: Function that retrieves the items to save from requirement links.
        """
        _set_with_req_links = {}  # type: _SetWithReqLinksType[_VarItemType]

        # Walk from `req_link_holders` through requirement links and items to save.
        for _req_link_holder in req_link_holders:  # type: typing.Union[_ReqRefType, _ReqTrackerType]
            for _req_link in _req_link_holder.req_links:  # type: ReqLink
                for _item in items_from_link(_req_link):  # type: _VarItemType
                    # Build unordered sets of requirement links first.
                    if _item not in _set_with_req_links:
                        _set_with_req_links[_item] = [_req_link]
                    else:
                        _req_links = _set_with_req_links[_item]  # type: typing.Sequence[ReqLink]
                        assert isinstance(_req_links, list)
                        _req_links.append(_req_link)

        # Sum up and sort sets of links in the end.
        for _item in _set_with_req_links:  # Type already declared above.
            _set_with_req_links[_item] = ReqLink.orderedset(_set_with_req_links[_item])

        return _set_with_req_links
