# -*- coding: utf-8 -*-

# Copyright 2020-2022 Alexis Royer <https://github.com/Alexis-ROYER/scenario>
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
Assertion methods.

The :class:`Assertions` class defines a collection of assertion methods.
"""

import builtins
import re
import typing

# `assertionhelpers` used in method signatures.
from . import assertionhelpers

if typing.TYPE_CHECKING:
    # `AnyPathType` used in method signatures.
    # Type declared for type checking only.
    from .path import AnyPathType
    # `StepExecution` used in method signatures.
    # In order to avoid risks of cylic dependencies in the future, we deliberately choose to import it under `if typing.TYPE_CHECKING:`.
    from .stepexecution import StepExecution
    # `JSONDict` used in method signatures.
    # Type declared for type checking only.
    from .typing import JSONDict

    #: Variable object type.
    VarObjType = typing.TypeVar("VarObjType", bound=object)


class Assertions:
    """
    The :class:`Assertions` class gathers static assertion methods.

    It can be subclasses by classes that onboard these assertion methods,
    like the base :class:`.scenariodefinition.ScenarioDefinition` and :class:`.stepdefinition.StepDefinition` classes.

    See the :ref:`assertion documentation <assertions>` for details.
    """

    # Scenario execution.

    @staticmethod
    def fail(
            err,  # type: str
    ):  # type: (...) -> typing.NoReturn
        """
        Makes the test fail with the given message.

        :param err: Error message.
        """
        assertionhelpers.unittest.fail(err)

    @staticmethod
    def todo(
            err,  # type: str
    ):  # type: (...) -> typing.NoReturn
        """
        Makes the test fail because it is not completely implemented.

        :param err: Error message.
        """
        assertionhelpers.unittest.fail(f"TODO: {err}")

    # General equality.

    @staticmethod
    def assertequal(
            obj1,  # type: typing.Any
            obj2,  # type: typing.Any
            err=None,  # type: assertionhelpers.ErrParamType
            evidence=False,  # type: assertionhelpers.EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks member equality.

        :param obj1: First member.
        :param obj2: Second member.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        from .debugutils import saferepr

        assertionhelpers.unittest.assertEqual(obj1, obj2, err)
        assertionhelpers.evidence(
            evidence,
            "%s == %s", saferepr(obj1), saferepr(obj2),
        )

    @staticmethod
    def assertnotequal(
            obj1,  # type: typing.Any
            obj2,  # type: typing.Any
            err=None,  # type: assertionhelpers.ErrParamType
            evidence=False,  # type: assertionhelpers.EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks member inequality.

        :param obj1: First member.
        :param obj2: Second member.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        from .debugutils import saferepr

        assertionhelpers.unittest.assertNotEqual(obj1, obj2, err)
        assertionhelpers.evidence(
            evidence,
            "%s != %s", saferepr(obj1), saferepr(obj2),
        )

    # Objects.

    @staticmethod
    def assertisnone(
            obj,  # type: typing.Any
            err=None,  # type: assertionhelpers.ErrParamType
            evidence=False,  # type: assertionhelpers.EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks a given value is ``None``.

        :param obj: Value expected to be ``None``.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        assertionhelpers.unittest.assertIsNone(obj, err)
        assertionhelpers.evidence(
            evidence,
            "None as expected",
        )

    @staticmethod
    def assertisnotnone(
            obj,  # type: typing.Optional[VarObjType]
            err=None,  # type: assertionhelpers.ErrParamType
            evidence=False,  # type: assertionhelpers.EvidenceParamType
    ):  # type: (...) -> VarObjType
        """
        Checks a given value is not ``None``.

        :param obj: Value expected to be not ``None``.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        :return: The value ``obj``, ensured not to be ``None``.
        """
        from .debugutils import saferepr

        assertionhelpers.unittest.assertIsNotNone(obj, err)
        assertionhelpers.evidence(
            evidence,
            "%s is not None", saferepr(obj),
        )
        return obj  # type: ignore  ## Incompatible return value type (got "Optional[VarObjType]", expected "VarObjType")

    @staticmethod
    def assertisinstance(
            obj,  # type: typing.Optional[VarObjType]
            type,  # type: assertionhelpers.TypeOrTypesType  # noqa  ## Shadows built-in name 'type'
            err=None,  # type: assertionhelpers.ErrParamType
            evidence=False,  # type: assertionhelpers.EvidenceParamType
    ):  # type: (...) -> VarObjType
        """
        Checks whether the object is of the given type, or one of the given types.

        :param obj: Object to check.
        :param type: Type or list of types to check the object against.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        :return: The value ``obj``, ensured not to be of type ``type``.

        .. note:: As it makes the API convenient, we deliberately shadow the built-in with the ``type`` parameter.
        """
        from .debugutils import saferepr

        assert type is not None, assertionhelpers.isnonemsg("assertisinstance()", "type")
        if not isinstance(type, builtins.type):
            type = tuple(type)  # noqa  ## Shadows built-in name 'type'

        assertionhelpers.unittest.assertIsInstance(obj, type, err)
        assertionhelpers.evidence(
            evidence,
            "%s is an instance of %s", saferepr(obj), saferepr(type),
        )
        return obj  # type: ignore  ## Incompatible return value type (got "Optional[VarObjType]", expected "VarObjType")

    @staticmethod
    def assertisnotinstance(
            obj,  # type: typing.Optional[VarObjType]
            type,  # type: assertionhelpers.TypeOrTypesType  # noqa  ## Shadows built-in name 'type'
            err=None,  # type: assertionhelpers.ErrParamType
            evidence=False,  # type: assertionhelpers.EvidenceParamType
    ):  # type: (...) -> VarObjType
        """
        Checks whether the object is not of the given type, or none of the given types.

        :param obj: Object to check.
        :param type: Type or list of types to check the object against.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).

        .. note:: As it makes the API convenient, we deliberately shadow the built-in with the ``type`` parameter.
        """
        from .debugutils import saferepr

        assert type is not None, assertionhelpers.isnonemsg("assertisnotinstance()", "type")
        if not isinstance(type, builtins.type):
            type = tuple(type)  # noqa  ## Shadows built-in name 'type'

        assertionhelpers.unittest.assertNotIsInstance(obj, type, err)
        assertionhelpers.evidence(
            evidence,
            "%s is not an instance of %s", saferepr(obj), saferepr(type),
        )
        return obj  # type: ignore  ## Incompatible return value type (got "Optional[VarObjType]", expected "VarObjType")

    @staticmethod
    def assertsameinstances(
            obj1,  # type: typing.Optional[object]
            obj2,  # type: typing.Optional[object]
            err=None,  # type: assertionhelpers.ErrParamType
            evidence=False,  # type: assertionhelpers.EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks two Python instances are the same.

        :param obj1: First instance to check.
        :param obj2: Second instance to check.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        from .debugutils import saferepr

        assert obj1 is not None, assertionhelpers.isnonemsg("assertsameinstances()", "obj1")
        assert obj2 is not None, assertionhelpers.isnonemsg("assertsameinstances()", "obj2")

        assert obj1 is obj2, assertionhelpers.errmsg(
            err,
            "instances %s and %s are not the same", saferepr(obj1), saferepr(obj2),
        )
        assertionhelpers.evidence(
            evidence,
            "%s and %s are same instances", saferepr(obj1), saferepr(obj2),
        )

    @staticmethod
    def assertnotsameinstances(
            obj1,  # type: typing.Optional[object]
            obj2,  # type: typing.Optional[object]
            err=None,  # type: assertionhelpers.ErrParamType
            evidence=False,  # type: assertionhelpers.EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks two Python instances are not the same.

        :param obj1: First instance to check.
        :param obj2: Second instance to check.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        from .debugutils import saferepr

        assert obj1 is not None, assertionhelpers.isnonemsg("assertdifferentinstances()", "obj1")
        assert obj2 is not None, assertionhelpers.isnonemsg("assertdifferentinstances()", "obj2")

        assert obj1 is not obj2, assertionhelpers.errmsg(
            err,
            "%s and %s should be different instances", saferepr(obj1), saferepr(obj2),
        )
        assertionhelpers.evidence(
            evidence,
            "%s and %s - different instances", saferepr(obj1), saferepr(obj2),
        )

    # Booleans.

    @staticmethod
    def asserttrue(
            value,  # type: typing.Optional[typing.Any]
            err=None,  # type: assertionhelpers.ErrParamType
            evidence=False,  # type: assertionhelpers.EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks a value is ``True``.

        :param value: Value to check.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        assertionhelpers.unittest.assertTrue(value, err)
        assertionhelpers.evidence(
            evidence,
            "True as expected",
        )

    @staticmethod
    def assertfalse(
            value,  # type: typing.Optional[typing.Any]
            err=None,  # type: assertionhelpers.ErrParamType
            evidence=False,  # type: assertionhelpers.EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks a value is ``False``.

        :param value: Value to check.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        assertionhelpers.unittest.assertFalse(value, err)
        assertionhelpers.evidence(
            evidence,
            "False as expected",
        )

    # Numbers.

    @staticmethod
    def assertless(
            obj1,  # type: typing.Optional[assertionhelpers.ComparableType]
            obj2,  # type: typing.Optional[assertionhelpers.ComparableType]
            err=None,  # type: assertionhelpers.ErrParamType
            evidence=False,  # type: assertionhelpers.EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks a value is strictly less than another.

        :param obj1: Value expected to be below.
        :param obj2: Value expected to be above.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        from .debugutils import saferepr

        assertionhelpers.unittest.assertLess(obj1, obj2, err)
        assertionhelpers.evidence(
            evidence,
            "%s < %s", saferepr(obj1), saferepr(obj2),
        )

    @staticmethod
    def assertlessequal(
            obj1,  # type: typing.Optional[assertionhelpers.ComparableType]
            obj2,  # type: typing.Optional[assertionhelpers.ComparableType]
            err=None,  # type: assertionhelpers.ErrParamType
            evidence=False,  # type: assertionhelpers.EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks a value is less than or equal to another.

        :param obj1: Value expected to be below.
        :param obj2: Value expected to be above.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        from .debugutils import saferepr

        assertionhelpers.unittest.assertLessEqual(obj1, obj2, err)
        assertionhelpers.evidence(
            evidence,
            "%s <= %s", saferepr(obj1), saferepr(obj2),
        )

    @staticmethod
    def assertgreater(
            obj1,  # type: typing.Optional[assertionhelpers.ComparableType]
            obj2,  # type: typing.Optional[assertionhelpers.ComparableType]
            err=None,  # type: assertionhelpers.ErrParamType
            evidence=False,  # type: assertionhelpers.EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks a value is strictly greater than another.

        :param obj1: Value expected to be above.
        :param obj2: Value expected to be below.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        from .debugutils import saferepr

        assertionhelpers.unittest.assertGreater(obj1, obj2, err)
        assertionhelpers.evidence(
            evidence,
            "%s > %s", saferepr(obj1), saferepr(obj2),
        )

    @staticmethod
    def assertgreaterequal(
            obj1,  # type: typing.Optional[assertionhelpers.ComparableType]
            obj2,  # type: typing.Optional[assertionhelpers.ComparableType]
            err=None,  # type: assertionhelpers.ErrParamType
            evidence=False,  # type: assertionhelpers.EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks a value is greater than or equal to another.

        :param obj1: Value expected to be above.
        :param obj2: Value expected to be below.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        from .debugutils import saferepr

        assertionhelpers.unittest.assertGreaterEqual(obj1, obj2, err)
        assertionhelpers.evidence(
            evidence,
            "%s >= %s", saferepr(obj1), saferepr(obj2),
        )

    @staticmethod
    def assertstrictlybetween(
            between,  # type: typing.Optional[assertionhelpers.ComparableType]
            low,  # type: typing.Optional[assertionhelpers.ComparableType]
            high,  # type: typing.Optional[assertionhelpers.ComparableType]
            err=None,  # type: assertionhelpers.ErrParamType
            evidence=False,  # type: assertionhelpers.EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks a value is strictly between two others.

        :param between: Value expected to be between the others.
        :param low: Low value.
        :param high: High value.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        from .debugutils import saferepr

        assert between is not None, assertionhelpers.isnonemsg("assertstrictlybetween()", "between number")
        assert low is not None, assertionhelpers.isnonemsg("assertstrictlybetween()", "low number")
        assert high is not None, assertionhelpers.isnonemsg("assertstrictlybetween()", "high number")

        assert (between > low) and (between < high), assertionhelpers.errmsg(
            err,
            "%s is not strictly between %s and %s", saferepr(between), saferepr(low), saferepr(high),
        )
        assertionhelpers.evidence(
            evidence,
            "%s in ]%s; %s[", saferepr(between), saferepr(low), saferepr(high),
        )

    @staticmethod
    def assertbetweenorequal(
            between,  # type: typing.Optional[assertionhelpers.ComparableType]
            low,  # type: typing.Optional[assertionhelpers.ComparableType]
            high,  # type: typing.Optional[assertionhelpers.ComparableType]
            err=None,  # type: assertionhelpers.ErrParamType
            evidence=False,  # type: assertionhelpers.EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks a value is between or equal to two others.

        :param between: Value expected to be between the others.
        :param low: Low value.
        :param high: High value.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        from .debugutils import saferepr

        assert between is not None, assertionhelpers.isnonemsg("assertbetweenorequal()", "between number")
        assert low is not None, assertionhelpers.isnonemsg("assertbetweenorequal()", "low number")
        assert high is not None, assertionhelpers.isnonemsg("assertbetweenorequal()", "high number")

        assert (between >= low) and (between <= high), assertionhelpers.errmsg(
            err,
            "%s is not between %s and %s", saferepr(between), saferepr(low), saferepr(high),
        )
        assertionhelpers.evidence(
            evidence,
            "%s in [%s; %s]", saferepr(between), saferepr(low), saferepr(high),
        )

    @staticmethod
    def assertnear(
            obj1,  # type: typing.Optional[assertionhelpers.ComparableType]
            obj2,  # type: typing.Optional[assertionhelpers.ComparableType]
            margin,  # type: typing.Optional[assertionhelpers.ComparableType]
            err=None,  # type: assertionhelpers.ErrParamType
            evidence=False,  # type: assertionhelpers.EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks a value is near another oe.

        :param obj1: Value to check.
        :param obj2: Reference value.
        :param margin: Margin of error.
        :param err: Optional error message.
        :param evidence:
        :return: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        from .debugutils import saferepr

        assert obj1 is not None, assertionhelpers.isnonemsg("assertnear()", "value to check")
        assert not isinstance(obj1, str), assertionhelpers.ctxmsg("assertnear()", "value to check should not be a string")
        assert obj2 is not None, assertionhelpers.isnonemsg("assertnear()", "reference value")
        assert not isinstance(obj2, str), assertionhelpers.ctxmsg("assertnear()", "reference value should not be a string")
        assert margin is not None, assertionhelpers.isnonemsg("assertnear()", "margin of error")
        assert not isinstance(margin, str), assertionhelpers.ctxmsg("assertnear()", "margin should not be a string")
        assert float(margin) >= 0.0, assertionhelpers.ctxmsg("assertnear()", "margin of error should not be negative")

        _margin_rate = (margin / obj2) * 100.0  # type: float
        Assertions.assertbetweenorequal(
            between=obj1, low=obj2 - margin, high=obj2 + margin,
            err=assertionhelpers.errmsg(
                err,
                "%s is not near %s (margin: %.1f%% i.e. %s)",
                saferepr(obj1), saferepr(obj2),
                _margin_rate, saferepr(margin),
            ),
            evidence=False,
        )
        assertionhelpers.evidence(
            evidence,
            "%s is near %s (margin: %.1f%% i.e. %s)",
            saferepr(obj1), saferepr(obj2),
            _margin_rate, saferepr(margin),
        )

    # Strings (or bytes).

    @staticmethod
    def assertstartswith(
            string,  # type: typing.Optional[typing.AnyStr]
            start,  # type: typing.Optional[typing.AnyStr]
            err=None,  # type: assertionhelpers.ErrParamType
            evidence=False,  # type: assertionhelpers.EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks a string (or bytes) starts with a given pattern

        :param string: String (or bytes) to check.
        :param start: Expected start pattern.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        from .debugutils import saferepr

        assert string is not None, assertionhelpers.isnonemsg("assertstartswith()", "string")
        assert start is not None, assertionhelpers.isnonemsg("assertstartswith()", "pattern")

        assert string.startswith(start), assertionhelpers.errmsg(
            err,
            "%s does not start with %s", saferepr(string), saferepr(start),
        )
        assertionhelpers.evidence(
            evidence,
            "%s starts with %s", saferepr(string), saferepr(start),
        )

    @staticmethod
    def assertnotstartswith(
            string,  # type: typing.Optional[typing.AnyStr]
            start,  # type: typing.Optional[typing.AnyStr]
            err=None,  # type: assertionhelpers.ErrParamType
            evidence=False,  # type: assertionhelpers.EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks a string (or bytes) does not start with a given pattern.

        :param string: String (or bytes) to check.
        :param start: Unexpected start pattern.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        from .debugutils import saferepr

        assert string is not None, assertionhelpers.isnonemsg("assertnotstartswith()", "string")
        assert start is not None, assertionhelpers.isnonemsg("assertnotstartswith()", "pattern")

        assert not string.startswith(start), assertionhelpers.errmsg(
            err,
            "%s should not start with %s", saferepr(string), saferepr(start),
        )
        assertionhelpers.evidence(
            evidence,
            "%s does not start with %s", saferepr(string), saferepr(start),
        )

    @staticmethod
    def assertendswith(
            string,  # type: typing.Optional[typing.AnyStr]
            end,  # type: typing.Optional[typing.AnyStr]
            err=None,  # type: assertionhelpers.ErrParamType
            evidence=False,  # type: assertionhelpers.EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks a string (or bytes) ends with a given pattern.

        :param string: String (or bytes) to check.
        :param end: Expected end pattern.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        from .debugutils import saferepr

        assert string is not None, assertionhelpers.isnonemsg("assertendswith()", "string")
        assert end is not None, assertionhelpers.isnonemsg("assertendswith()", "pattern")

        assert string.endswith(end), assertionhelpers.errmsg(
            err,
            "%s does not end with %s", saferepr(string), saferepr(end),
        )
        assertionhelpers.evidence(
            evidence,
            "%s ends with %s", saferepr(string), saferepr(end),
        )

    @staticmethod
    def assertnotendswith(
            string,  # type: typing.Optional[typing.AnyStr]
            end,  # type: typing.Optional[typing.AnyStr]
            err=None,  # type: assertionhelpers.ErrParamType
            evidence=False,  # type: assertionhelpers.EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks a string (or bytes) does not end with a given pattern.

        :param string: String (or bytes) to check.
        :param end: Unexpected end pattern.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        from .debugutils import saferepr

        assert string is not None, assertionhelpers.isnonemsg("assertnotendswith()", "string")
        assert end is not None, assertionhelpers.isnonemsg("assertnotendswith()", "pattern")

        assert not string.endswith(end), assertionhelpers.errmsg(
            err,
            "%s should not end with %s", saferepr(string), saferepr(end),
        )
        assertionhelpers.evidence(
            evidence,
            "%s does not end with %s", saferepr(string), saferepr(end),
        )

    @staticmethod
    def assertregex(
            regex,  # type: typing.Optional[typing.AnyStr]
            string,  # type: typing.Optional[typing.AnyStr]
            err=None,  # type: assertionhelpers.ErrParamType
            evidence=False,  # type: assertionhelpers.EvidenceParamType
    ):  # type: (...) -> typing.Match[typing.AnyStr]
        """
        Checks a string (or bytes) matches a regular expression.

        :param regex: Regular expression to match with.
        :param string: String (or bytes) to check.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        :return: :mod:`re` match object.

        .. note::
            The ``regex`` and ``string`` parameters follow the usual order of :mod:`re` functions
            (contrary to :mod:`unittest` ``assertRegex()``).
        """
        from .debugutils import saferepr

        assert regex is not None, assertionhelpers.isnonemsg("assertregex()", "regex")
        assert string is not None, assertionhelpers.isnonemsg("assertregex()", "string")

        _match = re.search(regex, string)  # type: typing.Optional[typing.Match[typing.AnyStr]]
        assert _match, assertionhelpers.errmsg(
            err,
            "Regex did not match: %s not found in %s", saferepr(regex), saferepr(string),
        )
        _matched = string[_match.start():_match.end()]  # type: typing.AnyStr
        if _matched != string:
            assertionhelpers.evidence(
                evidence,
                "%s matches %s in %s", saferepr(_matched), saferepr(regex), saferepr(string, focus=_matched),
            )
        else:
            assertionhelpers.evidence(
                evidence,
                "%s matches %s", saferepr(string), saferepr(regex),
            )
        return _match

    @staticmethod
    def assertnotregex(
            regex,  # type: typing.Optional[typing.AnyStr]
            string,  # type: typing.Optional[typing.AnyStr]
            err=None,  # type: assertionhelpers.ErrParamType
            evidence=False,  # type: assertionhelpers.EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks a string (or bytes) does not match a regular expression.

        :param regex: Regular expression to match with.
        :param string: String (or bytes) to check.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).

        .. note::
            The ``regex`` and ``string`` parameters follow the usual order of :mod:`re` functions
            (contrary to :mod:`unittest` ``assertNotRegex()``).
        """
        from .debugutils import saferepr

        assert regex is not None, assertionhelpers.isnonemsg("assertnotregex()", "regex")
        assert string is not None, assertionhelpers.isnonemsg("assertnotregex()", "string")

        _match = re.search(regex, string)  # type: typing.Optional[typing.Match[typing.AnyStr]]
        if _match:
            _matched = string[_match.start():_match.end()]  # type: typing.AnyStr
            assert False, assertionhelpers.errmsg(
                err,
                "Regex did match: %s matches %s in %s", saferepr(_matched), saferepr(regex), saferepr(string, focus=_matched),
            )
        assertionhelpers.evidence(
            evidence,
            "%s not found in %s", saferepr(regex), saferepr(string),
        )

    # Times.

    @staticmethod
    def asserttimeinstep(
            time,  # type: typing.Optional[float]
            step,  # type: typing.Optional[assertionhelpers.StepExecutionSpecificationType]
            err=None,  # type: assertionhelpers.ErrParamType
            evidence=False,  # type: assertionhelpers.EvidenceParamType
            expect_end_time=True,  # type: bool
    ):  # type: (...) -> StepExecution
        """
        Checks the date/time is within the given step execution times.

        :param time: Date/time to check.
        :param step: Step specification (see :attr:`.assertionhelpers.StepExecutionSpecType`).
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        :param expect_end_time: ``True`` when the step execution is expected to be terminated.
        :return: Step execution that matched the specification.
        """
        from .datetimeutils import f2strtime
        from .debugutils import callback
        from .stepexecution import StepExecution

        assert time is not None, assertionhelpers.isnonemsg("asserttimeinstep()", "time")
        assert step is not None, assertionhelpers.isnonemsg("asserttimeinstep()", "step specification")

        _step_execution = assertionhelpers.getstepexecution(step)  # type: StepExecution
        _step_desc = str(_step_execution.definition)  # type: str
        _start = _step_execution.getstarttime()  # type: float
        _end = _step_execution.getendtime(expect=expect_end_time)  # type: float
        assert time >= _start, assertionhelpers.errmsg(
            err,
            "%s not in %s %s", callback(f2strtime, time), _step_desc, _step_execution.time,
        )
        assert time <= _end, assertionhelpers.errmsg(
            err,
            "%s not in %s %s", callback(f2strtime, time), _step_desc, _step_execution.time,
        )
        assertionhelpers.evidence(
            evidence,
            "%s in %s %s", callback(f2strtime, time), _step_desc, _step_execution.time,
        )

        return _step_execution

    @staticmethod
    def asserttimeinsteps(
            time,  # type: typing.Optional[float]
            start,  # type: typing.Optional[assertionhelpers.StepExecutionSpecificationType]
            end,  # type: typing.Optional[assertionhelpers.StepExecutionSpecificationType]
            err=None,  # type: assertionhelpers.ErrParamType
            evidence=False,  # type: assertionhelpers.EvidenceParamType
            expect_end_time=True,  # type: bool
    ):  # type: (...) -> typing.Tuple[StepExecution, StepExecution]
        """
        Checks the date/time is in the execution times of a given range of steps.

        :param time: Date/time to check.
        :param start: Specification of the first step of the range (see :attr:`.assertionhelpers.StepExecutionSpecType`).
        :param end: Specification of the last step of the range (see :attr:`.assertionhelpers.StepExecutionSpecType`).
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        :param expect_end_time: ``True`` when the ``end`` step execution is expected to be terminated.
        :return: Step execution that matched the ``start`` and ``end`` specifications.
        """
        from .datetimeutils import f2strtime
        from .debugutils import callback
        from .stats import TimeStats

        assert time is not None, assertionhelpers.isnonemsg("asserttimeinsteps()", "time")
        assert start is not None, assertionhelpers.isnonemsg("asserttimeinsteps()", "start step specification")
        assert end is not None, assertionhelpers.isnonemsg("asserttimeinsteps()", "end step specification")

        _step_execution1 = assertionhelpers.getstepexecution(start)  # type: StepExecution
        _step_desc1 = str(_step_execution1.definition)  # type: str
        _start1 = _step_execution1.getstarttime()  # type: float
        _end1 = _step_execution1.getendtime(expect=True)  # type: float
        _step_execution2 = assertionhelpers.getstepexecution(end)  # type: StepExecution
        _step_desc2 = str(_step_execution2.definition)  # type: str
        _start2 = _step_execution2.getstarttime()  # type: float
        _end2 = _step_execution2.getendtime(expect=expect_end_time)  # type: float
        _all = TimeStats()  # type: TimeStats
        _all.start = _start1
        _all.end = _end2
        assert _end1 < _start2, assertionhelpers.ctxmsg(
            "asserttimeinsteps()",
            "%s %s should precede %s %s", _step_desc1, _step_execution1.time, _step_desc2, _step_execution2.time,
        )
        assert time >= _start1, assertionhelpers.errmsg(
            err,
            "%s not in %s->%s %s", callback(f2strtime, time), _step_desc1, _step_desc2, _all,
        )
        assert time <= _end2, assertionhelpers.errmsg(
            err,
            "%s not in %s->%s %s", callback(f2strtime, time), _step_desc1, _step_desc2, _all,
        )
        assertionhelpers.evidence(
            evidence,
            "%s in %s->%s %s", callback(f2strtime, time), _step_desc1, _step_desc2, _all,
        )

        return _step_execution1, _step_execution2

    @staticmethod
    def asserttimebeforestep(
            time,  # type: typing.Optional[float]
            step,  # type: typing.Optional[assertionhelpers.StepExecutionSpecificationType]
            err=None,  # type: assertionhelpers.ErrParamType
            evidence=False,  # type: assertionhelpers.EvidenceParamType
    ):  # type: (...) -> StepExecution
        """
        Checks the date/time is (strictly) before a given step executime time.

        :param time: Date/time to check.
        :param step: Step specification (see :attr:`.assertionhelpers.StepExecutionSpecType`).
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        :return: Step execution that matched the specification.
        """
        from .datetimeutils import f2strtime
        from .debugutils import callback

        assert time is not None, assertionhelpers.isnonemsg("asserttimebeforestep()", "time")
        assert step is not None, assertionhelpers.isnonemsg("asserttimebeforestep()", "step specification")

        _step_execution = assertionhelpers.getstepexecution(step)  # type: StepExecution
        _step_desc = str(_step_execution.definition)  # type: str
        _start = _step_execution.getstarttime()  # type: float
        assert time < _start, assertionhelpers.errmsg(
            err,
            "%s is not before %s %s", callback(f2strtime, time), _step_desc, _step_execution.time,
        )
        assertionhelpers.evidence(
            evidence,
            "%s before %s %s", callback(f2strtime, time), _step_desc, _step_execution.time,
        )

        return _step_execution

    @staticmethod
    def asserttimeafterstep(
            time,  # type: typing.Optional[float]
            step,  # type: typing.Optional[assertionhelpers.StepExecutionSpecificationType]
            err=None,  # type: assertionhelpers.ErrParamType
            evidence=False,  # type: assertionhelpers.EvidenceParamType
    ):  # type: (...) -> StepExecution
        """
        Checks the date/time is (strictly) after a given step executime time.

        :param time: Date/time to check.
        :param step: Step specification (see :attr:`.assertionhelpers.StepExecutionSpecType`).
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        :return: Step execution that matched the specification.
        """
        from .datetimeutils import f2strtime
        from .debugutils import callback

        assert time is not None, assertionhelpers.isnonemsg("asserttimeafterstep()", "time")
        assert step is not None, assertionhelpers.isnonemsg("asserttimeafterstep()", "step specification")

        _step_execution = assertionhelpers.getstepexecution(step)  # type: StepExecution
        _step_desc = str(_step_execution.definition)  # type: str
        _end = _step_execution.getendtime(expect=True)  # type: float
        assert time > _end, assertionhelpers.errmsg(
            err,
            "%s is not after %s %s", callback(f2strtime, time), _step_desc, _step_execution.time,
        )
        assertionhelpers.evidence(
            evidence,
            "%s after %s %s", callback(f2strtime, time), _step_desc, _step_execution.time,
        )

        return _step_execution

    # Containers: strings (or bytes), lists, dictionaries, sets...

    @staticmethod
    def assertisempty(
            obj,  # type: typing.Optional[typing.Iterable[assertionhelpers.ItemType]]
            err=None,  # type: assertionhelpers.ErrParamType
            evidence=False,  # type: assertionhelpers.EvidenceParamType
    ):  # type: (...) -> typing.Iterable[assertionhelpers.ItemType]
        """
        Checks that a container object (string, bytes, list, dictionary, set, ...) is empty.

        :param obj: Container object to check.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        from .assertionhelpers import safecontainer
        from .debugutils import saferepr
        from .reflex import isiterable

        assert obj is not None, assertionhelpers.isnonemsg("assertisempty()", "obj")
        assert isiterable(obj), assertionhelpers.ctxmsg("assertisempty()", "invalid object type %s", saferepr(obj))

        assert not safecontainer(obj), assertionhelpers.errmsg(
            err,
            "%s is not empty", saferepr(obj),
        )
        assertionhelpers.evidence(
            evidence,
            "%s is empty", saferepr(obj),
        )
        return obj

    @staticmethod
    def assertisnotempty(
            obj,  # type: typing.Optional[typing.Iterable[assertionhelpers.ItemType]]
            err=None,  # type: assertionhelpers.ErrParamType
            evidence=False,  # type: assertionhelpers.EvidenceParamType
    ):  # type: (...) -> typing.Iterable[assertionhelpers.ItemType]
        """
        Checks that a container object (string, bytes, list, dictionary, set, ...) is not empty.

        :param obj: Container object to check.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        from .assertionhelpers import safecontainer
        from .debugutils import saferepr
        from .reflex import isiterable

        assert obj is not None, assertionhelpers.isnonemsg("assertisempty()", "obj")
        assert isiterable(obj), assertionhelpers.ctxmsg("assertisnotempty()", "invalid object type %s", saferepr(obj))

        assert safecontainer(obj), assertionhelpers.errmsg(
            err,
            "%s is empty", saferepr(obj),
        )
        assertionhelpers.evidence(
            evidence,
            "%s is not empty", saferepr(obj),
        )
        return obj

    @staticmethod
    def assertlen(
            obj,  # type: typing.Optional[typing.Iterable[assertionhelpers.ItemType]]
            length,  # type: typing.Optional[int]  # noqa
            err=None,  # type: assertionhelpers.ErrParamType
            evidence=False,  # type: assertionhelpers.EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks the length of a container object (string, bytes, list, dictionary, set, ...).

        :param obj: Container object which length to check.
        :param length: Expected length.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        from .assertionhelpers import safecontainer
        from .debugutils import saferepr
        from .reflex import isiterable

        assert obj is not None, assertionhelpers.isnonemsg("assertlen()", "obj")
        assert isiterable(obj), assertionhelpers.ctxmsg("assertlen()", "invalid object type %s", saferepr(obj))
        assert length is not None, assertionhelpers.isnonemsg("assertlen()", "length")

        _len = len(safecontainer(obj))  # type: int
        assert _len == length, assertionhelpers.errmsg(
            err,
            "len(%s) is %d, not %d", saferepr(obj), _len, length,
        )
        assertionhelpers.evidence(
            evidence,
            "Length of %s is %d", saferepr(obj), length,
        )

    @staticmethod
    def assertin(
            obj,  # type: typing.Optional[assertionhelpers.ItemType]
            container,  # type: typing.Optional[typing.Iterable[assertionhelpers.ItemType]]
            err=None,  # type: assertionhelpers.ErrParamType
            evidence=False,  # type: assertionhelpers.EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks a pattern or item is in a container object (string, bytes, list, dictionary, set, ...).

        :param obj: Pattern or item to check in ``container``.
        :param container: Container object.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        from .debugutils import saferepr
        from .reflex import isiterable

        if isinstance(container, (str, bytes)):
            assert obj is not None, assertionhelpers.isnonemsg("assertin()", "obj")
        assert container is not None, assertionhelpers.isnonemsg("assertin()", "container")
        assert isiterable(container), assertionhelpers.ctxmsg("assertin()", "invalid container type %s", saferepr(container))

        # Note 1: The error display proposed by unittest does not truncate the strings, which makes the reading hard.
        # assertionhelpers.unittest.assertIn(obj, container, err)
        # Note 2: Hard to make typings work with the `in` operator below and the variety of types. Use a `typing.cast(Any)` for the purpose.
        assert obj in typing.cast(typing.Any, container), assertionhelpers.errmsg(
            err,
            "%s not in %s", saferepr(obj), saferepr(container, focus=obj),
        )
        assertionhelpers.evidence(
            evidence,
            "%s in %s", saferepr(obj), saferepr(container, focus=obj),
        )

    @staticmethod
    def assertnotin(
            obj,  # type: typing.Optional[assertionhelpers.ItemType]
            container,  # type: typing.Optional[typing.Iterable[assertionhelpers.ItemType]]
            err=None,  # type: assertionhelpers.ErrParamType
            evidence=False,  # type: assertionhelpers.EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks a pattern or item is not in a container object (string, bytes, list, dictionary, set, ...).

        :param obj: Pattern or item to check not in ``container``.
        :param container: Container object.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        from .debugutils import saferepr
        from .reflex import isiterable

        if isinstance(container, (str, bytes)):
            assert obj is not None, assertionhelpers.isnonemsg("assertnotin()", "obj")
        assert container is not None, assertionhelpers.isnonemsg("assertnotin()", "container")
        assert isiterable(container), assertionhelpers.ctxmsg("assertnotin()", "invalid container type %s", saferepr(container))

        # Note 1: The error display proposed by unittest does not truncate the strings (for assertIn() at least), which makes the reading hard.
        # assertionhelpers.unittest.assertNotIn(obj, container, err)
        # Note 2: Hard to make typings work with the `not in` operator below and the variety of types. Use a `typing.cast(Any)` for the purpose.
        assert obj not in typing.cast(typing.Any, container), assertionhelpers.errmsg(
            err,
            "%s in %s", saferepr(obj), saferepr(container, focus=obj),
        )
        assertionhelpers.evidence(
            evidence,
            "%s not in %s", saferepr(obj), saferepr(container, focus=obj),
        )

    @staticmethod
    def assertcount(
            container,  # type: typing.Optional[typing.Iterable[assertionhelpers.ItemType]]
            obj,  # type: typing.Optional[assertionhelpers.ItemType]
            count,  # type: typing.Optional[int]
            err=None,  # type: assertionhelpers.ErrParamType
            evidence=False,  # type: assertionhelpers.EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks a string (or bytes), contains the expected number of patterns,
        or a list, dictionary or set contains the expected number of a given item.

        :param container: String (or bytes), list, dictionary or set that should contain ``obj`` ``count`` times.
        :param obj: Pattern or item to check ``count`` times in ``container``.
        :param count: Expected number of ``obj`` in ``container``.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        from .assertionhelpers import safecontainer
        from .debugutils import saferepr
        from .reflex import isiterable

        assert container is not None, assertionhelpers.isnonemsg("assertcount()", "container")
        assert isiterable(container), assertionhelpers.ctxmsg("assertcount()", "invalid container type %s", saferepr(container))
        assert obj is not None, assertionhelpers.isnonemsg("assertcount()", "obj")
        assert count is not None, assertionhelpers.isnonemsg("assertcount()", "count")

        # Note 2: Hard to make typings work with the `count()` method and the type of `obj`. Use a `typing.cast(Any)` for the purpose.
        _found = safecontainer(container).count(typing.cast(typing.Any, obj))  # type: int
        assert _found == count, assertionhelpers.errmsg(
            err,
            "%s should contain %d count of %s (%d found)", saferepr(container), count, saferepr(obj), _found,
        )
        assertionhelpers.evidence(
            evidence,
            "%s %d time(s) in %s", saferepr(obj), _found, saferepr(container, focus=obj),
        )

    # JSON (or data dictionaries).

    @staticmethod
    def assertjson(
            json_data,  # type: typing.Optional[JSONDict]
            jsonpath,  # type: typing.Optional[str]
            err=None,  # type: assertionhelpers.ErrParamType
            evidence=False,  # type: assertionhelpers.EvidenceParamType
            type=None,  # type: type  # noqa  ## Shadows built-in name 'type'
            value=None,  # type: typing.Union[int, str]
            ref=None,  # type: JSONDict
            count=1,  # type: typing.Optional[int]
            len=None,  # type: int  # noqa  ## Shadows built-in name 'len'
    ):  # type: (...) -> typing.Any
        """
        Checks JSON content.

        :param json_data: Input JSON dictionary.
        :param jsonpath:
            JSONPath.

            Currently a subset of the full syntax (see https://goessner.net/articles/JsonPath/).
        :param err: Optional error message.
        :param evidence: Evidence activation (see :class:`scenario.Assertions`'s documentation).
        :param type: Expected type for the matching elements.
        :param value: Expected value for the matching elements.
        :param ref: Reference JSON dictionary giving the expected value for the given path.
        :param count:
            Expected number of matching elements.

            1 by default. May be set to ``None``.
        :param len:
            Expected length.

            It assumes ``len()`` can be applied on the only searched item, which means that when using ``len``:

            - ``count`` must not be set to anything else but 1 (by default),
            - it is a good practice to specify the expected ``type`` as well (``list`` usually).
        :return:
            The matching element, when ``count`` is 1,
            list of matching elements otherwise.

        .. note:: As it makes the API convenient, we deliberately shadow the built-in with the ``type`` parameter.
        """
        from .debugutils import FmtAndArgs, saferepr
        from .reflex import qualname

        _json_safe_repr_max_length = 32  # type: int

        def _errormsg(fmt, *args):  # type: (str, typing.Any) -> str
            return assertionhelpers.errmsg(
                err,
                f"JSON %s | %s => {fmt}",
                saferepr(json_data, max_length=_json_safe_repr_max_length), saferepr(jsonpath), *args,
            )

        # Check input parameters.
        assert json_data is not None, assertionhelpers.isnonemsg("assertjson()", "json_data")
        assert jsonpath is not None, assertionhelpers.isnonemsg("assertjson()", "jsonpath")
        if (ref is not None) and (value is None):
            # Compute ``value`` from ``ref``: make a recursive call without parameters in order to retrieve the value pointed by ``jsonpath``.
            value = Assertions.assertjson(ref, jsonpath)
            assert isinstance(value, (builtins.type(None), int, str)), _errormsg("Invalid type %s", saferepr(value))

        # Compute the path list.
        _keys = []  # type: typing.List[str]
        for _key in jsonpath.split("."):  # type: str
            _keys.extend(_key.replace("]", "").split("["))

        # Walk through the json structure, following the keys.
        _items = []  # type: typing.List[typing.Any]
        _json_data = json_data  # type: typing.Any
        while _keys:
            _key = _keys.pop(0)
            if re.match(r"-?[0-9]+", _key):
                if not isinstance(_json_data, list):
                    break
                if int(_key) >= 0:
                    if int(_key) >= builtins.len(_json_data):
                        break
                else:
                    if -int(_key) - 1 >= builtins.len(_json_data):
                        break
                _json_data = _json_data[int(_key)]
            else:
                if not isinstance(_json_data, dict):
                    break
                if _key not in _json_data:
                    break
                _json_data = _json_data[_key]
            if not _keys:
                _items.append(_json_data)

        # Check types and values.
        for _item in _items:  # type: typing.Union[JSONDict, int, str]
            if type is not None:
                assert isinstance(_item, type), _errormsg("Wrong type %r, %s expected", _item, qualname(type))
            if value is not None:
                assert _json_data == value, _errormsg("Wrong value %r, %r expected", _item, value)
        # Check the number of matching items.
        if count is not None:
            _error_message = FmtAndArgs()  # type: FmtAndArgs
            if count == 0:
                _error_message.push("Unexpected item, %d found", builtins.len(_items))
            elif count == 1:
                if not _items:
                    _error_message.push("Missing item")
                else:
                    _error_message.push("Too many items, %d found, %d expected", builtins.len(_items), count)
            else:
                _error_message.push("Wrong count of items %d, %d expected", builtins.len(_items), count)
            assert builtins.len(_items) == count, _errormsg(_error_message.fmt, *_error_message.args)
        # Check the length of the item.
        if len is not None:
            assert count == 1, "Cannot specify `len` when expecting several items"
            assert builtins.len(_items[0]) == len, _errormsg(
                "Bad length, len(%s) = %d, %d expected",
                saferepr(_items[0], max_length=_json_safe_repr_max_length),
                builtins.len(_items[0]),
                len,
            )

        # Return value and evidence.
        _res = _items[0] if count == 1 else _items  # type: typing.Any
        _evidence_message = FmtAndArgs()  # type: FmtAndArgs
        if len is not None:
            _evidence_message.push("len(")
        _evidence_message.push("%s | %s", saferepr(json_data, max_length=_json_safe_repr_max_length), saferepr(jsonpath))
        if len is None:
            _evidence_message.push(" => ")
        else:
            _evidence_message.push(" i.e. ")
        _evidence_message.push("%s", saferepr(_res))
        if len is not None:
            _evidence_message.push(") = %d", len)
        assertionhelpers.evidence(evidence, _evidence_message)
        return _res

    # Files.

    @staticmethod
    def assertexists(
            path,  # type: typing.Optional[AnyPathType]
            err=None,  # type: assertionhelpers.ErrParamType
            evidence=False,  # type: assertionhelpers.EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks whether a path exists.

        :param path: Path to check.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        from .path import Path

        assert path is not None, assertionhelpers.isnonemsg("assertexists()", "path")
        if not isinstance(path, Path):
            path = Path(path)

        assert path.exists(), assertionhelpers.errmsg(
            err,
            "'%s' does not exist", path,
        )
        assertionhelpers.evidence(
            evidence,
            "'%s' exists", path,
        )

    @staticmethod
    def assertnotexists(
            path,  # type: typing.Optional[AnyPathType]
            err=None,  # type: assertionhelpers.ErrParamType
            evidence=False,  # type: assertionhelpers.EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks whether a path does not exist.

        :param path: Path to check.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        from .path import Path

        assert path is not None, assertionhelpers.isnonemsg("assertnotexists()", "path")
        if not isinstance(path, Path):
            path = Path(path)

        assert not path.exists(), assertionhelpers.errmsg(
            err,
            "'%s' exists", path,
        )
        assertionhelpers.evidence(
            evidence,
            "'%s' does not exist", path,
        )

    @staticmethod
    def assertisfile(
            path,  # type: typing.Optional[AnyPathType]
            err=None,  # type: assertionhelpers.ErrParamType
            evidence=False,  # type: assertionhelpers.EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks whether a path is a regular file.

        :param path: Path to check.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        from .path import Path

        assert path is not None, assertionhelpers.isnonemsg("assertisfile()", "path")
        if not isinstance(path, Path):
            path = Path(path)

        assert path.is_file(), assertionhelpers.errmsg(
            err,
            "'%s' is not a file", path,
        )
        assertionhelpers.evidence(
            evidence,
            "'%s' is a file", path,
        )

    @staticmethod
    def assertisdir(
            path,  # type: typing.Optional[AnyPathType]
            err=None,  # type: assertionhelpers.ErrParamType
            evidence=False,  # type: assertionhelpers.EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks whether a path is a directory.

        :param path: Path to check.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        from .path import Path

        assert path is not None, assertionhelpers.isnonemsg("assertisdir()", "path")
        if not isinstance(path, Path):
            path = Path(path)

        assert path.is_dir(), assertionhelpers.errmsg(
            err,
            "'%s' is not a directory", path,
        )
        assertionhelpers.evidence(
            evidence,
            "'%s' is a directory", path,
        )

    @staticmethod
    def assertsamepaths(
            path1,  # type: typing.Optional[AnyPathType]
            path2,  # type: typing.Optional[AnyPathType]
            err=None,  # type: assertionhelpers.ErrParamType
            evidence=False,  # type: assertionhelpers.EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks whether two paths are actually the same, even though they may be absolute or relative, or accessed through a symbolic link...

        :param path1: First path to check.
        :param path2: Second path to check.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        from .path import Path

        assert path1 is not None, assertionhelpers.isnonemsg("assertsamepaths()", "path1")
        assert path2 is not None, assertionhelpers.isnonemsg("assertsamepaths()", "path2")
        if not isinstance(path1, Path):
            path1 = Path(path1)
        if not isinstance(path2, Path):
            path2 = Path(path2)

        assert path1.samefile(path2), assertionhelpers.errmsg(
            err,
            "'%s' and '%s' are not the same", path1, path2,
        )
        assertionhelpers.evidence(
            evidence,
            "'%s' and '%s' are the same", path1, path2,
        )

    @staticmethod
    def assertisrelativeto(
            path,  # type: typing.Optional[AnyPathType]
            dir,  # type: typing.Optional[AnyPathType]  # noqa  ## Shadows built-in name 'dir'
            err=None,  # type: assertionhelpers.ErrParamType
            evidence=False,  # type: assertionhelpers.EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks whether a path is a sub-path of a directory.

        :param path: Path to check.
        :param dir: Container directory candidate.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        from .path import Path

        assert path is not None, assertionhelpers.isnonemsg("assertisrelativeto()", "path")
        assert dir is not None, assertionhelpers.isnonemsg("assertisrelativeto()", "dir")
        if not isinstance(path, Path):
            path = Path(path)
        if not isinstance(dir, Path):
            dir = Path(dir)  # noqa  ## Shadows built-in name 'dir'

        assert path.is_relative_to(dir), assertionhelpers.errmsg(
            err,
            "'%s' is not a sub-path of '%s'", path, dir,
        )
        assertionhelpers.evidence(
            evidence,
            "'%s' is a sub-path of '%s'", path, dir,
        )

    @staticmethod
    def assertisnotrelativeto(
            path,  # type: typing.Optional[AnyPathType]
            dir,  # type: typing.Optional[AnyPathType]  # noqa  ## Shadows built-in name 'dir'
            err=None,  # type: assertionhelpers.ErrParamType
            evidence=False,  # type: assertionhelpers.EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks whether a path is not a sub-path of a directory.

        :param path: Path to check.
        :param dir: Directory expected not to be a container directory for ``path``.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        from .path import Path

        assert path is not None, assertionhelpers.isnonemsg("assertisnotrelativeto()", "path")
        assert dir is not None, assertionhelpers.isnonemsg("assertisnotrelativeto()", "dir")
        if not isinstance(path, Path):
            path = Path(path)
        if not isinstance(dir, Path):
            dir = Path(dir)  # noqa  ## Shadows built-in name 'dir'

        assert not path.is_relative_to(dir), assertionhelpers.errmsg(
            err,
            "'%s' is a sub-path of '%s'", path, dir,
        )
        assertionhelpers.evidence(
            evidence,
            "'%s' is not a sub-path of '%s'", path, dir,
        )
