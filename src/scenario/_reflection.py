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
import pathlib
import sys
import types
import typing

if True:
    from ._debugclasses import DebugClass as _DebugClassImpl  # `DebugClass` used to instanciate global variable.
    from ._logger import Logger as _LoggerImpl  # `Logger` used to instanciate global variable.
if typing.TYPE_CHECKING:
    from ._path import AnyPathType as _AnyPathType


#: Logger instance for reflective programming.
REFLECTION_LOGGER = _LoggerImpl(log_class=_DebugClassImpl.REFLECTION)  # type: _LoggerImpl


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

    :param script_path: Python script path.
    :param sys_modules_cache: Read from modules previously loaded and cached in ``sys.modules``, save loaded modules in ``sys.modules`` otherwise.
    :return: Module loaded.

    .. admonition:: Known issues when loading a '__init__.py' package definition file
        :class: warning

        '__init__.py' scripts are imported as a regular scripts, not package definitions.

        Known side effects:

        - ``__path__`` definition is missing, preventing usage of `pkgutil.extend_path()` consequently.
    """
    from ._path import Path

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
        # Note: `pathlib.PurePath.is_relative_to()` exists from Python 3.9 only. Use `scenario.Path` for the purpose.
        if Path(script_path).is_relative_to(_python_path):
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

        # Register the module just loaded in the ``sys.modules`` dictionary.
        # Note: Works even if `_module_name` is in the "package.module" form.
        if sys_modules_cache:
            sys.modules[_module_name] = _module

        REFLECTION_LOGGER.debug("importmodulefrompath('%s') => %r", script_path, _module)
        return _module
    except Exception as _err:
        REFLECTION_LOGGER.debug("%s", _err, exc_info=sys.exc_info())
        raise _err


def getloadedmodulefrompath(
        script_path,  # type: _AnyPathType
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

    REFLECTION_LOGGER.debug("getloadedmodulefrompath('%s') => %r", script_path, _module)
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
    from ._scenariodefinition import MetaScenarioDefinition

    def _walkmodule(
            module,  # type: types.ModuleType
    ):  # type: (...) -> typing.Optional[str]
        _res = None  # type: typing.Optional[str]
        try:
            REFLECTION_LOGGER.debug("Walking %r", module)
            REFLECTION_LOGGER.pushindentation()
            for _class_name, _cls in inspect.getmembers(module, inspect.isclass):  # type: str, type
                _res = _walkclass(_cls)
                if _res is not None:
                    return _res
            for _func_name, _func in inspect.getmembers(module, inspect.isfunction):  # type: str, types.FunctionType
                _res = _walkfunction(_func)
                if _res is not None:
                    return _res
            if func_name == "<module>":
                REFLECTION_LOGGER.debug("_walkmodule(): %r matches '%s'! => returning '%s'", module, func_name, qualname(module))
                return qualname(module)
        finally:
            REFLECTION_LOGGER.popindentation()
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
        try:
            REFLECTION_LOGGER.debug("Walking class %r", cls)
            REFLECTION_LOGGER.pushindentation()
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
            REFLECTION_LOGGER.popindentation()
        return None

    def _walkfunction(
            func,  # type: types.FunctionType
    ):  # type: (...) -> typing.Optional[str]
        # Filter-out non-matching modules.
        if (not hasattr(func, "__module__")) or (func.__module__ != qualname(_module)):
            # Many non-matching functions... do not log them all.
            # REFLECTION_LOGGER.debug("_walkfunction(%r): '%s' != '%s'", func, func.__module__, qualname(_module))
            return None

        return _walkcode(qualname(func), func.__code__)

    def _walkcode(
            code_name,  # type: str
            code,  # type: types.CodeType
    ):  # type: (...) -> typing.Optional[str]
        try:
            REFLECTION_LOGGER.debug("Walking '%s' %r", code_name, code)
            REFLECTION_LOGGER.pushindentation()

            # Filter-out non-matching lines.
            _code_line_count = codelinecount(code)  # type: int
            if (line < code.co_firstlineno) or (line > code.co_firstlineno + _code_line_count):
                REFLECTION_LOGGER.debug("_walkcode(): Line %d out of [%d, %d]", line, code.co_firstlineno, code.co_firstlineno + _code_line_count)
                return None
            else:
                REFLECTION_LOGGER.debug("_walkcode(): Line %d in [%d, %d]", line, code.co_firstlineno, code.co_firstlineno + _code_line_count)

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
                        REFLECTION_LOGGER.warning(f"{_const!r} following {_last_code!r} expected to be of type str, {qualname(type(_const))} found")
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
                REFLECTION_LOGGER.debug("_walkcode(): '%s' matches '%s'!", code_name, func_name)
                return code_name

        finally:
            REFLECTION_LOGGER.popindentation()
        return None

    REFLECTION_LOGGER.debug("checkfuncqualname(file='%s', line=%d, func_name='%s')", file, line, func_name)
    REFLECTION_LOGGER.pushindentation()

    _fqn = None  # type: typing.Optional[str]
    _module = getloadedmodulefrompath(file)  # type: typing.Optional[types.ModuleType]
    if _module:
        _fqn = _walkmodule(_module)

    if not _fqn:
        REFLECTION_LOGGER.warning(f"Could not find fully qualified name for {file}:{line}:{func_name}()")
    REFLECTION_LOGGER.popindentation()
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
    REFLECTION_LOGGER.debug("codelinecount(): code.co_lnotab = 0x%s", code.co_lnotab.hex())
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
            REFLECTION_LOGGER.debug("codelinecount(): byte-code-addr(%+d) = %d, lineno(%+d) = %d", _byte_code_incr, _byte_code_addr, _lineno_incr, _lineno)
    return _lineno
