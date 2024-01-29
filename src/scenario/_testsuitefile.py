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

import typing

if True:
    from ._logger import Logger as _LoggerImpl  # `Logger` used for inheritance.
    from ._path import Path as _PathImpl  # `Path` imported once for performance concerns.
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
        from ._debugclasses import DebugClass

        _LoggerImpl.__init__(self, log_class=DebugClass.TEST_SUITE_FILE)

        #: Test suite file path.
        self.path = _PathImpl(path)  # type: _PathType

        #: Script paths describes by the test suite file.
        #:
        #: Filled once the test suite file has been successfully read.
        #:
        #: .. seealso:: :meth:`read()`.
        self.script_paths = []  # type: typing.List[_PathType]

    def __repr__(self):  # type: () -> str
        """
        Canonical string representation.
        """
        from ._reflection import qualname

        return f"<{qualname(type(self))} path='{self.path}'>"

    def read(self):  # type: (...) -> None
        """
        Reads and parses the test suite file.

        :raise ._errcodes.ErrorCodeError: With :attr:`._errcodes.ErrorCode.INPUT_FORMAT_ERROR`, when the file could not be parsed.
        """
        from ._errcodes import ErrorCode, ErrorCodeError
        from ._textfileutils import TextFile

        # Reset the script path list in case :meth:`parse()` is called several times..
        self.script_paths = []

        # Foe each line in the campaign file.
        self.debug("Reading '%s'", self.path)
        with self.pushindentation():
            for _line in TextFile(self.path, "r").readlines():  # type: str
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
                                for _test_script_path in self.script_paths:  # type: _PathType
                                    if _test_script_path.samefile(_rm_path):
                                        self.debug("- '%s'", _test_script_path)
                                        self.script_paths.remove(_test_script_path)

                    else:
                        # White list.
                        self.debug("White list line: %r", _line)
                        with self.pushindentation():
                            if _line.startswith("+"):
                                _line = _line[1:].strip()
                            if "*" in _line:
                                for _add_path in self.path.parent.glob(_line):  # type: typing.Optional[_PathType]
                                    assert _add_path
                                    if not _add_path.is_file():
                                        continue
                                    for _test_script_path in self.script_paths:  # type already declared above
                                        if _test_script_path.samefile(_add_path):
                                            _add_path = None
                                            break
                                    if _add_path is not None:
                                        self.debug("+ '%s'", _add_path)
                                        self.script_paths.append(_add_path)
                            else:
                                _add_path = self.path.parent / _line  # Type already declared above
                                self.debug("+ '%s'", _add_path)
                                self.script_paths.append(_add_path)

                except Exception as _err:
                    raise ErrorCodeError(
                        error_code=ErrorCode.INPUT_FORMAT_ERROR,
                        message=f"Error while parsing '{self.path}': {_err}",
                        exception=_err,
                    )
