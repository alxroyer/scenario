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
No-dependency module that makes data available without importing other modules.

Avoids cyclic module dependencies, and numerous local imports in the same time.

Nevertheless, usage of this global data approach shall be reserved when performance issues are revealed,
and justified in the related data docstring.
"""

import typing

if typing.TYPE_CHECKING:
    from ._args import Args as _ArgsType
    from ._configdb import ConfigDatabase as _ConfigDatabaseType
    from ._scenarioconfig import ScenarioConfig as _ScenarioConfigType


class FastPath:
    """
    Fast path data container.

    Avoids numerous local imports, especially in low-level functions (like logging functions for instance).
    """

    def __init__(self):  # type: (...) -> None
        """
        Declares fast path data.
        """
        #: :class:`._args.Args` instance installed.
        #:
        #: Reference set by :meth:`._args.Args.setinstance()`.
        self.args = None  # type: typing.Optional[_ArgsType]

        #: :class:`._configdb.ConfigDatabase` instance installed.
        #:
        #: Singleton reference resolved by :meth:`config_db()` property.
        self._config_db = None  # type: typing.Optional[_ConfigDatabaseType]

        #: :class:`._scenarioconfig.ScenarioConfig` instance installed.
        #:
        #: Singleton reference resolved by :meth:`scenario_config()` property.
        self._scenario_config = None  # type: typing.Optional[_ScenarioConfigType]

    @property
    def config_db(self):  # type: () -> _ConfigDatabaseType
        """
        :class:`._configdb.ConfigDatabase` instance installed.
        """
        if self._config_db is None:
            from ._configdb import CONFIG_DB
            self._config_db = CONFIG_DB
        return self._config_db

    @property
    def scenario_config(self):  # type: () -> _ScenarioConfigType
        """
        :class:`._scenarioconfig.ScenarioConfig` instance installed.
        """
        if self._scenario_config is None:
            from ._scenarioconfig import SCENARIO_CONFIG
            self._scenario_config = SCENARIO_CONFIG
        return self._scenario_config


#: Main instance of :class:`FastPath`.
FAST_PATH = FastPath()
