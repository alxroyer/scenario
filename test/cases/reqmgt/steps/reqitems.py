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

import typing

import scenario


class CheckReqItemStep(scenario.Step):

    def checkreqref(
            self,
            req_ref1,  # type: scenario.ReqRef
            req_ref2,  # type: typing.Union[str, typing.Tuple[str, typing.Tuple[str, ...]]]
            evidence=False,  # type: bool
    ):  # type: (...) -> None
        """
        :param req_ref1:
            Requirement reference to check.
        :param req_ref2:
            Expected requirement reference.

            Either a simple requirement reference id, or a detailed tuple of reference id and sub-part specifications.
        :param evidence:
            Evidence flag.
        """
        if isinstance(req_ref2, str):
            self.assertequal(req_ref1.id, req_ref2, evidence=evidence and "Requirement reference id")
        else:
            self.assertequal(req_ref1.req.id, req_ref2[0], evidence=evidence and "Requirement id")
            if not req_ref2[1]:
                self.assertisempty(req_ref1.subs, evidence=evidence and "Requirement sub-part specification")
            else:
                self.assertequal(req_ref1.subs, req_ref2[1], evidence=evidence and "Requirement sub-part specification")
            self.assertequal(req_ref1.id, "/".join([req_ref2[0], *req_ref2[1]]), evidence=evidence and "Requirement reference id")

    def checkreqlink(
            self,
            req_link,  # type: scenario.ReqLink
            req_ref,  # type: typing.Union[str, typing.Tuple[str, typing.Tuple[str, ...]]]
            req_trackers,  # type: typing.Sequence[scenario.ReqTracker]
            comments=None,  # type: str
            evidence=False,  # type: bool
    ):  # type: (...) -> None
        """
        :param req_link: Requirement link to check.
        :param req_ref: Expected requirement reference. See :meth:`checkreqref()` for details.
        :param req_trackers: Expected requirement trackers.
        :param comments: Expected comments. Optional.
        :param evidence: Evidence flag.
        """
        # Check the requirement reference.
        self.checkreqref(req_link.req_ref, req_ref, evidence=evidence)

        # Check trackers.
        self.assertlen(req_link.req_trackers, len(req_trackers), evidence=evidence and (False if req_trackers else "No requirement trackers"))
        for _index, _src_req_tracker in enumerate(req_trackers):  # type: int, scenario.ReqTracker
            self.assertsameinstances(req_link.req_trackers[_index], _src_req_tracker, evidence=evidence and f"Requirement tracker #{_index + 1}")

        # Optionally check comments.
        if comments is not None:
            if comments:
                self.assertequal(req_link.comments, comments, evidence=evidence and "Comments")
            else:
                self.assertisempty(req_link.comments, evidence=evidence and "Comments")
