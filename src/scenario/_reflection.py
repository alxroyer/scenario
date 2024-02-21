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
Reflective programming tools and Python augmentations.
"""

import importlib.util
import inspect
import os
import pathlib
import sys
import types
import typing

if True:
    from ._fastpath import FAST_PATH as _FAST_PATH  # `FAST_PATH` imported once for performance concerns.
if typing.TYPE_CHECKING:
    from ._path import AnyPathType as _AnyPathType


def qualname(
        obj,  # type: typing.Any
):  # type: (...) -> str
    """
    Returns the qualified name of an object,
    i.e. its name from its definition module.

    :param obj:
        Object to retrieve the qualified name for.
        No types.
    :return:
        Qualified name.
    """
    if obj is None:
        return repr(obj)
    if type(obj).__module__ == "typing":
        raise ValueError(f"qualname() shouldn't be called on types. Cannot find name for {obj}")
    if hasattr(obj, "__qualname__"):
        return str(obj.__qualname__)
    if hasattr(obj, "__name__"):
        return str(obj.__name__)
    raise ValueError(f"Cannot evaluate qualified name from {obj!r}")


def fqname(
        obj,  # type: typing.Any
):  # type: (...) -> str
    """
    Returns the fully qualified name of an object,
    i.e. its name with its definition module.

    :param obj:
        Object to retrieve the fully qualified name for.
        No types.
    :return:
        Fully qualified name.
    """
    if obj is None:
        return qualname(obj)
    if inspect.ismodule(obj):
        return qualname(obj)
    return f"{qualname(inspect.getmodule(obj))}.{qualname(obj)}"


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
        script_path,  # type: _AnyPathType
        sys_modules_cache=True,  # type: bool
):  # type: (...) -> types.ModuleType
    """
    Imports a module from its Python script path.

    :param script_path:
        Python script path.
    :param sys_modules_cache:
        When ``True``,
        read from modules previously loaded and cached in ``sys.modules``,
        or save newly loaded modules in ``sys.modules``.

        When ``False``,
        just load the module and leave ``sys.modules`` unchanged.
    :return:
        Module loaded.

    .. admonition:: Known issues when loading a '__init__.py' package definition file
        :class: warning

        '__init__.py' scripts are imported as a regular scripts, not package definitions.

        Known side effects:

        - ``__path__`` definition is missing, preventing usage of `pkgutil.extend_path()` consequently.
    """
    script_path = pathlib.Path(script_path).resolve()
    assert script_path.is_file(), f"No such file '{script_path}'"
    assert script_path.suffix == ".py", f"Not a Python script '{script_path}'"

    # Determine the module name:
    # - Use the directory name in case of a '__init__.py' file.
    if script_path.name == "__init__.py":
        _module_name = script_path.parent.name  # type: str
    # - Use the module basename without extension otherwise.
    else:
        _module_name = script_path.stem  # Type already declared above.
    # - Then check whether the script is part of a `sys.path`, in order to preserve the module's package belonging.
    for _python_path in sys.path:  # type: str
        # Note: `pathlib.PurePath.is_relative_to()` exists from Python 3.9 only. Compare absolute strings.
        # if script_path.is_relative_to(_python_path):
        if os.fspath(script_path).startswith(os.fspath(_python_path)):
            _module_name = script_path.relative_to(
                # Note: `_python_path` may be a relative path. Ensure an absolute path in order to be able to compute a relative path from it.
                pathlib.Path(_python_path).resolve()
            ).as_posix().replace("/", ".")[:-3]
            if _module_name.endswith(".__init__"):
                _module_name = _module_name[:-len(".__init__")]

    # First check whether the scenario has already been loaded.
    if sys_modules_cache:
        if _module_name in sys.modules:
            return sys.modules[_module_name]

    # If not in `sys.modules`, save `sys.modules` keys before we load `script_path`.
    _initial_sys_modules_keys = list(sys.modules)  # type: typing.Sequence[str]

    try:
        # Inspired from https://stackoverflow.com/questions/67631/how-to-import-a-module-given-the-full-path
        assert sys.version_info >= (3, 6), f"Incorrect Python version {sys.version}, 3.6 required at least"
        _module_spec = importlib.util.spec_from_file_location(_module_name, script_path)  # Implicit type: `importlib._bootstrap.ModuleSpec`
        if (not _module_spec) or (not _module_spec.loader):
            raise ImportError(f"Could not build spec to load '{script_path}'")
        _module = importlib.util.module_from_spec(_module_spec)  # type: typing.Optional[types.ModuleType]
        if _module is None:
            raise ImportError(f"Could not load '{script_path}'")
        _module_spec.loader.exec_module(_module)
    except Exception as _err:
        _FAST_PATH.reflection_logger.debug("%s", _err, exc_info=sys.exc_info())
        raise _err

    if sys_modules_cache:
        # Register the module just loaded in the `sys.modules` dictionary.
        # Note: Works even if `_module_name` is in the "package.module" form.
        _FAST_PATH.reflection_logger.debug("Saving %s -> %r in `sys.modules`", _module_name, _module)
        sys.modules[_module_name] = _module
    else:
        # Save the module just loaded in `_non_cached_modules`.
        # Useful for :func:`_inspectgetfilehack()` just after.
        _FAST_PATH.reflection_logger.debug("Saving %s -> %r in `_non_cached_modules`", _module_name, _module)
        _non_cached_modules[_module_name] = _module

        # Ensure `sys.modules` remain unchanged.
        # Move new modules to `_non_cached_modules` as well.
        for _sys_module_name in list(sys.modules.keys()):  # type: str
            if _sys_module_name not in _initial_sys_modules_keys:
                _FAST_PATH.reflection_logger.debug("Moving %s -> %r from `sys.modules` to `_non_cached_modules`", _module_name, _module)
                _non_cached_modules[_sys_module_name] = sys.modules[_sys_module_name]
                del sys.modules[_sys_module_name]

    _FAST_PATH.reflection_logger.debug("importmodulefrompath('%s') => %r", script_path, _module)
    return _module


#: Modules loaded by :func:`importmodulefrompath()` with ``sys_modules_cache=False``.
#:
#: Useful for :func:`_inspectgetfilehack()`.
_non_cached_modules = {}  # type: typing.Dict[str, types.ModuleType]


def _inspectgetfilehack(
        object,  # type: typing.Any  # noqa  ## Shadows built-in name 'object'
):  # type: (...) -> str
    """
    Replacement hack function for ``inspect.getfile()``.

    :param object: Object to find the file path from from.
    :return: File path as a string.
    """
    # Class defined in modules registered in `_non_cached_modules`.
    if inspect.isclass(object):
        if hasattr(object, "__module__") and (object.__module__ in _non_cached_modules):
            _module = _non_cached_modules[object.__module__]  # type: types.ModuleType
            if getattr(_module, "__file__", None):
                return str(_module.__file__)

    # Call the original `inspect.getfile()` implementation by default.
    return _inspect_getfile_origin(object)


#: Original `inspect.getfile()` implementation.
_inspect_getfile_origin = inspect.getfile  # type: typing.Callable[[typing.Any], str]

# Install `_inspectgetfilehack()`.
inspect.getfile = _inspectgetfilehack


def getloadedmodulefrompath(
        script_path,  # type: _AnyPathType
):  # type: (...) -> typing.Optional[types.ModuleType]
    """
    Retrieves a module already loaded corresponding to the given path.

    Walks both ``sys.modules`` and :attr:`_non_cached_modules`.

    :param script_path: Python script path.
    :return: Corresponding module if already loaded.
    """
    script_path = pathlib.Path(script_path)
    _module = None  # type: typing.Optional[types.ModuleType]
    for _module_registry in [_non_cached_modules, sys.modules]:  # type: typing.Dict[str, types.ModuleType]
        if _module is None:
            for _module_name in _module_registry:  # type: str
                if hasattr(_module_registry[_module_name], "__file__"):
                    if pathlib.Path(_module_registry[_module_name].__file__ or "").samefile(script_path):
                        _module = _module_registry[_module_name]
                        break

    _FAST_PATH.reflection_logger.debug("getloadedmodulefrompath('%s') => %r", script_path, _module)
    return _module


def extendnamespacepackagepath(
        namespace_package,  # type: types.ModuleType
        root_src_path,  # type: _AnyPathType
):  # type: (...) -> None
    """
    Extends the list of paths that define a namespace package.

    See:
    - [PEP 382](https://peps.python.org/pep-0382/): Namespace Packages
    - [PEP 420](https://peps.python.org/pep-0420/): Implicit Namespace Packages

    :param namespace_package: Namespace package which path to extend.
    :param root_src_path: New root source path.
    :raise ImportError: If the namespace package already includes the given path.
    """
    # Determine the new path from `root_src_path` and the namespace package name.
    _new_path = pathlib.Path(root_src_path).resolve()  # type: pathlib.Path
    for _part in qualname(namespace_package).split("."):  # type: str
        _new_path = _new_path / _part

    # Check the namespace package does not already include the path.
    for _path in namespace_package.__path__:  # type: str
        if pathlib.Path(_path).samefile(_new_path):
            raise ImportError(f"{namespace_package} already includes {_new_path}")

    # Extend the namespace package with the new path.
    namespace_package.__path__.append(str(_new_path))

    # Eventually add the source root path in `sys.path` (if not already in).
    if not any([pathlib.Path(_sys_path).exists() and pathlib.Path(_sys_path).samefile(root_src_path) for _sys_path in sys.path]):
        sys.path.append(str(pathlib.Path(root_src_path)))


def checkfuncqualname(
        file,  # type: _AnyPathType
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
    # === Inner functions ===

    def _walkmodule(
            module,  # type: types.ModuleType
    ):  # type: (...) -> typing.Optional[str]
        _res = None  # type: typing.Optional[str]
        _FAST_PATH.reflection_logger.debug("Walking %r", module)
        with _FAST_PATH.reflection_logger.pushindentation():
            for _class_name, _cls in inspect.getmembers(module, inspect.isclass):  # type: str, type
                _res = _walkclass(_cls)
                if _res is not None:
                    return _res
            for _func_name, _func in inspect.getmembers(module, inspect.isfunction):  # type: str, types.FunctionType
                _res = _walkfunction(_func)
                if _res is not None:
                    return _res
            if func_name == "<module>":
                _FAST_PATH.reflection_logger.debug("_walkmodule(): %r matches '%s'! => returning '%s'", module, func_name, qualname(module))
                return qualname(module)
        return None

    def _walkclass(
            cls,  # type: type
    ):  # type: (...) -> typing.Optional[str]
        # Filter-out non-matching modules.
        if cls.__module__ != qualname(_module):
            # Many non-matching classes... do not log them all.
            # REFLECTION_LOGGER.debug("_walkclass(%r): '%s' != '%s'", cls, cls.__module__, qualname(_module))
            return None

        _res = None  # type: typing.Optional[str]
        _FAST_PATH.reflection_logger.debug("Walking class %r", cls)
        with _FAST_PATH.reflection_logger.pushindentation():
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
            # Member methods.
            for _method_name, _meth in inspect.getmembers(cls, inspect.ismethod):  # type: str, types.MethodType
                _res = _walkfunction(_meth.__func__)
                if _res is not None:
                    return _res
            # Properties.
            for _prop_name, _prop in inspect.getmembers(cls, lambda obj: isinstance(obj, property)):  # type: str, property
                _res = _walkproperty(_prop)
                if _res is not None:
                    return _res
            # Method / function wrappers.
            for _wrapper_name, _wrapper in inspect.getmembers(cls, lambda obj: all([
                # Not already processed above.
                not inspect.isclass(obj),
                not inspect.isfunction(obj),
                not inspect.ismethod(obj),
                not isinstance(obj, property),
                # But still a callable object.
                hasattr(obj, "__call__"),
            ])):  # type: str, typing.Any
                for _wrapper_func_name, _wrapper_func in inspect.getmembers(_wrapper, inspect.isfunction):  # type: str, types.FunctionType
                    _res = _walkfunction(_wrapper_func)
                    if _res is not None:
                        return _res
                for _wrapper_method_name, _wrapper_method in inspect.getmembers(_wrapper, inspect.ismethod):  # type: str, types.MethodType
                    _res = _walkfunction(_wrapper_method.__func__)
                    if _res is not None:
                        return _res
                for _wrapper_prop_name, _wrapper_prop in inspect.getmembers(_wrapper, lambda obj: isinstance(obj, property)):  # type: str, property
                    _res = _walkproperty(_wrapper_prop)
                    if _res is not None:
                        return _res
        return None

    def _walkfunction(
            func,  # type: types.FunctionType
    ):  # type: (...) -> typing.Optional[str]
        # Filter-out non-matching modules.
        if (not hasattr(func, "__module__")) or (func.__module__ != qualname(_module)):
            # Many non-matching functions... do not log them all.
            # REFLECTION_LOGGER.debug("_walkfunction(%r): '%s' != '%s'", func, func.__module__, qualname(_module))
            return None

        return _walkcode("function", qualname(func), func.__code__)

    def _walkproperty(
            prop,  # type: property
    ):  # type: (...) -> typing.Optional[str]
        if prop.fget:
            _res = _walkfunction(typing.cast(types.FunctionType, prop.fget))
            if _res is not None:
                return _res
        if prop.fset:
            _res = _walkfunction(typing.cast(types.FunctionType, prop.fset))
            if _res is not None:
                return _res
        if prop.fdel:
            _res = _walkfunction(typing.cast(types.FunctionType, prop.fdel))
            if _res is not None:
                return _res
        return None

    def _walkcode(
            code_type,  # type: str
            code_name,  # type: str
            code,  # type: types.CodeType
    ):  # type: (...) -> typing.Optional[str]
        _FAST_PATH.reflection_logger.debug("Walking %s '%s' %r", code_type, code_name, code)
        with _FAST_PATH.reflection_logger.pushindentation():
            # Filter-out non-matching lines.
            _FAST_PATH.reflection_logger.debug("_walkcode(): Computing line bounds...")
            with _FAST_PATH.reflection_logger.pushindentation():
                _code_line_count = codelinecount(code)  # type: int
            if (line < code.co_firstlineno) or (line > code.co_firstlineno + _code_line_count):
                _FAST_PATH.reflection_logger.debug("_walkcode(): Line %d out of [%d, %d]", line, code.co_firstlineno, code.co_firstlineno + _code_line_count)
                return None
            else:
                _FAST_PATH.reflection_logger.debug("_walkcode(): Line %d in [%d, %d]", line, code.co_firstlineno, code.co_firstlineno + _code_line_count)

            # Try to walk through inner classes and functions.
            # Inner classes and functions can be found through the `co_consts` attribute.
            # In this tuple, inner classes and functions are given as a code object, followed by a name.
            # The name seems to be a short name for classes, but fully qualified names for functions...
            _FAST_PATH.reflection_logger.debug("_walkcode(): Scanning code items:")
            with _FAST_PATH.reflection_logger.pushindentation():
                _last_code = None  # type: typing.Optional[types.CodeType]
                _inner_codes = []  # type: typing.List[typing.Tuple[str, types.CodeType]]
                for _const in code.co_consts:  # type: typing.Any
                    _FAST_PATH.reflection_logger.debug("<%s>: %r", type(_const).__name__, _const)
                    if (_last_code is None) and isinstance(_const, types.CodeType):
                        # Lambda.
                        if _const.co_name == "<lambda>":
                            # By definition, lambdas have no name.
                            # Save them as is.
                            _inner_codes.append((_const.co_name, _const))
                            _FAST_PATH.reflection_logger.debug("  => Inner code saved: %r", _inner_codes[-1])
                            continue

                        # Inline `for` iteration.
                        # Examples:
                        # - `[x for x in ...]` => '<listcomp>'
                        # - `(x for x in ...)` => '<genexpr>'
                        if _const.co_name in ("<listcomp>", "<genexpr>"):
                            _FAST_PATH.reflection_logger.debug("  => Inline `for` iteration, skipped")
                            continue

                        # No special name, hence should be an inner class or function.
                        # Let's save it as `_last_code`, and wait for a `str` name as the next code item.
                        _last_code = _const
                        _FAST_PATH.reflection_logger.debug("  => Inner code detected, `str` name expected juste after...")
                        continue

                    # Inner function name.
                    if _last_code is not None:
                        if isinstance(_const, str):
                            _inner_codes.append((_const, _last_code))
                            _FAST_PATH.reflection_logger.debug("  => Inner code saved: %r", _inner_codes[-1])
                        else:
                            _FAST_PATH.reflection_logger.warning(f"{_const!r} following {_last_code!r} expected to be of type str, "
                                                                 f"{qualname(type(_const))} found")
                        _last_code = None
                        continue
            for _inner_code_name, _inner_code in _inner_codes:  # type: str, types.CodeType
                # Recursive call:
                # - Direct recursion for functions.
                # - For classes, this call will list the class methods which are described as code objects as well,
                #   and then make recursive calls for each.
                _res = _walkcode("inner code", _inner_code_name, _inner_code)  # type: typing.Optional[str]
                if _res is not None:
                    return _res

            # Eventually check that the name of this code instance matches the expected function name.
            # Memo: `code_name` is always passed on as fully qualified names for functions.
            if code_name.endswith(func_name):
                _FAST_PATH.reflection_logger.debug("_walkcode(): '%s' matches '%s'!", code_name, func_name)
                return code_name

        return None

    # === Main implementation ===

    _FAST_PATH.reflection_logger.debug("checkfuncqualname(file='%s', line=%d, func_name=%r)", file, line, func_name)

    _fqn = None  # type: typing.Optional[str]
    with _FAST_PATH.reflection_logger.pushindentation():
        _module = getloadedmodulefrompath(file)  # type: typing.Optional[types.ModuleType]
        if _module:
            _fqn = _walkmodule(_module)

    if not _fqn:
        _FAST_PATH.reflection_logger.warning(f"Could not find fully qualified name for {file}:{line}:{func_name}()")
    # Return `func_name` as is by default.
    _FAST_PATH.reflection_logger.debug("checkfuncqualname(file='%s', line=%d, func_name=%r) -> %r", file, line, func_name, _fqn or func_name)
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
    _FAST_PATH.reflection_logger.debug("codelinecount(): code.co_lnotab = 0x%s", code.co_lnotab.hex())
    _byte_code_addr = 0  # type: int
    _line_count = 0  # type: int
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
            _line_count += _lineno_incr
            _index += 1
            _FAST_PATH.reflection_logger.debug(
                "codelinecount(): byte-code-addr(%+d) = %d, line_count(%+d) = %d, lines = [%d; %d]",
                _byte_code_incr, _byte_code_addr, _lineno_incr,
                _line_count,
                code.co_firstlineno, code.co_firstlineno + _line_count,
            )
    return _line_count
