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

import inspect
import re
import sys
import traceback
import types
import typing


def fqname(
        obj,  # type: typing.Any
):  # type: (...) -> str
    """
    .. todo:: Check whether :func:`fqname()` could be factorized with :func:`scenario._reflex.qualname()`.
    """
    if inspect.ismodule(obj):
        return str(obj.__name__)
    return f"{inspect.getmodule(obj)}.{obj.__name__}"


def isspecialfunction(
        obj,  # type: typing.Any
):  # type: (...) -> bool
    """
    Due to [sphinx#6808](https://github.com/sphinx-doc/sphinx/issues/6808), it seems preferrable to rely on the actual object,
    rather than the ``what`` and ``name`` parameters, in this class's *autodoc* handlers,
    which behaviour does not always conform to their respective documentation.

    Inspired from:
    - https://stackoverflow.com/questions/5599254/how-to-use-sphinxs-autodoc-to-document-a-classs-init-self-method
    - https://docs.python.org/3/reference/datamodel.html
    """
    return (inspect.isfunction(obj) or inspect.ismethod(obj)) and (obj.__name__ in (
        # 3. Data model (https://docs.python.org/3/reference/datamodel.html#data-model)
        # 3.1. Objects, values and types (https://docs.python.org/3/reference/datamodel.html#objects-values-and-types)
        # 3.2. The standard type hierarchy (https://docs.python.org/3/reference/datamodel.html#the-standard-type-hierarchy)
        #     Memo: Interesting description about special attributes.
        # 3.3. Special method names (https://docs.python.org/3/reference/datamodel.html#special-method-names)
        # 3.3.1. Basic customization (https://docs.python.org/3/reference/datamodel.html#basic-customization).
        "__new__",              # https://docs.python.org/3/reference/datamodel.html#object.__new__
        "__init__",             # https://docs.python.org/3/reference/datamodel.html#object.__init__
        "__del__",              # https://docs.python.org/3/reference/datamodel.html#object.__del__
        "__repr__",             # https://docs.python.org/3/reference/datamodel.html#object.__repr__
        "__str__",              # https://docs.python.org/3/reference/datamodel.html#object.__str__
        "__bytes__",            # https://docs.python.org/3/reference/datamodel.html#object.__bytes__
        "__format__",           # https://docs.python.org/3/reference/datamodel.html#object.__format__
        "__lt__",               # https://docs.python.org/3/reference/datamodel.html#object.__lt__
        "__le__",               # https://docs.python.org/3/reference/datamodel.html#object.__le__
        "__eq__",               # https://docs.python.org/3/reference/datamodel.html#object.__eq__
        "__ne__",               # https://docs.python.org/3/reference/datamodel.html#object.__ne__
        "__gt__",               # https://docs.python.org/3/reference/datamodel.html#object.__gt__
        "__ge__",               # https://docs.python.org/3/reference/datamodel.html#object.__ge__
        "__hash__",             # https://docs.python.org/3/reference/datamodel.html#object.__hash__
        "__bool__",             # https://docs.python.org/3/reference/datamodel.html#object.__bool__
        # 3.3.2. Customizing attribute access (https://docs.python.org/3/reference/datamodel.html#customizing-attribute-access)
        "__getattr__",          # https://docs.python.org/3/reference/datamodel.html#object.__getattr__
        "__getattributes__",    # https://docs.python.org/3/reference/datamodel.html#object.__getattribute__
        "__setattr__",          # https://docs.python.org/3/reference/datamodel.html#object.__setattr__
        "__delattr__",          # https://docs.python.org/3/reference/datamodel.html#object.__delattr__
        "__dir__",              # https://docs.python.org/3/reference/datamodel.html#object.__dir__
        # 3.3.2.1. Customizing module attribute access (https://docs.python.org/3/reference/datamodel.html#customizing-module-attribute-access)
        # 3.3.2.2. Implementing Descriptors (https://docs.python.org/3/reference/datamodel.html#implementing-descriptors)
        "__get__",              # https://docs.python.org/3/reference/datamodel.html#object.__get__
        "__set__",              # https://docs.python.org/3/reference/datamodel.html#object.__set__
        "__delete__",           # https://docs.python.org/3/reference/datamodel.html#object.__delete__
        # 3.3.2.3. Invoking Descriptors (https://docs.python.org/3/reference/datamodel.html#invoking-descriptors)
        # 3.3.2.4. __slots__ (https://docs.python.org/3/reference/datamodel.html#slots)
        "__slots__",            # https://docs.python.org/3/reference/datamodel.html#object.__slots__
        # 3.3.2.4.1. Notes on using __slots__ (https://docs.python.org/3/reference/datamodel.html#notes-on-using-slots)
        # 3.3.3. Customizing class creation (https://docs.python.org/3/reference/datamodel.html#customizing-class-creation)
        "__init_subclass__",    # https://docs.python.org/3/reference/datamodel.html#object.__init_subclass__
        "__set_name__",         # https://docs.python.org/3/reference/datamodel.html#object.__set_name__
        # 3.3.3.1. Metaclasses (https://docs.python.org/3/reference/datamodel.html#metaclasses)
        # 3.3.3.2. Resolving MRO entries (https://docs.python.org/3/reference/datamodel.html#resolving-mro-entries)
        # 3.3.3.3. Determining the appropriate metaclass (https://docs.python.org/3/reference/datamodel.html#determining-the-appropriate-metaclass)
        # 3.3.3.4. Preparing the class namespace (https://docs.python.org/3/reference/datamodel.html#preparing-the-class-namespace)
        # 3.3.3.5. Executing the class body (https://docs.python.org/3/reference/datamodel.html#executing-the-class-body)
        # 3.3.3.6. Creating the class object (https://docs.python.org/3/reference/datamodel.html#creating-the-class-object)
        # 3.3.3.7. Uses for metaclasses (https://docs.python.org/3/reference/datamodel.html#uses-for-metaclasses)
        # 3.3.4. Customizing instance and subclass checks (https://docs.python.org/3/reference/datamodel.html#customizing-instance-and-subclass-checks)
        "__instancecheck__",    # https://docs.python.org/3/reference/datamodel.html#class.__instancecheck__
        "__subclasscheck__",    # https://docs.python.org/3/reference/datamodel.html#class.__subclasscheck__
        # 3.3.5. Emulating generic types (https://docs.python.org/3/reference/datamodel.html#emulating-generic-types)
        "__class_getitem__",    # https://docs.python.org/3/reference/datamodel.html#object.__class_getitem__
        # 3.3.5.1. The purpose of __class_getitem__ (https://docs.python.org/3/reference/datamodel.html#the-purpose-of-class-getitem)
        # 3.3.5.2. __class_getitem__ versus __getitem__ (https://docs.python.org/3/reference/datamodel.html#class-getitem-versus-getitem)
        # 3.3.6. Emulating callable objects (https://docs.python.org/3/reference/datamodel.html#emulating-callable-objects)
        "__call__",             # https://docs.python.org/3/reference/datamodel.html#object.__call__
        # 3.3.7. Emulating container types (https://docs.python.org/3/reference/datamodel.html#emulating-container-types)
        "__len__",              # https://docs.python.org/3/reference/datamodel.html#object.__len__
        "__length_hint__",      # https://docs.python.org/3/reference/datamodel.html#object.__length_hint__
        "__getitem__",          # https://docs.python.org/3/reference/datamodel.html#object.__getitem__
        "__setitem__",          # https://docs.python.org/3/reference/datamodel.html#object.__setitem__
        "__delitem__",          # https://docs.python.org/3/reference/datamodel.html#object.__delitem__
        "__missing__",          # https://docs.python.org/3/reference/datamodel.html#object.__missing__
        "__iter__",             # https://docs.python.org/3/reference/datamodel.html#object.__iter__
        "__reversed__",         # https://docs.python.org/3/reference/datamodel.html#object.__reversed__
        "__contains__",         # https://docs.python.org/3/reference/datamodel.html#object.__contains__
        # 3.3.8. Emulating numeric types (https://docs.python.org/3/reference/datamodel.html#emulating-numeric-types)
        "__add__",              # https://docs.python.org/3/reference/datamodel.html#object.__add__
        "__sub__",              # https://docs.python.org/3/reference/datamodel.html#object.__sub__
        "__mul__",              # https://docs.python.org/3/reference/datamodel.html#object.__mul__
        "__matmul__",           # https://docs.python.org/3/reference/datamodel.html#object.__matmul__
        "__truediv__",          # https://docs.python.org/3/reference/datamodel.html#object.__truediv__
        "__floordiv__",         # https://docs.python.org/3/reference/datamodel.html#object.__floordiv__
        "__mod__",              # https://docs.python.org/3/reference/datamodel.html#object.__mod__
        "__divmod__",           # https://docs.python.org/3/reference/datamodel.html#object.__divmod__
        "__pow__",              # https://docs.python.org/3/reference/datamodel.html#object.__pow__
        "__lshift__",           # https://docs.python.org/3/reference/datamodel.html#object.__lshift__
        "__rshift__",           # https://docs.python.org/3/reference/datamodel.html#object.__rshift__
        "__and__",              # https://docs.python.org/3/reference/datamodel.html#object.__and__
        "__xor__",              # https://docs.python.org/3/reference/datamodel.html#object.__xor__
        "__or__",               # https://docs.python.org/3/reference/datamodel.html#object.__or__
        "__radd__",             # https://docs.python.org/3/reference/datamodel.html#object.__radd__
        "__rsub__",             # https://docs.python.org/3/reference/datamodel.html#object.__rsub__
        "__rmul__",             # https://docs.python.org/3/reference/datamodel.html#object.__rmul__
        "__rmatmul__",          # https://docs.python.org/3/reference/datamodel.html#object.__rmatmul__
        "__rtruediv__",         # https://docs.python.org/3/reference/datamodel.html#object.__rtruediv__
        "__rfloordiv__",        # https://docs.python.org/3/reference/datamodel.html#object.__rfloordiv__
        "__rmod__",             # https://docs.python.org/3/reference/datamodel.html#object.__rmod__
        "__rdivmod__",          # https://docs.python.org/3/reference/datamodel.html#object.__rdivmod__
        "__rpow__",             # https://docs.python.org/3/reference/datamodel.html#object.__rpow__
        "__rlshift__",          # https://docs.python.org/3/reference/datamodel.html#object.__rlshift__
        "__rrshift__",          # https://docs.python.org/3/reference/datamodel.html#object.__rrshift__
        "__rand__",             # https://docs.python.org/3/reference/datamodel.html#object.__rand__
        "__rxor__",             # https://docs.python.org/3/reference/datamodel.html#object.__rxor__
        "__ror__",              # https://docs.python.org/3/reference/datamodel.html#object.__ror__
        "__iadd__",             # https://docs.python.org/3/reference/datamodel.html#object.__iadd__
        "__isub__",             # https://docs.python.org/3/reference/datamodel.html#object.__isub__
        "__imul__",             # https://docs.python.org/3/reference/datamodel.html#object.__imul__
        "__imatmul__",          # https://docs.python.org/3/reference/datamodel.html#object.__imatmul__
        "__itruediv__",         # https://docs.python.org/3/reference/datamodel.html#object.__itruediv__
        "__ifloordiv__",        # https://docs.python.org/3/reference/datamodel.html#object.__ifloordiv__
        "__imod__",             # https://docs.python.org/3/reference/datamodel.html#object.__imod__
        "__ipow__",             # https://docs.python.org/3/reference/datamodel.html#object.__ipow__
        "__ilshift__",          # https://docs.python.org/3/reference/datamodel.html#object.__ilshift__
        "__irshift__",          # https://docs.python.org/3/reference/datamodel.html#object.__irshift__
        "__iand__",             # https://docs.python.org/3/reference/datamodel.html#object.__iand__
        "__ixor__",             # https://docs.python.org/3/reference/datamodel.html#object.__ixor__
        "__ior__",              # https://docs.python.org/3/reference/datamodel.html#object.__ior__
        "__neg__",              # https://docs.python.org/3/reference/datamodel.html#object.__neg__
        "__pos__",              # https://docs.python.org/3/reference/datamodel.html#object.__pos__
        "__abs__",              # https://docs.python.org/3/reference/datamodel.html#object.__abs__
        "__invert__",           # https://docs.python.org/3/reference/datamodel.html#object.__invert__
        "__complex__",          # https://docs.python.org/3/reference/datamodel.html#object.__complex__
        "__int__",              # https://docs.python.org/3/reference/datamodel.html#object.__int__
        "__float__",            # https://docs.python.org/3/reference/datamodel.html#object.__float__
        "__index__",            # https://docs.python.org/3/reference/datamodel.html#object.__index__
        "__round__",            # https://docs.python.org/3/reference/datamodel.html#object.__round__
        "__trunc__",            # https://docs.python.org/3/reference/datamodel.html#object.__trunc__
        "__floor__",            # https://docs.python.org/3/reference/datamodel.html#object.__floor__
        "__ceil__",             # https://docs.python.org/3/reference/datamodel.html#object.__ceil__
        # 3.3.9. With Statement Context Managers (https://docs.python.org/3/reference/datamodel.html#with-statement-context-managers)
        "__enter__",            # https://docs.python.org/3/reference/datamodel.html#object.__enter__
        "__exit__",             # https://docs.python.org/3/reference/datamodel.html#object.__exit__
        # 3.3.10. Customizing positional arguments in class pattern matching
        #         (https://docs.python.org/3/reference/datamodel.html#customizing-positional-arguments-in-class-pattern-matching)
        # 3.3.11. Special method lookup (https://docs.python.org/3/reference/datamodel.html#special-method-lookup)
        # 3.4. Coroutines (https://docs.python.org/3/reference/datamodel.html#coroutines)
        # 3.4.1. Awaitable Objects (https://docs.python.org/3/reference/datamodel.html#awaitable-objects)
        "__await__",            # https://docs.python.org/3/reference/datamodel.html#object.__await__
        # 3.4.2. Coroutine Objects (https://docs.python.org/3/reference/datamodel.html#coroutine-objects)
        # 3.4.3. Asynchronous Iterators (https://docs.python.org/3/reference/datamodel.html#asynchronous-iterators)
        "__aiter__",            # https://docs.python.org/3/reference/datamodel.html#object.__aiter__
        "__anext__",            # https://docs.python.org/3/reference/datamodel.html#object.__anext__
        # 3.4.4. Asynchronous Context Managers (https://docs.python.org/3/reference/datamodel.html#asynchronous-context-managers)
        "__aenter__",           # https://docs.python.org/3/reference/datamodel.html#object.__aenter__
        "__aexit__",            # https://docs.python.org/3/reference/datamodel.html#object.__aexit__

        # Other special methods.
        "__fspath__",           # https://docs.python.org/3/library/os.html#os.PathLike.__fspath__
    ))


def reloadscenariowithtypechecking():  # type: (...) -> None
    """
    Inspired from [sphinx-autodoc-typehints#22](https://github.com/tox-dev/sphinx-autodoc-typehints/issues/22#issuecomment-423289499)
    """
    from ._logging import Logger

    _logger = Logger.getinstance(Logger.Id.TYPE_CHECKING_RELOAD)  # type: Logger
    _logger.debug("reloadscenariowithtypechecking()")

    # Find out `scenario` modules to reload.
    _module_names_to_reload = []  # type: typing.List[str]
    for _module_name in sys.modules:  # type: str
        _words = _module_name.split(".")  # type: typing.Sequence[str]
        if (len(_words) > 0) and (_words[0] == "scenario") and ((len(_words) == 1) or (_words[1] not in ("tools", "test"))):
            _module_names_to_reload.append(_module_name)

    # Reload them with `typing.TYPE_CHECKING` enabled.
    _module_names_to_reload.sort()
    while _module_names_to_reload:
        _module_name = _module_names_to_reload.pop(0)  # Type already defined above.
        _logger.info(f"Reloading {_module_name!r} with `typing.TYPE_CHECKING` enabled")
        try:
            reloadwithtypechecking(_module_name)
        except Exception as _err:
            _logger.warning(f"Error while reloading {_module_name!r}: {_err!r}")


# Cache of module names that have already been `typing.TYPE_CHECKING`-reloaded.
_reloadwithtypechecking_cache = []  # type: typing.List[str]


def reloadwithtypechecking(
        module_name,  # type: str
):  # type: (...) -> None
    from scenario._reflex import importmodulefrompath  # noqa  ## Access to a protected member.
    from ._logging import Logger

    _logger = Logger.getinstance(Logger.Id.TYPE_CHECKING_RELOAD)  # type: Logger
    _logger.debug("reloadwithtypechecking(module_name=%r)", module_name)

    # Check the cache at first.
    if module_name in _reloadwithtypechecking_cache:
        _logger.debug("Already reloaded!")
        return

    # List of module names being reloaded along the recursive calls below,
    # in order to prevent infinite loops due to type checking cyclic dependencies.
    _being_reloaded = []  # type: typing.List[str]

    def _reload(
            module_name,  # type: str  # noqa  ## Shadows name 'module_name' from outer scope
    ):  # type: (...) -> None
        """
        Recursive function that reloads a module,
        and in case of ``ImportError`` exceptions, tries to reload typing dependencies.
        """
        # Mark the given module name as being reloaded.
        _being_reloaded.append(module_name)

        # Original module, previously loaded with `typing.TYPE_CHECKING` disabled.
        _original_module = sys.modules[module_name]  # type: types.ModuleType
        _logger.debug("_original_module = %r", _original_module)
        _logger.debug("_original_module.__file__ = %r", _original_module.__file__)

        # Keep trying to reload the module with `typing.TYPE_CHECKING` enabled until:
        # - either it succeeds directly,
        # - or it succeeds after typing dependencies have been reloaded with `typing.TYPE_CHECKING` enabled as well,
        # - or it fails due to type checking cyclic dependencies (`ImportError` raised).
        while True:
            try:
                # Activate `typing.TYPE_CHECKING`.
                typing.TYPE_CHECKING = True

                # Reload the module:
                # - Don't use `importlib.reload()`, otherwise the original modules would be replaced, possibly breaking consistency by the way.
                # importlib.reload(_original_module)
                # - Reload as a detached module...
                _logger.debug("Reloading %r...", module_name)
                assert _original_module.__file__
                _reloaded_module = importmodulefrompath(
                    _original_module.__file__,
                    # Don't read from `sys.modules`, nor save the reloaded module in `sys.modules`.
                    sys_modules_cache=False,
                )
                _logger.debug("_reloaded_module = %r", _reloaded_module)

                #   ... then copy extra members from the reloaded module to the original one.
                _original_members = vars(_original_module)  # type: typing.Dict[str, typing.Any]
                _reloaded_members = vars(_reloaded_module)  # type: typing.Dict[str, typing.Any]
                for _member_name in _reloaded_members:  # type: str
                    if _member_name not in _original_members:
                        # Note: It seems that the copy below copies the docstring attached with the members as well, so far so good!
                        _logger.debug("Copying %r member from reloaded to original module", _member_name)
                        setattr(_original_module, _member_name, _reloaded_members[_member_name])
                _logger.debug("Overwriting docstring from reloaded to original module")
                setattr(_original_module, "__doc__", _reloaded_members["__doc__"])

                # Success.
                _reloadwithtypechecking_cache.append(module_name)
                return

            except ImportError as _err:
                _logger.debug("Import error: %r", _err)
                # Memo: The `_err.name` and `_err.path` fields don't seem to be set...
                _logger.debug("_err.name = %r", _err.name)
                _logger.debug("_err.path = %r", _err.path)

                # Find out the name of the typing module dependency.
                _module_dependency = ""  # type: str
                _match = re.search(r"cannot import name '([^']*)' from '([^']*)'", str(_err))  # type: typing.Optional[typing.Match[str]]
                if _match:
                    _module_dependency = _match.group(2)
                else:
                    # If the regex above fails, fallback on analyzing the exception traceback
                    # (case with python 3.6: the 'from ...' part of the exception message is not given, just the name).
                    _tb_err = traceback.TracebackException.from_exception(_err)  # type: traceback.TracebackException
                    _tb_lines = "".join(_tb_err.stack.format()).splitlines()  # type: typing.Sequence[str]
                    for _tb_line in _tb_lines:  # type: str
                        _logger.debug(_tb_line)
                    _match = re.search(r"from \.(.*) import ", _tb_lines[-1])  # Type already declared above.
                    if _match:
                        _module_dependency = f"scenario.{_match.group(1)}"

                # Try to reload the typing dependency recursively...
                if _module_dependency:
                    if _module_dependency in _being_reloaded:
                        # ... unless we detect a type checking cyclic dependency.
                        raise ImportError(f"Cannot import {module_name!r} due to type checking cyclic dependencies with {_module_dependency!r}")
                    else:
                        # Reload the typing dependency.
                        _reload(_module_dependency)

                        # If the typing dependency could be reloaded successfully, try again reloading the module for this `_reload()` call.
                        continue

                # Unhandled `ImportError`, re-raise the exception as is.
                raise _err

            finally:
                # Whatever happened, reset `typing.TYPE_CHECKING` eventually.
                typing.TYPE_CHECKING = False

    # Initial recursive call.
    _reload(module_name)
