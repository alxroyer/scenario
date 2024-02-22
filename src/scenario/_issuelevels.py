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
Issue levels.
"""

import abc
import enum
import typing

if True:
    from ._fastpath import FAST_PATH as _FAST_PATH  # `FAST_PATH` imported once for performance concerns.


if typing.TYPE_CHECKING:
    #: Known issue level type.
    #:
    #: Issue levels are basically ``int`` values, the higher the more critical.
    #:
    #: In order to attach these levels with useful semantics,
    #: may be passed as `enum.IntEnum` values as well.
    AnyIssueLevelType = typing.Union[int, enum.IntEnum]


class IssueLevel(abc.ABC):
    """
    Abstract class that gathers useful issue level methods.
    """

    #: Named issue levels.
    _named = {}  # type: typing.Dict[str, AnyIssueLevelType]

    @staticmethod
    def definenames(
            named_issue_levels,  # type: typing.Union[typing.Type[enum.IntEnum], typing.Mapping[str, AnyIssueLevelType]]
    ):  # type: (...) -> None
        """
        Defines the named issue level list.

        :param named_issue_levels: New issue level definition.

        Resets names previously defined if any.
        """
        IssueLevel._named.clear()
        for _named in named_issue_levels:  # type: typing.Union[enum.IntEnum, str]
            if isinstance(_named, enum.IntEnum):
                IssueLevel.addname(_named)
            else:
                IssueLevel.addname(_named, named_issue_levels[_named])

    @staticmethod
    @typing.overload
    def addname(
            __issue_level,  # type: enum.IntEnum
    ):  # type: (...) -> None
        """
        Add an issue level name from an ``enum.IntEnum`` value.

        :param __issue_level: Issue level as a ``enum.IntEnum``.
        """

    @staticmethod
    @typing.overload
    def addname(
            __name,  # type: str
            __issue_level,  # type: AnyIssueLevelType
    ):  # type: (...) -> None
        """
        Add an issue level name from a ``str`` name with its corresponding value.

        :param __name: Issue level name.
        :param __issue_level: Issue level value.
        """

    @staticmethod
    def addname(
            arg1,  # type: typing.Union[enum.IntEnum, str]
            arg2=None,  # type: AnyIssueLevelType
    ):  # type: (...) -> None
        """
        Add an issue level name.

        See overloads for argument details.
        """
        if isinstance(arg1, enum.IntEnum):
            IssueLevel._named[arg1.name] = arg1
        else:
            assert arg2 is not None
            if isinstance(arg2, int):
                # Convert the simple `int` as a `enum.IntEnum` value.
                _enum_type_builder = enum.IntEnum  # type: typing.Any  ## Bypass typing issues about dynamic names passed on below.
                _enum_type = _enum_type_builder(str(IssueLevel), {arg1: arg2})  # type: typing.Type[enum.IntEnum]
                arg2 = _enum_type(arg2)
            if isinstance(arg2, enum.IntEnum):
                assert arg2.name == arg1, f"Inconsistent {arg2!r}, name does not match {arg1!r}"
            IssueLevel._named[arg1] = arg2

    @staticmethod
    def getnamed():  # type: (...) -> typing.Mapping[str, int]
        """
        Retrieves the current list of named issue levels.

        :return: Dictionary of {``str`` name => ``int`` issue level}.
        """
        _named = {}  # type: typing.Dict[str, int]
        for _name in IssueLevel._named:  # type: str
            _named[_name] = int(IssueLevel._named[_name])
        return _named

    @staticmethod
    def getnameddesc(
            reverse=False,  # type: bool
    ):  # type: (...) -> str
        """
        Retrieves a textual description for the current list of named issue levels.

        :param reverse: ``True`` to sort names by descending issue levels, ``False`` by default.
        :return: '<name>=<int>' comma separated string, sorted depending on ``reverse``.
        """
        _tuples = [(int(IssueLevel._named[_name]), _name) for _name in IssueLevel._named]  # type: typing.List[typing.Tuple[int, str]]
        return f", ".join([f"{_tuple[1]}={_tuple[0]}" for _tuple in sorted(_tuples, reverse=reverse)])

    @staticmethod
    def getdesc(
            level,  # type: typing.Optional[AnyIssueLevelType]
    ):  # type: (...) -> str
        """
        Retrieves a textual description for the given issue level.

        :param level: Issue level to describe.
        :return: '<name>=<int>' or '<int>' description depending on whether ``level`` is an ``enum.IntEnum`` or an ``int``.
        """
        if level is None:
            return str(None)
        elif isinstance(level, enum.IntEnum):
            return f"{level.name}={level.value}"
        else:
            return str(level)

    @staticmethod
    def parse(
            level,  # type: typing.Optional[typing.Union[str, int]]
    ):  # type: (...) -> typing.Optional[AnyIssueLevelType]
        """
        Converts an optional ``str`` or ``int`` value
        to a ``enum.IntEnum`` if given in the named issue levels,
        or a simple ``int``.

        :param level: ``str`` or ``int`` data to parse.
        :return: ``enum.IntEnum`` or ``int`` value.

        Logs a warning if named issue levels are set
        but the given issue level number does not match with any.
        """
        # `None` => return `None`.
        if level is None:
            return None

        # Try to match strings with named issue levels.
        if isinstance(level, str):
            try:
                return IssueLevel._named[level]
            except KeyError:
                # The string value is not a named issue level.
                # Let's try to analyze it as an ``int`` value.
                level = int(level)

        # Try to match numbers with named issue levels.
        for _name in IssueLevel._named:  # type: str
            if int(IssueLevel._named[_name]) == level:
                return IssueLevel._named[_name]

        # Number not matching with named issue levels.
        if IssueLevel._named:
            _FAST_PATH.main_logger.warning(f"Unknown issue level {level!r}, not in {IssueLevel.getnameddesc()}")

        return level
