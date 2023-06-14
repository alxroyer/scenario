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
if typing.TYPE_CHECKING:
    from ._path import AnyPathType as _AnyPathType


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
        from ._path import Path

        _LoggerImpl.__init__(self, log_class=DebugClass.TEST_SUITE_FILE)

        #: Test suite file path.
        self.path = Path(path)  # type: Path

        #: Script paths describes by the test suite file.
        #:
        #: Filled once the test suite file has been successfully read.
        #:
        #: .. seealso:: :meth:`read()`.
        self.script_paths = []  # type: typing.List[Path]

    def __repr__(self):  # type: () -> str
        """
        Canonical string representation.
        """
        from ._reflection import qualname

        return f"<{qualname(type(self))} path='{self.path}'>"

    def read(self):  # type: (...) -> bool
        """
        Reads and parses the test suite file.

        :return: ``True`` for success, ``False`` otherwise.
        """
        from ._path import Path
        from ._textfile import TextFile

        # Reset the script path list in case :meth:`parse()` is called several times..
        self.script_paths = []

        # Foe each line in the campaign file.
        self.debug("Reading '%s'", self.path)
        self.pushindentation()
        for _line in TextFile(self.path, "r").readlines():  # type: str
            _line = _line.strip()
            if not _line:
                continue
            if _line.startswith("#"):
                continue

            if _line.startswith("-"):
                # Black list.
                _line = _line[1:].strip()
                self.debug("Black list line: %r", _line)
                self.pushindentation()
                for _rm_path in self.path.parent.glob(_line):  # type: Path
                    for _test_script_path in self.script_paths:  # type: Path
                        if _test_script_path.samefile(_rm_path):
                            self.debug("- '%s'", _test_script_path)
                            self.script_paths.remove(_test_script_path)
                self.popindentation()

            else:
                # White list.
                self.debug("White list line: %r", _line)
                self.pushindentation()
                if _line.startswith("+"):
                    _line = _line[1:].strip()
                if "*" in _line:
                    for _add_path in self.path.parent.glob(_line):  # type: typing.Optional[Path]
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
                self.popindentation()
        self.popindentation()

        return True
