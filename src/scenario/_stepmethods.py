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
Step methods management.
"""

import inspect
import types
import typing

if True:
    from ._reflection import qualname as _qualname  # `qualname()` imported once for performance concerns.
if typing.TYPE_CHECKING:
    from ._logger import Logger as _LoggerType


class StepMethods:
    """
    Collection of static methods to help manipulating step methods.
    """

    @staticmethod
    def _hierarchycount(
            logger,  # type: _LoggerType
            method,  # type: types.MethodType
    ):  # type: (...) -> int
        """
        Returns the number of classes in class hierarchy that have this method being declared.

        :param logger: Logger to use for debugging.
        :param method: Method to look for accessibility in class hierarchy.
        :return: Count. The higher, the upper class the method is defined into.

        Used by the :meth:`sortbyhierarchythennames()` and :meth:`sortbyreversehierarchythennames()` methods.
        """
        _count = 0  # type: int
        for _cls in inspect.getmro(method.__self__.__class__):  # type: type
            for _method_name, _method in inspect.getmembers(_cls, predicate=inspect.isfunction):  # type: str, types.MethodType
                if _method_name == method.__name__:
                    _count += 1

        logger.debug("StepMethods._hierarchycount(%s) -> %d", _qualname(method), _count)
        return _count

    @staticmethod
    def _dispmethodlist(
            methods,  # type: typing.List[types.MethodType]
    ):  # type: (...) -> str
        """
        Computes a debug representation of a method list.

        :param methods: Array of methods to debug.
        :return: Debug representation.
        """
        return f"[{', '.join(_qualname(_method) for _method in methods)}]"

    @staticmethod
    def sortbynames(
            logger,  # type: _LoggerType
            methods,  # type: typing.List[types.MethodType]
    ):  # type: (...) -> None
        """
        Sorts an array of methods by method names.

        :param logger: Logger to use for debugging.
        :param methods: Array of methods to sort.
        """
        logger.debug("StepMethods.sortbynames(%s)", StepMethods._dispmethodlist(methods))
        methods.sort(key=lambda method: method.__name__)
        logger.debug("                     -> %s", StepMethods._dispmethodlist(methods))

    @staticmethod
    def sortbyhierarchythennames(
            logger,  # type: _LoggerType
            methods,  # type: typing.List[types.MethodType]
    ):  # type: (...) -> None
        """
        Sorts an array of methods by hierarchy at first, then by method names.

        :param logger: Logger to use for debugging.
        :param methods: Array of methods to sort.

        Makes the methods defined in the higher classes be executed prior to those defined in the lower classes,
        i.e. makes the most specific methods be executed at last.

        Formerly used by *before-test* and *before-step* steps.
        """
        logger.debug("StepMethods.sortbyhierarchythennames(%s)", StepMethods._dispmethodlist(methods))
        # We want to execute the higher class methods at first.
        # When a method is defined in an upper class, its hierarchy count is high.
        # Let's negate the result of :meth:`StepMethods._hierarchycount()` in order to sort the higher class methods at the beginning of the list.
        methods.sort(key=lambda method: (- StepMethods._hierarchycount(logger, method), method.__name__))
        logger.debug("                                  -> %s", StepMethods._dispmethodlist(methods))

    @staticmethod
    def sortbyreversehierarchythennames(
            logger,  # type: _LoggerType
            methods,  # type: typing.List[types.MethodType]
    ):  # type: (...) -> None
        """
        Sorts an array of methods by reverse hierarchy first, then by method names.

        :param logger: Logger to use for debugging.
        :param methods: Array of methods to sort.

        Makes the methods defined in the lower classes be executed prior to those defined in the upper classes,
        i.e. makes the most specific methods be executed at first.

        Formerly used by *after-test* and *after-step* steps.
        """
        logger.debug("StepMethods.sortbyreversehierarchythennames(%s)", StepMethods._dispmethodlist(methods))
        # We want to execute the lower class methods at first.
        # When a method is defined in a lower class, its hierarchy count is low.
        # Do not negate the result of :meth:`StepMethods._hierarchycount()` in order to sort the lower class methods at the beginning of the list.
        methods.sort(key=lambda method: (StepMethods._hierarchycount(logger, method), method.__name__))
        logger.debug("                                         -> %s", StepMethods._dispmethodlist(methods))
