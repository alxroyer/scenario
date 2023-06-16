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
import types
import typing

if True:
    from ._logger import Logger as _LoggerImpl  # `Logger` used for inheritance.
if typing.TYPE_CHECKING:
    from ._path import AnyPathType as _AnyPathType


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
        Computes an :class:`CodeLocation` based on a traceback item.

        :param tb_item: Traceback item.
        :return: :class:`CodeLocation` instance.
        """
        from ._path import Path

        assert tb_item.lineno is not None, f"Invalid traceback item {tb_item!r} (line missing)"
        return CodeLocation(
            file=Path(tb_item.filename),
            line=tb_item.lineno,
            qualname=tb_item.name,
        )

    @staticmethod
    def frommethod(
            method,  # type: types.MethodType
    ):  # type: (...) -> CodeLocation
        """
        Computes an :class:`CodeLocation` based on a method.

        :param method: Method to locate.
        :return: :class:`CodeLocation` instance.
        """
        from ._path import Path
        from ._reflection import qualname

        _source_file = inspect.getsourcefile(method)  # type: typing.Optional[str]
        assert _source_file
        return CodeLocation(
            file=Path(_source_file),
            line=inspect.getsourcelines(method)[1],
            qualname=qualname(method),
        )

    @staticmethod
    def fromclass(
            cls,  # type: type
    ):  # type: (...) -> CodeLocation
        """
        Computes an :class:`CodeLocation` based on a class.

        :param cls: Class to locate.
        :return: :class:`CodeLocation` instance.
        """
        from ._path import Path
        from ._reflection import qualname

        _source_file = inspect.getsourcefile(cls)  # type: typing.Optional[str]
        assert _source_file
        return CodeLocation(
            file=Path(_source_file),
            line=inspect.getsourcelines(cls)[1],
            qualname=qualname(cls),
        )

    def __init__(
            self,
            file,  # type: _AnyPathType
            line,  # type: int
            qualname,  # type: str
    ):  # type: (...) -> None
        """
        Inititializes the :class:`CodeLocation` instance with the given values.

        :param file: File path where the execution takes place.
        :param line: Line in the file where the execution takes place.
        :param qualname: Qualified name of the class/function pointed.
        """
        from ._path import Path

        #: File path.
        #:
        #: Set as a :class:`._path.Path` when ``file`` is passed on as a :class:`._path.Path`.
        #: Set as a ``pathlib.Path`` otherwise, possibly a relative path in that case.
        self.file = pathlib.Path(file)  # type: typing.Union[pathlib.Path, Path]
        if isinstance(file, Path):
            self.file = file
        #: Line number in the file.
        self.line = line  # type: int
        #: Method name.
        self.qualname = qualname  # type: str

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
        from ._path import Path

        if isinstance(self.file, Path):
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
    """

    def __init__(self):  # type: (...) -> None
        """
        Sets up logging for the :class:`ExecutionLocations` class.
        """
        from ._debugclasses import DebugClass

        _LoggerImpl.__init__(self, log_class=DebugClass.EXECUTION_LOCATIONS)

    def fromcurrentstack(
            self,
            limit=None,  # type: int
            fqn=False,  # type: bool
    ):  # type: (...) -> typing.List[CodeLocation]
        """
        Builds a stack of :class:`CodeLocation` from the current call stack.

        :param limit: Maximum number of backward items.
        :param fqn: ``True`` to ensure fully qualified names.
        :return: Stack of :class:`CodeLocation`.
        """
        return self._fromtbitems(traceback.extract_stack(), limit=limit, fqn=fqn)

    def fromexception(
            self,
            exception,  # type: traceback.TracebackException
            limit=None,  # type: int
            fqn=False,  # type: bool
    ):  # type: (...) -> typing.List[CodeLocation]
        """
        Builds a stack of :class:`CodeLocation` from an exception.

        :param exception: Exception to build the stack from.
        :param limit: Maximum number of backward items.
        :param fqn: ``True`` to ensure fully qualified names.
        :return: Stack of :class:`CodeLocation`.
        """
        return self._fromtbitems(exception.stack, limit=limit, fqn=fqn)

    def _fromtbitems(
            self,
            tb_items,  # type: typing.List[traceback.FrameSummary]
            limit=None,  # type: int
            fqn=False,  # type: bool
    ):  # type: (...) -> typing.List[CodeLocation]
        """
        Builds a stack of :class:`CodeLocation` from traceback items.

        :param tb_items: Traceback items to build the stack from.
        :return: Stack of :class:`CodeLocation`.
        """
        from ._path import Path
        from ._reflection import checkfuncqualname

        self.debug("Computing test location:")

        _locations = []  # type: typing.List[CodeLocation]

        self.debug("len(tb_items) = %d", len(tb_items))
        self.pushindentation()

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
            if isinstance(_location.file, Path) and _location.file.is_relative_to(pathlib.Path(__file__).parent):
                _keep = False
            for _skipped_path in (
                # - Avoid unittest sources.
                pathlib.Path("unittest") / "case.py",
                # - Avoid PyCharm sources (visible in the execution stack when debugging).
                pathlib.Path("pydevd.py"),
                pathlib.Path("_pydev_execfile.py"),
            ):  # type: pathlib.Path
                if _location.file.as_posix().endswith(_skipped_path.as_posix()):
                    _keep = False

            if _keep:
                self.debug("Location stack trace - %s:%d: %s", _location.file, _location.line, _location.qualname)
                if fqn:
                    # Ensure the location function name is fully qualified.
                    _location.qualname = checkfuncqualname(file=_location.file, line=_location.line, func_name=_location.qualname)
                    # Fix the `traceback` item as well.
                    _tb_item.name = _location.qualname
                _locations.insert(0, _location)
            else:
                self.debug("Skipped stack trace - %s:%s: %s", _location.file, _location.line, _location.qualname)
                _scenario_runner_path = pathlib.Path("scenario") / "src" / "scenario" / "scenariorunner.py"  # type: pathlib.Path
                if _location.file.as_posix().endswith(_scenario_runner_path.as_posix()) and (_location.qualname == "main"):
                    self.debug("End of test location computation")
                    break

        self.popindentation()
        self.debug("%d locations returned", len(_locations))
        return _locations


#: Main instance of :class:`ExecutionLocations`.
EXECUTION_LOCATIONS = ExecutionLocations()  # type: ExecutionLocations
