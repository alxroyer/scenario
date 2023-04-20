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

import importlib
import inspect
import pathlib
import re
import sphinx.application
import sphinx.pycode
import sys
import traceback
import types
import typing


# Cache of module names that have already been `typing.TYPE_CHECKING`-reloaded.
_RELOADWITHTYPECHECKING_CACHE = []  # type: typing.List[str]

# Dictionary of {fqname: type}.
SCENARIO_TYPES = {}  # type: typing.Dict[str, typing.Any]


def _scenariodocumentedmodulenames():  # type: (...) -> typing.Sequence[str]
    _scenario_documented_module_names = []  # type: typing.List[str]
    for _module_name in sys.modules:  # type: str
        _words = _module_name.split(".")  # type: typing.Sequence[str]
        if (
            (len(_words) > 0) and (_words[0] == "scenario")
            and (
                (len(_words) == 1)
                or (_words[1] not in ("tools", "test"))
            )
        ):
            _scenario_documented_module_names.append(_module_name)
    _scenario_documented_module_names.sort()

    return _scenario_documented_module_names


def _reloadscenariomoduleswithtypechecking():  # type: (...) -> None
    """
    Inspired from [sphinx-autodoc-typehints#22](https://github.com/tox-dev/sphinx-autodoc-typehints/issues/22#issuecomment-423289499)
    """
    from ._logging import Logger

    _logger = Logger.getinstance(Logger.Id.TYPE_CHECKING_RELOAD)  # type: Logger
    _logger.debug("_reloadscenariowithtypechecking()")

    # Reload scenario modules with `typing.TYPE_CHECKING` enabled.
    for _module_name in _scenariodocumentedmodulenames():  # type: str
        _logger.info(f"Reloading {_module_name!r} with `typing.TYPE_CHECKING` enabled")
        try:
            _reloadmodulewithtypechecking(_module_name)
        except Exception as _err:
            _logger.warning(f"Error while reloading {_module_name!r}: {_err!r}")


def _reloadmodulewithtypechecking(
        module_name,  # type: str
):  # type: (...) -> None
    from scenario._reflection import importmodulefrompath  # noqa  ## Access to a protected member.
    from ._logging import Logger
    from ._reflection import fqname

    _logger = Logger.getinstance(Logger.Id.TYPE_CHECKING_RELOAD)  # type: Logger
    _logger.debug("_reloadwithtypechecking(module_name=%r)", module_name)

    # Check the cache at first.
    if module_name in _RELOADWITHTYPECHECKING_CACHE:
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
        _logger.debug("_original_module = [%d] %r", id(_original_module), _original_module)
        _logger.debug("_original_module.__file__ = %r", _original_module.__file__)

        # Keep trying to reload the module with `typing.TYPE_CHECKING` enabled until:
        # - either it succeeds directly,
        # - or it succeeds after typing dependencies have been reloaded with `typing.TYPE_CHECKING` enabled as well,
        # - or it fails due to type checking cyclic dependencies (`ImportError` raised).
        while True:
            try:
                # Activate `typing.TYPE_CHECKING`.
                typing.TYPE_CHECKING = True

                # Reload the module (without replacing the original one).
                _logger.debug("Reloading %r...", module_name)
                assert _original_module.__file__
                if pathlib.Path(_original_module.__file__).name != "__init__.py":
                    # Don't use `importlib.reload()` in general, otherwise the original modules would be replaced, possibly breaking consistency by the way.
                    _reloaded_module = importmodulefrompath(
                        _original_module.__file__,
                        # Don't read from `sys.modules`, nor save the reloaded module in `sys.modules`.
                        sys_modules_cache=False,
                    )  # type: types.ModuleType
                else:
                    # Don't use `importlib.reload()`, except for packages!
                    # due to `importmodulefrompath()` can't ensure the `__path__` symbol to be defined,
                    # which is required for the `scenario` package.
                    try:
                        _reloaded_module = importlib.reload(_original_module)  # Type already declared above.
                    finally:
                        # Fix `sys.modules` in order to keep the original module as the reference.
                        _logger.debug("Restoring original module [%d] %s in `sys.modules`", id(_original_module), fqname(_original_module))
                        sys.modules[module_name] = _original_module
                _logger.debug("_reloaded_module = [%d] %r", id(_reloaded_module), _reloaded_module)

                # Copy extra members from the reloaded module to the original one.
                _original_members = vars(_original_module)  # type: typing.Dict[str, typing.Any]
                _logger.debug("_original_members = %r", list(_original_members))
                _reloaded_members = vars(_reloaded_module)  # type: typing.Dict[str, typing.Any]
                _logger.debug("_reloaded_members = %r", list(_reloaded_members))
                for _member_name in _reloaded_members:  # type: str
                    if _member_name not in _original_members:
                        # Note:
                        # It seems that the attribute copy below is enough to enable the corresponding documentation attached with it.
                        # The documentation is probably retrieved later in Sphinx through `sphinx.pycode.Parser.comments`.
                        _logger.debug("Copying %r member from reloaded [%d] to original module [%d] %s",
                                      _member_name, id(_reloaded_module), id(_original_module), fqname(_original_module))
                        setattr(_original_module, _member_name, _reloaded_members[_member_name])
                _logger.debug("Overwriting docstring from reloaded to original module %s", fqname(_original_module))
                setattr(_original_module, "__doc__", _reloaded_members["__doc__"])

                # Success.
                _RELOADWITHTYPECHECKING_CACHE.append(module_name)
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


def _trackscenariotypes():  # type: (...) -> None
    from ._logging import Logger
    from ._reflection import fqname

    _logger = Logger.getinstance(Logger.Id.TRACK_SCENARIO_TYPES)  # type: Logger
    _logger.debug("_trackscenariotypes()")

    for _module_name in _scenariodocumentedmodulenames():  # type: str
        _module = sys.modules[_module_name]  # type: types.ModuleType
        _logger.debug("Analyzing %r", _module)

        # Use `sphinx.pycode.Parser.comments` to find out original types in the module.
        # Don't use `vars()`, otherwise all neighbour modules that import an original type will be tracked as well,
        # and we won't be able to discriminate which one should be used to configure type aliases in `configuretypealiases()` after.
        # Note: It means that undocumented types won't be tracked by the way. So much the worse!
        _parser = sphinx.pycode.Parser(inspect.getsource(_module))  # type: sphinx.pycode.Parser
        _parser.parse()
        for _class_name, _obj_name in _parser.comments:  # type: str, str
            # Only module members, skip class members.
            if _class_name:
                continue

            _member = getattr(_module, _obj_name)  # type: typing.Any
            # Memo: `fqname()` fails on types, build the type fully qualified name from the local information we have in this function.
            _fq_name = f"{fqname(_module)}.{_obj_name}"  # type: str

            if inspect.getmodule(type(_member)) == typing:
                # `repr()` on a type gives a useful string, let's display that string with `%r` below.
                _logger.debug("  Tracking %s type %r", _fq_name, repr(_member))
                SCENARIO_TYPES[_fq_name] = _member
            else:
                _logger.debug("  (not a type %s: %r)", _fq_name, _member)


def configuretypealiases(
        app,  # type: sphinx.application.Sphinx
        env,  # type: sphinx.application.BuildEnvironment
):  # type: (...) -> None
    from ._logging import Logger

    _logger = Logger.getinstance(Logger.Id.CONFIGURE_TYPE_ALIASES)  # type: Logger
    _logger.debug("configuretypealiases()")

    _logger.debug("Reloading `scenario` modules with `typing.TYPE_CHECKING` enabled")
    _reloadscenariomoduleswithtypechecking()

    _logger.debug("Tracking scenario types")
    _trackscenariotypes()

    # Feed the `autodoc_type_aliases` configuration.
    _logger.debug("Configuring type aliases")
    for _fq_name in SCENARIO_TYPES:  # type: str
        _short_name = _fq_name.split(".")[-1]  # type: str
        if _short_name in env.config.autodoc_type_aliases:
            _logger.warning(f"Duplicate type name {_short_name!r}, already aliased with {env.config.autodoc_type_aliases[_short_name]!r}")
        else:
            env.config.autodoc_type_aliases[_short_name] = f"~{_fq_name}"
            _logger.info("Aliasing %r with %r", _short_name, env.config.autodoc_type_aliases[_short_name])


def checkredundantoptionaltypes(
        annotation,  # type: str
):  # type: (...) -> str
    from ._logging import Logger

    _logger = Logger.getinstance(Logger.Id.CHECK_REDUNDANT_OPTIONAL_TYPE)  # type: Logger
    _logger.debug("checkredundantoptionaltype(annotation=%r)", annotation)

    for _fq_name in SCENARIO_TYPES:  # type: str
        _type = SCENARIO_TYPES[_fq_name]  # type: typing.Any

        # Find out whether the type already describes something optional.
        _repr = repr(_type)  # type: str
        _logger.debug("repr(%s) = %r", _fq_name, _repr)
        if (
            # Python <= 3.7
            _repr.startswith("typing.Optional[")
            or (_repr.startswith("typing.Union[") and _repr.endswith(", NoneType]"))
            # Python >= 3.8
            or _repr.endswith(" | None")
        ):
            _logger.debug("Optional type %s", _fq_name)
        else:
            _logger.debug("(%s not an optional type)", _fq_name)
            # Switch to next type definition.
            continue

        # Search for redundant optional patterns in the given annotation.
        for _redundant_annotation in (
            # Python <= 3.7
            f"~typing.Optional[~{_fq_name}]",
            f"typing.Optional[~{_fq_name}]",
            # Python >= 3.8
            f"~{_fq_name} | None",
        ):  # type: str
            if _redundant_annotation in annotation:
                # If found, simplify the annotation.
                _simple_annotation = f"~{_fq_name}"  # type: str
                _logger.debug("Simplifying %r into %r", _redundant_annotation, _simple_annotation)
                annotation = annotation.replace(_redundant_annotation, _simple_annotation)
                _logger.debug("New annotation: %r", annotation)

    return annotation
