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


def tracktoolversion(
        tool_name,  # type: str
        cmd_line,  # type: typing.List[typing.Union[str, scenario.AnyPathType]]
        cwd=None,  # type: scenario.AnyPathType
        exit_on_error=True,  # type: bool
):  # type: (...) -> typing.Optional[str]
    """
    Checks that a tool exists and tracks its version.

    :param tool_name: Tool name, for display purpose.
    :param cmd_line: Command line used to display the tool's version.
    :param cwd: Current working directory to use, if required.
    :param exit_on_error: ``False`` when the program should not fail if the tool is not found. ``True`` by default.
    :return: Version of the tool if found, ``None`` otherwise.
    """
    from ._subprocess import SubProcess

    _cmd = SubProcess(*cmd_line)  # type: SubProcess
    if cwd:
        _cmd.setcwd(cwd)
    _cmd.showstdout(False).showstderr(False)
    _cmd.exitonerror(exit_on_error)
    _cmd.run()

    scenario.logging.debug("%s: reading _version", tool_name)
    _version = _cmd.stdout  # type: bytes
    if not _version:
        # dot, ... print out their version in stderr.
        _version = _cmd.stderr
    assert _version

    _version = _version.splitlines()[0].strip()
    scenario.logging.debug("%s: _version=%r", tool_name, _version)
    # "Python 3.8.6"
    # "mypy 0.770"
    # "sphinx-apidoc 3.0.4"
    # "sphinx-build 3.0.4"
    if _version.lower().startswith(tool_name.lower().encode("utf-8")):
        _version = _version[len(tool_name):].lstrip()
        scenario.logging.debug("%s: _version=%r", tool_name, _version)
    # "dot - graphviz version 2.44.1 (20200629.0800)"
    if b'version' in _version:
        _version = _version[_version.find(b'version') + len(b'version'):].lstrip()
        scenario.logging.debug("%s: _version=%r", tool_name, _version)
    # "java version "1.8.0_251""
    if _version.startswith(b'"') and _version.endswith(b'"'):
        _version = _version[1:-1]
    # "chmod (GNU coreutils) 8.26"
    if _version.startswith(b'(') and (b')' in _version):
        _version = _version[_version.find(b')') + 1:].lstrip()
        scenario.logging.debug("%s: _version=%r", tool_name, _version)
    scenario.logging.info(f"VERSION: {tool_name} = {_version.decode('utf-8')}")
    return _version.decode("utf-8")
