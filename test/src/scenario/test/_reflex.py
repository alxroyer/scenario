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
Package black list implementation
inspired from https://stackoverflow.com/questions/1350466/preventing-python-code-from-importing-certain-modules#47854417.
"""

import builtins
import importlib
import types
import typing


#: List of package names which imports are black-listed.
PACKAGE_BLACK_LIST = []  # type: typing.List[str]


#: Configuration key that defines a comma-separated list of black-listed package names.
#:
#: Actually, this configuration key never reaches the configuration database,
#: but is rather defined for passing on configurations through command line arguments only:
#:
#: - When a package black list must be defined for a subprocess,
#:   the :meth:`scenario.test.SubProcess.run()` override uses the 'test/tools/package-black-list-starter.py' as an intermediate script
#:   with a ``--config-value`` option set with this configuration key.
#: - The 'package-black-list-starter.py' script catches and drops the related ``--config-value`` options,
#:   and feeds the :attr:`PACKAGE_BLACK_LIST`.
#: - The 'package-black-list-starter.py' script eventually executes the final launcher script
#:   with the given package black list being configured.
PACKAGE_BLACK_LIST_CONF_KEY = "scenario.test.package-black-list"  # type: str


def _blacklistimporter(
        name,  # type: str
        globals=None,  # type: typing.Optional[typing.Mapping[str, typing.Any]]  # noqa  ## Shadows the built-in name 'globals'
        locals=None,  # type: typing.Optional[typing.Mapping[str, typing.Any]]  # noqa  ## Shadows the built-in name 'locals'
        fromlist=(),  # type: typing.Sequence[str]
        level=0,  # type: int
):  # type: (...) -> types.ModuleType
    # Check whether the package name is in the black list.
    if name in PACKAGE_BLACK_LIST:
        raise ImportError(f"Module '{name}' black-listed")

    # Regular import by default.
    return importlib.__import__(name, globals, locals, fromlist, level)


# Install our `_blacklistimporter()` function as the python global importer function.
builtins.__import__ = _blacklistimporter
