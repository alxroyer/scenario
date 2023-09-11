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
    from ._reqtypes import SetWithReqLinksType as _SetWithReqLinksType
    from ._reqtypes import VarReqTrackerType as _VarReqTrackerType
    from ._setutils import OrderedSetType as _OrderedSetType
    from ._textutils import AnyLongTextType as _AnyLongTextType
    from ._typingutils import VarItemType as _VarItemType


class ReqLink:
    """
    Link between
    a requirement item (requirement or part of requirement)
    and a test item (scenario or step),
    with optional justification.
    """

    def __init__(
            self,
            req_ref,  # type: _AnyReqRefType
            comments=None,  # type: _AnyLongTextType
    ):  # type: (...) -> None
        """
        Initializes a requirement / test coverage link,
        possibly on a subitem of the requirement,
        and with optional justification comments.

        :param req_ref: Tracked requirement reference.
        :param comments: Optional justification comments.
        """
        from ._textutils import anylongtext2str

        #: Tracked requirement reference.
        #:
        #: Unresolved input data for the :meth:`req_ref()` property.
        self._any_req_ref = req_ref  # type: _AnyReqRefType
        #: Unordered attached requirement trackers.
        self._req_trackers = set()  # type: typing.Set[_ReqTrackerType]
        #: Justification comments.
        self.comments = ""  # type: str
        if comments:
            self.comments = anylongtext2str(comments)

    def __repr__(self):  # type: () -> str
        """
        Canonical string representation of the requirement link.
        """
        from ._reflection import qualname
        from ._reqtracker import ReqTrackerHelper

        return "".join([
            f"<{qualname(type(self))}",
            f" req_ref={self.req_ref!r}",
            f" req_trackers={[ReqTrackerHelper.key(_req_tracker) for _req_tracker in self.req_trackers]!r}",
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
        Attached requirement trackers, ordered by scenario names then steps.
        """
        from ._reqtracker import ReqTrackerHelper
        from ._setutils import OrderedSetHelper

        return OrderedSetHelper.build(
            self._req_trackers,
            # Sort by scenario names, then steps.
            key=ReqTrackerHelper.key,
        )

    def matches(
            self,
            *,
            req_ref=None,  # type: _AnyReqRefType
            req_tracker=None,  # type: _ReqTrackerType
    ):  # type: (...) -> bool
        """
        Tells whether the given requirement with optional subitem matches this link.

        :param req_ref:
            Optional requirement reference predicate.
        :param req_tracker:
            Optional requirement tracker predicate.
        :return:
            ``True`` in case of a match, ``False`` otherwise.

            ``True`` when the ``req_ref`` predicate is ``None``.
        """
        return all([
            (req_ref is None) or self.req_ref.matches(req_ref),
            (req_tracker is None) or (req_tracker in self._req_trackers),
        ])

    def coveredby(
            self,
            first,  # type: _VarReqTrackerType
            *others,  # type: _ReqTrackerType
    ):  # type: (...) -> _VarReqTrackerType
        """
        Attaches requirement trackers with this link.

        :param first: First requirement tracker at least.
        :param others: More requirement trackers.
        :return: First requirement tracker.
        """
        from ._reqdb import REQ_DB

        # As soon as the link is actually bound with trackers:
        # - ensure the database knows the requirement reference (non main references only),
        if self.req_ref.subs:
            REQ_DB.push(self.req_ref)
        # - ensure the link is saved in the requirement reference link set,
        if self not in self.req_ref.req_links:
            self.req_ref._req_links.add(self)  # noqa  ## Access to protected member.

        # Try to save requirement tracker references with this link.
        _first = first  # type: _ReqTrackerType  # Ensure `first` is of type `_ReqTrackerType` (and not `_VarReqTrackerType`).
        for _req_tracker in [_first, *others]:  # type: _ReqTrackerType
            if _req_tracker not in self.req_trackers:
                # New tracker reference.
                self._req_trackers.add(_req_tracker)

                # Debug the downstream requirement link.
                REQ_DB.debug("Requirement link: %s -> %r", self.req_ref.id, _req_tracker)

                # Link <-> tracker cross-reference.
                _req_tracker.covers(self)

        # Return the first step of the list.
        return first


class ReqLinkHelper(abc.ABC):
    """
    Helper class for :class:`ReqLink` items.
    """

    @staticmethod
    def key(
            req_link,  # type: ReqLink
    ):  # type: (...) -> typing.Tuple[str, ...]
        """
        Key function to sort :class:`ReqLink` items by requirement reference ids.

        By requirement reference ids, then scenario names and steps.

        :param req_link: Requirement link item to sort.
        :return: Key tuple.
        """
        from ._reqtracker import ReqTrackerHelper

        return (
            req_link.req_ref.id,
            *[ReqTrackerHelper.key(req_tracker) for req_tracker in req_link.req_trackers],
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
        from ._setutils import OrderedSetHelper

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
            _set_with_req_links[_item] = OrderedSetHelper.build(
                _set_with_req_links[_item],
                # Sort links by requirement reference ids.
                key=ReqLinkHelper.key,
            )

        return _set_with_req_links
