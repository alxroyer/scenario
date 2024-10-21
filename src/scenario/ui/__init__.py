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
:mod:`scenario.ui` subpackage definition.

:mod:`scenario.ui` provides a HTTP user interface that:

- lists requirements,
- lists test suites and test cases,
- displays test case details (steps, actions, expected results),
- displays campaign results,
- displays requirement traceability reports.

Subpackage of :mod:`scenario`,
but designed as an independant package, relying on it as some tier user software would do
(except for a couple of inner symbols not officially exported by :mod:`scenario`).
"""

import typing


# Export management
# =================

# Explicit export declarations (see https://docs.python.org/3/tutorial/modules.html#importing-from-a-package).
__all__ = []  # type: typing.List[str]


# Documentation management
# ========================

# See 'scenario/__init__.py'.


__doc__ += """
Package exports
===============
"""

if True:
    __doc__ += """
    .. py:attribute:: main

        User interface launcher.

        .. seealso:: :func:`._main.main()` implementation.
    """
    from ._main import main as main
    __all__.append("main")

if True:
    __doc__ += """
    .. py:attribute:: Args

        User interface program arguments.

        .. seealso:: :class:`._args.UIArgs` implementation.
    """
    from ._args import UIArgs as Args
    __all__.append("Args")

if True:
    __doc__ += """
    .. py:attribute:: ConfigKey

        `scenario` configuration keys.

        .. seealso:: :class:`._scenarioconfig.ScenarioConfig.Key` implementation.
    """
    # Note: Can't reexport `ScenarioConfig.Key` as `ConfigKey` with a single `import` statement. Use an intermediate private instance.
    from ._configdb import UIConfig as _UIConfigImpl  # @module-level-instantiation
    ConfigKey = _UIConfigImpl.Key
    __all__.append("ConfigKey")
