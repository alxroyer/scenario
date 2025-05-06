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
Execution location management.

Execution locations may be used:

- to locate a class / function / method definition (see :class:`._scenariodefinition.ScenarioDefinition` and :class:`._stepdefinition.StepDefinition`),
- to locate the place of the current execution, or where an exception occurred.
"""

import inspect
import pathlib
import re
import traceback
import typing

if True:
    from ._debugclasses import DebugClass as _DebugClassImpl  # @perf
    from ._fastpath import FAST_PATH as _FAST_PATH  # @perf
    from ._logger import Logger as _LoggerImpl  # @inheritance
    from ._path import Path as _PathImpl  # @perf
    from ._path import SRC_SCENARIO_PATH as _SRC_SCENARIO_PATH  # @perf
if typing.TYPE_CHECKING:
    from ._path import AnyPathType as _AnyPathType
    from ._path import Path as _PathType
    from ._reflection import Reflection as _ReflectionType


class CodeLocation:
    """
    Class that describes a code location,
    i.e. a point where an element is defined, or the test execution takes place.
    """

    @staticmethod
    def fromtbitem(
            tb_item,  # type: traceback.FrameSummary
    ):  # type: (...) -> CodeLocation
        """
        Computes a :class:`CodeLocation` from a traceback item.

        :param tb_item: Traceback item.
        :return: :class:`CodeLocation` instance.
        """
        return CodeLocation(tb_item)

    #: Cache for :meth:`fromcodeowner()`.
    _code_owner_locations_cache = {}  # type: typing.Dict[_ReflectionType.CodeOwnerType, CodeLocation]

    @staticmethod
    def fromcodeowner(
            obj,  # type: _ReflectionType.CodeOwnerType
    ):  # type: (...) -> CodeLocation
        """
        Computes a :class:`CodeLocation` from a code owner.

        :param obj: Code owner to locate.
        :return: :class:`CodeLocation` instance.
        """
        # First, search for the location in the cache.
        _location = CodeLocation._code_owner_locations_cache.get(obj)  # type: typing.Optional[CodeLocation]
        if _location is not None:
            return _location

        # Build a `CodeLocation` instance.
        _location = CodeLocation(obj)

        # Save it in the cache and return.
        CodeLocation._code_owner_locations_cache[obj] = _location
        return _location

    @typing.overload
    def __init__(
            self,
            *,
            file,  # type: _AnyPathType
            line,  # type: int
            qualname,  # type: str
    ):  # type: (...) -> None
        ...

    @typing.overload
    def __init__(
            self,
            obj,  # type: typing.Union[traceback.FrameSummary, _ReflectionType.CodeOwnerType]
    ):  # type: (...) -> None
        ...

    def __init__(
            self,
            obj=None,  # type: typing.Union[traceback.FrameSummary, _ReflectionType.CodeOwnerType]
            *,
            file=None,  # type: _AnyPathType
            line=None,  # type: int
            qualname=None,  # type: str
    ):  # type: (...) -> None
        """
        Inititializes the :class:`CodeLocation` instance with the given values.

        :param obj: Object attached with this code location.
        :param file: File path where the execution takes place.
        :param line: Line in the file where the execution takes place.
        :param qualname: Qualified name of the module/class/function.
        """
        #: Object attached with this code location.
        #:
        #: If initialized with a traceback item, resolved to the code owner once :meth:`_resolve()` has been executed.
        self._obj = obj  # type: typing.Optional[typing.Union[traceback.FrameSummary, _ReflectionType.CodeOwnerType]]

        #: File path cache.
        #:
        #: If specified:
        #:
        #: - Set as a :class:`._path.Path` when ``file`` is passed on as a :class:`._path.Path`.
        #: - Set as a ``pathlib.Path`` otherwise, possibly a relative path in that case.
        #:
        #: Resolved by :meth:`_resolve()` from :attr:`_obj` if not specified.
        self._file = (
            file if isinstance(file, _PathImpl)
            else pathlib.Path(file) if (file is not None)
            else None
        )  # type: typing.Optional[typing.Union[pathlib.Path, _PathType]]

        #: Line number cache.
        #:
        #: Resolved by :meth:`_resolve()` from :attr:`_obj` if not specified.
        self._line = line  # type: typing.Optional[int]

        #: Qualified name cache.
        #:
        #: Resolved by :meth:`_resolve()` from :attr:`_obj` if not specified.
        self._qualname = qualname  # type: typing.Optional[str]

    @property
    def file(self):  # type: () -> typing.Union[_PathType, pathlib.Path]
        """
        File path.
        """
        if self._file is None:
            self._resolve()
        if self._file is None:
            raise Exception("Internal error")
        return self._file

    @property
    def line(self):  # type: () -> int
        """
        Line number in the file.
        """
        if self._line is None:
            self._resolve()
        if self._line is None:
            raise Exception("Internal error")
        return self._line

    @property
    def qualname(self):  # type: () -> str
        """
        Qualified name of the module/class/function.
        """
        if self._qualname is None:
            self._resolve()
        if self._qualname is None:
            raise Exception("Internal error")
        return self._qualname

    @property
    def code_owner(self):  # type: () -> typing.Optional[_ReflectionType.CodeOwnerType]
        """
        Module/class/function.

        May be ``None`` if the code location had been instantiated with file, line and qualified name.
        """
        if (self._obj is None) or isinstance(self._obj, traceback.FrameSummary):
            self._resolve()
        if isinstance(self._obj, traceback.FrameSummary):
            raise Exception(f"Can't determine code owner for {self!r}")
        return self._obj

    def _resolve(self):  # type: (...) -> None
        """
        Resolves :attr:`file`, :attr:`line`, :attr:`qualname` properties.
        """
        if self._obj is None:
            raise ValueError("Can't resolve location from None object")

        elif isinstance(self._obj, traceback.FrameSummary):
            self._file = _PathImpl(self._obj.filename)
            if self._obj.lineno is None:
                raise RuntimeError(f"Invalid traceback item {self._obj!r} (line missing)")
            self._line = self._obj.lineno
            self._qualname = self._obj.name

            # Try to resolve the code owner, and ensure the qualified name is actually a qualified name.
            _code_owners = _FAST_PATH.reflection.codeowners(
                file=self._obj.filename,
                line=self._obj.lineno,
                name=self._obj.name,
            )  # type: typing.Optional[typing.Sequence[_ReflectionType.CodeOwnerType]]
            if _code_owners:
                self._obj = _code_owners[-1]
                self._qualname = _FAST_PATH.reflection.qualname(self._obj)

        else:
            # Get the source file of the class/function.
            try:
                _source_file = inspect.getsourcefile(typing.cast(typing.Any, self._obj))  # type: typing.Optional[str]
                assert _source_file is not None
            except Exception:
                raise RuntimeError(f"Can't determine source file for {self._obj!r}")
            self._file = _PathImpl(_source_file)

            # Find the code location of the class/function in the source file.
            self._line = inspect.getsourcelines(typing.cast(typing.Any, self._obj))[1]

            # Compute the qualified name.
            self._qualname = _FAST_PATH.reflection.qualname(self._obj)

    def __repr__(self):  # type: () -> str
        """
        Canonical string representation.
        """
        return f"<CodeLocation (obj={self._obj!r}) file={self._file!r}, line={self._line}, qualname={self._qualname!r}>"

    def __eq__(
            self,
            other,  # type: typing.Any
    ):  # type: (...) -> bool
        """
        Compares the :class:`CodeLocation` instance with another object.

        :param other: Candidate object.
        :return: ``True`` if the objects are similar, ``False`` otherwise.
        """
        if isinstance(other, CodeLocation):
            if other.tolongstring() == self.tolongstring():
                return True
        return False

    def tolongstring(self):  # type: (...) -> str
        """
        Long text representation.
        """
        if isinstance(self.file, _PathImpl):
            return f"{self.file.prettypath}:{self.line}:{self.qualname}"
        else:
            return f"{self.file.as_posix()}:{self.line}:{self.qualname}"

    @staticmethod
    def fromlongstring(
            long_string,  # type: str
    ):  # type: (...) -> CodeLocation
        """
        Computes an :class:`CodeLocation` from its long text representation.

        :param long_string: Long text, as returned by :meth:`tolongstring()`.
        :return: :class:`CodeLocation` instance.
        """
        _match = re.match(r"^(.*):([0-9]+):(.*)$", long_string)
        assert _match, f"Not a valid location: {long_string!r}"

        return CodeLocation(
            file=pathlib.Path(_match.group(1)),
            line=int(_match.group(2)),
            qualname=_match.group(3),
        )


class ExecutionLocations(_LoggerImpl):
    """
    Methods to build execution location stacks.

    Instantiated once with the :data:`EXECUTION_LOCATIONS` singleton.
    """

    def __init__(self):  # type: (...) -> None
        """
        Sets up logging for the :class:`ExecutionLocations` class.
        """
        _LoggerImpl.__init__(self, log_class=_DebugClassImpl.EXECUTION_LOCATIONS)

    def fromcurrentstack(
            self,
            *,
            limit=None,  # type: int
    ):  # type: (...) -> typing.List[CodeLocation]
        """
        Builds a stack of :class:`CodeLocation` from the current call stack.

        :param limit: Maximum number of backward items.
        :return: Stack of :class:`CodeLocation`, from first to last call.
        """
        return self._fromtbitems(traceback.extract_stack(), limit=limit)

    def fromexception(
            self,
            exception,  # type: traceback.TracebackException
            *,
            limit=None,  # type: int
    ):  # type: (...) -> typing.List[CodeLocation]
        """
        Builds a stack of :class:`CodeLocation` from an exception.

        :param exception: Exception to build the stack from.
        :param limit: Maximum number of backward items.
        :return: Stack of :class:`CodeLocation`.
        """
        return self._fromtbitems(exception.stack, limit=limit)

    def _fromtbitems(
            self,
            tb_items,  # type: typing.List[traceback.FrameSummary]
            *,
            limit=None,  # type: int
    ):  # type: (...) -> typing.List[CodeLocation]
        """
        Builds a stack of :class:`CodeLocation` from traceback items.

        :param tb_items: Traceback items to build the stack from.
        :param limit: Maximum number of backward items.
        :return: Stack of :class:`CodeLocation`, from first to last call.
        """
        self.debug("Computing test location:")

        _locations = []  # type: typing.List[CodeLocation]

        self.debug("len(tb_items) = %d", len(tb_items))

        with self.pushindentation():
            # For each stack trace element which class is just above `ScenarioDefinition`.
            for _tb_item in reversed(tb_items):  # type: traceback.FrameSummary
                # Stop when `limit` is reached.
                if limit is not None:
                    if len(_locations) >= limit:
                        break

                try:
                    _location = CodeLocation.fromtbitem(_tb_item)  # type: CodeLocation
                except Exception as _err:
                    # The creation of the `CodeLocation` instance may file for core Python traceback items.
                    self.debug("Could not create `CodeLocation` from %r: %s", _tb_item, _err)
                    self.debug("=> skipping traceback item")
                    continue

                # Filter-out stack trace elements based on file paths:
                _keep = True
                # - Avoid 'src/scenario' sources.
                if isinstance(_location.file, _PathImpl) and _location.file.is_relative_to(_SRC_SCENARIO_PATH):
                    _keep = False
                else:
                    for _skipped_path in (
                        # - Avoid unittest sources.
                        pathlib.Path("unittest") / "case.py",
                        # - Avoid PyCharm sources (visible in the execution stack when debugging).
                        pathlib.Path("pydevd.py"),
                        pathlib.Path("_pydev_execfile.py"),
                    ):  # type: pathlib.Path
                        if _location.file.as_posix().endswith(_skipped_path.as_posix()):
                            _keep = False
                            break

                if _keep:
                    self.debug("Location stack trace - %s:%d: %s", _location.file, _location.line, _location.qualname)
                    _locations.insert(0, _location)
                else:
                    self.debug("Skipped stack trace - %s:%s: %s", _location.file, _location.line, _location.qualname)
                    _scenario_runner_path = pathlib.Path("scenario") / "src" / "scenario" / "scenariorunner.py"  # type: pathlib.Path
                    if _location.file.as_posix().endswith(_scenario_runner_path.as_posix()) and (_location.qualname == "main"):
                        self.debug("End of test location computation")
                        break

        self.debug("%d locations returned", len(_locations))
        return _locations


#: Main instance of :class:`ExecutionLocations`.
#:
#: Also available as :attr:`._fastpath.FastPath.execution_locations`.
#: Please prefer the latter instead of using local imports of this module.
EXECUTION_LOCATIONS = ExecutionLocations()  # type: ExecutionLocations
