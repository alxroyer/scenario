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


def pluralize(
        singular_word,  # type: str
        count=0,  # type: int
):  # type: (...) -> str
    """
    .. warning::

        Works mainly for nouns, and a small set of other common words.

        Does not work for regular verbs for which the final 's' should be removed...
    """
    if count == 1:
        return singular_word
    else:
        _special_plurals = {
            "has": "have",
            "he": "they",
            "her": "their",
            "his": "their",
            "is": "are",
            "it": "they",
            "its": "their",
            "was": "were",
        }  # type: typing.Dict[str, str]
        if singular_word in _special_plurals:
            return _special_plurals[singular_word]

        if "/" in singular_word:
            return "/".join([pluralize(_word, count) for _word in singular_word.split("/")])

        if singular_word.endswith("s"):
            return singular_word + "es"
        if singular_word.endswith("f"):
            return singular_word[:-1] + "ves"
        if singular_word.endswith("fe"):
            return singular_word[:-2] + "ves"
        return singular_word + "s"


class Countable:
    """
    An instance of :class:`Countable` represents a set of objects that may be several, or just 1, or even 0.

    It provides methods to easily build human readable texts with it, depending on the actual count of objects.

    On the coding side, the plural form is considered by default (except for the :meth:`pluralize()` method argument).
    When the count is actually 1, the text turns to its singular form.

    Example:

    .. code-block:: python

        _keys = scenario.test.text.Countable("key", _count)
        _text = f"The {len(_keys)} {_keys} {_keys.have} been hidden in {_keys.their} respective {_keys.pluralize('lock')}, "
                f"so that {_keys.they} {_keys.are} safe from the dragons."

    When:

        - ``_count == 10``, then ``_text`` is ``"The 10 keys have been hidden in their respective locks, so that they are safe from the dragons."``,
        - ``_count == 1``, then ``_text`` is ``"The 1 key has been hidden in its respective lock, so that it is safe from the dragons."``,
        - ``_count == 0``, then ``_text`` is ``"The 0 keys have been hidden in their respective locks, so that they are safe from the dragons."``.
    """

    def __init__(
            self,
            singular_word,  # type: str
            count_or_iterable,  # type: typing.Optional[typing.Union[int, typing.Iterable[typing.Any]]]
    ):  # type: (...) -> None
        self._singular_word = singular_word  # type: str
        self._count = 0  # type: int
        if count_or_iterable is None:
            self._count = 0
        elif isinstance(count_or_iterable, int):
            self._count = count_or_iterable
        elif isinstance(count_or_iterable, (list, tuple, dict)):
            self._count = len(count_or_iterable)
        else:
            self._count = len(list(count_or_iterable))

    def __len__(self):  # type: (...) -> int
        return self._count

    def __str__(self):  # type: (...) -> str
        return self.pluralize(self._singular_word)

    @property
    def singular(self):  # type: (...) -> str
        return self._singular_word

    @property
    def plural(self):  # type: (...) -> str
        return pluralize(self._singular_word, 0)

    @property
    def are(self):  # type: (...) -> str
        return self.pluralize("is")

    @property
    def have(self):  # type: (...) -> str
        return self.pluralize("has")

    @property
    def their(self):  # type: (...) -> str
        return self.pluralize("its")

    @property
    def they(self):  # type: (...) -> str
        return self.pluralize("it")

    @property
    def were(self):  # type: (...) -> str
        return self.pluralize("was")

    def ifany(
            self,
            if_any,  # type: str
            if_none,  # type: str
    ):  # type: (...) -> str
        if self._count > 0:
            return if_any
        else:
            return if_none

    def pluralize(
            self,
            singular_word,  # type: str
    ):  # type: (...) -> str
        return pluralize(singular_word, self._count)
