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

import typing

import scenario
import scenario.inners


def ensurelicenseheader(
        path,  # type: scenario.Path
):  # type: (...) -> None
    """
    Ensures license header in ``path``.

    :param path: Path of the file to ensure license header into.
    """
    # Ensure `path` is of a compatible format.
    if not scenario.inners.JsonDict.isyaml(path):
        raise ValueError(f"Not a YAML file '{path}'")

    # Read the file and find the encoding specification line in `path`.
    _dest_lines = path.read_bytes().splitlines()  # type: typing.List[bytes]
    _dest_index = _dest_lines.index(b'# -*- coding: utf-8 -*-') + 1  # type: int

    # Let's copy the license header of this source file.
    # Find the encoding specification line as well.
    _src_lines = scenario.Path(__file__).read_bytes().splitlines()  # type: typing.List[bytes]
    _src_index = _src_lines.index(b'# -*- coding: utf-8 -*-') + 1  # type: int

    # Copy each line up to the first `import` line in this source file.
    while not _src_lines[_src_index].startswith(b'import'):
        _dest_lines.insert(_dest_index, _src_lines[_src_index])
        _src_index += 1
        _dest_index += 1

    # Remove unnecessary blank lines after the license header.
    while not _dest_lines[_dest_index]:
        del _dest_lines[_dest_index]
    # Ensure a final blank line.
    if _dest_lines[-1]:
        _dest_lines.append(b'')

    # Update `path` in the end.
    path.write_bytes(b'\n'.join(_dest_lines))
