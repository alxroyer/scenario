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
Known issues.
"""

import logging
import re
import typing

from ._testerrors import TestError  # `TestError` used for inheritance.

if typing.TYPE_CHECKING:
    from ._issuelevels import AnyIssueLevelType
    from ._logger import Logger as _LoggerType
    from ._typing import JsonDictType


if typing.TYPE_CHECKING:
    #: Issue URL builder type.
    #:
    #: :param:
    #:     The issue as given in known-issue functions.
    #:     Generally a string starting with the '#' character.
    #: :return:
    #:     The URL string on success, ``None`` on failure.
    IssueUrlBuilderType = typing.Callable[[str], typing.Optional[str]]


class KnownIssue(TestError):
    """
    Known issue object.

    May be:

    - considered as an error,
    - considered as a warning,
    - ignored.
    """

    #: URL builder handler configured.
    _url_builder = None  # type: typing.Optional[IssueUrlBuilderType]

    @staticmethod
    def seturlbuilder(
            url_builder,  # type: typing.Optional[IssueUrlBuilderType]
    ):  # type: (...) -> None
        """
        Sets or unsets a URL builder handler.

        :param url_builder:
            URL builder handler to set, or ``None`` to unset.

            This handler shall return a URL string when it succeeded in building an URL for a given issue identifier,
            or ``None`` otherwise.
        """
        KnownIssue._url_builder = url_builder

    def __init__(
            self,
            message,  # type: str
            level=None,  # type: AnyIssueLevelType
            id=None,  # type: str  # noqa  ## Shadows built-in name 'id'
            url=None,  # type: str
    ):  # type: (...) -> None
        """
        Creates a known issue instance from the info given and the current execution stack.

        :param message: Error or warning message to display with.
        :param level: Issue level. Optional.
        :param id: Issue identifier. Optional.
        :param url: Issue URL. Optional.
        """
        from ._issuelevels import IssueLevel
        from ._locations import CodeLocation, EXECUTION_LOCATIONS

        TestError.__init__(
            self,
            message=message,
            location=EXECUTION_LOCATIONS.fromcurrentstack(limit=1, fqn=True)[-1],
        )

        #: Issue level.
        self.level = level  # type: typing.Optional[AnyIssueLevelType]
        if isinstance(self.level, int):
            # Try to match with a named issue level.
            self.level = IssueLevel.parse(self.level)

        #: Issue identifier.
        self.id = id  # type: typing.Optional[str]

        #: Issue URL set, or computed from :attr:`id` and :attr:`_url_builder`.
        self._url = url  # type: typing.Optional[str]

        #: Redefinition of :attr:`._testerrors.TestError.location` in order to explicitize it cannot be ``None`` for :class:`KnownIssue` instances.
        self.location = self.location  # type: CodeLocation

    def __str__(self):  # type: () -> str
        """
        Short representation of the known issue.

        'Issue(({level-name}=){level})( {id})! {message}'.
        """
        from ._issuelevels import IssueLevel

        _str = "Issue"  # type: str
        if self.level is not None:
            _str += f"({IssueLevel.getdesc(self.level)})"
        if self.id is not None:
            _str += f" {self.id}"
        _str += "!"
        _str += f" {self.message}"
        return _str

    @property
    def url(self):  # type: () -> typing.Optional[str]
        """
        Issue URL getter.

        :return: Issue URL if set, ``None`` otherwise.
        """
        if (self._url is None) and (self.id is not None) and KnownIssue._url_builder:
            self._url = KnownIssue._url_builder(self.id)
        return self._url

    @url.setter
    def url(self, url):  # type: (typing.Optional[str]) -> None
        """
        Issue URL setter.

        :param url:
            Issue URL to set. ``None`` to unset.

            .. warning:: When unset and a URL builder is installed, this makes the issue URL fall back to the URL builder result.
        """
        self._url = url

    @staticmethod
    def fromstr(
            string,  # type: str
    ):  # type: (...) -> KnownIssue
        """
        Builds a :class:`KnownIssue` instance from its string representation.

        :param string: String representation, as computed by :meth:`__str__()`.
        :return: New :class:`KnownIssue` instance.
        """
        from ._issuelevels import IssueLevel

        _match = re.match(r"^Issue(\((.+=)?(\d+)\))? *(.*)! (.*)$", string)  # type: typing.Optional[typing.Match[str]]
        assert _match, f"Invalid known issue string ${string!r}"

        return KnownIssue(
            level=(
                IssueLevel.parse(_match.group(2)) if _match.group(2)
                else IssueLevel.parse(_match.group(3)) if _match.group(3)
                else None
            ),
            id=_match.group(4),
            message=_match.group(5),
        )

    def __eq__(
            self,
            other,  # type: typing.Any
    ):  # type: (...) -> bool
        """
        Known isue equality operator.

        :param other: Candidate object.
        :return: ``True`` when known issues hold the same information, ``False`` otherwise.
        """
        if isinstance(other, KnownIssue):
            return (
                (other.level == self.level)
                and (other.id == self.id)
                and (other.message == self.message)
                and (other.location == self.location)
            )
        return False

    def iserror(self):  # type: (...) -> bool
        from ._scenarioconfig import SCENARIO_CONFIG

        _issue_level_error = SCENARIO_CONFIG.issuelevelerror()  # type: typing.Optional[int]
        if _issue_level_error is None:
            # When the error issue level is not set, do not consider known issues as errors by default.
            return False
        if self.level is None:
            # If the error level is set, but the known issue level is not set, consider it is an error (worst case).
            return True
        # When both known issue level and error level are set, compare the two values.
        return int(self.level) >= _issue_level_error

    def iswarning(self):  # type: (...) -> bool
        # Cannot be a warning if already an error.
        if self.iserror():
            return False
        # Not a warning neither if ignored.
        if self.isignored():
            return False
        # Otherwise, known issues are considered as simple warnings by default.
        return True

    def isignored(self):  # type: (...) -> bool
        from ._scenarioconfig import SCENARIO_CONFIG

        # Cannot ignore an error!
        if self.iserror():
            return False

        _issue_level_ignored = SCENARIO_CONFIG.issuelevelignored()  # type: typing.Optional[int]
        if _issue_level_ignored is None:
            # When the ignored issue level is not set, known issues are not ignored by default.
            return False
        if self.level is None:
            # If the known issue level is not set, it cannot be ignored neither.
            return False
        # When both known issue level and ignored level are set, compare the two values.
        return int(self.level) <= _issue_level_ignored

    def logerror(
            self,
            logger,  # type: _LoggerType
            level=logging.WARNING,  # type: int
            indent="",  # type: str
    ):  # type: (...) -> None
        """
        :meth:`._testerrors.TestError.logerror` override in order to display the issue URL on a second line (if any).
        """
        super().logerror(logger=logger, level=level, indent=indent)

        if self.url:
            logger.log(level, f"%s  %s", indent, self.url)

    def tojson(self):  # type: (...) -> JsonDictType
        """
        Converts the :class:`._testerrors.TestError` instance into a JSON dictionary.

        :return: JSON dictionary.
        """
        # Mandatory fields.
        _json = {
            "type": "known-issue",
            "message": self.message,
            "location": self.location.tolongstring(),
        }  # type: JsonDictType

        # Optional fields.
        if self.level is not None:
            _json["level"] = int(self.level)
        if self.id is not None:
            _json["id"] = self.id
        if self.url is not None:
            _json["url"] = self.url

        return _json

    @staticmethod
    def fromjson(
            json_data,  # type: JsonDictType
    ):  # type: (...) -> TestError
        """
        Builds a :class:`KnownIssue` instance from its JSON representation.

        :param json_data: JSON dictionary.
        :return: New :class:`KnownIssue` instance.
        """
        from ._issuelevels import IssueLevel
        from ._locations import CodeLocation

        # Mandatory fields.
        _known_issue = KnownIssue(
            message=json_data["message"],
        )  # type: KnownIssue
        _known_issue.location = CodeLocation.fromlongstring(json_data["location"])

        # Optional fields.
        if "level" in json_data:
            _known_issue.level = IssueLevel.parse(json_data["level"])
        if "id" in json_data:
            _known_issue.id = json_data["id"]
        if "url" in json_data:
            _known_issue.url = json_data["url"]

        return _known_issue
