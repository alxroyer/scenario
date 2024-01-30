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
Assertion methods.

The :class:`Assertions` class defines a collection of assertion methods.
"""

import abc
import builtins
import re
import time
import typing

if True:
    from . import _assertionhelpers as _assertionhelpers  # `_assertionhelpers` used for global instanciation.
    from ._debugutils import callback as _callback  # `callback()` imported once for performance concerns.
    from ._debugutils import FmtAndArgs as _FmtAndArgsImpl  # `FmtAndArgs` imported once for performance concerns.
    from ._debugutils import saferepr as _saferepr  # `saferepr()` imported once for performance concerns.
    from ._path import Path as _PathImpl  # `Path` imported once for performance concerns.
if typing.TYPE_CHECKING:
    from ._assertionhelpers import ErrParamType as _ErrParamType
    from ._assertionhelpers import EvidenceParamType as _EvidenceParamType
    from ._debugutils import FmtAndArgs as _FmtAndArgsType
    from ._jsondictutils import JsonDictType as _JsonDictType
    from ._path import AnyPathType as _AnyPathType
    from ._stepexecution import StepExecution as _StepExecutionType
    from ._stepspecifications import AnyStepExecutionSpecificationType as _AnyStepExecutionSpecificationType
    from ._typeutils import TypeOrTypesType as _TypeOrTypesType
    from ._typeutils import VarComparableType as _VarComparableType
    from ._typeutils import VarItemType as _VarItemType


class Assertions(abc.ABC):
    """
    The :class:`Assertions` class gathers static assertion methods.

    It can be subclasses by classes that onboard these assertion methods,
    like the base :class:`._scenariodefinition.ScenarioDefinition` and :class:`._stepdefinition.StepDefinition` classes.

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
        _assertionhelpers.unittest.fail(err)

    @staticmethod
    def todo(
            err,  # type: str
    ):  # type: (...) -> typing.NoReturn
        """
        Makes the test fail because it is not completely implemented.

        :param err: Error message.
        """
        _assertionhelpers.unittest.fail(f"TODO: {err}")

    # General equality.

    @staticmethod
    def assertequal(
            obj1,  # type: typing.Any
            obj2,  # type: typing.Any
            err=None,  # type: _ErrParamType
            evidence=False,  # type: _EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks member equality.

        :param obj1: First member.
        :param obj2: Second member.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        _assertionhelpers.unittest.assertEqual(obj1, obj2, err)
        _assertionhelpers.evidence(
            evidence,
            "%s == %s", _saferepr(obj1), _saferepr(obj2),
        )

    @staticmethod
    def assertnotequal(
            obj1,  # type: typing.Any
            obj2,  # type: typing.Any
            err=None,  # type: _ErrParamType
            evidence=False,  # type: _EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks member inequality.

        :param obj1: First member.
        :param obj2: Second member.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        _assertionhelpers.unittest.assertNotEqual(obj1, obj2, err)
        _assertionhelpers.evidence(
            evidence,
            "%s != %s", _saferepr(obj1), _saferepr(obj2),
        )

    # Objects.

    @staticmethod
    def assertisnone(
            obj,  # type: typing.Any
            err=None,  # type: _ErrParamType
            evidence=False,  # type: _EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks a given value is ``None``.

        :param obj: Value expected to be ``None``.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        _assertionhelpers.unittest.assertIsNone(obj, err)
        _assertionhelpers.evidence(
            evidence,
            "None as expected",
        )

    @staticmethod
    def assertisnotnone(
            obj,  # type: typing.Optional[_VarItemType]
            err=None,  # type: _ErrParamType
            evidence=False,  # type: _EvidenceParamType
    ):  # type: (...) -> _VarItemType
        """
        Checks a given value is not ``None``.

        :param obj: Value expected to be not ``None``.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        :return: The value ``obj``, ensured not to be ``None``.
        """
        _assertionhelpers.unittest.assertIsNotNone(obj, err)
        _assertionhelpers.evidence(
            evidence,
            "%s is not None", _saferepr(obj),
        )
        return obj  # type: ignore[return-value]  ## "Optional[VarItemType]", expected "VarItemType"

    @staticmethod
    @typing.overload
    def assertisinstance(
            obj,  # type: typing.Any
            type,  # type: typing.Type[_VarItemType]  # noqa  ## Shadows built-in name 'type'
            err=None,  # type: _ErrParamType
            evidence=False,  # type: _EvidenceParamType
    ):  # type: (...) -> _VarItemType
        ...

    @staticmethod
    @typing.overload
    def assertisinstance(
            obj,  # type: typing.Optional[_VarItemType]
            type,  # type: typing.Sequence[type]  # noqa  ## Shadows built-in name 'type'
            err=None,  # type: _ErrParamType
            evidence=False,  # type: _EvidenceParamType
    ):  # type: (...) -> _VarItemType
        ...

    @staticmethod
    def assertisinstance(
            obj,  # type: typing.Any
            type,  # type: _TypeOrTypesType  # noqa  ## Shadows built-in name 'type'
            err=None,  # type: _ErrParamType
            evidence=False,  # type: _EvidenceParamType
    ):  # type: (...) -> typing.Any
        """
        Checks whether the object is of the given type, or one of the given types.

        :param obj: Object to check.
        :param type: Type or list of types to check the object against.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        :return: The value ``obj``, ensured not to be of type ``type``.

        .. note:: As it makes the API convenient, we deliberately shadow the built-in with the ``type`` parameter.
        """
        assert type is not None, _assertionhelpers.isnonemsg("assertisinstance()", "type")
        if not isinstance(type, builtins.type):
            type = tuple(type)  # noqa  ## Shadows built-in name 'type'

        _assertionhelpers.unittest.assertIsInstance(obj, type, err)
        _assertionhelpers.evidence(
            evidence,
            "%s is an instance of %s", _saferepr(obj), _saferepr(type),
        )
        return obj

    @staticmethod
    def assertisnotinstance(
            obj,  # type: typing.Optional[_VarItemType]
            type,  # type: _TypeOrTypesType  # noqa  ## Shadows built-in name 'type'
            err=None,  # type: _ErrParamType
            evidence=False,  # type: _EvidenceParamType
    ):  # type: (...) -> _VarItemType
        """
        Checks whether the object is not of the given type, or none of the given types.

        :param obj: Object to check.
        :param type: Type or list of types to check the object against.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).

        .. note:: As it makes the API convenient, we deliberately shadow the built-in with the ``type`` parameter.
        """
        assert type is not None, _assertionhelpers.isnonemsg("assertisnotinstance()", "type")
        if not isinstance(type, builtins.type):
            type = tuple(type)  # noqa  ## Shadows built-in name 'type'

        _assertionhelpers.unittest.assertNotIsInstance(obj, type, err)
        _assertionhelpers.evidence(
            evidence,
            "%s is not an instance of %s", _saferepr(obj), _saferepr(type),
        )
        return obj  # type: ignore[return-value]  ## "Optional[VarItemType]", expected "VarItemType"

    @staticmethod
    def assertsameinstances(
            obj1,  # type: typing.Optional[object]
            obj2,  # type: typing.Optional[object]
            err=None,  # type: _ErrParamType
            evidence=False,  # type: _EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks two Python instances are the same.

        :param obj1: First instance to check.
        :param obj2: Second instance to check.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        assert obj1 is not None, _assertionhelpers.isnonemsg("assertsameinstances()", "obj1")
        assert obj2 is not None, _assertionhelpers.isnonemsg("assertsameinstances()", "obj2")

        assert obj1 is obj2, _assertionhelpers.errmsg(
            err,
            "instances %s and %s are not the same", _saferepr(obj1), _saferepr(obj2),
        )
        _assertionhelpers.evidence(
            evidence,
            "%s and %s are same instances", _saferepr(obj1), _saferepr(obj2),
        )

    @staticmethod
    def assertnotsameinstances(
            obj1,  # type: typing.Optional[object]
            obj2,  # type: typing.Optional[object]
            err=None,  # type: _ErrParamType
            evidence=False,  # type: _EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks two Python instances are not the same.

        :param obj1: First instance to check.
        :param obj2: Second instance to check.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        assert obj1 is not None, _assertionhelpers.isnonemsg("assertdifferentinstances()", "obj1")
        assert obj2 is not None, _assertionhelpers.isnonemsg("assertdifferentinstances()", "obj2")

        assert obj1 is not obj2, _assertionhelpers.errmsg(
            err,
            "%s and %s should be different instances", _saferepr(obj1), _saferepr(obj2),
        )
        _assertionhelpers.evidence(
            evidence,
            "%s and %s - different instances", _saferepr(obj1), _saferepr(obj2),
        )

    # Booleans.

    @staticmethod
    def asserttrue(
            value,  # type: typing.Optional[typing.Any]
            err=None,  # type: _ErrParamType
            evidence=False,  # type: _EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks a value is ``True``.

        :param value: Value to check.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        _assertionhelpers.unittest.assertTrue(value, err)
        _assertionhelpers.evidence(
            evidence,
            "True as expected",
        )

    @staticmethod
    def assertfalse(
            value,  # type: typing.Optional[typing.Any]
            err=None,  # type: _ErrParamType
            evidence=False,  # type: _EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks a value is ``False``.

        :param value: Value to check.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        _assertionhelpers.unittest.assertFalse(value, err)
        _assertionhelpers.evidence(
            evidence,
            "False as expected",
        )

    # Numbers.

    @staticmethod
    def assertless(
            obj1,  # type: typing.Optional[_VarComparableType]
            obj2,  # type: typing.Optional[_VarComparableType]
            err=None,  # type: _ErrParamType
            evidence=False,  # type: _EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks a value is strictly less than another.

        :param obj1: Value expected to be below.
        :param obj2: Value expected to be above.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        assert obj1 is not None, _assertionhelpers.isnonemsg("assertless()", "obj1")
        assert obj2 is not None, _assertionhelpers.isnonemsg("assertless()", "obj2")

        _assertionhelpers.unittest.assertLess(obj1, obj2, err)
        _assertionhelpers.evidence(
            evidence,
            "%s < %s", _saferepr(obj1), _saferepr(obj2),
        )

    @staticmethod
    def assertlessequal(
            obj1,  # type: typing.Optional[_VarComparableType]
            obj2,  # type: typing.Optional[_VarComparableType]
            err=None,  # type: _ErrParamType
            evidence=False,  # type: _EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks a value is less than or equal to another.

        :param obj1: Value expected to be below.
        :param obj2: Value expected to be above.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        assert obj1 is not None, _assertionhelpers.isnonemsg("assertlessequal()", "obj1")
        assert obj2 is not None, _assertionhelpers.isnonemsg("assertlessequal()", "obj2")

        _assertionhelpers.unittest.assertLessEqual(obj1, obj2, err)
        _assertionhelpers.evidence(
            evidence,
            "%s <= %s", _saferepr(obj1), _saferepr(obj2),
        )

    @staticmethod
    def assertgreater(
            obj1,  # type: typing.Optional[_VarComparableType]
            obj2,  # type: typing.Optional[_VarComparableType]
            err=None,  # type: _ErrParamType
            evidence=False,  # type: _EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks a value is strictly greater than another.

        :param obj1: Value expected to be above.
        :param obj2: Value expected to be below.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        assert obj1 is not None, _assertionhelpers.isnonemsg("assertgreater()", "obj1")
        assert obj2 is not None, _assertionhelpers.isnonemsg("assertgreater()", "obj2")

        _assertionhelpers.unittest.assertGreater(obj1, obj2, err)
        _assertionhelpers.evidence(
            evidence,
            "%s > %s", _saferepr(obj1), _saferepr(obj2),
        )

    @staticmethod
    def assertgreaterequal(
            obj1,  # type: typing.Optional[_VarComparableType]
            obj2,  # type: typing.Optional[_VarComparableType]
            err=None,  # type: _ErrParamType
            evidence=False,  # type: _EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks a value is greater than or equal to another.

        :param obj1: Value expected to be above.
        :param obj2: Value expected to be below.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        assert obj1 is not None, _assertionhelpers.isnonemsg("assertgreaterequal()", "obj1")
        assert obj2 is not None, _assertionhelpers.isnonemsg("assertgreaterequal()", "obj2")

        _assertionhelpers.unittest.assertGreaterEqual(obj1, obj2, err)
        _assertionhelpers.evidence(
            evidence,
            "%s >= %s", _saferepr(obj1), _saferepr(obj2),
        )

    @staticmethod
    def assertstrictlybetween(
            between,  # type: typing.Optional[_VarComparableType]
            low,  # type: typing.Optional[_VarComparableType]
            high,  # type: typing.Optional[_VarComparableType]
            err=None,  # type: _ErrParamType
            evidence=False,  # type: _EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks a value is strictly between two others.

        :param between: Value expected to be between the others.
        :param low: Low value.
        :param high: High value.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        assert between is not None, _assertionhelpers.isnonemsg("assertstrictlybetween()", "between")
        assert low is not None, _assertionhelpers.isnonemsg("assertstrictlybetween()", "low")
        assert high is not None, _assertionhelpers.isnonemsg("assertstrictlybetween()", "high")

        assert (between > low) and (between < high), _assertionhelpers.errmsg(
            err,
            "%s is not strictly between %s and %s", _saferepr(between), _saferepr(low), _saferepr(high),
        )
        _assertionhelpers.evidence(
            evidence,
            "%s in ]%s; %s[", _saferepr(between), _saferepr(low), _saferepr(high),
        )

    @staticmethod
    def assertbetweenorequal(
            between,  # type: typing.Optional[_VarComparableType]
            low,  # type: typing.Optional[_VarComparableType]
            high,  # type: typing.Optional[_VarComparableType]
            err=None,  # type: _ErrParamType
            evidence=False,  # type: _EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks a value is between or equal to two others.

        :param between: Value expected to be between the others.
        :param low: Low value.
        :param high: High value.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        assert between is not None, _assertionhelpers.isnonemsg("assertbetweenorequal()", "between")
        assert low is not None, _assertionhelpers.isnonemsg("assertbetweenorequal()", "low")
        assert high is not None, _assertionhelpers.isnonemsg("assertbetweenorequal()", "high")

        assert (between >= low) and (between <= high), _assertionhelpers.errmsg(
            err,
            "%s is not between %s and %s", _saferepr(between), _saferepr(low), _saferepr(high),
        )
        _assertionhelpers.evidence(
            evidence,
            "%s in [%s; %s]", _saferepr(between), _saferepr(low), _saferepr(high),
        )

    @staticmethod
    def assertnear(
            obj1,  # type: typing.Optional[_VarComparableType]
            obj2,  # type: typing.Optional[_VarComparableType]
            margin,  # type: typing.Optional[_VarComparableType]
            err=None,  # type: _ErrParamType
            evidence=False,  # type: _EvidenceParamType
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
        assert obj1 is not None, _assertionhelpers.isnonemsg("assertnear()", "obj1")
        assert not isinstance(obj1, str), _assertionhelpers.ctxmsg("assertnear()", "obj1 should not be a string")
        assert isinstance(obj1, (int, float))  # Should be obvious... Whatever, let's help the type checker.
        assert obj2 is not None, _assertionhelpers.isnonemsg("assertnear()", "obj2")
        assert not isinstance(obj2, str), _assertionhelpers.ctxmsg("assertnear()", "obj2 should not be a string")
        assert isinstance(obj2, (int, float))  # Should be obvious... Whatever, let's help the type checker.
        assert margin is not None, _assertionhelpers.isnonemsg("assertnear()", "margin")
        assert not isinstance(margin, str), _assertionhelpers.ctxmsg("assertnear()", "margin should not be a string")
        assert isinstance(margin, (int, float))  # Should be obvious... Whatever, let's help the type checker.
        assert float(margin) >= 0.0, _assertionhelpers.ctxmsg("assertnear()", "margin should not be negative")

        _margin_rate = (margin / obj2) * 100.0  # type: float
        Assertions.assertbetweenorequal(
            between=obj1, low=obj2 - margin, high=obj2 + margin,
            err=_assertionhelpers.errmsg(
                err,
                "%s is not near %s (margin: %.1f%% i.e. %s)",
                _saferepr(obj1), _saferepr(obj2),
                _margin_rate, _saferepr(margin),
            ),
            evidence=False,
        )
        _assertionhelpers.evidence(
            evidence,
            "%s is near %s (margin: %.1f%% i.e. %s)",
            _saferepr(obj1), _saferepr(obj2),
            _margin_rate, _saferepr(margin),
        )

    # Strings (or bytes).

    @staticmethod
    def assertstartswith(
            string,  # type: typing.Optional[typing.AnyStr]
            start,  # type: typing.Optional[typing.AnyStr]
            err=None,  # type: _ErrParamType
            evidence=False,  # type: _EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks a string (or bytes) starts with a given pattern

        :param string: String (or bytes) to check.
        :param start: Expected start pattern.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        assert string is not None, _assertionhelpers.isnonemsg("assertstartswith()", "string")
        assert start is not None, _assertionhelpers.isnonemsg("assertstartswith()", "pattern")

        assert string.startswith(start), _assertionhelpers.errmsg(
            err,
            "%s does not start with %s", _saferepr(string), _saferepr(start),
        )
        _assertionhelpers.evidence(
            evidence,
            "%s starts with %s", _saferepr(string), _saferepr(start),
        )

    @staticmethod
    def assertnotstartswith(
            string,  # type: typing.Optional[typing.AnyStr]
            start,  # type: typing.Optional[typing.AnyStr]
            err=None,  # type: _ErrParamType
            evidence=False,  # type: _EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks a string (or bytes) does not start with a given pattern.

        :param string: String (or bytes) to check.
        :param start: Unexpected start pattern.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        assert string is not None, _assertionhelpers.isnonemsg("assertnotstartswith()", "string")
        assert start is not None, _assertionhelpers.isnonemsg("assertnotstartswith()", "pattern")

        assert not string.startswith(start), _assertionhelpers.errmsg(
            err,
            "%s should not start with %s", _saferepr(string), _saferepr(start),
        )
        _assertionhelpers.evidence(
            evidence,
            "%s does not start with %s", _saferepr(string), _saferepr(start),
        )

    @staticmethod
    def assertendswith(
            string,  # type: typing.Optional[typing.AnyStr]
            end,  # type: typing.Optional[typing.AnyStr]
            err=None,  # type: _ErrParamType
            evidence=False,  # type: _EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks a string (or bytes) ends with a given pattern.

        :param string: String (or bytes) to check.
        :param end: Expected end pattern.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        assert string is not None, _assertionhelpers.isnonemsg("assertendswith()", "string")
        assert end is not None, _assertionhelpers.isnonemsg("assertendswith()", "pattern")

        assert string.endswith(end), _assertionhelpers.errmsg(
            err,
            "%s does not end with %s", _saferepr(string), _saferepr(end),
        )
        _assertionhelpers.evidence(
            evidence,
            "%s ends with %s", _saferepr(string), _saferepr(end),
        )

    @staticmethod
    def assertnotendswith(
            string,  # type: typing.Optional[typing.AnyStr]
            end,  # type: typing.Optional[typing.AnyStr]
            err=None,  # type: _ErrParamType
            evidence=False,  # type: _EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks a string (or bytes) does not end with a given pattern.

        :param string: String (or bytes) to check.
        :param end: Unexpected end pattern.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        assert string is not None, _assertionhelpers.isnonemsg("assertnotendswith()", "string")
        assert end is not None, _assertionhelpers.isnonemsg("assertnotendswith()", "pattern")

        assert not string.endswith(end), _assertionhelpers.errmsg(
            err,
            "%s should not end with %s", _saferepr(string), _saferepr(end),
        )
        _assertionhelpers.evidence(
            evidence,
            "%s does not end with %s", _saferepr(string), _saferepr(end),
        )

    @staticmethod
    def assertregex(
            regex,  # type: typing.Optional[typing.AnyStr]
            string,  # type: typing.Optional[typing.AnyStr]
            err=None,  # type: _ErrParamType
            evidence=False,  # type: _EvidenceParamType
    ):  # type: (...) -> typing.Match[typing.AnyStr]
        """
        Checks a string (or bytes) matches a regular expression.

        :param regex: Regular expression to match with.
        :param string: String (or bytes) to check.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        :return: ``re`` match object.

        .. note::
            The ``regex`` and ``string`` parameters follow the usual order of ``re`` functions
            (contrary to ``unittest`` ``assertRegex()``).
        """
        assert regex is not None, _assertionhelpers.isnonemsg("assertregex()", "regex")
        assert string is not None, _assertionhelpers.isnonemsg("assertregex()", "string")

        _match = re.search(regex, string)  # type: typing.Optional[typing.Match[typing.AnyStr]]
        assert _match, _assertionhelpers.errmsg(
            err,
            "Regex did not match: %s not found in %s", _saferepr(regex), _saferepr(string),
        )
        _matched = string[_match.start():_match.end()]  # type: typing.AnyStr
        if _matched != string:
            _assertionhelpers.evidence(
                evidence,
                "%s matches %s in %s", _saferepr(_matched), _saferepr(regex), _saferepr(string, focus=_matched),
            )
        else:
            _assertionhelpers.evidence(
                evidence,
                "%s matches %s", _saferepr(string), _saferepr(regex),
            )
        return _match

    @staticmethod
    def assertnotregex(
            regex,  # type: typing.Optional[typing.AnyStr]
            string,  # type: typing.Optional[typing.AnyStr]
            err=None,  # type: _ErrParamType
            evidence=False,  # type: _EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks a string (or bytes) does not match a regular expression.

        :param regex: Regular expression to match with.
        :param string: String (or bytes) to check.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).

        .. note::
            The ``regex`` and ``string`` parameters follow the usual order of ``re`` functions
            (contrary to ``unittest`` ``assertNotRegex()``).
        """
        assert regex is not None, _assertionhelpers.isnonemsg("assertnotregex()", "regex")
        assert string is not None, _assertionhelpers.isnonemsg("assertnotregex()", "string")

        _match = re.search(regex, string)  # type: typing.Optional[typing.Match[typing.AnyStr]]
        if _match:
            _matched = string[_match.start():_match.end()]  # type: typing.AnyStr
            assert False, _assertionhelpers.errmsg(
                err,
                "Regex did match: %s matches %s in %s", _saferepr(_matched), _saferepr(regex), _saferepr(string, focus=_matched),
            )
        _assertionhelpers.evidence(
            evidence,
            "%s not found in %s", _saferepr(regex), _saferepr(string),
        )

    # Times.

    @staticmethod
    def asserttimeinstep(
            time,  # type: typing.Optional[float]  # noqa  ## Shadows name 'time' from outer scope
            step,  # type: typing.Optional[_AnyStepExecutionSpecificationType]
            err=None,  # type: _ErrParamType
            evidence=False,  # type: _EvidenceParamType
            expect_end_time=True,  # type: bool
    ):  # type: (...) -> _StepExecutionType
        """
        Checks the date/time is within the given step execution times.

        :param time: Date/time to check.
        :param step: Step specification (see :obj:`._stepspecifications.AnyStepExecutionSpecificationType`).
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        :param expect_end_time: ``True`` when the step execution is expected to be terminated.
        :return: Step execution that matched the specification.
        """
        from ._datetimeutils import f2strtime
        from ._stepspecifications import StepExecutionSpecification

        assert time is not None, _assertionhelpers.isnonemsg("asserttimeinstep()", "time")
        assert step is not None, _assertionhelpers.isnonemsg("asserttimeinstep()", "step specification")
        if not isinstance(step, StepExecutionSpecification):
            step = StepExecutionSpecification(step)

        _step_execution = step.expect()  # type: _StepExecutionType
        _step_desc = str(_step_execution.definition)  # type: str
        _start = _AssertionHelperFunctions.getstepstarttime(_step_execution)  # type: float
        _end = _AssertionHelperFunctions.getstependtime(_step_execution, expect=expect_end_time)  # type: float
        assert _start <= time <= _end, _assertionhelpers.errmsg(
            err,
            "%s not in %s %s", _callback(f2strtime, time), _step_desc, _step_execution.time,
        )
        _assertionhelpers.evidence(
            evidence,
            "%s in %s %s", _callback(f2strtime, time), _step_desc, _step_execution.time,
        )

        return _step_execution

    @staticmethod
    def asserttimeinsteps(
            time,  # type: typing.Optional[float]  # noqa  ## Shadows name 'time' from outer scope
            start,  # type: typing.Optional[_AnyStepExecutionSpecificationType]
            end,  # type: typing.Optional[_AnyStepExecutionSpecificationType]
            err=None,  # type: _ErrParamType
            evidence=False,  # type: _EvidenceParamType
            expect_end_time=True,  # type: bool
    ):  # type: (...) -> typing.Tuple[_StepExecutionType, _StepExecutionType]
        """
        Checks the date/time is in the execution times of a given range of steps.

        :param time: Date/time to check.
        :param start: Specification of the first step of the range (see :obj:`._stepspecifications.AnyStepExecutionSpecificationType`).
        :param end: Specification of the last step of the range (see :obj:`._stepspecifications.AnyStepExecutionSpecificationType`).
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        :param expect_end_time: ``True`` when the ``end`` step execution is expected to be terminated.
        :return: Step execution that matched the ``start`` and ``end`` specifications.
        """
        from ._datetimeutils import f2strtime
        from ._stats import TimeStats
        from ._stepspecifications import StepExecutionSpecification

        assert time is not None, _assertionhelpers.isnonemsg("asserttimeinsteps()", "time")
        assert start is not None, _assertionhelpers.isnonemsg("asserttimeinsteps()", "start step specification")
        if not isinstance(start, StepExecutionSpecification):
            start = StepExecutionSpecification(start)
        assert end is not None, _assertionhelpers.isnonemsg("asserttimeinsteps()", "end step specification")
        if not isinstance(end, StepExecutionSpecification):
            end = StepExecutionSpecification(end)

        _step_execution1 = start.expect()  # type: _StepExecutionType
        _step_desc1 = str(_step_execution1.definition)  # type: str
        _start1 = _AssertionHelperFunctions.getstepstarttime(_step_execution1)  # type: float
        _end1 = _AssertionHelperFunctions.getstependtime(_step_execution1, expect=True)  # type: float
        _step_execution2 = end.expect()  # type: _StepExecutionType
        _step_desc2 = str(_step_execution2.definition)  # type: str
        _start2 = _AssertionHelperFunctions.getstepstarttime(_step_execution2)  # type: float
        _end2 = _AssertionHelperFunctions.getstependtime(_step_execution2, expect=expect_end_time)  # type: float
        _all = TimeStats()  # type: TimeStats
        _all.start = _start1
        _all.end = _end2
        assert _end1 < _start2, _assertionhelpers.ctxmsg(
            "asserttimeinsteps()",
            "%s %s should precede %s %s", _step_desc1, _step_execution1.time, _step_desc2, _step_execution2.time,
        )
        assert _start1 <= time <= _end2, _assertionhelpers.errmsg(
            err,
            "%s not in %s->%s %s", _callback(f2strtime, time), _step_desc1, _step_desc2, _all,
        )
        _assertionhelpers.evidence(
            evidence,
            "%s in %s->%s %s", _callback(f2strtime, time), _step_desc1, _step_desc2, _all,
        )

        return _step_execution1, _step_execution2

    @staticmethod
    def asserttimebeforestep(
            time,  # type: typing.Optional[float]  # noqa  ## Shadows name 'time' from outer scope
            step,  # type: typing.Optional[_AnyStepExecutionSpecificationType]
            err=None,  # type: _ErrParamType
            evidence=False,  # type: _EvidenceParamType
    ):  # type: (...) -> _StepExecutionType
        """
        Checks the date/time is (strictly) before a given step executime time.

        :param time: Date/time to check.
        :param step: Step specification (see :obj:`._stepspecifications.AnyStepExecutionSpecificationType`).
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        :return: Step execution that matched the specification.
        """
        from ._datetimeutils import f2strtime
        from ._stepspecifications import StepExecutionSpecification

        assert time is not None, _assertionhelpers.isnonemsg("asserttimebeforestep()", "time")
        assert step is not None, _assertionhelpers.isnonemsg("asserttimebeforestep()", "step specification")
        if not isinstance(step, StepExecutionSpecification):
            step = StepExecutionSpecification(step)

        _step_execution = step.expect()  # type: _StepExecutionType
        _step_desc = str(_step_execution.definition)  # type: str
        _start = _AssertionHelperFunctions.getstepstarttime(_step_execution)  # type: float
        assert time < _start, _assertionhelpers.errmsg(
            err,
            "%s is not before %s %s", _callback(f2strtime, time), _step_desc, _step_execution.time,
        )
        _assertionhelpers.evidence(
            evidence,
            "%s before %s %s", _callback(f2strtime, time), _step_desc, _step_execution.time,
        )

        return _step_execution

    @staticmethod
    def asserttimeafterstep(
            time,  # type: typing.Optional[float]  # noqa  ## Shadows name 'time' from outer scope
            step,  # type: typing.Optional[_AnyStepExecutionSpecificationType]
            err=None,  # type: _ErrParamType
            evidence=False,  # type: _EvidenceParamType
    ):  # type: (...) -> _StepExecutionType
        """
        Checks the date/time is (strictly) after a given step executime time.

        :param time: Date/time to check.
        :param step: Step specification (see :obj:`._stepspecifications.AnyStepExecutionSpecificationType`).
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        :return: Step execution that matched the specification.
        """
        from ._datetimeutils import f2strtime
        from ._stepspecifications import StepExecutionSpecification

        assert time is not None, _assertionhelpers.isnonemsg("asserttimeafterstep()", "time")
        assert step is not None, _assertionhelpers.isnonemsg("asserttimeafterstep()", "step specification")
        if not isinstance(step, StepExecutionSpecification):
            step = StepExecutionSpecification(step)

        _step_execution = step.expect()  # type: _StepExecutionType
        _step_desc = str(_step_execution.definition)  # type: str
        _end = _AssertionHelperFunctions.getstependtime(_step_execution, expect=True)  # type: float
        assert time > _end, _assertionhelpers.errmsg(
            err,
            "%s is not after %s %s", _callback(f2strtime, time), _step_desc, _step_execution.time,
        )
        _assertionhelpers.evidence(
            evidence,
            "%s after %s %s", _callback(f2strtime, time), _step_desc, _step_execution.time,
        )

        return _step_execution

    # Containers: strings (or bytes), lists, dictionaries, sets...

    @staticmethod
    def assertisempty(
            obj,  # type: typing.Optional[typing.Iterable[_VarItemType]]
            err=None,  # type: _ErrParamType
            evidence=False,  # type: _EvidenceParamType
    ):  # type: (...) -> typing.Iterable[_VarItemType]
        """
        Checks that a container object (string, bytes, list, dictionary, set, ...) is empty.

        :param obj: Container object to check.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        from ._reflection import isiterable

        assert obj is not None, _assertionhelpers.isnonemsg("assertisempty()", "obj")
        assert isiterable(obj), _assertionhelpers.ctxmsg("assertisempty()", "invalid object type %s", _saferepr(obj))

        assert not _AssertionHelperFunctions.safecontainer(obj), _assertionhelpers.errmsg(
            err,
            "%s is not empty", _saferepr(obj),
        )
        _assertionhelpers.evidence(
            evidence,
            "%s is empty", _saferepr(obj),
        )
        return obj

    @staticmethod
    def assertisnotempty(
            obj,  # type: typing.Optional[typing.Iterable[_VarItemType]]
            err=None,  # type: _ErrParamType
            evidence=False,  # type: _EvidenceParamType
    ):  # type: (...) -> typing.Iterable[_VarItemType]
        """
        Checks that a container object (string, bytes, list, dictionary, set, ...) is not empty.

        :param obj: Container object to check.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        from ._reflection import isiterable

        assert obj is not None, _assertionhelpers.isnonemsg("assertisempty()", "obj")
        assert isiterable(obj), _assertionhelpers.ctxmsg("assertisnotempty()", "invalid object type %s", _saferepr(obj))

        assert _AssertionHelperFunctions.safecontainer(obj), _assertionhelpers.errmsg(
            err,
            "%s is empty", _saferepr(obj),
        )
        _assertionhelpers.evidence(
            evidence,
            "%s is not empty", _saferepr(obj),
        )
        return obj

    @staticmethod
    def assertlen(
            obj,  # type: typing.Optional[typing.Iterable[_VarItemType]]
            length,  # type: typing.Optional[int]  # noqa
            err=None,  # type: _ErrParamType
            evidence=False,  # type: _EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks the length of a container object (string, bytes, list, dictionary, set, ...).

        :param obj: Container object which length to check.
        :param length: Expected length.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        from ._reflection import isiterable

        assert obj is not None, _assertionhelpers.isnonemsg("assertlen()", "obj")
        assert isiterable(obj), _assertionhelpers.ctxmsg("assertlen()", "invalid object type %s", _saferepr(obj))
        assert length is not None, _assertionhelpers.isnonemsg("assertlen()", "length")

        _len = len(_AssertionHelperFunctions.safecontainer(obj))  # type: int
        assert _len == length, _assertionhelpers.errmsg(
            err,
            "len(%s) is %d, not %d", _saferepr(obj), _len, length,
        )
        _assertionhelpers.evidence(
            evidence,
            "Length of %s is %d", _saferepr(obj), length,
        )

    @staticmethod
    def assertin(
            obj,  # type: typing.Optional[_VarItemType]
            container,  # type: typing.Optional[typing.Iterable[_VarItemType]]
            err=None,  # type: _ErrParamType
            evidence=False,  # type: _EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks a pattern or item is in a container object (string, bytes, list, dictionary, set, ...).

        :param obj: Pattern or item to check in ``container``.
        :param container: Container object.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        from ._reflection import isiterable

        if isinstance(container, (str, bytes)):
            assert obj is not None, _assertionhelpers.isnonemsg("assertin()", "obj")
        assert container is not None, _assertionhelpers.isnonemsg("assertin()", "container")
        assert isiterable(container), _assertionhelpers.ctxmsg("assertin()", "invalid container type %s", _saferepr(container))

        # Note 1: The error display proposed by unittest does not truncate the strings, which makes the reading hard.
        # assertionhelpers.unittest.assertIn(obj, container, err)
        # Note 2: Hard to make typings work with the `in` operator below and the variety of types. Use a `typing.cast(Any)` for the purpose.
        assert obj in typing.cast(typing.Any, container), _assertionhelpers.errmsg(
            err,
            "%s not in %s", _saferepr(obj), _saferepr(container, focus=obj),
        )
        _assertionhelpers.evidence(
            evidence,
            "%s in %s", _saferepr(obj), _saferepr(container, focus=obj),
        )

    @staticmethod
    def assertnotin(
            obj,  # type: typing.Optional[_VarItemType]
            container,  # type: typing.Optional[typing.Iterable[_VarItemType]]
            err=None,  # type: _ErrParamType
            evidence=False,  # type: _EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks a pattern or item is not in a container object (string, bytes, list, dictionary, set, ...).

        :param obj: Pattern or item to check not in ``container``.
        :param container: Container object.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        from ._reflection import isiterable

        if isinstance(container, (str, bytes)):
            assert obj is not None, _assertionhelpers.isnonemsg("assertnotin()", "obj")
        assert container is not None, _assertionhelpers.isnonemsg("assertnotin()", "container")
        assert isiterable(container), _assertionhelpers.ctxmsg("assertnotin()", "invalid container type %s", _saferepr(container))

        # Note 1: The error display proposed by unittest does not truncate the strings (for assertIn() at least), which makes the reading hard.
        # assertionhelpers.unittest.assertNotIn(obj, container, err)
        # Note 2: Hard to make typings work with the `not in` operator below and the variety of types. Use a `typing.cast(Any)` for the purpose.
        assert obj not in typing.cast(typing.Any, container), _assertionhelpers.errmsg(
            err,
            "%s in %s", _saferepr(obj), _saferepr(container, focus=obj),
        )
        _assertionhelpers.evidence(
            evidence,
            "%s not in %s", _saferepr(obj), _saferepr(container, focus=obj),
        )

    @staticmethod
    def assertcount(
            container,  # type: typing.Optional[typing.Iterable[_VarItemType]]
            obj,  # type: typing.Optional[_VarItemType]
            count,  # type: typing.Optional[int]
            err=None,  # type: _ErrParamType
            evidence=False,  # type: _EvidenceParamType
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
        from ._reflection import isiterable

        assert container is not None, _assertionhelpers.isnonemsg("assertcount()", "container")
        assert isiterable(container), _assertionhelpers.ctxmsg("assertcount()", "invalid container type %s", _saferepr(container))
        assert obj is not None, _assertionhelpers.isnonemsg("assertcount()", "obj")
        assert count is not None, _assertionhelpers.isnonemsg("assertcount()", "count")

        # Note 2: Hard to make typings work with the `count()` method and the type of `obj`. Use a `typing.cast(Any)` for the purpose.
        _found = _AssertionHelperFunctions.safecontainer(container).count(typing.cast(typing.Any, obj))  # type: int
        assert _found == count, _assertionhelpers.errmsg(
            err,
            "%s should contain %d count of %s (%d found)", _saferepr(container), count, _saferepr(obj), _found,
        )
        _assertionhelpers.evidence(
            evidence,
            "%s %d time(s) in %s", _saferepr(obj), _found, _saferepr(container, focus=obj),
        )

    # JSON (or data dictionaries).

    @staticmethod
    def assertjson(
            json_data,  # type: typing.Optional[_JsonDictType]
            jsonpath,  # type: typing.Optional[str]
            err=None,  # type: _ErrParamType
            evidence=False,  # type: _EvidenceParamType
            type=None,  # type: type  # noqa  ## Shadows built-in name 'type'
            value=None,  # type: typing.Union[int, str]
            ref=None,  # type: _JsonDictType
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
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
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
        from ._reflection import qualname

        _json_safe_repr_max_length = 32  # type: int

        def _errormsg(fmt, *args):  # type: (str, typing.Any) -> str
            return _assertionhelpers.errmsg(
                err,
                f"JSON %s | %s => {fmt}",
                _saferepr(json_data, max_length=_json_safe_repr_max_length), _saferepr(jsonpath), *args,
            )

        # Check input parameters.
        assert json_data is not None, _assertionhelpers.isnonemsg("assertjson()", "json_data")
        assert jsonpath is not None, _assertionhelpers.isnonemsg("assertjson()", "jsonpath")
        if (ref is not None) and (value is None):
            # Compute ``value`` from ``ref``: make a recursive call without parameters in order to retrieve the value pointed by ``jsonpath``.
            value = Assertions.assertjson(ref, jsonpath)
            assert isinstance(value, (builtins.type(None), int, str)), _errormsg("Invalid type %s", _saferepr(value))

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
        for _item in _items:  # type: typing.Union[_JsonDictType, int, str]
            if type is not None:
                assert isinstance(_item, type), _errormsg("Wrong type %r, %s expected", _item, qualname(type))
            if value is not None:
                assert _json_data == value, _errormsg("Wrong value %r, %r expected", _item, value)
        # Check the number of matching items.
        if count is not None:
            _error_message = _FmtAndArgsImpl()  # type: _FmtAndArgsType
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
                _saferepr(_items[0], max_length=_json_safe_repr_max_length),
                builtins.len(_items[0]),
                len,
            )

        # Return value and evidence.
        _res = _items[0] if count == 1 else _items  # type: typing.Any
        _evidence_message = _FmtAndArgsImpl()  # type: _FmtAndArgsType
        if len is not None:
            _evidence_message.push("len(")
        _evidence_message.push("%s | %s", _saferepr(json_data, max_length=_json_safe_repr_max_length), _saferepr(jsonpath))
        if len is None:
            _evidence_message.push(" => ")
        else:
            _evidence_message.push(" i.e. ")
        _evidence_message.push("%s", _saferepr(_res))
        if len is not None:
            _evidence_message.push(") = %d", len)
        _assertionhelpers.evidence(evidence, _evidence_message)
        return _res

    # Files.

    @staticmethod
    def assertexists(
            path,  # type: typing.Optional[_AnyPathType]
            err=None,  # type: _ErrParamType
            evidence=False,  # type: _EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks whether a path exists.

        :param path: Path to check.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        assert path is not None, _assertionhelpers.isnonemsg("assertexists()", "path")
        if not isinstance(path, _PathImpl):
            path = _PathImpl(path)

        assert path.exists(), _assertionhelpers.errmsg(
            err,
            "'%s' does not exist", path,
        )
        _assertionhelpers.evidence(
            evidence,
            "'%s' exists", path,
        )

    @staticmethod
    def assertnotexists(
            path,  # type: typing.Optional[_AnyPathType]
            err=None,  # type: _ErrParamType
            evidence=False,  # type: _EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks whether a path does not exist.

        :param path: Path to check.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        assert path is not None, _assertionhelpers.isnonemsg("assertnotexists()", "path")
        if not isinstance(path, _PathImpl):
            path = _PathImpl(path)

        assert not path.exists(), _assertionhelpers.errmsg(
            err,
            "'%s' exists", path,
        )
        _assertionhelpers.evidence(
            evidence,
            "'%s' does not exist", path,
        )

    @staticmethod
    def assertisfile(
            path,  # type: typing.Optional[_AnyPathType]
            err=None,  # type: _ErrParamType
            evidence=False,  # type: _EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks whether a path is a regular file.

        :param path: Path to check.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        assert path is not None, _assertionhelpers.isnonemsg("assertisfile()", "path")
        if not isinstance(path, _PathImpl):
            path = _PathImpl(path)

        assert path.is_file(), _assertionhelpers.errmsg(
            err,
            "'%s' is not a file", path,
        )
        _assertionhelpers.evidence(
            evidence,
            "'%s' is a file", path,
        )

    @staticmethod
    def assertisdir(
            path,  # type: typing.Optional[_AnyPathType]
            err=None,  # type: _ErrParamType
            evidence=False,  # type: _EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks whether a path is a directory.

        :param path: Path to check.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        assert path is not None, _assertionhelpers.isnonemsg("assertisdir()", "path")
        if not isinstance(path, _PathImpl):
            path = _PathImpl(path)

        assert path.is_dir(), _assertionhelpers.errmsg(
            err,
            "'%s' is not a directory", path,
        )
        _assertionhelpers.evidence(
            evidence,
            "'%s' is a directory", path,
        )

    @staticmethod
    def assertsamepaths(
            path1,  # type: typing.Optional[_AnyPathType]
            path2,  # type: typing.Optional[_AnyPathType]
            err=None,  # type: _ErrParamType
            evidence=False,  # type: _EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks whether two paths are actually the same, even though they may be absolute or relative, or accessed through a symbolic link...

        :param path1: First path to check.
        :param path2: Second path to check.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        assert path1 is not None, _assertionhelpers.isnonemsg("assertsamepaths()", "path1")
        assert path2 is not None, _assertionhelpers.isnonemsg("assertsamepaths()", "path2")
        if not isinstance(path1, _PathImpl):
            path1 = _PathImpl(path1)
        if not isinstance(path2, _PathImpl):
            path2 = _PathImpl(path2)

        assert path1.samefile(path2), _assertionhelpers.errmsg(
            err,
            "'%s' and '%s' are not the same", path1, path2,
        )
        _assertionhelpers.evidence(
            evidence,
            "'%s' and '%s' are the same", path1, path2,
        )

    @staticmethod
    def assertisrelativeto(
            path,  # type: typing.Optional[_AnyPathType]
            dir,  # type: typing.Optional[_AnyPathType]  # noqa  ## Shadows built-in name 'dir'
            err=None,  # type: _ErrParamType
            evidence=False,  # type: _EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks whether a path is a sub-path of a directory.

        :param path: Path to check.
        :param dir: Container directory candidate.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        assert path is not None, _assertionhelpers.isnonemsg("assertisrelativeto()", "path")
        assert dir is not None, _assertionhelpers.isnonemsg("assertisrelativeto()", "dir")
        if not isinstance(path, _PathImpl):
            path = _PathImpl(path)
        if not isinstance(dir, _PathImpl):
            dir = _PathImpl(dir)  # noqa  ## Shadows built-in name 'dir'

        assert path.is_relative_to(dir), _assertionhelpers.errmsg(
            err,
            "'%s' is not a sub-path of '%s'", path, dir,
        )
        _assertionhelpers.evidence(
            evidence,
            "'%s' is a sub-path of '%s'", path, dir,
        )

    @staticmethod
    def assertisnotrelativeto(
            path,  # type: typing.Optional[_AnyPathType]
            dir,  # type: typing.Optional[_AnyPathType]  # noqa  ## Shadows built-in name 'dir'
            err=None,  # type: _ErrParamType
            evidence=False,  # type: _EvidenceParamType
    ):  # type: (...) -> None
        """
        Checks whether a path is not a sub-path of a directory.

        :param path: Path to check.
        :param dir: Directory expected not to be a container directory for ``path``.
        :param err: Optional error message.
        :param evidence: Evidence activation (see the :ref:`dedicated note <assertions.evidence-param>`).
        """
        assert path is not None, _assertionhelpers.isnonemsg("assertisnotrelativeto()", "path")
        assert dir is not None, _assertionhelpers.isnonemsg("assertisnotrelativeto()", "dir")
        if not isinstance(path, _PathImpl):
            path = _PathImpl(path)
        if not isinstance(dir, _PathImpl):
            dir = _PathImpl(dir)  # noqa  ## Shadows built-in name 'dir'

        assert not path.is_relative_to(dir), _assertionhelpers.errmsg(
            err,
            "'%s' is a sub-path of '%s'", path, dir,
        )
        _assertionhelpers.evidence(
            evidence,
            "'%s' is not a sub-path of '%s'", path, dir,
        )


class _AssertionHelperFunctions(abc.ABC):
    """
    Assertion helper functions.

    Set in a private class to avoid public exposure.
    """

    @staticmethod
    def safecontainer(
            obj,  # type: typing.Iterable[_VarItemType]
    ):  # type: (...) -> typing.Union[str, bytes, typing.List[_VarItemType]]
        """
        Ensures working with a string or list-like object.

        :param obj:
            Input iterable object.
        :return:
            String or list-like object:

            - may be used as is, in order to check its emptiness,
            - may be applied ``len()`` on it,
            - has a ``count()`` method,
            - ...
        """
        if isinstance(obj, (str, bytes, list)):
            return obj
        else:
            return list(obj)

    @staticmethod
    def getstepstarttime(
            step_execution,  # type: _StepExecutionType
    ):  # type: (...) -> float
        """
        Retrieves the expected starting time of the step execution.

        :param step_execution:
            Step execution to retrieve the start time for.
        :return:
            Step execution start time.
        """
        assert step_execution.time.start is not None, f"{step_execution.definition} not started"
        return step_execution.time.start

    @staticmethod
    def getstependtime(
            step_execution,  # type: _StepExecutionType
            *,
            expect,  # type: bool
    ):  # type: (...) -> float
        """
        Retrieves the ending time of the step execution.

        :param step_execution:
            Step execution to retrieve the end time for.
        :param expect:
            ``True`` when this step execution is expected to be terminated.
            Otherwise, if not terminated, the current time will be returned by default.
        :return:
            Step execution end time, or current time.
        """
        if step_execution.time.end is not None:
            return step_execution.time.end
        elif expect:
            raise AssertionError(f"{step_execution.definition} not terminated")
        else:
            return time.time()
