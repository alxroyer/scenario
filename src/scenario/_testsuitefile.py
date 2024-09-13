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
Test suite file management.
"""
import collections
import typing

if True:
    from ._debugclasses import DebugClass as _DebugClassImpl  # @perf
    from ._errcodes import ErrorCode as _ErrorCodeImpl  # @perf
    from ._errcodes import ErrorCodeError as _ErrorCodeErrorImpl  # @perf
    from ._logger import Logger as _LoggerImpl  # @inheritance
    from ._path import Path as _PathImpl  # @perf
    from ._reflection import qualname as _qualname  # @perf
    from ._textfileutils import TextFile as _TextFileImpl  # @perf
if typing.TYPE_CHECKING:
    from ._path import AnyPathType as _AnyPathType
    from ._path import Path as _PathType


class TestSuiteFile(_LoggerImpl):
    """
    Test suite file reader.
    """

    def __init__(
            self,
            path,  # type: _AnyPathType
    ):  # type: (...) -> None
        """
        Initializes a test suite file reader from its path.

        :param path: Test suite file path.
        """
        _LoggerImpl.__init__(self, log_class=_DebugClassImpl.TEST_SUITE_FILE)

        #: Test suite file path.
        self.path = _PathImpl(path)  # type: _PathType

        #: Script paths described by the test suite file.
        #:
        #: Filled once the test suite file has been successfully read.
        #:
        #: .. seealso:: :meth:`read()`.
        self.script_paths = []  # type: typing.Sequence[_PathType]

    def __repr__(self):  # type: () -> str
        """
        Canonical string representation.
        """
        return f"<{_qualname(type(self))} path='{self.path}'>"

    def read(self):  # type: (...) -> None
        """
        Reads and parses the test suite file.

        :raise ._errcodes.ErrorCodeError: With :attr:`._errcodes.ErrorCode.INPUT_FORMAT_ERROR`, when the file could not be parsed.
        """
        # Reset the script path list in case :meth:`parse()` is called several times..
        self.script_paths = []

        # In order to avoid calling `Path.samefile()` many times,
        # let's build the resulting script path list with an ordered dictionary
        # using abspaths for keys.
        _script_paths = collections.OrderedDict()  # type: collections.OrderedDict[str, _PathType]

        # For each line in the campaign file.
        self.debug("Reading '%s'", self.path)
        with self.pushindentation():
            for _line in _TextFileImpl(self.path, "r").readlines():  # type: str
                _line = _line.strip()
                if not _line:
                    continue
                if _line.startswith("#"):
                    continue

                try:
                    if _line.startswith("-"):
                        # Black list.
                        _line = _line[1:].strip()
                        self.debug("Black list line: %r", _line)
                        with self.pushindentation():
                            for _rm_path in self.path.parent.glob(_line):  # type: _PathType
                                if _rm_path.abspath in _script_paths:
                                    self.debug("- '%s'", _rm_path)
                                    del _script_paths[_rm_path.abspath]

                    else:
                        # White list.
                        self.debug("White list line: %r", _line)
                        with self.pushindentation():
                            if _line.startswith("+"):
                                _line = _line[1:].strip()
                            if "*" in _line:
                                for _add_path in self.path.parent.glob(_line):  # type: _PathType
                                    if not _add_path.is_file():
                                        continue
                                    if _add_path.abspath not in _script_paths:
                                        self.debug("+ '%s'", _add_path)
                                        _script_paths[_add_path.abspath] = _add_path
                            else:
                                _add_path = self.path.parent / _line  # Type already declared above
                                self.debug("+ '%s'", _add_path)
                                _script_paths[_add_path.abspath] = _add_path

                except Exception as _err:
                    raise _ErrorCodeErrorImpl(
                        error_code=_ErrorCodeImpl.INPUT_FORMAT_ERROR,
                        message=f"Error while parsing '{self.path}': {_err}",
                        exception=_err,
                    )

        # Eventually feed the resulting script path list.
        self.script_paths = list(_script_paths.values())
