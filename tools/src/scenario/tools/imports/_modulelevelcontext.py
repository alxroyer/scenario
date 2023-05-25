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

import re
import typing

import scenario


class ModuleLevelContext:
    def __init__(
            self,
            path,  # type: scenario.Path
            line_number,  # type: int
            src,  # type: typing.Optional[bytes]
    ):  # type: (...) -> None
        if line_number <= 0:
            raise ValueError(f"Invalid line number {line_number!r}")

        self.path = path  # type: scenario.Path

        #: Module level context starting definition line.
        self.line_number = line_number  # type: int

        #: Ending definition line.
        #:
        #: May differ from :attr:`.line_number2`, especially for docstrings and function definitions.
        #: Not set until the context is fully defined.
        self._ending_line_number = None  # type: typing.Optional[int]

        #: Code context source.
        #:
        #: ``None`` for pure module level contexts.
        #: Initialized otherwise with :meth:`__init__()`, then possibly continued with :meth:`feed()`.
        self.src = None  # type: typing.Optional[bytes]

        if src:
            # Use `feed()` in order to determine whether this is a one-line definition or not.
            self.feed(line_number, src)
        else:
            # Automatically consider pure module level contexts as fully defined.
            self._ending_line_number = line_number

    def __repr__(self):  # type: () -> str
        return "".join([
            "<CodeContext",
            " pure-module-level" if self.ispuremodulelevel() else "",
            " docstring" if self.isdocstring() else "",
            " try-block" if self.istryblock() else "",
            (
                " if-block-impl" if self.isifblockimpl()
                else " if-block-type" if self.isifblocktype()
                else " if-block-main" if self.isifblockmain()
                else f" if-block {self.src!r}" if self.isifblock()
                else ""
            ),
            f" function {self.src!r}" if self.isfunction() else "",
            f" {self.src!r}" if self.isclass() else "",
            ">",
        ])

    def isanymodulelevel(self):  # type: (...) -> bool
        return any([
            self.ispuremodulelevel(),
            self.istryblock(),
            self.isifblockimpl(),
            self.isifblocktype(),
            self.isifblockmain(),
            self.isifblock(),
        ])

    def ispuremodulelevel(self):  # type: (...) -> bool
        return self.src is None

    def isdocstring(self):  # type: (...) -> bool
        # Memo: Don't end the regex with '$'. Just check the starting pattern.
        return self._checkregex(rb'^(__doc__ *\+ *= *)?""".*')

    def istryblock(self):  # type: (...) -> bool
        return self._checkregex(rb'^try *:$')

    def isifblock(self):  # type: (...) -> bool
        return self._checkregex(rb'^if +(.+) *:$')

    def isifblockimpl(self):  # type: (...) -> bool
        return self._checkregex(rb'^if +True *:$')

    def isifblocktype(self):  # type: (...) -> bool
        return self._checkregex(rb'^if +typing *\. *TYPE_CHECKING *:$')

    def isifblockmain(self):  # type: (...) -> bool
        return self._checkregex(rb'^if +__name__ *== *"__main__" *:$')

    def isunqualifiedifblock(self):  # type: (...) -> bool
        return self.isifblock() and (not any([
            self.isifblockimpl(),
            self.isifblocktype(),
            self.isifblockmain(),
        ]))

    def isfunction(self):  # type: (...) -> bool
        # Memo: Don't search for a final '):' pattern.
        return self._checkregex(rb'^def +([^ ]+) *\(.*$')

    def isclass(self):  # type: (...) -> bool
        return self._checkregex(rb'class +([^ ]+)( *\(.*\))? *:$')

    def _checkregex(
            self,
            regex,  # type: bytes
    ):  # type: (...) -> bool
        if self.src is not None:
            return re.match(regex, self.src) is not None
        return False

    def isfullydefined(self):  # type: (...) -> bool
        return self._ending_line_number is not None

    def feed(
            self,
            line_number,  # type: int
            line,  # type: bytes
    ):  # type: (...) -> None
        from ._moduleparser import ModuleParser

        _just_initialized = False  # type: bool
        if self.src is None:
            self.line_number = line_number
            self.src = ModuleParser.stripsrc(line)
            _just_initialized = True

        # Track context definition endings.
        if self._ending_line_number is None:
            if self.isdocstring():
                if not _just_initialized:
                    self.src += (b'\n' + line.rstrip())
                    if self.src.endswith(b'"""'):
                        self._ending_line_number = line_number
            elif self.isfunction():
                if not _just_initialized:
                    self.src += ModuleParser.stripsrc(line)
                if self.src.endswith(b'):'):
                    self._ending_line_number = line_number
            else:
                self._ending_line_number = line_number
