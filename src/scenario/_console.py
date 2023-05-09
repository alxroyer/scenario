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
Console management.
"""

import enum
import sys
import typing


class Console:
    """
    Console management.
    """

    class Color(enum.IntEnum):
        """
        Log colors.

        Color numbers as they are used in the console.
        """
        RESET = 0  #: Code color to reset colors.
        WHITE01 = 1  #: White.
        DARKGREY02 = 2  #: Dark grey.
        BLACK30 = 30  #: Black.
        RED31 = 31  #: Red.
        GREEN32 = 32  #: Green.
        YELLOW33 = 33  #: Yellow.
        DARKBLUE34 = 34  #: Dark blue.
        PURPLE35 = 35  #: Purple.
        LIGHTBLUE36 = 36  #: Light blue.
        LIGHTGREY37 = 37  #: Light grey.
        DARKGREY90 = 90  #: Another dark grey.
        RED91 = 91  #: Another red.
        GREEN92 = 92  #: Another green.
        YELLOW93 = 93  #: Another yellow.
        DARKBLUE94 = 94  #: Another dark blue.
        PURPLE95 = 95  #: Another purple.
        LIGHTBLUE96 = 96  #: Another light blue.
        WHITE97 = 97  #: Another white.
        LIGHTGREY98 = 98  #: Another light grey.


def disableconsolebuffering():  # type: (...) -> None
    """
    Disables stdout & stderr buffering.
    """

    class Unbuffered:
        """
        Inspired from https://stackoverflow.com/questions/107705/disable-output-buffering.
        """

        def __init__(
                self,
                stream,  # type: typing.TextIO
        ):  # type: (...) -> None
            self.stream = stream  # type: typing.TextIO

        def write(
                self,
                data,  # type: str
        ):  # type: (...) -> None
            self.stream.write(data)
            self.stream.flush()

        def writelines(
                self,
                datas,  # type: typing.List[str]
        ):  # type: (...) -> None
            self.stream.writelines(datas)
            self.stream.flush()

        def __getattr__(
                self,
                attr,  # type: str
        ):  # type: (...) -> typing.Any
            return getattr(self.stream, attr)

    sys.stdout = Unbuffered(sys.stdout)  # type: ignore[assignment]  ## Expression has type "Unbuffered", variable has type "IO[str]"
    sys.stderr = Unbuffered(sys.stderr)  # type: ignore[assignment]  ## Expression has type "Unbuffered", variable has type "IO[str]"
