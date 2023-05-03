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
Text file management.
"""

import io
import re
import typing

if typing.TYPE_CHECKING:
    from ._path import AnyPathType


class TextFile:
    """
    Wrapper for reading and writing text files.

    This class doesn't aim to be a faithful IO class, but rather a wrapper to common file operations.
    """

    def __init__(
            self,
            path,  # type: AnyPathType
            mode,  # type: str
            encoding=None,  # type: str
    ):  # type: (...) -> None
        """
        :param path: File path.
        :param mode: "r" or "w".
        :param encoding: Explicit file encoding when specified.
                         Will be guessed from the input file when reading otherwise.
                         UTF-8 by default.
        """
        io.IOBase.__init__(self)

        #: Python file instance.
        self._file = open(__file__, "rb")  # type: typing.BinaryIO
        assert mode in ("r", "w")
        if mode == "w":
            self._file = open(path, mode="wb")
        else:
            self._file = open(path, mode="rb")

        #: File encoding.
        self.encoding = "utf-8"  # type: str
        if encoding is not None:
            self.encoding = encoding
        elif mode == "r":
            self._guessencoding()

    def _guessencoding(self):  # type: (...) -> None
        """
        Tries to guess the file encoding from a dedicated comment in the first lines of it.

        Stores the result in the :attr:`encoding` attribute.
        """
        # Read up to 2 lines at the beginning of the file, and check for a coding specification.
        _lines = 2
        while _lines > 0:
            _first_line = self._file.readline()  # type: bytes
            if not _first_line:
                break
            # Inspired from https://www.python.org/dev/peps/pep-0263/
            _match = re.match(rb'^[ \t\f]*#.*?coding[:=][ \t]*([-_.a-zA-Z0-9]+)', _first_line)
            if _match:
                self.encoding = _match.group(1).decode("utf-8")
                break
            _lines -= 1
        # Reset the cursor at the beginning of the file.
        self._file.seek(0)

    def read(
            self,
            size=-1,  # type: int
    ):  # type: (...) -> str
        """
        Reads a string from the file.

        :param size: Size to read.
        :return: Content string.
        """
        _file_content = self._file.read(size)  # type: bytes
        return _file_content.decode(self.encoding)

    def readlines(self):  # type: (...) -> typing.List[str]
        """
        Reads all lines from a file.

        :return: File lines.
        """
        return self.read().splitlines()

    def write(
            self,
            text,  # type: str
    ):  # type: (...) -> int
        """
        Writes a string to the file.

        :param text: String to write.
        :return: Number of bytes written. May not equal the string length depending on the encoding.
        """
        return self._file.write(text.encode(self.encoding))

    def close(self):  # type: (...) -> None
        """
        Closes the file.
        """
        self._file.close()


def guessencoding(
        path,  # type: AnyPathType
):  # type: (...) -> str
    """
    Return the encoding guessed from a text file.

    :param path: Path of the file to guess encoding for.
    :return: Encoding guessed from the file. UTF-8 by default.

    .. seealso:: :meth:`TextFile._guessencoding()` and :attr:`TextFile.encoding`.
    """
    return TextFile(path, "r").encoding
