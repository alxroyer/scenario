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
Functions and classes for debugging.
"""

import abc
import json
import typing

if typing.TYPE_CHECKING:
    from .typing import JSONDict


class DelayedStr(abc.ABC):
    """
    Abstract class that defines a string which computation can be delayed.

    The main interest of it is to postpone heavy processing,
    so that if ever useless, it is not executed at all.
    """

    def __init__(self):  # type: (...) -> None
        """
        Initializes the string computation result cache.
        """
        #: Cached string computation result.
        self.__str = None  # type: typing.Optional[str]

    def __repr__(self):  # type: (...) -> str
        """
        Canonical string representation.

        This method may be useless.
        Whatever, let's return the canonical representation of the string defined by this object.
        """
        return repr(str(self))

    def __str__(self):  # type: (...) -> str
        """
        Triggers the string computation on the first call, and cache it for later calls.
        """
        if self.__str is None:
            self.__str = self._computestr()
        return self.__str

    @abc.abstractmethod
    def _computestr(self):  # type: (...) -> str
        """
        String computation handler.

        :return:
            String computed for the object.

            Will be cached by :meth:`__str__()`.
        """
        raise NotImplementedError("Not implemented")


class FmtAndArgs(DelayedStr):
    """
    Makes it possible to prepare a string format with its corresponding arguments,
    as usual with the ``%`` operator,
    and have it computed if needed.
    """

    def __init__(
            self,
            fmt="",  # type: str
            *args  # type: typing.Any
    ):  # type: (...) -> None
        """
        Prepares the string format and arguments, possibly with initial values.

        :param fmt: Inital string format.
        :param args: Initial string arguments.
        """
        DelayedStr.__init__(self)

        #: String format.
        self.fmt = fmt  # type: str
        #: Format arguments.
        self.args = list(args)  # type: typing.List[typing.Any]

    def push(
            self,
            fmt,  # type: str
            *args  # type: typing.Any
    ):  # type: (...) -> FmtAndArgs
        """
        Pushes additional format and arguments.

        Makes it possible to prepare the string step by step, and/or conditionally.

        :param fmt: String format to appens.
        :param args: Corresponding arguments.
        :return: ``self``
        """
        self.fmt += fmt
        self.args.extend(args)
        return self

    def _computestr(self):  # type: (...) -> str
        return self.fmt % tuple(self.args)


class SafeRepr(DelayedStr):
    """
    Delays the computation of the safe canonical representation of an object.

    Same as :mod:`unittest`, safe representation means that the string computed while not exceed a given length,
    so that it remains human readable.
    """

    def __init__(
            self,
            obj,  # type: typing.Any
            max_length=256,  # type: int
            focus=None,  # type: typing.Any
    ):  # type: (...) -> None
        """
        Stores the object reference for later safe representation computation.

        :param obj: Object to represent.
        :param max_length: Maximum length for the resulting string.
        :param focus: Data to focus on.
        """
        DelayedStr.__init__(self)

        #: Object to represent.
        self.obj = obj  # type: typing.Any
        #: Maximum length for the resulting string.
        self.max_length = max_length  # type: int
        #: Data to focus on.
        self.focus = focus  # type: typing.Any

    def _computestr(self):  # type: (...) -> str
        # ``focus`` parameter is set.
        if (self.focus is (str, bytes)) and isinstance(self.obj, type(self.focus)):
            _start = 0  # type: int
            _end = len(self.obj)  # type: int
            if len(self.obj) > self.max_length:
                _start = self.obj.find(self.focus)
                _start -= 10
                if _start < 0:
                    _start = 0
                _end = _start + self.max_length
                if _end > len(self.obj):
                    _start -= (_end - len(self.obj))
                    _end = len(self.obj)
            _anystr = type(self.obj)()  # type: typing.Union[str, bytes]
            if _start > 0:
                if isinstance(_anystr, str):
                    _anystr += "...[truncated] "
                if isinstance(_anystr, bytes):
                    _anystr += b'...[truncated] '
            _anystr += self.obj[_start:_end]
            if _end < len(self.obj):
                if isinstance(_anystr, str):
                    _anystr += " [truncated]..."
                if isinstance(_anystr, bytes):
                    _anystr += b' [truncated]...'
            return repr(_anystr)

        # ``focus`` parameter not set.
        # noinspection PyBroadException
        try:
            _repr = repr(self.obj)
        except Exception:
            _repr = object.__repr__(self.obj)
        if len(_repr) <= self.max_length:
            return _repr
        return _repr[:self.max_length] + " [truncated]..." + _repr[-1:]


def saferepr(
        obj,  # type: typing.Any
        max_length=256,  # type: int
        focus=None,  # type: typing.Any
):  # type: (...) -> SafeRepr
    """
    Safe representation of an object.

    :param obj: Object to represent.
    :param max_length: Maximum length for the resulting string.
    :param focus: Data to focus on.
    :return: :class:`SafeRepr` delayed computation object.
    """
    return SafeRepr(obj, max_length=max_length, focus=focus)


class JsonDump(DelayedStr):
    """
    Delays the dump of JSON data.
    """

    def __init__(
            self,
            json_data,  # type: JSONDict
            **kwargs,  # type: typing.Any
    ):  # type: (...) -> None
        """
        Stores the JSON data for later dump.

        :param json_data: JSON data to dump.
        :param kwargs: :func:`json.dumps()`-like arguments.
        """
        DelayedStr.__init__(self)

        #: JSON data to dump.
        self.json_data = json_data  # type: JSONDict
        #: :func:`json.dumps()`-like arguments.
        self.kwargs = kwargs  # type: typing.Dict[str, typing.Any]

    def _computestr(self):  # type: (...) -> str
        return json.dumps(self.json_data, **self.kwargs)


def jsondump(
        json_data,  # type: JSONDict
        **kwargs,  # type: typing.Any
):  # type: (...) -> JsonDump
    """
    Dump of JSON data.

    :param json_data: JSON data to dump.
    :param kwargs: :func:`json.dumps()`-like arguments.
    :return: :class:`JsonDump` delayed computation object.
    """
    return JsonDump(json_data, **kwargs)


class CallbackStr(DelayedStr):
    """
    String builder callback manager.
    """

    def __init__(
            self,
            callback,  # type: typing.Callable[..., str]  # noqa  ## Shadows name 'callback' from outer scope.
            *args,  # type: typing.Any
            **kwargs,  # type: typing.Any
    ):  # type: (...) -> None
        """
        Stores the callback with its arguments for later execution.

        :param callback: String builder callback.
        :param args: Callback positional arguments.
        :param kwargs: Callback named arguments.
        """
        DelayedStr.__init__(self)

        #: String builder callback.
        self.callback = callback  # type: typing.Callable[..., str]
        #: Callback positional arguments.
        self.args = args  # type: typing.Tuple[typing.Any, ...]
        #: Callback named arguments.
        self.kwargs = kwargs  # type: typing.Dict[str, typing.Any]

    def _computestr(self):  # type: (...) -> str
        return self.callback(*self.args, **self.kwargs)


def callback(
        callback,  # type: typing.Callable[..., str]  # noqa  ## Shadows name 'callback' from outer scope.
        *args,  # type: typing.Any
        **kwargs,  # type: typing.Any
):  # type: (...) -> CallbackStr
    """
    Stores a string builder callback with its arguments for later execution.

    :param callback: String builder callback.
    :param args: Callback positional arguments.
    :param kwargs: Callback named arguments.
    :return: :class:`CallbackStr` delayed computation object.
    """
    return CallbackStr(callback, *args, **kwargs)
