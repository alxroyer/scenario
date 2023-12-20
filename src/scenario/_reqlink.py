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
    from ._reqtypes import AnyReqRefType as _AnyReqRefType
    from ._reqtypes import ReqLinkDefType as _ReqLinkDefType
    from ._reqtypes import SetWithReqLinksType as _SetWithReqLinksType
    from ._reqtypes import VarReqVerifierType as _VarReqVerifierType
    from ._reqverifier import ReqVerifier as _ReqVerifierType
    from ._setutils import OrderedSetType as _OrderedSetType
    from ._typeutils import VarItemType as _VarItemType


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

        #: Verified requirement reference.
        #:
        #: Unresolved input data for the :meth:`req_ref()` property.
        self._any_req_ref = ""  # type: _AnyReqRefType
        #: Justification comments.
        self.comments = ""  # type: str
        #: Unordered requirement verifiers tracing the given requirement reference with this link.
        self._req_verifiers = set()  # type: typing.Set[_ReqVerifierType]

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
        from ._reqverifier import ReqVerifierHelper

        return "".join([
            f"<{qualname(type(self))}",
            f" req_ref={self.req_ref!r}",
            f" req_verifiers={[ReqVerifierHelper.tolongstring(_req_verifier) for _req_verifier in self.req_verifiers]!r}",
            f" comments={self.comments!r}" if self.comments else "",
            ">",
        ])

    def __str__(self):  # type: () -> str
        """
        Human readable string representation of the requirement link.
        """
        from ._reqverifier import ReqVerifierHelper

        return "".join([
            str(self.req_ref),
            " <- ",
            "{", ", ".join([ReqVerifierHelper.tolongstring(_req_verifier) for _req_verifier in self.req_verifiers]), "}",
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
        Verified :class:`._req.Req` instance.
        """
        return self.req_ref.req

    @property
    def req_ref(self):  # type: () -> _ReqRefType
        """
        Verified requirement reference.

        Resolution of :attr:`_any_req_ref`.
        """
        from ._reqdb import REQ_DB

        return REQ_DB.getreqref(self._any_req_ref, push_unknown=True)

    @property
    def req_verifiers(self):  # type: () -> _OrderedSetType[_ReqVerifierType]
        """
        Requirement verifiers tracing the given requirement reference with this link.

        See :meth:`._reqverifier.ReqVerifier.orderedset()` for order details.
        """
        from ._reqverifier import ReqVerifier

        return ReqVerifier.orderedset(self._req_verifiers)

    def matches(
            self,
            *,
            req_ref=None,  # type: _AnyReqRefType
            walk_subrefs=False,  # type: bool
            req_verifier=None,  # type: _ReqVerifierType
            walk_steps=False,  # type: bool
    ):  # type: (...) -> bool
        """
        Tells whether the link matches the given predicates.

        :param req_ref:
            Optional requirement reference predicate.
        :param walk_subrefs:
            When ``req_ref`` is a main requirement,
            ``True`` makes the link match if it traces a subreference of the requirement.

            Ignored when ``req_ref`` is not set.
        :param req_verifier:
            Optional requirement verifier predicate.
        :param walk_steps:
            When ``req_verifier`` is a scenario,
            ``True`` makes the link match if it comes from a step of the scenario.

            Ignored when ``req_verifier`` is not set.
        :return:
            ``True`` in case of a match, ``False`` otherwise.

            ``True`` by default when no predicates are set.
        """
        from ._reqdb import REQ_DB
        from ._scenariodefinition import ScenarioDefinition

        # Requirement reference predicates.
        if req_ref is not None:
            req_ref = REQ_DB.getreqref(req_ref)
            if not self.req_ref.matches(req_ref):
                # Requirement reference mismatch.
                if walk_subrefs and req_ref.ismain():
                    # Main requirement reference and `walk_subrefs`.
                    if not any([self.req_ref.matches(_subref) for _subref in req_ref.req.subrefs]):
                        return False
                else:
                    return False

        # Requirement verifier predicates.
        if req_verifier is not None:
            if req_verifier not in self._req_verifiers:
                # Requirement verifier mismatch.
                if walk_steps and isinstance(req_verifier, ScenarioDefinition):
                    # Scenario and `walk_steps`.
                    if not any([(_step in self._req_verifiers) for _step in req_verifier.steps]):
                        return False
                else:
                    return False

        # All predicates passed.
        return True

    def verifiedby(
            self,
            req_verifier,  # type: _VarReqVerifierType
    ):  # type: (...) -> ReqLink
        """
        Adds a requirement verifier that traces the requirement reference with this link.

        :param req_verifier: Requirement verifier that traces the requirement reference with this link.
        :return: ``self``
        """
        from ._reqdb import REQ_DB

        # As soon as the link is actually traced by verifiers:
        # - ensure the database knows the requirement reference (subreferences only),
        if self.req_ref.issubref():
            REQ_DB.push(self.req_ref)
        # - ensure the link is saved in the requirement reference link set,
        if self not in self.req_ref.req_links:
            self.req_ref._req_links.add(self)  # noqa  ## Access to protected member

        # Try to save the requirement verifier with this link.
        if req_verifier not in self.req_verifiers:
            # New requirement verifier.
            self._req_verifiers.add(req_verifier)

            # Debug the downstream requirement link.
            REQ_DB.debug("Requirement link: %s -> %r", self.req_ref.id, req_verifier)

            # Link <-> verifier cross-reference.
            req_verifier.verifies(self)

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
        from ._reqverifier import ReqVerifierHelper

        return (
            req_link.req_ref.id,
            *[ReqVerifierHelper.sortkeyfunction(_req_verifier) for _req_verifier in req_link.req_verifiers],
        )

    @staticmethod
    def buildsetwithreqlinks(
            req_link_holders,  # type: typing.Sequence[typing.Union[_ReqRefType, _ReqVerifierType]]
            items_from_link,  # type: typing.Callable[[ReqLink], typing.Iterable[_VarItemType]]
    ):  # type: (...) -> _SetWithReqLinksType[_VarItemType]
        """
        Builds a set of items with related requirement links.

        :param req_link_holders: List of requirement references or requirement verifiers to walk through.
        :param items_from_link: Function that retrieves the items to save from requirement links.
        """
        _set_with_req_links = {}  # type: _SetWithReqLinksType[_VarItemType]

        # Walk from `req_link_holders` through requirement links and items to save.
        for _req_link_holder in req_link_holders:  # type: typing.Union[_ReqRefType, _ReqVerifierType]
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
