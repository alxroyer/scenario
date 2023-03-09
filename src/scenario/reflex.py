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
Reflexive programmation tools and Python augmentations.
"""

import importlib.util
import inspect
import pathlib
import sys
import types
import typing

from .debugclasses import DebugClass  # `DebugClass` used to instanciate global variable.
from .logger import Logger  # `Logger` used to instanciate global variable.

if typing.TYPE_CHECKING:
    from .path import AnyPathType


__doc__ += """
.. py:attribute:: REFLEX_LOGGER

    Logger instance for reflexive programming.
"""
REFLEX_LOGGER = Logger(log_class=DebugClass.REFLEX)


def qualname(
        obj,  # type: typing.Any
):  # type: (...) -> str
    """
    Returns the qualified name of an object.

    :param obj: Object to retrieve the qualified name for.
    :return: Qualified name.

    .. note:: Accessing directly the `__qualname__` attribute makes mypy generate errors like '"..." has no attribute "__qualname__"'.
    """
    if hasattr(obj, "__qualname__"):
        _qualname = obj.__qualname__  # type: str
    elif hasattr(obj, "__name__"):
        _qualname = obj.__name__
    else:
        # Should never occur... whatever, let's fallback on calling `repr()`.
        _qualname = repr(obj)
    return _qualname


def isiterable(
        obj,  # type: typing.Any
):  # type: (...) -> bool
    """
    Tells whether an object is iterable or not.

    :param obj: Object to check.
    :return: ``True`` when the object is iterable, ``False`` otherwise.

    Inspired from https://stackoverflow.com/questions/1952464/in-python-how-do-i-determine-if-an-object-is-iterable#1952481.
    """
    try:
        _iter = iter(obj)  # type: typing.Iterator[typing.Any]
        return True
    except TypeError:
        return False


def importmodulefrompath(
        script_path,  # type: AnyPathType
):  # type: (...) -> types.ModuleType
    """
    Imports a module from its Python script path.

    :param script_path: Python script path.
    :return: Module loaded.
    """
    from .path import Path

    script_path = pathlib.Path(script_path).resolve()
    assert script_path.is_file(), f"No such file '{script_path}'"
    assert script_path.name.endswith(".py"), f"Not a Python script '{script_path}'"

    # Determine the module name:
    # - Use the module basename by default.
    _module_name = script_path.name[:-3]  # type: str
    # - Check whether the script is part of a `sys.path`, in order to preserve the module's package belonging.
    for _python_path in sys.path:  # type: str
        # Note: `pathlib.PurePath.is_relative_to()` exists from Python 3.9 only. Use `scenario.Path` for the purpose.
        if Path(script_path).is_relative_to(_python_path):
            _module_name = script_path.relative_to(
                # Note: `_python_path` may be a relative path. Ensure an absolute path in order to be able to compute a relative path from it.
                pathlib.Path(_python_path).resolve()
            ).as_posix().replace("/", ".")[:-3]

    # First check whether the scenario has already been loaded.
    if _module_name in sys.modules:
        return sys.modules[_module_name]

    try:
        # Inspired from https://stackoverflow.com/questions/67631/how-to-import-a-module-given-the-full-path
        assert sys.version_info >= (3, 6), f"Incorrect Python version {sys.version}, 3.6 required at least"
        _module_spec = importlib.util.spec_from_file_location(_module_name, script_path)  # type: typing.Any
        _module = importlib.util.module_from_spec(_module_spec)  # type: typing.Optional[types.ModuleType]
        if _module is None:
            raise ImportError(f"Could not load '{script_path}'")
        _module_spec.loader.exec_module(_module)

        # Register the module just loaded in the ``sys.modules`` dictionary.
        # Note: Works even if `_module_name` is in the "package.module" form.
        sys.modules[_module_name] = _module

        REFLEX_LOGGER.debug("importmodulefrompath('%s') => %r", script_path, _module)
        return _module
    except Exception as _err:
        REFLEX_LOGGER.debug("%s", _err, exc_info=sys.exc_info())
        raise _err


def getloadedmodulefrompath(
        script_path,  # type: AnyPathType
):  # type: (...) -> typing.Optional[types.ModuleType]
    """
    Retrieves a module already loaded corresponding to the given path.

    :param script_path: Python script path.
    :return: Corresponding module if already loaded.
    """
    script_path = pathlib.Path(script_path)
    _module = None  # type: typing.Optional[types.ModuleType]
    for _module_name in sys.modules:  # type: str
        if hasattr(sys.modules[_module_name], "__file__"):
            if pathlib.Path(sys.modules[_module_name].__file__ or "").samefile(script_path):
                _module = sys.modules[_module_name]
                break

    REFLEX_LOGGER.debug("getloadedmodulefrompath('%s') => %r", script_path, _module)
    return _module


def checkfuncqualname(
        file,  # type: AnyPathType
        line,  # type: int
        func_name,  # type: str
):  # type: (...) -> str
    """
    Tries to retrieve the fully qualified name of a function or method.

    :param file: Path of the file the function is defined int.
    :param line: Line number inside the function.
    :param func_name: Short name of the function.
    :return: Fully qualified name of the function, or ``func_name`` as is by default.
    """
    from .scenariodefinition import MetaScenarioDefinition

    def _walkmodule(
            module,  # type: types.ModuleType
    ):  # type: (...) -> typing.Optional[str]
        _res = None  # type: typing.Optional[str]
        try:
            REFLEX_LOGGER.debug("Walking %r", module)
            REFLEX_LOGGER.pushindentation()
            for _class_name, _cls in inspect.getmembers(module, inspect.isclass):  # type: str, type
                _res = _walkclass(_cls)
                if _res is not None:
                    return _res
            for _func_name, _func in inspect.getmembers(module, inspect.isfunction):  # type: str, types.FunctionType
                _res = _walkfunction(_func)
                if _res is not None:
                    return _res
            if func_name == "<module>":
                REFLEX_LOGGER.debug("_walkmodule(): %r matches '%s'! => returning '%s'", module, func_name, qualname(module))
                return qualname(module)
        finally:
            REFLEX_LOGGER.popindentation()
        return None

    def _walkclass(
            cls,  # type: type
    ):  # type: (...) -> typing.Optional[str]
        # Filter-out non-matching modules.
        if cls.__module__ != qualname(_module):
            # Many non-matching classes... do not log them all.
            # REFLEX_LOGGER.debug("_walkclass(%r): '%s' != '%s'", cls, cls.__module__, qualname(_module))
            return None

        _res = None  # type: typing.Optional[str]
        try:
            REFLEX_LOGGER.debug("Walking class %r", cls)
            REFLEX_LOGGER.pushindentation()
            # Inner classes.
            for _class_name, _cls in inspect.getmembers(cls, inspect.isclass):  # type: str, type
                _res = _walkclass(_cls)
                if _res is not None:
                    return _res
            # Static methods.
            for _func_name, _func in inspect.getmembers(cls, inspect.isfunction):  # type: str, types.FunctionType
                _res = _walkfunction(_func)
                if _res is not None:
                    return _res
            # `ScenarioDefinition.__init__()` wrappers.
            for _wrapper_name, _wrapper in inspect.getmembers(cls, lambda obj: isinstance(obj, MetaScenarioDefinition.InitWrapper)):  \
                    # type: str, MetaScenarioDefinition.InitWrapper
                _res = _walkfunction(_wrapper.init_method)
                if _res is not None:
                    return _res
            # Member methods.
            for _method_name, _meth in inspect.getmembers(cls, inspect.ismethod):  # type: str, types.MethodType
                _res = _walkfunction(_meth.__func__)
                if _res is not None:
                    return _res
            # Properties.
            for _prop_name, _prop in inspect.getmembers(cls, lambda obj: isinstance(obj, property)):  # type: str, property
                if _prop.fget:
                    _res = _walkfunction(typing.cast(types.FunctionType, _prop.fget))
                    if _res is not None:
                        return _res
                if _prop.fset:
                    _res = _walkfunction(typing.cast(types.FunctionType, _prop.fset))
                    if _res is not None:
                        return _res
                if _prop.fdel:
                    _res = _walkfunction(typing.cast(types.FunctionType, _prop.fdel))
                    if _res is not None:
                        return _res
        finally:
            REFLEX_LOGGER.popindentation()
        return None

    def _walkfunction(
            func,  # type: types.FunctionType
    ):  # type: (...) -> typing.Optional[str]
        # Filter-out non-matching modules.
        if (not hasattr(func, "__module__")) or (func.__module__ != qualname(_module)):
            # Many non-matching functions... do not log them all.
            # REFLEX_LOGGER.debug("_walkfunction(%r): '%s' != '%s'", func, func.__module__, qualname(_module))
            return None

        return _walkcode(qualname(func), func.__code__)

    def _walkcode(
            code_name,  # type: str
            code,  # type: types.CodeType
    ):  # type: (...) -> typing.Optional[str]
        try:
            REFLEX_LOGGER.debug("Walking '%s' %r", code_name, code)
            REFLEX_LOGGER.pushindentation()

            # Filter-out non-matching lines.
            _code_line_count = codelinecount(code)  # type: int
            if (line < code.co_firstlineno) or (line > code.co_firstlineno + _code_line_count):
                REFLEX_LOGGER.debug("_walkcode(): Line %d out of [%d, %d]", line, code.co_firstlineno, code.co_firstlineno + _code_line_count)
                return None
            else:
                REFLEX_LOGGER.debug("_walkcode(): Line %d in [%d, %d]", line, code.co_firstlineno, code.co_firstlineno + _code_line_count)

            # Try to walk through inner classes and functions.
            # Inner classes and functions can be found through the `co_consts` attribute.
            # In this tuple, inner classes and functions are given as a code object, followed by a name.
            # The name seems to be a short name for classes, but fully qualified names for functions...
            _last_code = None  # type: typing.Optional[types.CodeType]
            _inner_codes = []  # type: typing.List[typing.Tuple[str, types.CodeType]]
            for _const in code.co_consts:  # type: typing.Any
                if _last_code is not None:
                    if isinstance(_const, str):
                        _inner_codes.append((_const, _last_code))
                    else:
                        REFLEX_LOGGER.warning(f"{_const!r} following {_last_code!r} expected to be of type str, {qualname(type(_const))} found")
                    _last_code = None
                elif isinstance(_const, types.CodeType):
                    # ...except for lambdas, which don't have a name.
                    if _const.co_name == "<lambda>":
                        _inner_codes.append((_const.co_name, _const))
                    else:
                        _last_code = _const
            for _inner_code_name, _inner_code in _inner_codes:  # type: str, types.CodeType
                # Recursive call:
                # - Direct recursion for functions.
                # - For classes, this call will list the class methods which are described as code objects as well,
                #   and then make recursive calls for each.
                _res = _walkcode(_inner_code_name, _inner_code)  # type: typing.Optional[str]
                if _res is not None:
                    return _res

            # Eventually check that the name of this code instance matches the expected function name.
            # Memo: `code_name` is always passed on as fully qualified names for functions.
            if code_name.endswith(func_name):
                REFLEX_LOGGER.debug("_walkcode(): '%s' matches '%s'!", code_name, func_name)
                return code_name

        finally:
            REFLEX_LOGGER.popindentation()
        return None

    REFLEX_LOGGER.debug("checkfuncqualname(file='%s', line=%d, func_name='%s')", file, line, func_name)
    REFLEX_LOGGER.pushindentation()

    _fqn = None  # type: typing.Optional[str]
    _module = getloadedmodulefrompath(file)  # type: typing.Optional[types.ModuleType]
    if _module:
        _fqn = _walkmodule(_module)

    if not _fqn:
        REFLEX_LOGGER.warning(f"Could not find fully qualified name for {file}:{line}:{func_name}()")
    REFLEX_LOGGER.popindentation()
    # Return `func_name` as is by default.
    return _fqn or func_name


def codelinecount(
        code,  # type: types.CodeType
):  # type: (...) -> int
    """
    Retrieves the number of lines of the given code object.

    :param code: Code object which lines to count.
    :return: Number of lines.

    Apparently, `inspect <https://docs.python.org/3/library/inspect.html#types-and-members>`_ does give the straight forward information.

    The `co_lnotab` attribute, being an "encoded mapping of line numbers to bytecode indices", is our best chance for the purpose.

    The https://svn.python.org/projects/python/branches/pep-0384/Objects/lnotab_notes.txt resource gives complementary information
    on how to parse this `co_lnotab` attribute.

    .. admonition:: `co_lnotab` depreciation.
        :class: warning

        According to https://www.python.org/dev/peps/pep-0626/#backwards-compatibility:
        "The co_lnotab attribute will be deprecated in 3.10 and removed in 3.12."
    """
    assert sys.version_info < (3, 12)

    # Inspired from https://svn.python.org/projects/python/branches/pep-0384/Objects/lnotab_notes.txt
    REFLEX_LOGGER.debug("codelinecount(): code.co_lnotab = 0x%s", code.co_lnotab.hex())
    _byte_code_addr = 0  # type: int
    _lineno = 0  # type: int
    _index = 0
    while _index < len(code.co_lnotab):
        _byte_code_incr = code.co_lnotab[_index]  # type: int
        _byte_code_addr += _byte_code_incr
        _index += 1
        if _index < len(code.co_lnotab):
            _lineno_incr = code.co_lnotab[_index]  # type: int
            # Because single bytes are used to encode line increments,
            # positive line increments are stuck to 127 (i.e. 0x7f), and possibly repeated when bigger.
            # When the first bit of the byte is set, it encodes a negative value (255=0xff stands for -1, 254=0xfe stands for -2, ...).
            if _lineno_incr > 0x7f:
                _lineno_incr -= 256
            _lineno += _lineno_incr
            _index += 1
            REFLEX_LOGGER.debug("codelinecount(): byte-code-addr(%+d) = %d, lineno(%+d) = %d", _byte_code_incr, _byte_code_addr, _lineno_incr, _lineno)
    return _lineno
