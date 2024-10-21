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

if True:
    from ._errortrackerlogger import ErrorTrackerLogger as _ErrorTrackerLoggerImpl  # @inheritance
if typing.TYPE_CHECKING:
    from ._import import Import as _ImportType


class ModuleParser(_ErrorTrackerLoggerImpl):

    def __init__(
            self,
            path,  # type: scenario.Path
    ):  # type: (...) -> None
        _ErrorTrackerLoggerImpl.__init__(self, f"{path}:")

        self.path = path  # type: scenario.Path

        self._imports = []  # type: typing.List[_ImportType]
        self._module_level_imports = None  # type: typing.Optional[typing.Sequence[_ImportType]]
        self._implementation_imports = None  # type: typing.Optional[typing.Sequence[_ImportType]]
        self._typing_imports = None  # type: typing.Optional[typing.Sequence[_ImportType]]
        self._local_imports = None  # type: typing.Optional[typing.Sequence[_ImportType]]

    def parse(self):  # type: (...) -> None
        from ._import import Import
        from ._modulelevelcontext import ModuleLevelContext

        _context = ModuleLevelContext(
            path=self.path, line_number=1, src=None,
            upper_context=None,
        )  # type: ModuleLevelContext

        for _line_number, _line in enumerate(self.path.read_bytes().splitlines()):  # type: int, bytes
            # Line numbers start from 1.
            _line_number += 1

            self.debug("%d: %r: %r", _line_number, _context, _line)

            # Context definition continuation.
            if not _context.isfullydefined():
                _context.feed(_line_number, _line)
                if _context.isfullydefined():
                    self.debug("%d: %r fully defined", _line_number, _context)
                    if _context.isdocstring():
                        _context = ModuleLevelContext(
                            path=self.path, line_number=_line_number + 1, src=None,
                            upper_context=None,
                        )
                        self.debug("%d: New context: %r", _line_number, _context)
                continue

            # Back to upper context(s) when applicable.
            while _context.isbrokenby(_line) and _context.upper_context:
                _context = _context.upper_context
                self.debug("%d: Back to upper context: %r", _line_number, _context)

            # Import line, at any level.
            if re.match(rb'^import +.+$', _line.strip()) or re.match(rb'^from +[^ ]+ +import +.*$', _line.strip()):
                # Save the import.
                self._imports.append(Import(self.path, _line_number, _context, _line))
                continue

            # Module level lines.
            if _line and (not _line.startswith((b' ', b'\t', b'#'))):
                # New contexts.
                if any([
                    re.match(rb'^(__doc__ *\+= *)?"""$', _line),
                    re.match(rb'^try *:$', _line),
                    re.match(rb'^if +(.*) *:$', _line),
                    re.match(rb'^with +(.*) *:$', _line),
                    re.match(rb'^def .*\(.*$', _line),
                    re.match(rb'^class .*:$', _line),
                ]):
                    _context = ModuleLevelContext(
                        path=self.path, line_number=_line_number, src=_line,
                        upper_context=_context,
                    )
                    self.debug("%d: New context: %r", _line_number, _context)
                    continue

                # Skipped lines.
                if any([
                    # `try` blocks.
                    re.match(rb'^except.*:.*$', _line),
                    re.match(rb'^finally *:.*$', _line),
                    # Assignments.
                    b'=' in _line,
                    re.match(rb'^[)\]}] *# +type: .*$', _line),
                    # Function & method calls.
                    re.search(rb'\. *(append|debug|exit|insert) *\(', _line),
                ]):
                    self.debug("%d: Line skipped", _line_number)
                    continue

                # Unexpected lines.
                raise SyntaxError(f"Unexpected line {_line_number} at module level: {_line!r}")

            # Type checking blocks, inside other block.
            _candidate_context = ModuleLevelContext(
                path=self.path, line_number=_line_number, src=_line,
                upper_context=_context,
            )  # type: ModuleLevelContext
            if _candidate_context.isifblocktype() and not any([
                _context.isfunction(),
                _context.isclass(),
            ]):
                _context = _candidate_context
                self.debug("%d: New context: %r", _line_number, _context)
                continue

    @property
    def imports(self):  # type: () -> typing.Sequence[_ImportType]
        return self._imports

    @property
    def module_level_imports(self):  # type: () -> typing.Sequence[_ImportType]
        if self._module_level_imports is None:
            self._module_level_imports = list(filter(
                lambda imp: imp.context.isanymodulelevel(),
                self._imports,
            ))
        return self._module_level_imports

    @property
    def implementation_imports(self):  # type: () -> typing.Sequence[_ImportType]
        if self._implementation_imports is None:
            self._implementation_imports = list(filter(
                lambda imp: imp.context.isifblockimpl(),
                self._imports,
            ))
        return self._implementation_imports

    @property
    def typing_imports(self):  # type: () -> typing.Sequence[_ImportType]
        if self._typing_imports is None:
            self._typing_imports = list(filter(
                lambda imp: imp.context.isifblocktype(),
                self._imports,
            ))
        return self._typing_imports

    @property
    def local_imports(self):  # type: () -> typing.Sequence[_ImportType]
        if self._local_imports is None:
            self._local_imports = list(filter(
                lambda imp: not imp.context.isanymodulelevel(),
                self._imports,
            ))
        return self._local_imports

    @staticmethod
    def stripsrc(
            line,  # type: bytes
    ):  # type: (...) -> bytes
        """
        Strips the trailing comment from the source line if any.
        Also strips leading and trailing whitespaces.
        """
        _match = re.match(rb'^([^#]*)( *#.*)?$', line.strip())  # type: typing.Optional[typing.Match[bytes]]
        assert _match and (_match.group(1) is not None), f"Invalid source line {line!r}"
        return _match.group(1).strip()
