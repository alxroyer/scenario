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

import typing

if typing.TYPE_CHECKING:
    from ._reqtracker import ReqTracker as _ReqTrackerType
    from ._reqtypes import AnyReqType as _AnyReqType
    from ._reqtypes import VarReqTrackerType as _VarReqTrackerType
    from ._textutils import AnyLongTextType as _AnyLongTextType


class ReqLink:
    """
    Link between
    a requirement item (requirement or part of requirement)
    and a test item (scenario or step),
    with optional justification.
    """

    def __init__(
            self,
            req,  # type: _AnyReqType
            sub_req_item=None,  # type: str
            comments=None,  # type: _AnyLongTextType
    ):  # type: (...) -> None
        """
        Initializes a requirement / test coverage link,
        possibly on a subitem of the requirement,
        and with optional justification comments.

        :param req: Tracked requirement.
        :param sub_req_item: Optional requirement subitem.
        :param comments: Optional justification comments.
        """
        from ._req import Req
        from ._reqdb import REQ_DB
        from ._textutils import anylongtext2str

        #: Requirement identifier.
        self.req = REQ_DB.getreq(req)  # type: Req
        #: Optional requirement subitem.
        self.sub_req_item = sub_req_item  # type: typing.Optional[str]
        #: Attached requirement trackers.
        self.req_trackers = set()  # type: typing.Set[_ReqTrackerType]
        #: Justification comments.
        self.comments = ""  # type: str
        if comments:
            self.comments = anylongtext2str(comments)

    def __repr__(self):  # type: () -> str
        """
        Canonical string representation of the requirement link.
        """
        from ._reflection import qualname

        return "".join([
            f"<{qualname(type(self))}",
            f" req={self.req!r}",
            f" sub_req_item={self.sub_req_item}" if self.sub_req_item else "",
            f" req_trackers={self.req_trackers!r}",
            f" comments={self.comments}" if self.comments else "",
            ">",
        ])

    def __str__(self):  # type: () -> str
        """
        Human readable string representation of the requirement link.
        """
        return "".join([
            self.req.id,
            f"/{self.sub_req_item}" if self.sub_req_item else "",
            " <- ",
            "{", ", ".join([str(_req_tracker) for _req_tracker in self.req_trackers]), "}",
            f" | {self.comments}" if self.comments else "",
        ])

    def matches(
            self,
            req=None,  # type: _AnyReqType
            sub_req_item=None,  # type: str
    ):  # type: (...) -> bool
        """
        Tells whether the given requirement with optional subitem matches this link.

        :param req:
            Optional requirement predicate.
        :param sub_req_item:
            Optional requirement subitem predicate.
            ``None`` for the main of the requirement.
        :return:
            ``True`` in case of a match, ``False`` otherwise.
        """
        from ._reqdb import REQ_DB

        return all([
            (req is None) or (REQ_DB.getreq(req) is self.req),
            (req is None) or (sub_req_item == self.sub_req_item),
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
        # Ensure the link is saved in the requirement link set
        # as soon as it is actually used to link a requirement with trackers.
        self.req.req_links.add(self)

        # Try to save requirement tracker references with this link.
        _first = first  # type: _ReqTrackerType  # Ensure `first` is of type `_ReqTrackerType` (and not `_VarReqTrackerType`).
        for _req_tracker in [_first, *others]:  # type: _ReqTrackerType
            if _req_tracker not in self.req_trackers:
                # New tracker reference.
                self.req_trackers.add(_req_tracker)

                # Link <-> tracker cross-reference.
                _req_tracker.covers(self)

        # Return the first step of the list.
        return first
